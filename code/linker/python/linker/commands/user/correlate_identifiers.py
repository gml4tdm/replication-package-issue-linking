import json
import pathlib
import typing

import alive_progress
import matplotlib.pyplot as pyplot
import numpy
import pandas
import pingouin
import scipy.stats
import tap

from ...utils.issue_db import IssueDatabaseWrapper
from ...utils.text_cleaning.identifiers import count_identifiers
from ...features.file_utils import FeatureLoader
from ..._accelerator import LiveIndexLoader
from ..base import BaseCommand, register


class CorrelateIdentifiersConfig(tap.Tap):
    files: list[pathlib.Path]
    data_directory: pathlib.Path
    issue_directory: str
    split: str
    run_on: int
    output: pathlib.Path
    repo: str
    postgres_url: str
    no_plots: bool = False
    mode: typing.Literal[
        'normal',
        'issue-type-restricted',
        'issue-type-partial',
        'issue-type-ancova',
        'issue-type-ancova-interactions'
    ] = 'normal'
    restricted_issue_types: str | None = None
    metrics: list[str] = [
        'retrieval-precision-top-1',
        'retrieval-precision-top-5',
        'retrieval-precision-top-10',
        'hit-rate-top-5',
        'hit-rate-top-10',
        'retrieval-recall-top-1',
        'retrieval-recall-top-5',
        'retrieval-recall-top-10',
        'r-precision',
        'mrr'
    ]

    def configure(self) -> None:
        self.add_argument('--no-plots', action='store_true', default=False)



@register('correlate-identifiers')
class CorrelateIdentifiersCommand(BaseCommand):

    @staticmethod
    def config_type() -> type[tap.Tap]:
        return CorrelateIdentifiersConfig


    def execute(self):
        assert isinstance(self.config, CorrelateIdentifiersConfig)

        self.logger.info('Loading performance scores')
        scores = []
        for filename in self.config.files:
            with open(filename / 'performance.json') as file:
                data = json.load(file)
            if 'details' not in data:
                raise ValueError('File does not contain performance details')
            scores.append(data['details'])

        self.logger.info('Loading Index')
        loader = LiveIndexLoader.load(
            str(self.config.data_directory / 'index.json'),
        )

        bins = split(
            range(loader.number_of_issues),
            *(int(x) for x in self.config.split.split('/'))
        )
        selected_bin = bins[self.config.run_on]

        if not all(len(x) == len(selected_bin) for x in scores):
            raise ValueError('Number of issues in selected bin does not match')

        feature_loader = FeatureLoader(self.config.data_directory,
                                       self.config.issue_directory)

        self.logger.info('Computing Identifier Counts')
        counts = []
        counts_with_data = []
        with alive_progress.alive_bar(len(selected_bin)) as bar:
            for issue_index in selected_bin:
                collection = loader.get_issue(issue_index)
                commit = collection.get_commit(0)
                text_data = feature_loader.get_issue(commit.issue_index)

                if text_data['summary'] and text_data['description']:
                    raw_text = f'{text_data["summary"]}. {text_data["description"]}'
                elif text_data['summary']:
                    raw_text = text_data['summary']
                elif text_data['description']:
                    raw_text = text_data['description']
                else:
                    raw_text = ''

                counts.append(count_identifiers(raw_text))

                counts_with_data.append({
                    'issue-key': collection.issue_key,
                    'count': counts[-1],
                    'issue-type': None
                })

                bar()

        db = IssueDatabaseWrapper.from_url_sync(self.config.postgres_url)
        keys = [cnt['issue-key'] for cnt in counts_with_data]
        issues = db.get_issues_by_key_sync(
            self.config.repo,
            *keys
        )
        db.fetch_issue_fields_sync(
            list(issues.values()),
            'issue_type'
        )
        for cnt in counts_with_data:
            cnt['issue-type'] = issues[cnt['issue-key']].other_fields['issue_type']

        self.logger.info('Computing Correlations')
        self.config.output.mkdir(parents=True, exist_ok=True)

        with open(self.config.output / 'counts.json', 'w') as f:
            json.dump(counts_with_data, f, indent=2)

        #assert len(scores) == len(counts_with_data), [len(scores), len(counts_with_data)]
        assert all(len(x) == len(counts_with_data) for x in scores)
        assert len(counts) == len(counts_with_data)
        if self.config.mode in ('issue-type-restricted', 'issue-type-partial', 'issue-type-ancova', 'issue-type-ancova-interactions'):
            restricted_types = {}
            for group in self.config.restricted_issue_types.split(';'):
                group = group.strip()
                if ':' not in group:
                    raise ValueError('Invalid group')
                key, value = group.split(':')
                for v in value.split(','):
                    restricted_types[v.strip()] = key.strip()
            scores = [
                [
                    x
                    for x, y in zip(s, counts_with_data)
                    if y['issue-type'] in restricted_types
                ]
                for s in scores
            ]
            counts = [
                x
                for x, y in zip(counts, counts_with_data)
                if y['issue-type'] in restricted_types
            ]
            types = [
                restricted_types[x['issue-type']]  # type: ignore
                for x in counts_with_data
                if x['issue-type'] in restricted_types
            ]

        else:
            types = None

        # LIST[LIST[DICT]]
        # Outer lists: files
        # inner list: issues
        # dict: metric -> value
        scores = transpose([
            transpose(x) for x in scores
        ])
        correlations = {
            #'$all': {}
        }
        global_counts = []
        for _ in range(len(self.config.files)):
            global_counts.extend(counts)
        for metric_name in self.config.metrics:
            values = scores[metric_name]
            # File-specific correlations
            for path, value in zip(self.config.files, values):
                name = path.name
                if name not in correlations:
                    correlations[name] = {}
                if self.config.mode in ('normal', 'issue-type-restricted'):
                    correlations[name][metric_name] = correlate(counts, value)
                elif self.config.mode == 'issue-type-partial':
                    correlations[name][metric_name] = correlate_partial(counts, value, types)
                elif self.config.mode == 'issue-type-ancova' or self.config.mode == 'issue-type-ancova-interactions':
                    correlations[name][metric_name] = correlate_ancova(
                        counts, value, types, interactions=self.config.mode == 'issue-type-ancova-interactions'
                        )
                else:
                    raise ValueError(f'Unknown mode {self.config.mode}')
                if not self.config.no_plots:
                    self.scatter(counts, value, metric_name, name)
            # # Global correlations
            # global_values = []
            # for v in values:
            #     global_values.extend(v)
            # correlations['$all'][metric_name] = correlate(global_counts, global_values)
            # if not self.config.no_plots:
            #     self.scatter(global_counts, global_values, metric_name, 'all')
        with open(self.config.output / 'correlations.json', 'w') as f:
            json.dump(correlations, f, indent=2)         # type: ignore
            
    def scatter(self, x, y, metric, name):
        assert isinstance(self.config, CorrelateIdentifiersConfig)
        fig, ax = pyplot.subplots()
        ax.scatter(x, y)
        ax.set_xlabel('# Identifiers')
        ax.set_ylabel(metric)
        path = self.config.output / name
        path.mkdir(parents=True, exist_ok=True)
        fig.savefig(path / f'{metric}.png')
        pyplot.close(fig)


def correlate(x, y):
    result = scipy.stats.spearmanr(x, y)
    return {
        'p-value': result.pvalue,
        'statistic': result.statistic,
    }


def correlate_partial(x, y, z):
    # x, y, z = counts, values[scores], types
    assert len(x) == len(y)
    assert len(x) == len(z)
    dataframe = pandas.DataFrame({
        'x': x,
        'y': y,
        'z': z
    })
    result = pingouin.partial_corr(
        dataframe,
        x='x',
        y='y',
        covar='z',
        #x_covar='z',
        #y_covar='z',
        method='spearman'
    )
    return {
        'p-value': result['p-val']['spearman'],
        'statistic': result['r']['spearman'],
    }


def correlate_ancova(x, y, z, interactions=False):
    # x, y, z = counts, values[scores], types
    assert len(x) == len(y)
    assert len(x) == len(z)
    df = pandas.DataFrame({
        'x': x,
        'y': y,
        'z': z
    })
    #df = dataframe.get_dummies(columns=['z'])
    result = regression_analysis(
        ('performance',  df['y'].to_list()),
        [('issue-type', 'categorical', df['z'].to_list())],
        [('identifier-count', 'interval', df['x'].to_list())],
        include_interactions=interactions
    )
    return {
        'statistic': {
            k: v
            for k, v in zip(result['Source'].to_list(), result['F'].to_list())
            if k != 'Residual'
        },
        'p-value': {
            k: v
            for k, v in zip(result['Source'].to_list(), result['p-unc'].to_list())
            if k != 'Residual'
        },
        'effect-size': {
            k: v
            for k, v in zip(result['Source'].to_list(), result['effect'].to_list())
            if k != 'Residual'
        }
    }


def regression_analysis(dependent: tuple[str, list[float]],
                        independent: list[tuple[str, str, list[float]]],
                        covariates: list[tuple[str, str, list[float]]],
                        *,
                        include_interactions: bool = False,
                        include_intercept: bool = False) -> pandas.DataFrame:
    # Heavily based on https://pingouin-stats.org/build/html/_modules/pingouin/parametric.html#ancova
    from statsmodels.formula.api import ols, quantreg
    from statsmodels.api import stats
    def _fmt_term(name, kind):
        return f"C(Q('{name}'))" if kind == 'categorical' else f"Q('{name}')"
    terms = [
        _fmt_term(name, kind)
        for group in [independent, covariates]
        for name, kind, _ in group
    ]
    if include_interactions:
        terms.extend(
            f'{_fmt_term(name_1, kind_1)}:{_fmt_term(name_2, kind_2)}'
            for name_1, kind_1, _ in independent
            for name_2, kind_2, _ in covariates
        )
    if include_intercept:
        terms.append("1")
    formula = f"Q('{dependent[0]}') ~ {' + '.join(terms)}"
    # model = quantreg(
    #     formula,
    #     data={
    #         dependent[0]: dependent[1],
    #         **{
    #             name: values
    #             for name, _, values in independent
    #         },
    #         **{
    #             name: values
    #             for name, _, values in covariates
    #         }
    #     }
    # )
    # model = model.fit(q=0.5)
    # print(model.summary())
    # raise
    model = ols(
        formula,
        data={
            dependent[0]: dependent[1],
            **{
                name: values
                for name, _, values in independent
            },
            **{
                name: values
                for name, _, values in covariates
            }
        }
    )
    model = model.fit()
    aov = stats.anova_lm(model, typ=2).reset_index()
    aov.rename(
        columns={"index": "Source", "sum_sq": "SS", "df": "DF", "PR(>F)": "p-unc"}, inplace=True
    )
    for i in range(len(terms)):
        aov.at[i, 'Source'] = aov.at[i, 'Source'].replace("'", '').replace("C(", "").replace(")", "").replace("Q(", '')
    aov["DF"] = aov["DF"].astype(int)
    # Effect size;
    ss_resid = aov["SS"].iloc[-1]
    all_effect_size = aov["SS"].apply(lambda x: x / (x + ss_resid)).to_numpy()
    all_effect_size[-1] = numpy.nan
    aov['effect'] = all_effect_size
    return aov


def transpose(x: list[dict[str, typing.Any]]) -> dict[str, list[typing.Any]]:
    result = {}
    for item in x:
        for key, value in item.items():
            result.setdefault(key, []).append(value)
    return result


def split(items, *x):
    assert sum(x) == 100
    assert all(y > 0 for y in x)
    indices = []
    remaining = len(items)
    for i, y in enumerate(x[:-1]):
        i = _split_bin(remaining, y, sum(x[i+1:]))
        remaining -= i
        indices.append(i)
    return list(_make_splits(items, indices))


def _make_splits(items, indices):
    prev = 0
    for i in indices:
        yield items[prev:prev + i]
        prev += i
    yield items[prev:]


def _split_bin(total, p, q):
    y = total*p // (p + q)
    if abs(y/total - p/(p + q)) < abs((y + 1)/total - p/(p + q)):
        return y
    return y + 1


