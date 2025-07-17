import collections
import json
import pathlib

from tap import Tap 

from ..base import BaseCommand, register
from ..._accelerator import LiveIndexLoader



class AnalyseCommitSizesConfig(Tap):
    files: list[pathlib.Path]
    output: pathlib.Path
    include_unit_commits: bool = False 

    def configure(self):
        self.add_argument('--include-unit-commits', action='store_true', default=False)


@register('analyse-commit-sizes')
class AnalyseCommitSizes(BaseCommand):

    @staticmethod
    def config_type() -> type[Tap]:
        return AnalyseCommitSizesConfig
    
    def execute(self):
        assert isinstance(self.config, AnalyseCommitSizesConfig)

        hist = collections.defaultdict(list)

        for filename in self.config.files:
            self.logger.info(f'Analysing {filename}...')
            loader = LiveIndexLoader.load(str(filename / 'index.json'))
            for issue_index in range(loader.number_of_issues):
                issue = loader.get_issue(issue_index)
                if issue.number_of_commits <= 1 and not self.config.include_unit_commits:
                    continue
                positives_by_commit = []
                for commit_index in range(issue.number_of_commits):
                    commit = issue.get_commit(commit_index)
                    n_positives = sum(
                        sample.label for sample in commit.lightweight_samples()
                    )
                    positives_by_commit.append(n_positives)
                total = sum(positives_by_commit)
                proportions = [p / total for p in positives_by_commit]
                for i, p in enumerate(proportions):
                    hist[i].append(p)

        self.config.output.parent.mkdir(exist_ok=True, parents=True)
        with open(self.config.output, 'w') as f:
            json.dump(hist, f, indent=2)
