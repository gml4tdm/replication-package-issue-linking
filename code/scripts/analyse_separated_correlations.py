################################################################################
################################################################################
# Imports
################################################################################

from __future__ import annotations

import collections
import dataclasses
import itertools
import json
import pathlib
import typing

import pandas
import tap
import texttable

import matplotlib.pyplot as pyplot
import matplotlib.colors as mpl_colors
import seaborn

################################################################################
################################################################################
# Auxiliary data types
################################################################################


@dataclasses.dataclass
class Statistics:
    statistic: float
    p_value: float

    @classmethod
    def from_json(cls, data: dict[str, float]):
        return cls(
            statistic=data['statistic'],
            p_value=data['p-value']
        )


################################################################################
################################################################################
# Table formatting
################################################################################


class TableText:
    class Underline:
        def __init__(self, text: FormattedText):
            self.text = text
        def render_markdown(self) -> str:
            return f'<ins>{_maybe_render(self.text, "markdown")}</ins>'
        def render_latex(self) -> str:
            return f'\\underline{{{_maybe_render(self.text, "latex")}}}'
    class Bold:
        def __init__(self, text: FormattedText):
            self.text = text
        def render_markdown(self) -> str:
            return f'**{_maybe_render(self.text, "markdown")}**'
        def render_latex(self) -> str:
            return f'\\textbf{{{_maybe_render(self.text, "latex")}}}'
    class Italic:
        def __init__(self, text: FormattedText):
            self.text = text
        def render_markdown(self) -> str:
            return f'*{_maybe_render(self.text, "markdown")}*'
        def render_latex(self) -> str:
            return f'\\textit{{{_maybe_render(self.text, "latex")}}}'
    class Monospace:
        def __init__(self, text: FormattedText):
            self.text = text
        def render_markdown(self) -> str:
            return f'`{_maybe_render(self.text, "markdown")}`'
        def render_latex(self) -> str:
            return f'\\texttt{{{_maybe_render(self.text, "latex")}}}'
    class Join:
        def __init__(self, sep: FormattedText, texts: list[FormattedText]):
            self.sep = sep
            self.texts = texts
        def render_markdown(self) -> str:
            return _maybe_render(self.sep, 'markdown').join(
                _maybe_render(text, "markdown")
                for text in self.texts
            )
        def render_latex(self) -> str:
            return _maybe_render(self.sep, 'latex').join(
                _maybe_render(text, "latex")
                for text in self.texts
            )
    class Concat:
        def __init__(self, *texts: FormattedText):
            self.texts = texts
        def render_markdown(self) -> str:
            return ''.join(
                _maybe_render(text, "markdown")
                for text in self.texts
            )
        def render_latex(self) -> str:
            return ''.join(
                _maybe_render(text, "latex")
                for text in self.texts
            )
    class Symbol:
        _table = {
            'markdown': {
                '*': '&ast;',
                '<': '&lt;',
                '>': '&gt;'
            },
            'latex': {
                '<': '$<$',
                '>': '$>$'
            }
        }
        def __init__(self, symbol: str):
            self.symbol = symbol
        def render_markdown(self) -> str:
            return self._table['markdown'].get(self.symbol, self.symbol)
        def render_latex(self) -> str:
            return self._table['latex'].get(self.symbol, self.symbol)


def _maybe_render(text: FormattedText, kind: str) -> str:
    if isinstance(text, str):
        return text
    if kind == 'markdown':
        return text.render_markdown()
    elif kind == 'latex':
        return text.render_latex()
    else:
        raise ValueError(f'Unknown kind {kind}')

FormattedText = typing.Union[
    str,
    TableText.Underline,
    TableText.Bold,
    TableText.Italic,
    TableText.Monospace,
    TableText.Join,
    TableText.Concat,
    TableText.Symbol
]


class Table:

    def __init__(self,
                 header: list[FormattedText], *,
                 row_headers: list[FormattedText] | None = None):
        self._header = header
        self._row_headers = row_headers
        self._rows = []

    def add_row(self, row: list[FormattedText]):
        self._rows.append(row)

    def render_latex(self):
        align = self._alignment('latex')
        text = ['\\toprule']
        text.append(
            ' & '.join(
                self._align(x, a) for x, a in zip(self._header, align)
            ) + '\\\\ \\midrule'
        )
        for row in self._full_rows('latex'):
            text.append(
                ' & '.join(self._align(x, a) for x, a in zip(row, align)) + '\\\\'
            )
        text.append('\\bottomrule')

        return '\n'.join(text)

    def _full_rows(self, kind: str):
        if self._row_headers is not None:
            for header, row in zip(self._row_headers, self._rows):
                rendered_row = [_maybe_render(cell, kind) for cell in row]
                yield [_maybe_render(header, kind)] + rendered_row
        else:
            for row in self._rows:
                rendered_row = [_maybe_render(cell, kind) for cell in row]
                yield rendered_row

    def _alignment(self, kind: str, tight=False):
        align = [len(h) for h in self._header]
        for row in self._full_rows(kind):
            for i, col in enumerate(row):
                align[i] = max(align[i], len(col))
        if not tight:
            align = [((a + 2) // 4 + 1) * 4 for a in align]
        return align

    @staticmethod
    def _align(x, a, *, fill=' '):
        y = a - len(x)
        return x + fill*y

    def render_text(self):
        table = texttable.Texttable()
        table.header(self._header)
        table.add_rows(self._full_rows())
        return table.draw()

    def render_markdown(self):
        align = self._alignment('markdown', tight=True)
        text = []
        # Header
        header_base = ' | '.join(self._align(x, a) for x, a in zip(self._header, align))
        text.append('| ' + header_base + ' |')
        # Sep
        fill_base = '-|-'.join(self._align('-', a, fill='-') for a in align)
        text.append('|-' + fill_base + '-|')
        # Rows
        for row in self._full_rows('markdown'):
            row_base = ' | '.join(self._align(x, a) for x, a in zip(row, align))
            text.append('| ' + row_base + ' |')
        # Join
        return '\n'.join(text)

################################################################################
################################################################################
# Auxiliary functions
################################################################################


def load_data(path: pathlib.Path) -> dict[str, dict[str, dict[str, dict[str, Statistics]]]]:
    data_by_method = collections.defaultdict(
        lambda: collections.defaultdict(
            lambda: collections.defaultdict(dict)
        )
    )
    for type_dir in path.iterdir():
        issue_type = type_dir.name
        for project_dir in type_dir.iterdir():
            project = project_dir.name
            with open(project_dir / 'correlations.json') as file:
                data = json.load(file)
            for key, value in data.items():
                method = key.split('sub-tokens-')[-1]
                for metric, stats in value.items():
                    parsed = Statistics.from_json(stats)
                    data_by_method[method][metric][project][issue_type] = parsed
    return data_by_method


def method_to_table(
        data: dict[str, dict[str, dict[str, Statistics]]],
        projects: dict[str, str],
        metrics: dict[str, str],
        issue_types: list[str]) -> Table:
    table = Table(
        header=['Method'] + list(projects.values()),
        row_headers=list(metrics.values())
    )
    for metric in metrics:
        row = []
        for project in projects:
            cell_content = [
                _format_correlation(data[metric][project][issue_type])
                for issue_type in issue_types
            ]
            cell = TableText.Join('/', cell_content)
            row.append(cell)
        table.add_row(row)
    return table


def _format_correlation(stats: Statistics) -> FormattedText:
    text = f'{stats.statistic:.2f}'
    if 0 <= abs(stats.statistic) < 0.19:
        text = text
    elif 0.19 <= abs(stats.statistic) < 0.4:
        text = TableText.Underline(text)
    elif 0.4 <= abs(stats.statistic) < 0.6:
        text = TableText.Bold(text)
    elif 0.6 <= abs(stats.statistic) < 0.8:
        text = TableText.Italic(text)
    elif 0.8 <= abs(stats.statistic) < 1.0:
        text = TableText.Monospace(text)
    if stats.p_value < 0.05:
        text = TableText.Concat(text, TableText.Symbol('*'))
        #text = TableText.Concat('<span style="color: red">', text, '</span>')
    return text


def method_to_heatmap(
        data: dict[str, dict[str, dict[str, Statistics]]],
        projects: dict[str, str],
        metrics: dict[str, str],
        issue_types: list[str]):
    matrix = []
    frame_data = collections.defaultdict(list)
    for metric in metrics:
        row = []
        for project in projects:
            for issue_type in issue_types:
                cell = _format_cell(data[metric][project][issue_type])
                row.append(cell)
                frame_data['project'].append(projects[project])
                frame_data['metric'].append(metric)
                frame_data['issue_type'].append(issue_type)
                frame_data['cell'].append(cell)
        matrix.append(row)

    viridis = pyplot.cm.get_cmap('viridis')
    cmap = mpl_colors.ListedColormap([
        'white',
        viridis(0/2),
        viridis(1/2),
        viridis(2/2)
    ])

    v_min = min(frame_data['cell'])
    v_max = max(frame_data['cell'])
    df = pandas.DataFrame(frame_data)
    grid = seaborn.FacetGrid(
        df, col='project', sharey=True,
        height=4, aspect=1
    )
    #cax = grid.fig.add_axes([.92, .12, .02, .8])
    grid.map_dataframe(
        _pandas_heatmap,
        vmin=v_min, vmax=v_max,
        cmap=cmap,
        linewidths=1.0,
        linecolor='black',
        cbar=False,
        #cbar_ax=cax,
        issue_types=issue_types, metrics=list(metrics),
    )
    #grid.fig.subplots_adjust(right=.9)
    grid.set_yticklabels(
        list(metrics.values()),
        rotation=0
    )
    grid.set_xticklabels(
        [tp[0].upper() for tp in issue_types]
    )
    grid.tick_params(
        labelsize=20
    )
    grid.set_titles(
        col_template="{col_name}",
        size=20
    )
    from matplotlib.patches import Patch
    from matplotlib.transforms import BboxTransformTo, TransformedBbox, Affine2D
    from matplotlib.transforms import Bbox

    legend_items = {
        'Insignificant ($p \\geq 0.05$)': Patch(
            facecolor=cmap(0/3),
            edgecolor='black',
            label='Insignificant ($p \\geq 0.05$)'
        ),
        'Very Weak ($|\\rho| \\in [0, 0.2)$)': Patch(
            facecolor=cmap(1/3),
            edgecolor='black',
            label='Very Weak ($|\\rho| \\in [0, 0.2)$)'
        ),
        'Weak ($|\\rho| \\in [0.2, 0.4)$)': Patch(
            facecolor=cmap(2/3),
            edgecolor='black',
            label='Weak ($|\\rho| \\in [0.2, 0.4)$)'
        ),
        'Moderate ($|\\rho| \\in [0.4, 0.6)$)': Patch(
            facecolor=cmap(3/3),
            edgecolor='black',
            label='Moderate ($|\\rho| \\in [0.4, 0.6)$)'
        ),
    }

    if len(grid.axes) % 2 == 0:
        raise NotImplementedError('Odd number of axes required')
    #grid.tight_layout()
    #grid.fig.set_constrained_layout(True)
    grid.figure.subplots_adjust(right=0.99, left=0.04)
    ax = grid.axes[0][len(grid.axes) // 2]
    alpha = 0.6
    print(grid.figure.subplotpars.bottom)
    beta = 0.05
    # bb = (
    #     grid.figure.subplotpars.left + (grid.figure.subplotpars.right - grid.figure.subplotpars.left)*(1 - alpha)/2,
    #     grid.figure.subplotpars.bottom - beta,
    #     (grid.figure.subplotpars.right - grid.figure.subplotpars.left) * alpha,
    #     beta

    # )
    grid.figure.legend(
        bbox_to_anchor=(0.5 - 0.7/2, -0.01, 0.7, 0.1),     # bb,
        mode='expand',
        handles=list(legend_items.values()),
        loc='lower left',
        ncol=4,
        #bbox_transform=grid.figure.transFigure,
        fontsize=20
    )
    grid.figure.subplots_adjust(bottom=0.26)

    pyplot.show()


def _pandas_heatmap(data, **kwargs):
    df = data
    issue_types = kwargs.pop('issue_types')
    metrics = kwargs.pop('metrics')
    as_dict = {}
    for p, m, c in df[['issue_type', 'metric', 'cell']].values:
        as_dict[(p, m)] = c
    matrix = []
    for metric in metrics:
        row = []
        for issue_type in issue_types:
            row.append(as_dict[(issue_type, metric)])
        matrix.append(row)
    return seaborn.heatmap(matrix, **kwargs)


    # fig, ax = pyplot.subplots()
    # seaborn.heatmap(
    #     matrix, annot=False, ax=ax, cmap='viridis',
    #     yticklabels=list(metrics),
    #     linewidths=0.5,
    # )
    # ax.set_xticks(
    #     [(i + 0.5) * len(issue_types) for i in range(len(projects))]
    # )
    # ax.set_xticklabels(
    #     list(projects.values()),
    #     # rotation=10,
    #     # ha='right',
    #     # #anchor='center'
    # )
    # pyplot.show()


def _format_cell(stats: Statistics) -> int:
    if stats.p_value >= 0.05:
        return 0
    if 0 <= abs(stats.statistic) < 0.19:
        return 1
    if 0.19 <= abs(stats.statistic) < 0.4:
        return 2
    if 0.4 <= abs(stats.statistic) < 0.6:
        return 3
    if 0.6 <= abs(stats.statistic) < 0.8:
        return 4
    if 0.8 <= abs(stats.statistic) < 1.0:
        return 5
    raise NotImplementedError(f'Unknown statistic value {stats.statistic}')


#
# def bootstrap_differences(
#         data: dict[str, dict[str, dict[str, dict[str, Statistics]]]]):
#     # data_by_method[method][metric][project][issue_type]
#     result = {}
#     for a, b in itertools.combinations(data, 2):
#         result[(a, b)] = bootstrap_difference(data[a], data[b])
#     return result
#
#
# def bootstrap_difference(
#         a: dict[str, dict[str, dict[str, Statistics]]],
#         b: dict[str, dict[str, dict[str, Statistics]]]):
#     # a[metric][project][issue_type]
#     # b[metric][project][issue_type]
#     result = {}
#     for metric in a:
#         result[metric] = {}
#         for project in a[metric]:
#             result[metric][project] = {}
#             for issue_type in a[metric][project]:
#                 result[metric][project][issue_type] = bootstrap_one(
#                     a[metric][project][issue_type],
#                     b[metric][project][issue_type]
#                 )
#     return result
#
#
# def bootstrap_one(a: Statistics, b: Statistics):
#     pass


################################################################################
################################################################################
# Main
################################################################################


class Args(tap.Tap):
    directory: pathlib.Path
    out: pathlib.Path
    projects: list[str] = [
        'avro:Avro',
        'maven:Maven',
        'tika:Tika',
        'thrift:Thrift',
        'tomee:TomEE',
        'spring-data-mongodb:DMDB',
        'spring-roo:Roo'
    ]
    metrics: list[str] = [
        'retrieval-precision-top-1:P@1',
        'retrieval-precision-top-5:P@5',
        'retrieval-precision-top-10:P@10',
        'hit-rate-top-5:H@5',
        'hit-rate-top-10:H@10',
        'retrieval-recall-top-1:R@1',
        'retrieval-recall-top-5:R@5',
        'retrieval-recall-top-10:R@10',
        'r-precision:RP',
        'mrr:MRR'
    ]
    issue_types: list[str] = [
        'bug',
        'feature',
        'improvement',
        'task'
    ]


def main(args: Args):
    data = load_data(args.directory)
    args.out.mkdir(parents=True, exist_ok=True)
    projects = {
        project.split(':')[0]: project.split(':')[1]
        for project in args.projects
    }
    metrics = {
        metric.split(':')[0]: metric.split(':')[1]
        for metric in args.metrics
    }
    table = method_to_table(
        data['bm25'],
        projects,
        metrics,
        args.issue_types
    )
    print(table.render_latex())


    with open(args.out / 'tables.md', 'w') as file:
        for method in data:
            file.write(f'# {method}\n\n')
            table = method_to_table(
                data[method],
                projects,
                metrics,
                args.issue_types
            )
            file.write(table.render_markdown())
            file.write('\n\n\n')
    method_to_heatmap(
        data['bm25'],
        projects,
        {m: metrics[m] for m in metrics if 'hit-rate' not in m},
        args.issue_types
    )


if __name__ == '__main__':
    main(Args(underscores_to_dashes=True).parse_args())
