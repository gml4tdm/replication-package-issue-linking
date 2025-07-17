import collections
import json
import pathlib
import sys
import os 
import texttable

import tap 


class Args(tap.Tap):
    file_int: pathlib.Path
    file_sep: pathlib.Path
    out: pathlib.Path
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


def stream_methods(int_file: pathlib.Path, sep_file: pathlib.Path):
    assert os.listdir(int_file) == os.listdir(sep_file)
    for filename in os.listdir(int_file):
        with open(int_file / filename / 'correlations.json') as file:
            int_data = json.load(file)
        with open(sep_file / filename / 'correlations.json') as file:
            sep_data = json.load(file)
        assert int_data.keys() == sep_data.keys()
        for key, int_value in int_data.items():
            sep_value = sep_data[key]
            methods = [x for x in known_methods.keys() if x in key]
            assert len(methods) == 1
            method = known_methods[methods[0]]
            projects = [x for x in project_mapping if x in key]
            assert len(projects) == 1
            project = project_mapping[projects[0]]
            yield project, method, int_value, sep_value


def stream_metrics(int_data: dict, sep_data: dict):
    assert int_data.keys() == sep_data.keys()
    for metric_key, int_value in int_data.items():
        sep_value = sep_data[metric_key]
        assert set(sep_value['p-value'].keys()) == {'issue-type', 'identifier-count'}
        assert set(int_value['p-value'].keys()) == {'issue-type', 'identifier-count', 'issue-type:identifier-count'}
        key = 'issue-type:identifier-count'
        is_significant = int_value['p-value'][key] < 0.05
        if is_significant:
            payload = [
                [
                    int_value['statistic']['issue-type'], 
                    int_value['p-value']['issue-type'], 
                    int_value['effect-size']['issue-type']
                ],
                [
                    int_value['statistic']['identifier-count'], 
                    int_value['p-value']['identifier-count'], 
                    int_value['effect-size']['identifier-count']
                ],
                [
                    int_value['statistic'][key],
                    int_value['p-value'][key],
                    int_value['effect-size'][key]
                ]
            ]
        else:
            payload = [
                [
                    sep_value['statistic']['issue-type'], 
                    sep_value['p-value']['issue-type'], 
                    sep_value['effect-size']['issue-type']
                ],
                [
                    sep_value['statistic']['identifier-count'], 
                    sep_value['p-value']['identifier-count'], 
                    sep_value['effect-size']['identifier-count']
                ]
            ]
        yield (
            rename_metric(metric_key),
            is_significant,
            payload
        )



def main(args: Args):
    stream = stream_methods(args.file_int, args.file_sep)
    data = collections.defaultdict(
        lambda: collections.defaultdict(dict)
    )
    for project, method, int_data, sep_data in stream:
        for metric, is_sig, payload in stream_metrics(int_data, sep_data):
            data[method][metric][project] = (is_sig, payload)

    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / 'tables.md', 'w') as file:
        for method, data_for_method in data.items():
            table = Table(
                header=['Metric'] + projects,
                row_headers=[rename_metric(m) for m in metrics]
            )
            latex_table = Table(
                header=['Metric'] + projects,
                row_headers=[rename_metric(m) for m in metrics]
            )
            for metric in map(rename_metric, metrics):
                row = []
                row_latex = []
                for project in projects:
                    is_sig, payload = data_for_method[metric][project]
                    atoms = []
                    atoms_latex = []
                    for stat, p, eta in payload:
                        eta = max(eta, 0)
                        fmt = f'{eta:.3f} ({p:.3f})'
                        fmt_latex = f'{eta:.2f}'
                        if 0.01 <= eta < 0.06:
                            fmt = f'<ins>{fmt}</ins>'
                            fmt_latex = '\\underline{%s}' % fmt_latex
                        elif 0.06 <= eta < 0.14:
                            fmt = f'<ins>**{fmt}**</ins>'
                            fmt_latex = '\\underline{\\textbf{%s}}' % fmt_latex
                        elif 0.14 < eta:
                            raise NotImplementedError(f'eta > 0.14 ({eta})')
                        if p < 0.05:
                            fmt = f'{fmt}&ast;'
                            fmt_latex = f'{fmt_latex}*'
                        atoms.append(fmt)
                        atoms_latex.append(fmt_latex)
                    row.append('/'.join(atoms))
                    row_latex.append('/'.join(atoms_latex))
                table.add_row(row)
                latex_table.add_row(row_latex)
            file.write(f'# {method}\n\n')
            file.write(table.render_markdown())
            file.write('\n\n\n')

            if method == 'BM25':
                print(latex_table.render_latex())


if __name__ == '__main__':
    main(
        Args(underscores_to_dashes=True).parse_args()
    )
