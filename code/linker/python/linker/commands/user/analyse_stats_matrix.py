import collections
import json
import pathlib
import statistics

from tap import Tap

from ..base import BaseCommand, register


class AnalyseStatsMatrixConfig(Tap):
    file: pathlib.Path


@register('analyse-stats-matrix')
class AnalyseStatsMatrix(BaseCommand):

    @staticmethod
    def config_type() -> type[Tap]:
        return AnalyseStatsMatrixConfig

    def execute(self):
        assert isinstance(self.config, AnalyseStatsMatrixConfig)

        with open(self.config.file) as f:
            data = json.load(f)

        mean_rankings = collections.defaultdict(list)
        mean_first = collections.defaultdict(int)
        median_rankings = collections.defaultdict(list)
        median_first = collections.defaultdict(int)
        first_mean_significant = collections.defaultdict(int)
        first_median_significant = collections.defaultdict(int)
        total_significant = 0
        total_tested = 0
        total = 0

        for entry in data.values():
            total += 1
            n = len(entry['mean']['order'])
            for i, key in enumerate(entry['mean']['order']):
                if i == n - 1:
                    mean_first[key] += 1
                mean_rankings[key].append(n - i)
            for i, key in enumerate(entry['median']['order']):
                if i == n - 1:
                    median_first[key] += 1
                median_rankings[key].append(n - i)
            if entry['test'] is not None:
                total_tested += 1
                total_significant += entry['test']['significant']
                if entry['test']['significant']:
                    first_mean_significant[entry['mean']['order'][-1]] += 1
                    first_median_significant[entry['median']['order'][-1]] += 1

        keys = sorted(mean_rankings)
        for key in keys:

            print(f'===== {key} ======')
            print(f'Mean Mean Rank:', statistics.mean(mean_rankings[key]))
            print(f'Median Mean Rank:', statistics.median(mean_rankings[key]))
            print(f'Mean Median Rank:', statistics.mean(median_rankings[key]))
            print(f'Median Median Rank:', statistics.median(median_rankings[key]))
            print(f'First Mean: {mean_first[key]} / {total}')
            print(f'First Median: {median_first[key]} / {total}')
            print(f'First Mean Significant: {first_mean_significant[key]} / {total_significant}')
            print(f'First Median Significant: {first_median_significant[key]} / {total_significant}')
            print()
