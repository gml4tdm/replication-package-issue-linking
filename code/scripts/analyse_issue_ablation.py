import itertools
import json
import pathlib
import pprint
import statistics
import sys

import matplotlib.pyplot as pyplot

import texttable


class Table:

    def __init__(self, header, *, row_headers=None):
        self._header = header
        self._row_headers = row_headers
        self._rows = []

    def add_row(self, row):
        self._rows.append(row)

    def render_latex(self):
        align = self._alignment()
        text = ['\\toprule']
        text.append(
            ' & '.join(
                self._align(x, a) for x, a in zip(self._header, align)
            ) + '\\\\ \\midrule'
        )
        for row in self._full_rows():
            text.append(
                ' & '.join(self._align(x, a) for x, a in zip(row, align)) + '\\\\'
            )
        text.append('\\bottomrule')

        return '\n'.join(text)

    def _full_rows(self):
        if self._row_headers is not None:
            for header, row in zip(self._row_headers, self._rows):
                yield [header] + row
        else:
            yield from self._rows

    def _alignment(self, tight=False):
        align = [len(h) for h in self._header]
        for row in self._full_rows():
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
        align = self._alignment(tight=True)
        text = []
        # Header
        header_base = ' | '.join(self._align(x, a) for x, a in zip(self._header, align))
        text.append('| ' + header_base + ' |')
        # Sep
        fill_base = '-|-'.join(self._align('-', a, fill='-') for a in align)
        text.append('|-' + fill_base + '-|')
        # Rows
        for row in self._full_rows():
            row_base = ' | '.join(self._align(x, a) for x, a in zip(row, align))
            text.append('| ' + row_base + ' |')
        # Join
        return '\n'.join(text)


_METRIC_MAPPING = {
    'retrieval-precision': 'Precision',
    'retrieval-recall': 'Recall',
    'mrr': 'MRR',
    'r-precision': 'r-Precision',
    'hit-rate': 'hit'
}


def rename_metric(m: str) -> str:
    if '-top-' in m:
        m, top = m.split('-top-')
        suffix = f'@{top}'
    else:
        suffix = ''
    return _METRIC_MAPPING[m] + suffix


def rename_project(m: str) -> str:
    return ' '.join(map(str.capitalize, m.split('-')))


project_order = [
    'avro',
    'maven',
    'tika',
    'thrift',
    'tomee',
    'spring-data-mongodb',
    'spring-roo',
]



def main(path: str, out: str):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)

    with open(path) as file:
        data = json.load(file)


    tables = []

    for method, by_method in data.items():
        by_metric_specific = {}
        by_metric_holdout = {}
        header = ['Metric']
        holdout_rows = {}
        specific_rows = {}
        holdout_rows_latex = {}
        specific_rows_latex = {}
        for project in project_order:
            by_project = by_method[project]
            header.append(rename_project(project))
            for metric, by_metric in by_project.items():
                H = by_metric["specific"]["pooled"]["statistic"]
                k = by_metric['specific']["pooled"]['n_groups']
                n = by_metric['specific']["pooled"]['n_observations']
                eta_squared = max(0, (H - k + 1) / (n - k))
                fmt = f'{eta_squared:.3f} / {by_metric["specific"]["pooled"]["p-value"]:.3f}'
                fmt_latex = f'{eta_squared:.3f}'
                if 0.01 <= eta_squared < 0.06:
                    fmt_latex = '\\underline{%s}' % fmt_latex
                    fmt = f'<ins>{fmt}</ins>'
                elif 0.06 <= eta_squared < 0.14:
                    fmt_latex = '\\textbf{%s}' % fmt_latex
                    fmt = f'**{fmt}**'
                elif 0.14 <= eta_squared:
                    # fmt_latex = '\\textbf{%s}' % fmt_latex
                    # fmt = f'**{fmt}**'
                    raise ValueError('No format specified for strong effect')
                if by_metric['specific']['pooled']['p-value'] < 0.05:
                    fmt_latex = f'{fmt_latex}*'
                    fmt = f'{fmt}&ast;'
                specific_rows.setdefault(rename_metric(metric), []).append(fmt)
                specific_rows_latex.setdefault(rename_metric(metric), []).append(fmt_latex)
                update_agg(by_metric_specific, metric, by_metric['specific'])

                H = by_metric["holdout"]["pooled"]["statistic"]
                k = by_metric['holdout']["pooled"]['n_groups']
                n = by_metric['holdout']["pooled"]['n_observations']
                eta_squared = max(0, (H - k + 1) / (n - k))
                fmt = f'{eta_squared:.3f} / {by_metric["holdout"]["pooled"]["p-value"]:.3f}'
                fmt_latex = f'{eta_squared:.3f}'
                if 0.01 <= eta_squared < 0.06:
                    fmt_latex = '\\underline{%s}' % fmt_latex
                    fmt = f'<ins>{fmt}</ins>'
                elif 0.06 <= eta_squared < 0.14:
                    fmt_latex = '\\textbf{%s}' % fmt_latex
                    fmt = f'**{fmt}**'
                elif 0.14 <= eta_squared:
                    # fmt_latex = '\\textbf{%s}' % fmt_latex
                    # fmt = f'**{fmt}**'
                    raise ValueError('No format specified for strong effect')
                if by_metric['holdout']['pooled']['p-value'] < 0.05:
                    fmt_latex = f'{fmt_latex}*'
                    fmt = f'{fmt}&ast;'
                holdout_rows.setdefault(rename_metric(metric), []).append(fmt)
                holdout_rows_latex.setdefault(rename_metric(metric), []).append(fmt_latex)
                update_agg(by_metric_holdout, metric, by_metric['holdout'])

        method_plot(data, method, 'specific', by_metric_specific, out)
        method_plot(data, method, 'holdout', by_metric_holdout, out)

        specific_table = Table(header, row_headers=specific_rows)
        for row in specific_rows.values():
            specific_table.add_row(row)
        holdout_table = Table(header, row_headers=holdout_rows)
        for row in holdout_rows.values():
            holdout_table.add_row(row)

        tables.append((method, specific_table.render_markdown(), holdout_table.render_markdown()))

        if method == 'bm25':
            specific_latex_table = Table(header, row_headers=specific_rows_latex)
            for row in specific_rows_latex.values():
                specific_latex_table.add_row(row)
            holdout_latex_table = Table(header, row_headers=holdout_rows_latex)
            for row in holdout_rows_latex.values():
                holdout_latex_table.add_row(row)
            print(specific_latex_table.render_latex())
            print(holdout_latex_table.render_latex())

    with open(out / 'tables.md', 'w') as file:
        for method, specific, holdout in tables:
            file.write(f'# {method}\n\n')
            file.write('### Specific\n\n')
            file.write(specific)
            file.write('\n\n\n')
            file.write('### Holdout\n\n')
            file.write(holdout)
            file.write('\n\n\n\n')


    detailed_tables(data, out)

        # pprint.pprint(by_metric_specific)
        #
        # pprint.pprint(by_metric_holdout)
        #



def update_agg(container, metric, data):
    x = container.setdefault(
        metric, {'significant': 0, 'total': 0, 'pairs': {}}
    )
    x['total'] += 1
    if data['pooled']['p-value'] < 0.05:
        x['significant'] += 1
        have_sig = False
        for item in data['pairwise']:
            if item['p-value'] >= 0.05:
                continue
            a, b = item['categories']
            if data['scores'][a] < data['scores'][b]:
                key = (a, '<', b)
            else:
                key = (b, '<', a)
            if key not in x['pairs']:
                x['pairs'][key] = 0
            x['pairs'][key] += 1
            have_sig = True
        if not have_sig:
            print('Significant Kruskal-Wallis without pairwise difference.')


def detailed_tables(data, out: pathlib.Path):
    spec = detailed_tables_key(data, 'specific', out)
    hold = detailed_tables_key(data, 'holdout', out)
    with open(out / 'pairwise-tables.md', 'w') as file:
        for key, value in spec.items():
            file.write(f'# {key}\n\n')
            file.write('### Specific\n\n')
            file.write(value)
            file.write('\n\n\n')
            file.write('### Holdout\n\n')
            file.write(hold[key])
            file.write('\n\n\n\n')



def detailed_tables_key(data, which, out: pathlib.Path, *, mode='md'):
    tables = []
    for method, by_method in data.items():
        header = ['Metric', 'Combination']
        tab_data = {}
        types = set()
        for project in project_order:
            by_project = by_method[project]
            header.append(rename_project(project))
            for metric, by_metric in by_project.items():
                by_metric = by_metric[which]
                types |= set(by_metric['scores'])
                #if by_metric['pooled']['p-value'] >= 0.05:
                #    tab_data.setdefault(key, {}).setdefault(metric, []).append(None)
                for item in by_metric['pairwise']:
                    a, b = sorted(item['categories'])
                    order = '<' if by_metric['scores'][a] < by_metric['scores'][b] else '>'
                    key = (a, b)
                    if by_metric['pooled']['p-value'] >= 0.05:
                        tab_data.setdefault(key, {}).setdefault(metric, []).append(None)
                    else:
                        tab_data.setdefault(key, {}).setdefault(metric, []).append((order, item['p-value']))

        table = Table(header)
        pairings = map(sorted, itertools.combinations(types, r=2))
        for a, b in pairings:
            if (a, b) not in tab_data:
                raise ValueError
            for m, values in tab_data[(a, b)].items():
                row = [f'{a} / {b}', rename_metric(m)]
                for x in values:
                    if x is None:
                        row.append('N/A')
                        continue
                    order, p = x
                    if mode == 'md':
                        order_sign = '&lt;' if order == '<' else '&gt;'
                        fmt = f'{p:.3f} ({order_sign})'
                        if p < 0.05:
                            fmt = f'**{fmt}**'
                    else:
                        order_sign = '$\\lt$' if order == '<' else '$\\gt$'
                        fmt = f'{p:.3f} ({order_sign})'
                        if p < 0.05:
                            fmt = '\\underline{%s}' % fmt
                    row.append(fmt)
                table.add_row(row)

        tables.append((method, table.render_markdown()))

    return dict(tables)


def method_plot(data, target_method, which, stats, out: pathlib.Path):
    bars_by_type = {}
    types = set()
    for method, by_method in data.items():
        if method != target_method:
            continue
        for project in project_order:
            by_project = by_method[project]
            for metric, by_metric in by_project.items():
                for tp, score in by_metric[which]['scores'].items():
                    bars_by_type.setdefault(metric, {}).setdefault(tp, []).append(score)
                    types.add(tp)

    fig, ax = pyplot.subplots(figsize=(8.27, 8.27 / 3))

    total_width = 0.75
    types = sorted(list(types))
    bar_width = total_width / len(types)
    x_base = list(range(len(bars_by_type)))
    metrics = list(bars_by_type)
    for i, tp in enumerate(types):
        ax.bar(
            [x - total_width/2 + bar_width*i + bar_width/2 for x in x_base],
            [statistics.mean(bars_by_type[m][tp]) for m in metrics],
            label=tp,
            width=bar_width
        )

    # for m, x in zip(metrics, x_base):
    #     n_tot = stats[m]['total']
    #     n_sig = stats[m]['significant']
    #     ax.text(
    #         x,
    #         max(statistics.mean(z) for z in bars_by_type[m].values()) + 0.01,
    #         f'{n_sig} / {n_tot}',
    #         horizontalalignment='center',
    #         verticalalignment='bottom'
    #     )

    ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
    ax.set_xticks(x_base)
    ax.set_xticklabels(
        [rename_metric(m) for m in metrics],
        rotation=25,
        rotation_mode='anchor',
        ha='right'
    )
    ax.legend(bbox_to_anchor=(0.125, 1.02, 0.75, 0.2), loc="lower left",
               mode="expand", borderaxespad=0, ncol=4)
    #ax.legend()

    fig.tight_layout()

    fig.savefig(out / f'{target_method}_{which}.png')

    pyplot.close(fig)




if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])