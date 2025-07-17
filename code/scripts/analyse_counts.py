import collections
import json
import math
import pathlib
import statistics
import sys
import texttable

from scipy.stats import shapiro, kruskal
from  scikit_posthocs import posthoc_conover

import matplotlib.pyplot as pyplot



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

groups = [
    {
      "name": "Bug",
      "types": ["Bug", "Defect"]
    },
    {
      "name": "Task",
      "types": ["Task", "Sub-task"]
    },
    {
      "name": "Improvement",
      "types": ["Improvement", "Suggestion"]
    },
    {
      "name": "New Feature",
      "types": ["New Feature", "Feature Request"]
    }
]


def plot_dict(data, order, out: pathlib.Path, name, slanted=False):
    fig, ax = pyplot.subplots(figsize=(8.27, 8.27 / 3))
    ax.boxplot(
        [
            [math.log(x + 1) for x in data[o]]
            for o in order
        ],
        tick_labels=order,
        showfliers=True
    )
    #ax.set_xlabel('Issue type' if name == 'by_type' else 'Project')
    ax.set_ylabel('log(#Identifiers + 1)')
    if slanted:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=15, ha='right', rotation_mode='anchor')
    fig.tight_layout()
    fig.savefig(out / f'{name}.png')
    pyplot.close(fig)

    # Is all data normal?
    if all(shapiro(x).pvalue >= 0.05 for x in data.values()):
        print('Normal data')
        raise ValueError('Normal data not implemented')
    else:
        stat = kruskal(
            *[data[o] for o in order]
        )
        pairs = posthoc_conover([data[o] for o in order])
        table = Table(['Category 1', 'Category 2', 'Order', 'p'])
        for i, a in enumerate(order):
            for j, b in enumerate(order[i+1:]):
                p = pairs[i+1][j+1]
                cmp_order = '<' if statistics.mean(data[a]) < statistics.mean(data[b]) else '>'
                #print(f'{a} vs. {b} -- {cmp_order} -- {p:.4f} -- {p < 0.05}')
                table.add_row([
                    a,
                    b,
                    '&lt;' if cmp_order == '<' else '&gt;',
                    f'{p:.4f}' if p >= 0.05 else f'**{p:.4f}**'
                ])
        with open(out / f'{name}.md', 'w') as file:
            file.write(f'Kruskal: statistic = {stat.statistic}, p-value = {stat.pvalue}\n\n\n')
            file.write(table.render_markdown())
            file.write('\n')




def main(inp_dir: pathlib.Path, out_dir: pathlib.Path):
    by_project = {}
    by_type = {}
    for project in project_mapping:
        with open(inp_dir / project / 'counts.json') as file:
            data = json.load(file)
        for x in data:
            by_project.setdefault(project_mapping[project], []).append(x['count'])
            by_type.setdefault(x['issue-type'], []).append(x['count'])

    out_dir.mkdir(parents=True, exist_ok=True)
    plot_dict(by_project, projects, out_dir, 'by_project', slanted=True)
    plot_dict(by_type, ['Bug', 'Improvement', 'New Feature', 'Task'], out_dir, 'by_type')



if __name__ == '__main__':
    main(
        pathlib.Path(sys.argv[1]),
        pathlib.Path(sys.argv[2])
    )