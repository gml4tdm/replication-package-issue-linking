import collections
import json
import pathlib
import sys
import texttable

import tap 


class Args(tap.Tap):
    file: pathlib.Path
    out: pathlib.Path
    key: str | None = None
    levels: list[float] = [0.19, 0.39, 0.59, 0.79, 1.0]


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

projects = [
    'Avro',
    'Maven',
    'Tika',
    'Thrift',
    'TomEE',
    'Spring Data MongoDB',
    'Spring Roo',
]
project_mapping = {
    p.lower().replace(' ', '-'): p for p in projects
}


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


metrics = [
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


known_methods = {
    'bm25': 'BM25',
    'lsa-500': 'LSI-500',
    'lsa-1000': 'LSI-1000',
    'rvsm': 'rVSM',
    'tfidf': 'TFIDF'
}


def _new_table():
    table = Table(
        header=['Metric'] + projects,
        row_headers=[rename_metric(m) for m in metrics]
    )
    return table


class _Getter:
    def __init__(self, key):
        self._key = key
    def __call__(self, mapping, item):
        if self._key is None:
            return mapping[item]
        else:
            return mapping[item][self._key]


def main(args: Args):
    getter = _Getter(args.key)
    table_data = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )
    table_data_latex = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )
    for project in project_mapping:
        with open(args.file / project / 'correlations.json') as file:
            data = json.load(file)
        for key, value in data.items():
            if key == '$all':
                continue
            method = [
                v for k, v in known_methods.items() if k in key
            ][0]
            for metric, x in value.items():
                statistic = getter(x, 'statistic')

                level = 0
                while abs(statistic) > args.levels[level]:
                    level += 1
                
                if getter(x, 'p-value') < 0.0001:
                    fmt = f'{getter(x, "statistic"):.3f} / {getter(x, "p-value"):.1e}'
                else:
                    fmt = f'{getter(x, "statistic"):.3f} / {getter(x, "p-value"):.3f}'
                fmt_latex = f'{getter(x, "statistic"):.2f}'
                if level == 0:
                    fmt = fmt 
                    fmt_latex = fmt_latex
                elif level == 1:
                    fmt = f'<ins>{fmt}</ins>'
                    fmt_latex = '\\underline{%s}' % fmt_latex
                else:
                    raise ValueError(f'level > 1 not implemented ({level}; {statistic})')
                if getter(x, 'p-value') < 0.05:
                    fmt = f'{fmt}&ast;'
                    fmt_latex = f'{fmt_latex}*'
                table_data[method][metric].append(fmt)
                table_data_latex[method][metric].append(fmt_latex)
                if getter(x, 'p-value') > 0.05:
                    print(f'Insignificant correlation found ({project}, {key})')

    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / 'tables.md', 'w') as file:
        for method, data_for_method in table_data.items():
            file.write(f'# {method}\n\n')

            table = Table(
                header=['Metric'] + projects,
                row_headers=[rename_metric(m) for m in metrics]
            )
            for metric in metrics:
                table.add_row(data_for_method[metric])
            file.write(table.render_markdown())

            file.write('\n\n\n')

    table = Table(
        header=['Metric'] + projects,
        row_headers=[rename_metric(m) for m in metrics]
    )
    for metric in metrics:
        table.add_row(table_data_latex['BM25'][metric])
    print(table.render_latex())



if __name__ == '__main__':
    main(
        # pathlib.Path(sys.argv[1]),
        # pathlib.Path(sys.argv[2]),
        # sys.argv[3] if len(sys.argv) >= 4 else None
        Args().parse_args()
    )