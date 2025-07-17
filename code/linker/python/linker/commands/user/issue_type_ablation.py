import dataclasses
import json
import pathlib
import re
import statistics
import typing

import alive_progress
import numpy
import pandas
import pingouin
import scikit_posthocs
import scipy.stats
import tap

from ...utils.issue_db import IssueDatabaseWrapper
from ..._accelerator import LiveIndexLoader
from ..base import BaseCommand, register


#      issue_type     | project_id | count
# --------------------+------------+-------
#  Brainstorming      |        125 |     7
#  Bug                |          3 |  1235
#  Bug                |         64 |  3908
#  Bug                |         94 |  2713
#  Bug                |        106 |  1767
#  Bug                |        125 |  3194
#  Bug                |        691 |  1764
#  Bug                |       1026 |  1963
#  Comment            |        125 |     1
#  DAC Feedback       |        691 |     1
#  Defect             |        691 |     1
#  Dependency upgrade |          3 |   635
#  Dependency upgrade |         64 |   260
#  Dependency upgrade |        125 |     9
#  Documentation      |          3 |   113
#  Documentation      |         94 |     1
#  Documentation      |        125 |    43
#  Documentation      |        691 |     2
#  Epic               |         94 |     4
#  Epic               |        125 |     7
#  Epic               |        691 |     2
#  Feature Request    |         94 |   285
#  Feature Request    |        691 |   157
#  Improvement        |          3 |   608
#  Improvement        |         64 |  1696
#  Improvement        |         94 |   249
#  Improvement        |        106 |  1557
#  Improvement        |        125 |  1683
#  Improvement        |        691 |    86
#  Improvement        |       1026 |  1274
#  IT Help            |        125 |     1
#  New Feature        |          3 |   356
#  New Feature        |         64 |   574
#  New Feature        |         94 |   110
#  New Feature        |        106 |   349
#  New Feature        |        125 |   304
#  New Feature        |        691 |    37
#  New Feature        |       1026 |   283
#  New Project        |        691 |     1
#  Proposal           |        125 |     1
#  Question           |        125 |    92
#  Request            |        125 |     7
#  Roadmap item       |         94 |     4
#  Roadmap item       |        691 |     1
#  RTC                |        125 |     1
#  Story              |         94 |     7
#  Story              |        125 |    14
#  Story              |        691 |    24
#  Sub-task           |          3 |   843
#  Sub-task           |         64 |   124
#  Sub-task           |         94 |   171
#  Sub-task           |        106 |   116
#  Sub-task           |        125 |   302
#  Sub-task           |        691 |    92
#  Sub-task           |       1026 |   116
#  Suggestion         |         94 |    60
#  Suggestion         |        691 |   253
#  Support Request    |         94 |     3
#  Support Request    |        691 |     4
#  Support Ticket     |        691 |     1
#  Task               |          3 |   223
#  Task               |         64 |   688
#  Task               |         94 |   354
#  Task               |        106 |   222
#  Task               |        125 |    96
#  Task               |        691 |   163
#  Task               |       1026 |   705
#  Technical Debt     |        125 |     1
#  Test               |          3 |    17
#  Test               |         64 |    13
#  Test               |         94 |     9
#  Test               |        106 |    72
#  Test               |        125 |    43
#  Test               |       1026 |    14
#  Test Task          |        691 |     1
#  Umbrella           |        125 |     2
#  Wish               |          3 |    10
#  Wish               |         64 |   123
#  Wish               |         94 |    17
#  Wish               |        106 |    53
#  Wish               |        125 |    61
#  Wish               |       1026 |    73
# (82 rows)
#
#
#
# Wish, Test, Suggestion, Story? Question? Documentation, Dependency Upgrade
#
# Bug, Defect -> Bug
# Sub-task, Task -> Task
# Feature Request, New Feature -> New Feature
# Improvement, Suggestion -> Improvement



class IssueTypeAblationConfig(tap.Tap):
    config: pathlib.Path


@dataclasses.dataclass
class IssueTypeAblationScript:
    files: list[str]
    file_filter: str
    project_regex: str
    data_directory: str
    data_dir_suffix: str
    split: str
    run_on: int
    postgres_url: str
    repo_mapping: dict[str, str]
    output: str
    method_regex: str
    plot: list[str]
    type_groups: list[dict]


@register('issue-type-ablation')
class IssueTypeAblationCommand(BaseCommand):

    @staticmethod
    def config_type() -> type[tap.Tap]:
        return IssueTypeAblationConfig

    def execute(self):
        assert isinstance(self.config, IssueTypeAblationConfig)

        with open(self.config.config) as f:
            script = IssueTypeAblationScript(**json.load(f))

        files = []
        for file in script.files:
            files.extend(pathlib.Path('.').glob(file))

        pattern = re.compile(script.file_filter)
        files = [x for x in files if pattern.fullmatch(x.name)]

        if len(files) == 0:
            raise ValueError('No files found')

        self.logger.info('Found %s files', len(files))

        files_by_project = {}
        pattern = re.compile(script.project_regex)
        for file in files:
            project = pattern.search(file.name).group(1)
            files_by_project.setdefault(project, []).append(file)

        self.logger.info('Found %s projects', len(files_by_project))

        db = IssueDatabaseWrapper.from_url_sync(script.postgres_url)

        pattern = re.compile(script.method_regex)
        one_vs_rest_groups = {}
        data_directory = pathlib.Path(script.data_directory)
        total = 0
        for project, files_for_project in files_by_project.items():
            self.logger.info('Processing %s', project)
            suffix = f'{project}-{script.data_dir_suffix}/index.json'
            loader = LiveIndexLoader.load(str(data_directory / suffix))
            bins = split(
                range(loader.number_of_issues),
                *(int(x) for x in script.split.split('/'))
            )
            selected_bin = bins[script.run_on]
            issue_keys = [loader.get_issue(i).issue_key
                          for i in selected_bin]
            issues = db.get_issues_by_key_sync(
                script.repo_mapping[project],
                *issue_keys
            )
            db.fetch_issue_fields_sync(
                list(issues.values()),
                'issue_type'
            )
            project_group = one_vs_rest_groups.setdefault(project, {})

            for project_file in files_for_project:
                method = pattern.search(project_file.name).group(1)
                method_group = project_group.setdefault(method, {})
                with open(project_file / 'performance.json') as f:
                    data = json.load(f)
                total += 1
                for group in script.type_groups:
                    group_name = group['name']
                    group_types = group['types']
                    mask = [
                        issues[key].other_fields['issue_type'] in group_types
                        for key in issue_keys
                    ]
                    method_group[group_name] = {
                        'one': [
                            x for m, x in zip(mask, data['details']) if m
                        ],
                        'rest': [
                            x for m, x in zip(mask, data['details']) if not m
                        ]
                    }

        self.logger.info('Running bootstrap experiments')

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

        result = {}
        with alive_progress.alive_bar(total * len(metrics)) as bar:
            for project, project_groups in one_vs_rest_groups.items():
                for method, method_groups in project_groups.items():
                    # for held_out, groups in method_groups.items():
                    #     for metric in metrics:
                    #         bar.title(f'{project} - {method} - {held_out} - {metric}')
                    #         bar()
                    for metric in metrics:
                        bar.title(f'{project} - {method} - {metric}')
                        bar()
                        categories = []
                        specific = []
                        holdout = []
                        for cat, subsets in method_groups.items():
                            categories.append(cat)
                            specific.append([x[metric] for x in subsets['one']])
                            holdout.append([x[metric] for x in subsets['rest']])
                        store = result.setdefault(method, {}).setdefault(project, {})
                        store[metric] = {
                            'specific': stats_for(categories, specific),
                            'holdout': stats_for(categories, holdout)
                        }

        path = pathlib.Path(script.output)
        path.mkdir(exist_ok=True)
        with open(path / 'results.json', 'w') as f:
            json.dump(result, f, indent=2)


def stats_for(categories, data):
    kw = scipy.stats.kruskal(*data)
    pvalue = kw.pvalue
    statistic = kw.statistic
    output = {
        'pooled': {
            'p-value': pvalue,
            'statistic': statistic,
            'n_groups': len(categories),
            'n_observations': sum(map(len, data))
        },
        'pairwise': [],
        'scores': {
            cat: statistics.mean(d)
            for cat, d in zip(categories, data)
        }
    }
    result = scikit_posthocs.posthoc_conover(data, p_adjust='fdr_bh')
    for i, cat_1 in enumerate(categories, start=1):
        for j, cat_2 in enumerate(categories[i+1-1:], start=1):
            output['pairwise'].append({
                'categories': [cat_1, cat_2],
                'p-value': result[i][j]
            })
    return output


def split(items, *x):
    assert sum(x) == 100
    assert all(y > 0 for y in x)
    indices = []
    remaining = len(items)
    for i, y in enumerate(x[:-1]):
        i = _split_bin(remaining, y, sum(x[i + 1:]))
        remaining -= i
        indices.append(i)
    return list(_make_splits(items, indices))


def _make_splits(items, indices):
    prev = 0
    for i in indices:
        yield items[prev:prev + i]
        prev += i
    yield items[prev:]


def _split_bin(total, p, q):
    y = total * p // (p + q)
    if abs(y / total - p / (p + q)) < abs((y + 1) / total - p / (p + q)):
        return y
    return y + 1


