from __future__ import annotations

import collections
import dataclasses
import graphlib
import itertools
import json
import logging
import pathlib
import random
import re
import statistics
import string
import sys
import typing
import warnings

import alive_progress
import matplotlib.pyplot as pyplot
import tap

from ..base import BaseCommand, register
from ...utils.git_utils import GitCmdClient
from ...utils.issue_db import IssueDatabaseWrapper, Commit


T = typing.TypeVar('T')

DISABLE_CHERRY_PICKING = True


class RefineCommitLinksConfig(tap.Tap):
    postgres_url: str
    repo: str
    project: str
    path: str
    iqr_out: pathlib.Path | None = None


@dataclasses.dataclass
class MergeDisambiguationConfig:
    case_1: typing.Literal['discard-merge', 'keep-merge']
    case_2: typing.Literal['keep-branch', 'remove-all']
    case_3: typing.Literal['keep-branch', 'keep-merge', 'keep-all', 'discard-all']
    case_4: typing.Literal['keep-branch', 'mark-merge', 'mark-all', 'discard-all']


@register('refine-commit-links')
class RefineCommitLinksCommand(BaseCommand):

    @staticmethod
    def config_type() -> type[tap.Tap]:
        return RefineCommitLinksConfig

    def execute(self):
        assert isinstance(self.config, RefineCommitLinksConfig)

        # Fetch data
        db = IssueDatabaseWrapper.from_url_sync(self.config.postgres_url)
        commits = db.get_commits_sync(self.config.repo,
                                      self.config.project,
                                      return_parents=True)
        links = db.get_commit_issue_links_sync(self.config.repo,
                                               self.config.project)
        linked_issues = {link[1] for link in links}
        issues = db.get_issues_by_db_id_sync(list(linked_issues))
        issue_keys_by_id = {uid: issue.key for uid, issue in issues.items()}

        # Build graph
        tail = self._build_commit_graph(commits, links)
        graph = CommitGraph(tail,
                            issue_keys_by_id,
                            self.config.path,
                            self.logger)
        self.logger.info('Total Linked Issues: %s', len(graph.all_issues))
        self.logger.info('Issues In Main: %s', len(graph.issues_in_main))
        self.logger.info('Issues In Branches: %s', len(graph.issues_in_branches))
        self.logger.info('Issues Only In Main: %s', len(graph.issues_only_in_main))
        #fig = graph.compute_issue_spread_statistics(issues)
        #pyplot.show()

        if self.config.iqr_out is not None:
            self.config.iqr_out.parent.mkdir(parents=True, exist_ok=True)
            iqr_out = str(self.config.iqr_out)
        else:
            iqr_out = None
        kept, diff_points = graph.get_commit_groups(test_iqr=iqr_out)
        refined = [
            [
                (issue_id, c.commit.uid, i, diff_points.get(c.commit.uid, None))
                for i, c in enumerate(commits)
            ]
            for issue_id, commits in kept.items()
        ]
        db.insert_refined_commit_issue_links_sync(refined)

    def _build_merge_dag(self, root: CommitNode):
        dag = MergeDAG(root)
        dag.render()

    def _build_commit_graph(self, commits: list[Commit], links: list[tuple[int, int]]):
        nodes = {
            commit.uid: CommitNode(
                commit=commit,
                linked_issues=[],
                parents=[],
                children=[]
            )
            for commit in commits
        }
        for commit_id, issue_id in links:
            nodes[commit_id].linked_issues.append(issue_id)
        for commit in commits:
            nodes[commit.uid].parents = [
                nodes[p] for p in commit.parents
            ]
            for p in commit.parents:
                nodes[p].children.append(nodes[commit.uid])
        roots = [
            node
            for node in nodes.values()
            if not node.children
        ]
        assert len(roots) == 1
        return roots[0]

@dataclasses.dataclass
class CommitNode:
    commit: Commit
    linked_issues: list[int]
    parents: list[CommitNode]
    children: list[CommitNode]


class CommitGraph:

    def __init__(self,
                 tail: CommitNode,
                 issue_keys_by_id: dict[int, str],
                 repo_path: str,
                 logger: logging.Logger):
        self._logger = logger
        self._tail = tail
        self._commits: dict[int, CommitNode] = {}
        self._heads = []
        self._main = set()
        self._keys = issue_keys_by_id
        self._path = repo_path

        def visit(n: CommitNode):
            self._main.add(n.commit.uid)

        self._walk_main(self._tail, visit)

        def visit(n: CommitNode):
            self._commits[n.commit.uid] = n
            if n.parents:
                return
            self._heads.append(n)

        self._walk_up(self._tail, visit)

    def _walk_main(self, node: CommitNode, visitor):
        while node.parents:
            visitor(node)
            node = node.parents[0]
        visitor(node)

    def _walk_up(self, node: CommitNode, visitor):
        seen = {node.commit.uid}
        stack = [node]
        while stack:
            current = stack.pop()
            visitor(current)
            for p in reversed(current.parents):
                if p.commit.uid in seen:
                    continue
                seen.add(p.commit.uid)
                stack.append(p)

    ###########################################################################
    ###########################################################################
    # Public Interface

    def get_commit_groups(self, *, test_iqr: str | None = None) -> tuple[dict[int, list[CommitNode]], dict[int, int]]:
        # The underlying methods also call commits_per_issue_cleaned,
        # which handles linearization and disambiguation.
        f = 1 / (24 * 60 * 60)
        threshold = self._temporal_spread_threshold(f, 0.9, test_iqr=test_iqr)

        commits_per_issue, diff_points = self.commits_per_issue_cleaned
        merged = {
            k: self._temporal_merge(v, threshold, f, 'oldest')
            for k, v in commits_per_issue.items()
        }
        return merged, diff_points

    ###########################################################################
    ###########################################################################
    # Getters
    ###########################################################################

    @property
    def total_commits(self) -> int:
        return len(self._commits)

    @property
    def commits_in_main(self) -> int:
        return len(self._main)

    @property
    def issues_in_branches(self) -> set[int]:
        result = set()
        for key, value in self._commits.items():
            if key in self._main:
                continue
            result |= set(value.linked_issues)
        return result

    @property
    def issues_in_main(self) -> set[int]:
        result = set()
        for key in self._main:
            result |= set(self._commits[key].linked_issues)
        return result

    @property
    def issues_only_in_main(self) -> set[int]:
        return self.issues_in_main - self.issues_in_branches

    @property
    def all_issues(self) -> set[int]:
        result = set()
        for v in self._commits.values():
            result |= set(v.linked_issues)
        return result

    ###########################################################################
    ###########################################################################
    # Cherry Picking
    ###########################################################################

    def _handle_cherry_picks(self,
                             commits_per_issue: dict[int, list[CommitNode]]):
        client = GitCmdClient(self._path)
        result = {}

        if DISABLE_CHERRY_PICKING:
            warnings.warn('Cherry-picking support is experimental and not enabled')

        with alive_progress.alive_bar(len(commits_per_issue)) as bar:
            for issue_id, commits in commits_per_issue.items():
                if DISABLE_CHERRY_PICKING or len(commits) == 1:
                    result[issue_id] = [commits]
                    bar()
                    continue

                by_key = collections.defaultdict(list)
                for commit in commits:
                    if len(commit.parents) != 1:
                        pid = ''.join(
                            random.choices(string.ascii_letters, k=20)
                        )
                    else:
                        pid = client.patch_id(commit.commit.commit_hash)
                    key = (commit.commit.message, commit.commit.timestamp, pid)
                    by_key[key].append(commit)

                for group in by_key.values():
                    if len(group) <= 1:
                        continue
                    self._logger.info(
                        f'Found cherry-pick group: %s',
                        [commit.commit.commit_hash for commit in group]
                    )

                result[issue_id] = self._path_product(list(by_key.values()))
                bar()
        return result

    def _path_product(self, groups: list[list[CommitNode]]):
        return list(itertools.product(*groups))

    ###########################################################################
    ###########################################################################
    # Branch Disambiguation
    ###########################################################################

    def _disambiguate_branches(self, heads: list[CommitNode]):
        front = collections.deque(heads)
        contained_commits = {}
        issue_assignments = {}
        original_assignments = {
            c.commit.uid: set(c.linked_issues)
            for c in self._commits.values()
        }
        ref_counts = {
            c.commit.uid: len(c.children) for c in self._commits.values()
        }
        visited = set()
        while front:
            current = front.popleft()

            if current.commit.uid in visited:
                continue

            # Make sure all parents have been processed
            if not all(parent.commit.uid in contained_commits for parent in current.parents):
                front.append(current)
                continue
            visited.add(current.commit.uid)

            if len(current.parents) == 0:
                contained_commits[current.commit.uid] = {current.commit.uid}
            elif len(current.parents) == 1:
                base = contained_commits[current.parents[0].commit.uid]
                contained_commits[current.commit.uid] = base | {current.commit.uid}
            else:
                # Disambiguate commits being merged into the 'main' branch
                main = contained_commits[current.parents[0].commit.uid]
                if len(current.parents) != 2:
                    raise ValueError(
                        f'Commit {current.commit.commit_hash} has more than 2 parents, '
                        f'which is not supported by the branch disambiguation algorithm.'
                    )
                new_from_branch = contained_commits[current.parents[1].commit.uid] - main
                merge_issues, merge_original, in_branch, diff_point, reason = self._disambiguate_merge(
                    current.commit.uid,
                    new_from_branch,
                    original_assignments
                )
                issue_assignments[current.commit.uid] = {
                    'merge_issues': merge_issues,
                    'merge_original': merge_original,
                    'in_branch': in_branch,
                    'branch_commits': new_from_branch,
                    'diff_point': diff_point,
                    'reason': reason
                }

                # Update state
                for parent in current.parents[1:]:
                    main |= contained_commits[parent.commit.uid]
                contained_commits[current.commit.uid] = main | {current.commit.uid}

            # Free memory for parents if possible
            for parent in current.parents:
                ref_counts[parent.commit.uid] -= 1
                if ref_counts[parent.commit.uid] == 0:
                    contained_commits.pop(parent.commit.uid)

            # Add children to queue
            front.extend(current.children)

        return issue_assignments

    def _disambiguate_merge(self,
                            merge_commit: int,
                            branch: set[int],
                            original_assignments: dict[int, set[int]], *,
                            aggregate_unlinked: bool=False):
        # Returns a 5-tuple:
        #   1) New issues linked to merge commit
        #   2) Old issues linked to merge commit
        #   3) All issues contained in the branch itself (excl. the merge commit)
        #   4) "Diff point" for the merge commit.
        #       Guaranteed to be not None when the merge commit has linked
        #       issues; None otherwise.
        #       Downstream code (index loader) assumes the branch does not
        #       contain any linked issues if the diff point is not None.
        #   5) The resolution rule applied.
        #
        # Until further notice, this function imposes the following invariant:
        #   A merge commit has linked issue if and only if all of the
        #   following conditions are met:
        #       i) The issues in the branch have no linked issues
        #       ii) The branch has a single 'entry' commit
        #
        # If this ever changes, downstream code will require further changes.
        # In particular, the 'merge commit diff point resolution' code.
        branch = list(branch)
        linked = [original_assignments[c] for c in branch]
        linked_merge = original_assignments[merge_commit]
        in_branch = set()
        for b in linked:
            in_branch |= b

        entry_points = self._find_entry_points_for_branch(set(branch))
        total_entry_points = sum(
            len(incoming) for _, incoming in entry_points
        )
        if total_entry_points != 1:
            # Only branches with exactly one entry point can be handled;
            # branches with 0 (merging of disjoint history) or
            # multiple cannot be handled.
            return set(), linked_merge, in_branch, None, 'entry-points'

        diff_point = list(entry_points[0][1])[0]

        if self._all_equal(linked, value=linked_merge):
            # Since all constituent commits have been flagged,
            # letting the merge commit keep its labels would
            # cause label duplication.
            # (the 'old' alternative was linked_merge)
            return set(), linked_merge, in_branch, None, 'all-equal'

        if self._all_equal(linked, value=set()):
            return linked_merge, linked_merge, in_branch, diff_point, 'all-empty'

        if self._all_equal(linked) and self._all_equal(linked, predicate=lambda v: v < linked_merge):
            # Since all constituent commits have been flagged,
            # letting the merge commit keep its labels would
            # cause label duplication.
            # (the 'old' alternative was linked[0])
            return set(), linked_merge, in_branch, None, 'subset'

        if aggregate_unlinked and len(linked_merge) == 1:
            # empty_or_exact_link = self._all_equal(
            #     linked, predicate=lambda v: v == linked_merge or not v
            # )
            # if empty_or_exact_link:
            #     return linked_merge, linked_merge, in_branch, diff_point, 'aggregate'
            raise NotImplementedError('Aggregate unlinked is not supported')

        return set(), linked_merge, in_branch, None, 'default'

    @staticmethod
    def _all_equal(x: list[T], *, value=None, predicate=None) -> bool:
        if value is not None and predicate is not None:
            raise ValueError('Value and predicate are mutually exclusive')
        if not x:
            return True
        if value is not None:
            predicate = lambda v: v == value
        elif predicate is None:
            predicate = lambda v: v == x[0]
        return all(map(predicate, x))

    def _find_entry_points_for_branch(self,
                                      branch: set[int]) -> list[tuple[int, set[int]]]:
        # 1) Determine a set of entry points.
        #       -> The subset of all commits in 'branch' where
        #           at least one of the commit's parents is not
        #           contained in 'branch'.
        entry_commits = branch.copy()
        for commit_id in branch:
            commit = self._commits[commit_id]
            if all(parent.commit.uid in branch for parent in commit.parents):
                entry_commits.remove(commit_id)

        # 2) For all commits, compute and return their actual entry points.
        entry_points = []
        for commit_id in entry_commits:
            commit = self._commits[commit_id]
            entry_parents = {
                parent.commit.uid
                for parent in commit.parents
                if parent.commit.uid not in branch
            }
            entry_points.append((commit_id, entry_parents))

        return entry_points

    ###########################################################################
    ###########################################################################
    # Computing commits per issue
    ###########################################################################

    @property
    def commits_per_issue(self) -> dict[int, list[CommitNode]]:
        result = collections.defaultdict(list)
        for n in self._commits.values():
            for i in n.linked_issues:
                result[i].append(n)
        return result

    @property
    def commits_per_issue_cleaned(self) -> tuple[dict[int, list[CommitNode]], dict[int, int]]:
        base = self.commits_per_issue

        # Remove issues violating branch consistency,
        # taking into account multiple path possibilities
        # stemming from cherry-picking
        all_paths = self._handle_cherry_picks(base)
        inconsistent, cut = self._check_issue_branch_consistency(self._tail, all_paths)
        for i in inconsistent:
            del base[i]
            self._logger.warning(
                f'Discarding issue {self._keys[i]} (violation of branch consistency)'
            )
        if DISABLE_CHERRY_PICKING:
            assert len(cut) == 0
        for i, commits in cut.items():
            for c in commits:
                if i not in base:
                    continue
                base[i] = [x for x in base[i] if x.commit.uid != c]
                sha = self._commits[c].commit.commit_hash
                self._logger.warning(
                    f'Removing issue {self._keys[i]} from commit {sha} (cherry pick)'
                )

        # Clean up merge commits
        assignments = self._disambiguate_branches(self._heads)
        diff_points = {}
        for commit_id, assignment in assignments.items():
            if (dp := assignment['diff_point']) is not None:
                diff_points[commit_id] = dp
            if assignment['merge_issues'] == assignment['merge_original']:
                continue
            removed_from_merge =  assignment['merge_original'] - assignment['merge_issues']
            removed = removed_from_merge - assignment['in_branch']
            # The issues in removed where only present in the merge commit,
            # and now no longer have an associated commit in the branch.
            # This issue is tainted and will be removed
            for i in removed:
                if i in base:
                    del base[i]
                self._logger.warning(
                    f'Discarding issue {self._keys[i]} (removed due to branch disambiguation)'
                )
            # Also update the merge commit accordingly.
            # First loop handles additions,
            # second loop handles deletions.
            sha = self._commits[commit_id].commit.commit_hash
            for i in assignment['merge_issues']:
                if i not in base:
                    continue
                if not any(c.commit.uid == commit_id for c in base[i]):
                    base[i].append(self._commits[commit_id])
                    self._logger.warning(
                        f'Annotating merge commit {sha} with extra issue {self._keys[i]} (merge disambiguation)'
                    )
            for i in removed_from_merge:
                if i not in base:
                    continue
                base[i] = [c for c in base[i] if c.commit.uid != commit_id]
                self._logger.warning(
                    f'Discarding issue {self._keys[i]} from commit {sha} (merge disambiguation)'
                )

            reason = assignment['reason']
            if assignment['merge_issues'] == assignment['merge_original']:
                if reason == 'all-equal' or reason == 'all-empty':
                    self._logger.info(f'Merge {sha} unchanged due to reason {reason}')
            else:
                if reason == 'subset' or reason == 'aggregate':
                    self._logger.info(f'Merge {sha} changed due to reason {reason}')

        return base, diff_points

    @staticmethod
    def _is_merge(n: CommitNode) -> bool:
        return len(n.parents) > 1

    ###########################################################################
    ###########################################################################
    # Issue branch consistency
    ###########################################################################

    def _distance_to_main(self, root: CommitNode) -> dict[int, int]:
        distances = {}
        queue = collections.deque([root])
        while queue:
            current = queue.popleft()
            uid = current.commit.uid
            if uid in distances:
                continue
            if not all(p.commit.uid in distances for p in current.children):
                queue.append(current)
                continue
            distances[uid] = min(
                (distances[p.commit.uid] for p in current.children),
                default=0
            )
            for p in current.parents:
                queue.append(p)
        return distances

    def _check_issue_branch_consistency(self,
                                        root: CommitNode,
                                        commits_per_issue: dict[int, list[list[CommitNode]]]):
        failures = []
        discarded_for_cherry = {}
        distances = self._distance_to_main(root)
        total = sum(len(x) for x in commits_per_issue.values())
        with alive_progress.alive_bar(total) as bar:
            for issue_id, paths in commits_per_issue.items():
                working_paths = []
                for commits in paths:
                    # No checks are needed if we only have 1 commit and 1 path.
                    # If we have multiple commits, we have to check whether a path exists
                    # If multiple paths exist, we have to determine their
                    # distance to main.
                    if len(commits) == 1 and len(paths) == 1:
                        working_paths.append(commits)
                        bar()
                        continue
                    target = {x.commit.uid for x in commits}
                    for c in commits:
                        if len(c.parents) > 1:
                            if len(c.parents) > 2:
                                raise ValueError(
                                    'Issue branch consistency algorithm only supports merge '
                                    'commits with up to 2 parents.'
                                )
                            # Add the parent merged into the branch, to make
                            # sure the branch is part of the path.
                            target.add(c.parents[1].commit.uid)
                    stack = [(root, set())]
                    cache = {}
                    while stack:
                        commit, seen = stack.pop()
                        if commit.commit.uid in cache:
                            previous = cache[commit.commit.uid]
                            if seen > previous:
                                pass                # This path is better; continue
                            else:
                                # Either equal/subset or non-empty symmetric difference;
                                # either failure or worse/equal result; no need to continue
                                continue
                        cache[commit.commit.uid] = seen

                        if commit.commit.uid in target:
                            seen = seen | {commit.commit.uid}
                        if not commit.parents:
                            if seen == target:
                                working_paths.append(commits)
                                break
                        for i, parent in reversed(list(enumerate(commit.parents))):
                            stack.append((parent, seen))
                    bar()
                if not working_paths:
                    failures.append(issue_id)
                    continue
                if len(working_paths) == 1:
                    continue
                best_path = max(
                    working_paths,
                    key=lambda p: max(distances[pc] for pc in p)
                )
                all_commits = set()
                for path in paths:
                    all_commits |= set(path)
                discarded = all_commits - set(best_path)
                discarded_for_cherry[issue_id] = discarded
        return failures, discarded_for_cherry

    ###########################################################################
    ###########################################################################
    # Temporal merging
    ###########################################################################

    def _temporal_merge(self,
                        group: list[CommitNode],
                        threshold: float,
                        f: float,
                        how: typing.Literal['oldest', 'newest', 'density']):
        # Divide into subgroups such that consecutive commits are separated
        # by at most 'threshold' seconds
        subgroups = []
        group.sort(key=lambda z: z.commit.timestamp)
        current = [group[0]]
        for x, y in zip(group[:-1], group[1:], strict=True):
            delta = (y.commit.timestamp - x.commit.timestamp).total_seconds() * f
            if delta > threshold:
                subgroups.append(current)
                current = [y]
            else:
                current.append(y)
        subgroups.append(current)

        # Select one representative subgroup based on the chosen
        # merge method.
        if len(subgroups) == 1:
            return subgroups[0]
        elif how == 'oldest':
            out = subgroups[0]
        elif how == 'newest':
            out = subgroups[-1]
        elif how == 'density':
            out = max(subgroups, key=len)
        else:
            raise ValueError(f'Unknown temporal merge method: {how}')

        total = len(group)
        merged = len(out)
        boundary_deltas = [
            (y[0].commit.timestamp - x[-1].commit.timestamp).total_seconds() * f
            for x, y in zip(subgroups[:-1], subgroups[1:], strict=True)
        ]
        bounds = ' - '.join(f'{x:.2f}' for x in boundary_deltas)
        self._logger.warning(
            'Discarding commits in temporal merge (%s / %s retained; boundary deltas: %s)',
            merged, total, bounds
        )
        return out

    def _temporal_spread_data(self, f: float = 1.0):
        commits_per_issue = self.commits_per_issue_cleaned[0]
        spread = sum(len(v) > 1 for v in commits_per_issue.values())
        self._logger.info('# Temporally Spread Commits: %s', spread)
        deltas = []
        for uid, commits in commits_per_issue.items():
            timestamps = sorted(c.commit.timestamp for c in commits)
            deltas_for_commit = [
                (y - x).total_seconds() * f
                for x, y in zip(timestamps[:-1], timestamps[1:], strict=True)
            ]
            deltas.extend(deltas_for_commit)
        return deltas

    def _temporal_spread_threshold(self,
                                   f: float = 1.0,
                                   th_pct: float = 0.9,
                                   test_iqr: str | None = None):
        deltas = sorted(self._temporal_spread_data(f))
        mean = statistics.mean(deltas)
        median = statistics.median(deltas)
        std = statistics.stdev(deltas)
        mode = statistics.mode(deltas)
        self._logger.info('# Samples for delta computation: %s', len(deltas))
        self._logger.info('Mean delta: %s', mean)
        self._logger.info('Median delta: %s', median)
        self._logger.info('Std dev delta: %s', std)
        self._logger.info('Mode of deltas: %s', mode)
        index = int(len(deltas) * th_pct)
        threshold = deltas[index]
        self._logger.info('Threshold (%s): %s', th_pct, threshold)

        if test_iqr is not None:
            q1, q2, q3 = statistics.quantiles(deltas)
            iqr = q3 - q1
            bound = q3 + 1.5*iqr
            included = [x for x in deltas if x < bound]
            report = {
                'mean': mean,
                'median': median,
                'std': std,
                'mode': mode,
                'q1': q1,
                'q3': q3,
                'iqr': iqr,
                'bound': bound,
                'th-filtered': {
                    'threshold': threshold,
                    'kept': th_pct,
                },
                'iqr-filtered': {
                    'threshold': bound,
                    'kept': len(included) / len(deltas),
                }
            }
            with open(test_iqr, 'w') as f:
                json.dump(report, f, indent=2)
            sys.exit(0)

        return threshold

    def compute_issue_spread_statistics(self, issues=None):
        f = 1 / (60 * 60 * 24)
        deltas = self._temporal_spread_data(f)
        fig, ax = pyplot.subplots()
        ax.hist(deltas, density=True, bins=100, cumulative=False)
        mu = statistics.mean(deltas)
        std = statistics.stdev(deltas)
        ax.axvline(mu, color = 'k', linestyle = 'dashed', linewidth=1)
        ax.axvline(mu - std, color='k', linestyle='dashed', linewidth=1)
        ax.axvline(mu + std, color='k', linestyle='dashed', linewidth=1)
        #ax.axhline(0.2, xmin=mu - std, xmax=mu + std, linestyle='dashed', color='k', linewidth=1)
        ax.axvline(statistics.median(deltas), color='k', linestyle='dotted', linewidth=1)
        for c in self._commits.values():
            if c.commit.uid not in self._main:
                continue
            if self._is_merge(c):
                continue
            if not c.linked_issues:
                continue
            key = issues[c.linked_issues[0]].key.split('-')[0]
            pattern = re.compile(fr'{key}-\d+', flags=re.IGNORECASE)
            h = self._head(c.commit.message)
            in_head = {
                x.upper()
                for x in pattern.findall(h)
            }
            in_body = {issues[x].key for x in c.linked_issues} - in_head
            if in_body:
                print(c.commit.commit_hash, h, in_body)
        return fig

    @staticmethod
    def _head(x: str) -> str:
        lines = [
            line.strip() for line in x.splitlines() if line.strip()
        ]
        return lines[0]


class MergeDAG:

    def __init__(self, root: CommitNode):
        nodes_on_main = set()
        init_nodes = set()
        foo = root
        nodes_on_main.add(foo.commit.uid)
        while foo.parents:
            foo = foo.parents[0]
            nodes_on_main.add(foo.commit.uid)

        links = set()
        nodes = {}
        while root.parents and len(root.parents) == 1:
            root = root.parents[0]
        nodes[root.commit.uid] = {
            'uid': root.commit.uid,
            'sha': root.commit.commit_hash,
            'msg': root.commit.message,
            'bgn': not bool(root.parents),
            'end': True
        }
        stack = [
            (parent, root, i) for i, parent in enumerate(root.parents)
        ]
        while stack:
            current, to, order = stack.pop()
            while current.parents and len(current.parents) == 1 and len(current.children) == 1:
                current = current.parents[0]
            if not current.parents:
                init_nodes.add(current.commit.uid)
            if current.commit.uid not in nodes:
                nodes[current.commit.uid] = {
                    'uid': current.commit.uid,
                    'sha': current.commit.commit_hash,
                    'msg': current.commit.message,
                    'bgn': not bool(current.parents),
                    'end': False
                }
                for o, parent in enumerate(current.parents):
                    stack.append((parent, current, o))
            links.add((current.commit.uid, to.commit.uid, order))

        self.links = {}
        for a, b, o in links:
            self.links.setdefault((a, b), set()).add(o)
        self.nodes = nodes
        self.nodes_on_main = nodes_on_main
        self.init_nodes = init_nodes

    def render(self):
        self._remove_by_threshold(2)
        self._remove_by_threshold(1)
        colors = [
            'red',
            'green',
            'orange',
            'purple'
        ]
        import graphviz
        digraph = graphviz.Digraph()
        for uid, node in self.nodes.items():
            if node['bgn']:
                shape = 'doubleoctagon'
            elif node['end']:
                shape = 'diamond'
            else:
                shape = 'oval'
            digraph.node(
                str(uid),
                label=str(node['uid']),
                shape=shape
            )
        for a, b in self.links:
            for order in self.links[(a, b)]:
                if a in self.nodes_on_main and b in self.nodes_on_main and order == 0:
                    color = 'blue'
                else:
                    color = colors[order]
                digraph.edge(
                    str(a),
                    str(b),
                    # label=str(order),
                    color=color
                )
        digraph.render('merge-dag.gv', view=True)

    def _remove_by_threshold(self, count: int):
        while True:
            incoming = collections.defaultdict(set)
            outgoing = collections.defaultdict(set)
            counts = collections.defaultdict(int)
            for a, b in self.links:
                counts[(a, b)] += len(self.links[(a, b)])
                incoming[b].add(a)
                outgoing[a].add(b)

            for b, inc in incoming.items():
                if b in self.init_nodes:
                    continue
                if len(inc) != 1:
                    continue
                a = list(inc)[0]
                if a in self.init_nodes:
                    continue
                if counts[(a, b)] < count:
                    continue
                if count == 1 and len(outgoing[b]) > 1:
                    continue
                # Remove link (a, b)
                # For each link (b, x), add (a, x)
                del self.links[(a, b)]
                for x in outgoing[b]:
                    payload = self.links[(b, x)]
                    self.links.setdefault((a, x), set()).update(payload)
                    del self.links[(b, x)]
                del self.nodes[b]
                break
            else:
                break


