import json
import pathlib
import re
import statistics
import warnings
import math

import tap
import matplotlib.pyplot as pyplot
import seaborn
import scipy.stats
import pandas

from ..base import BaseCommand, register


class MakeMatrixConfig(tap.Tap):
    files: list[pathlib.Path]
    row_pattern: str
    col_pattern: str
    out_dir: pathlib.Path


@register('make-matrix')
class MakeMatrix(BaseCommand):

    @staticmethod
    def config_type() -> type[tap.Tap]:
        return MakeMatrixConfig

    def execute(self):
        assert isinstance(self.config, MakeMatrixConfig)

        self.config.out_dir.mkdir(exist_ok=True, parents=True)

        with open(self.config.files[0]) as f:
            data = json.load(f)
        if isinstance(data['test'], dict):
            metrics = list(data['test'])
        else:
            metrics = list(data['test'][-1])

        print(self.config.files)

        stats = {}
        for m in metrics:
            (fig1, ax1), (fig2, ax2), stat = self._make_plot(m)
            fig1.savefig(str(self.config.out_dir / f'{m}.png'))
            if fig2 is not None:
                fig2.savefig(str(self.config.out_dir / f'{m}_density.png'))
            stats[m] = stat
            pyplot.close(fig1)
            if fig2 is not None:
                pyplot.close(fig2)
        with open(self.config.out_dir / 'stats.json', 'w') as f:
            json.dump(stats, f, indent=2)

    def _make_plot(self, metric: str):
        assert isinstance(self.config, MakeMatrixConfig)

        row = re.compile(self.config.row_pattern)
        col = re.compile(self.config.col_pattern)
        matrix = {}

        def _maybe_select(x, y):
            r = y.findall(x)
            if len(r) == 0:
                return ''
            return r[0]

        for filename in self.config.files:
            with open(filename) as f:
                data = json.load(f)
            if filename.name == 'performance.json':
                key = filename.parent.name
            else:
                key = filename.name.removesuffix('.json')
            r = _maybe_select(key, row)
            c = _maybe_select(key, col)
            #print(f'{filename} -> {r} x {c}')
            try:
                matrix.setdefault(r, {}).setdefault(c, []).append(
                    data['test'][metric] if isinstance(data['test'], dict) else data['test'][-1][metric]
                )
            except KeyError:
                av = ', '.join(data['test'])
                raise ValueError(f'Unknown metric {metric}. Available: {av}')

        cols = set()
        for v in matrix.values():
            cols.update(v.keys())

        rows = sorted(matrix)
        cols = sorted(cols)

        data = []
        for r in rows:
            current = []
            for c in cols:
                if r not in matrix or c not in matrix[r]:
                    warnings.warn(f'Missing data for {r} and {c}. Filling with 0')
                    current.append(0)
                else:
                    current.append(statistics.mean(matrix[r][c]))
            data.append(current)

        print(metric, data)

        fig, ax = pyplot.subplots()
        seaborn.heatmap(
            data,
            annot=True,
            cmap='coolwarm',
            fmt='.3f',
            xticklabels=cols,
            yticklabels=rows,
            ax=ax
        )


        stat = self._compute_statistic(rows, cols, matrix)
        #stat = None

        return (fig, ax), self._plot_densities(rows, cols, matrix), stat

    def _get_data_axis(self, rows, cols, data):
        if len(rows) > 1 and len(cols) > 1:
            return None
        if len(rows) == 1 and len(cols) == 1:
            return None

        if len(rows) >  1:
            names = rows
            data = [data.get(r, {}).get(cols[0], 0) for r in names]
        else:
            names = cols
            data = [data.get(rows[0], {}).get(c, 0) for c in names]

        return names, data

    def _plot_densities(self, rows, cols, data):
        x = self._get_data_axis(rows, cols, data)
        if x is None:
            return None, None
        names, data = x

        owner = []
        all_data = []
        for name, d in zip(names, data):
            owner += [name] * len(d)
            all_data += d

        df = pandas.DataFrame.from_dict({
            'score': all_data,
            'treatment': owner
        })

        fig, ax = pyplot.subplots()
        seaborn.kdeplot(df, x='score', hue='treatment', ax=ax)
        seaborn.rugplot(df, x='score', hue='treatment', ax=ax)

        return fig, ax

    def _compute_statistic(self, rows, cols, data):
        x = self._get_data_axis(rows, cols, data)
        if x is None:
            return
        names, data = x

        means = [statistics.mean(y) for y in data]
        medians = [statistics.median(y) for y in data]

        payload = {
            'mean': {
                'order': [
                    x
                    for _, x in sorted([(q, p) for p, q in zip(names, means)])
                ],
                'values': sorted(means),
            },
            'median': {
                'order': [
                    x
                    for _, x in sorted([(q, p) for p, q in zip(names, medians)])
                ],
                'values': sorted(medians),
            }
        }

        # Step 1: Check for normality of all means
        normals = [scipy.stats.shapiro(x) for x in data]
        is_normal = all(x.pvalue > 0.05 for x in normals)
        payload['normality-test'] = {
            'test': 'shapiro',
            'p-values': {
                name: x.pvalue
                for name, x in zip(names, normals)
            },
            'is-normal': _maybe_convert(is_normal)
        }

        # Step 2: Perform Test (independent samples)
        binary = len(data) == 2
        if is_normal and binary:
            # Student's t-test
            result = scipy.stats.ttest_ind(*data)
            payload['test'] = {
                'test': 'independent t-test',
                'p-value': result.pvalue,
                'significant': result.pvalue.item() < 0.05
            }
        elif is_normal and not binary:
            result = scipy.stats.f_oneway(*data)
            p = _maybe_convert(result.pvalue)
            payload['test'] = {
                'test': 'one-way ANOVA',
                'p-value': result.pvalue,
                'significant': p < 0.05
            }
        elif not is_normal and binary:
            # Mann-Whitney U test
            result = scipy.stats.mannwhitneyu(*data)
            payload['test'] = {
                'test': 'Mann-Whitney U test',
                'p-value': result.pvalue,
                'significant': result.pvalue.item() < 0.05
            }
        else:
            # Kruskal-Wallis test
            result = scipy.stats.kruskal(*data)
            payload['test'] = {
                'test': 'Kruskal-Wallis test',
                'p-value': result.pvalue,
                'significant': result.pvalue.item() < 0.05
            }

        if math.isnan(payload['test']['p-value']):
            payload['test'] = None


        return payload



def _maybe_convert(x):
    try:
        return x.item()
    except AttributeError:
        return x
