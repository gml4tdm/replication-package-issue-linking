import collections
import json
import pathlib
import re
import statistics
import typing

import matplotlib.pyplot as pyplot
import numpy
import seaborn
import tap

from ..base import BaseCommand, register


class PrintEvalConfig(tap.Tap):
    files: list[pathlib.Path]
    random_file: pathlib.Path | None = None
    which: str = 'test'
    epoch: int | None = None
    aggregation_pattern: str | None = None


@register('evaluate')
class PrintEvalCommand(BaseCommand):

    @staticmethod
    def config_type() -> type[tap.Tap]:
        return PrintEvalConfig

    def execute(self):
        assert isinstance(self.config, PrintEvalConfig)

        files = sorted(self.config.files)
        row_headers = []
        columns = collections.defaultdict(lambda: collections.defaultdict(list))
        common_metrics = None

        if self.config.random_file is not None:
            with open(self.config.random_file) as file:
                data = json.load(file)
            max_data = data['max_scores']
            random_fair_raw = data['random_scores_coin']
            random_weighted_raw = data['random_scores_weighted']
            random_fair = self._average(random_fair_raw)
            random_weighted = self._average(random_weighted_raw)
            row_headers.append('Random (50/50)')
            row_headers.append('Random (Weighted)')
            for metrics in [random_fair, random_weighted]:
                for metric, value in metrics.items():
                    if isinstance(value, (int, float)):
                        columns[metric].append(value)
        else:
            max_data = random_fair = random_weighted = {}

        for filename in files:
            print(filename)
            metrics_for_file = set()
            with open(self._resolve_perf_file(filename)) as file:
                data = json.load(file)
            # if which  in data and data['test'] is not None:
            #     row_headers.append(filename.stem)
            #     metrics = data['test'][-1]
            # else:
            #     row_headers.append(f'{filename.stem} (validation)')
            #     metrics = data['validation'][-1]
            if self.config.which == 'test' and not isinstance(data['test'], list):
                metrics = data['test']
            else:
                index = -1 if self.config.epoch is None else (self.config.epoch - 1)
                metrics = data[self.config.which][index]
            # if filename.stem == 'performance':
            #     row_headers.append(filename.parent.parent.name + '-' + filename.parent.name)
            # else:
            #     row_headers.append(filename.parent.name + '-' + filename.name.removesuffix('.json'))
            name_path = filename
            if name_path.stem == 'performance':
                name_path = name_path.parent
            pattern = re.compile(r'E(\d+|final)')
            if pattern.fullmatch(name_path.name):
                name_path = name_path.parent
            name = name_path.name.removesuffix('.json')
            if self.config.aggregation_pattern is not None:
                matches = re.findall(self.config.aggregation_pattern, name)
                if not matches:
                    raise ValueError(f'No matches for {self.config.aggregation_pattern} in {name}')
                name = matches[0]
            if name not in row_headers:
                row_headers.append(name)
            for metric, value in metrics.items():
                if isinstance(value, (int, float)):
                    columns[metric][name].append(value)
                    metrics_for_file.add(metric)
            if common_metrics is None:
                common_metrics = metrics_for_file
            else:
                common_metrics &= metrics_for_file

        if 'loss' in columns:
            del columns['loss']

        # if max_data:
            # for key in list(columns.keys()):
            #     if key.startswith('retrieval-recall'):
            #         max_v = max_data[key]
            #         columns[f'{key}-max-%'] = [x / max_v for x in columns[key]]
            #         rand_f = columns[key][0]
            #         rand_w = columns[key][1]
            #         columns[f'{key}-imp-fair'] = [(x - rand_f) / (max_v - rand_f) if max_v != rand_f else 1
            #                                       for x in columns[key]]
            #         columns[f'{key}-imp-weighted'] = [(x - rand_w) / (max_v - rand_w) if max_v != rand_w else 1
            #                                           for x in columns[key]]

        column_headers = sorted(common_metrics - {'loss'}, key=metric_rank)
        scale_matrix = numpy.asarray(
            [
                self._rescale(
                    [statistics.mean(columns[h][r]) for r in row_headers],
                    #x_max=None if not h.startswith('retrieval-recall') else max_data.get(h, None),
                    x_max=max_data.get(h, None),
                    x_min=0 if not h.endswith(('imp-fair', 'imp-weighted')) else -1
                )
                for h in column_headers
            ]
        )
        scale_matrix = scale_matrix
        annotation_matrix = [
            [
                self._format_value(
                    statistics.mean(columns[h][i]),
                    h,
                    max_data.get(h, None),
                    random_fair.get(h, None),
                    random_weighted.get(h, None)
                )
                for h in column_headers
            ]
            for i in row_headers
        ]
        annotation_matrix = list(zip(*annotation_matrix))

        fig, ax = pyplot.subplots()
        seaborn.heatmap(
            scale_matrix,
            annot=annotation_matrix,
            cbar=False,
            ax=ax,
            fmt='',
            xticklabels=row_headers,
            yticklabels=column_headers,
            cmap='viridis'
        )
        #ax.tick_params(axis='x', labelrotation=45, ha='right')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        pyplot.tight_layout()
        pyplot.show()

    def _format_value(self,
                      value: int | float,
                      metric: str,
                      max_data: int | float | None,
                      random_fair: int | float | None,
                      random_weighted: int | float | None) -> str:
        if not metric.startswith('retrieval-recall'):
            return f'{value:.3f}'
        else:
            #return f'{value:.3f} ({value / max_data:.3f})'
            return f'{value:.3f}'


    @staticmethod
    def _rescale(xs: list[int | float], x_max=None, x_min=0):
        if x_max is None:
            x_max = max(xs)
        else:
            x_max_act = max(xs)
            if x_max < x_max_act:
                raise ValueError(x_max, '<', x_max_act)
        if x_min == x_max:
            return [1] * len(xs)
        return [(x - x_min) / (x_max - x_min) for x in xs]

    def _average(self, xs: list[dict[str, typing.Any]]):
        assert len(xs) > 0
        current = xs[0]
        for x in xs[1:]:
            self._sum_into(current, x)
        self._mul_into(current, 1.0 / len(xs))
        return current

    def _sum_into(self, target, source):
        if isinstance(source, dict):
            assert isinstance(target, dict)
            assert source.keys() == target.keys()
            for k, v in source.items():
                if isinstance(v, (int, float)):
                    target[k] += v
                else:
                    self._sum_into(target[k], v)
        elif isinstance(source, list):
            assert isinstance(target, list)
            assert len(source) == len(target)
            for i in range(len(source)):
                if isinstance(source[i], (int, float)):
                    target[i] += source[i]
                else:
                    self._sum_into(target[i], source[i])
        else:
            raise ValueError(f'Unknown type {type(source)}')

    def _mul_into(self, target, x):
        if isinstance(target, dict):
            assert isinstance(x, (int, float))
            for k, v in target.items():
                if isinstance(v, (int, float)):
                    target[k] *= x
                else:
                    self._mul_into(target[k], x)
        elif isinstance(target, list):
            assert isinstance(x, (int, float))
            for i in range(len(target)):
                if isinstance(target[i], (int, float)):
                    target[i] *= x
                else:
                    self._mul_into(target[i], x)
        else:
            raise ValueError(f'Unknown type {type(target)}')

    def _resolve_perf_file(self, filename: pathlib.Path) -> pathlib.Path:
        if filename.name.endswith('.json'):
            return filename
        p = filename / 'performance.json'
        if p.exists():
            return p
        p = filename / 'Efinal' / 'performance.json'
        if p.exists():
            return p
        directories = list(filename.glob('E*'))
        directories.sort(key=lambda x: int(x.stem.replace('E', '')))
        return directories[-1] / 'performance.json'


def metric_rank(name: str):
    pattern = re.compile(r'-top-(?P<r>\d+)$')
    m = pattern.search(name)
    if m is not None:
        return name[:m.start()], int(m.group('r'))
    return name, 0
