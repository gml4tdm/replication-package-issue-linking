###############################################################################
###############################################################################
# Imports
###############################################################################

import json
import pathlib
import statistics
import typing

import tap
import texttable

###############################################################################
###############################################################################
# Types
###############################################################################

class Args(tap.Tap):
    files: list[pathlib.Path]
    columns: list[str]
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
    average_column: str | None = None
    kind: typing.Literal['markdown', 'latex'] = 'markdown'


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


###############################################################################
###############################################################################
# Constants
###############################################################################

_METRIC_MAPPING = {
    'retrieval-precision': 'Precision',
    'retrieval-recall': 'Recall',
    'mrr': 'MRR',
    'r-precision': 'r-Precision',
    'hit-rate': 'hit'
}

###############################################################################
###############################################################################
# Utility functions
###############################################################################

def rename_metric(m: str) -> str:
    if '-top-' in m:
        m, top = m.split('-top-')
        suffix = f'@{top}'
    else:
        suffix = ''
    return _METRIC_MAPPING[m] + suffix



def _align(x, a):
    y = a - len(x)
    return x + ' '*y


###############################################################################
###############################################################################
# Other functions
###############################################################################


def table_data_for_file(file: pathlib.Path, args: Args):
    with open(file) as f:
        data = json.load(f)

    column_headers = []
    column_keys = []
    for column in args.columns:
        if ':' in column:
            column, rename_to = column.split(':')
            column_headers.append(rename_to)
            column_keys.append(column)
        else:
            column_headers.append(column)
            column_keys.append(column)

    if args.average_column is not None:
        column_headers.append(args.average_column)

    header = ['Metric'] + column_headers

    rows = []
    for metric in args.metrics:
        row = [rename_metric(metric)]
        values = []
        values_for_mean = []
        for column in column_keys:
            index = data[metric]['mean']['order'].index(column)
            value = data[metric]['mean']['values'][index]
            values.append(f'{value:.3f}')
            values_for_mean.append(value)
        row.extend(values)
        if args.average_column is not None:
            m = statistics.mean(values_for_mean)
            row.append(f'{m:.3f}')
        rows.append(row)

    return header, rows


def combine_and_highlight(tables, args: Args):
    rows = []
    for row_index in range(len(tables[0])):
        row = [tables[0][row_index][0]]

        best_per_table = [
            max(range(1, len(table[row_index])), key=lambda i: float(table[row_index][i]))
            for table in tables
        ]

        for col_index in range(1, len(tables[0][row_index])):
            group = [table[row_index][col_index] for table in tables]
            best_in_group = max(range(len(group)), key=lambda i: float(group[i]))
            row.append(
                ' / '.join(
                    _fmt_cell(
                        x, 
                        best_per_table[g_index] == col_index,
                        g_index == best_in_group, 
                        args
                    )
                    for g_index, x in enumerate(group)
                )
            )
        rows.append(row)
    return rows


def _fmt_cell(x, best_in_row, best_in_group, args: Args):
    # row_highlight: str = '\\textbf{%s}'
    # group_highlight = '\\underline{%s}'
    if args.kind == 'markdown':
        if len(args.files) == 1:
            if best_in_row:
                x = f'<ins>{x}</ins>'
        else:
            if best_in_row:
                x = f'**{x}**'
            if best_in_group:
                x = f"<ins>{x}</ins>"
    else:
        if len(args.files) == 1:
            if best_in_row:
                x = '\\underline{%s}' % x
        else:
            if best_in_row:
                x = '\\textbf{%s}' % x
            if best_in_group and len(args.files) > 1:
                x = '\\underline{%s}' % x
    return x


###############################################################################
###############################################################################
# Main function
###############################################################################


def main(args: Args):
    global_header = None
    tables = []
    for file in args.files:
        header, rows = table_data_for_file(file, args)
        if global_header is None:
            global_header = header
        else:
            if header != global_header:
                raise ValueError('Headers do not match')
        tables.append(rows)

    if global_header is None:
        raise ValueError('No files provided')

    rows = combine_and_highlight(tables, args)


    table = Table(global_header)
    for row in rows:
        table.add_row(row)
    if args.kind == 'markdown':
        print(table.render_markdown())
    else:
        print(table.render_latex())

    # align = [len(h) for h in global_header]
    # for row in rows:
    #     for i, col in enumerate(row):
    #         align[i] = max(align[i], len(col))

    # align = [((a + 2) // 4 + 1) * 4 for a in align]

    # text = ['\\toprule']
    # text.append(
    #     ' & '.join(_align(x, a) for x, a in zip(global_header, align)) + '\\\\ \\midrule'
    # )
    # for row in rows:
    #     text.append(
    #         ' & '.join(_align(x, a) for x, a in zip(row, align)) + '\\\\'
    #     )
    # text.append('\\bottomrule')

    # print('\n'.join(text))


if __name__ == '__main__':
    main(Args(underscores_to_dashes=True).parse_args())
