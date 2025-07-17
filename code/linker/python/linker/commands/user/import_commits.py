import collections
import copy
import enum
import graphlib
import itertools
import json
import logging
import re
import typing

import alive_progress
import pydriller
import tap

from ...utils.issue_key_extractor import IssueKeyExtractor
from ...utils import logs
from ...utils.issue_db import IssueDatabaseWrapper
from ...utils.git_utils import GitCmdClient
from ..base import BaseCommand, register


class ImportCommitsConfig(tap.Tap):
    repository_path: str
    postgres_url: str
    organisation: str
    project: str
    key_pattern: str
    multiple_key_handling: typing.Literal['first', 'last', 'ignore', 'all'] = 'first'
    extract_from: typing.Literal['title', 'body'] = 'title'



class KeyFinderResult(enum.Enum):
    NoMessage = enum.auto()
    NoMatches = enum.auto()
    ExactMatch = enum.auto()
    MultipleMatches = enum.auto()


@register('import-commits')
class ImportCommitsCommand(BaseCommand):

    @staticmethod
    def config_type() -> type[tap.Tap]:
        return ImportCommitsConfig

    def execute(self):
        assert isinstance(self.config, ImportCommitsConfig)
        logger = logs.get_logger(self.__class__.__name__)

        commit_info = self._collect_commit_information(logger)
        commits = commit_info[0]
        commit_file_modifications = commit_info[1]
        commit_parents = commit_info[2]
        commit_issue_links = commit_info[3]

        db = IssueDatabaseWrapper.from_url_sync(self.config.postgres_url)

        link_failures = db.insert_commit_information_sync(
            self.config.organisation,
            self.config.project,
            commits,
            commit_file_modifications,
            commit_parents,
            commit_issue_links
        )

        if link_failures:
            logger.warning(f'Failed to link %s commits', link_failures)

            filename = f'{self.config.organisation}-{self.config.project}-link-failures.json'
            with open(filename, 'w') as file:
                json.dump(list(link_failures), file)

    def _collect_commit_information(self, logger: logging.Logger):
        assert isinstance(self.config, ImportCommitsConfig)

        client = GitCmdClient(self.config.repository_path)
        total = client.count_commits()
        commit_mapping = {}
        order = []
        repo = pydriller.Repository(self.config.repository_path, order='topo-order')
        with alive_progress.alive_bar(total) as bar:
            bar.title('First pass')
            for i, commit in enumerate(repo.traverse_commits()):
                bar()
                commit_mapping[commit.hash] = (i, commit)
                order.append(commit.hash)

        print('Collecting commits')
        commits, by_hash = self._collect_commits(order, commit_mapping)
        print('Collecting modifications')
        commit_file_modifications = self._collect_modifications(order, commit_mapping)
        print('Collecting parents')
        commit_parents = self._collect_parents(order, commit_mapping, by_hash)

        key_extractor = IssueKeyExtractor(
            self.config.key_pattern,
            multiple_key_handling=self.config.multiple_key_handling
        )
        commit_issue_links = {}
        print('Collecting commit issue links')
        logger.setLevel(logging.ERROR)
        with alive_progress.alive_bar(len(order)) as bar:
            for a_i, commit_hash in enumerate(order):
                bar()
                seq, commit = commit_mapping[commit_hash]
                result, keys = key_extractor.get_key_from_message(
                    self._get_text_for_extraction(commit.msg),
                    logger
                )
                if keys is not None:
                    commit_issue_links[a_i] = [key.upper() for key in keys]
        return commits, commit_file_modifications, commit_parents, commit_issue_links

    def _get_text_for_extraction(self, msg: str) -> str:
        assert isinstance(self.config, ImportCommitsConfig)
        match self.config.extract_from:
            case 'title':
                lines = [x.strip() for x in msg.splitlines(keepends=False) if x.strip()]
                if not lines:
                    return ''
                return lines[0]
            case 'body':
                return msg 
            case x:
                raise ValueError(f'Invalid extraction method: {x}')

    def _all_consecutive(self, issue, commits, parents):
        for x, y in zip(commits[:-1], commits[1:]):
            if not any(p[0] == x for p in parents[y]):
                return False
        return True

    def _collect_commits(self, order, commit_mapping):
        commits = []
        by_hash = {}
        with alive_progress.alive_bar(len(order)) as bar:
            for a_i, commit_hash in enumerate(order):
                seq, commit = commit_mapping[commit_hash]
                bar()

                by_hash[commit.hash] = a_i

                commits.append(
                    (
                        commit.hash,
                        seq,
                        commit.committer_date,
                        commit.msg if commit.msg is not None else '',
                        len(commit.parents) > 1,
                        a_i
                    )
                )
        return commits, by_hash

    def _collect_modifications(self, order, commit_mapping):
        commit_file_modifications = []
        with alive_progress.alive_bar(len(order)) as bar:
            for a_i, commit_hash in enumerate(order):
                bar()
                seq, commit = commit_mapping[commit_hash]
                if len(commit.parents) <= 1:
                    modified_files = commit.modified_files
                else:
                    # For merge commits, determining the list of changed files might be tricky.
                    # We use the convention that the "left most" commit (parents[0]) is the
                    # main branch, and we use that to determine what files changed.
                    # In particular, we can diff the current commit with its parent
                    # to obtain a list of changes files -- since PyDriller does not
                    # readily provide us with one.
                    # Hence, for merge commits, we have to
                    #   1) diff the merge commit against its parent
                    #   2) parse the diff to obtain the modified files
                    #
                    # To do this, we use the `normal` implementation for obtaining the
                    # modified files from PyDriller, although it requires access to the
                    # internals of their code (_c_object and _parse_diff).
                    #
                    # Note that this strategy implies that changes from the right parents
                    # are in some sense duplicated for this commit, but we argue that
                    # this is okay for our use case.
                    diff_index = commit._c_object.parents[0].diff(
                        other=commit._c_object,
                        paths=None,
                        create_patch=True,
                    )
                    modified_files = commit._parse_diff(diff_index)
                files_for_commit = []
                for file in modified_files:
                    files_for_commit.append(
                        (file.old_path, file.new_path, file.change_type.name)
                    )
                commit_file_modifications.append(files_for_commit)
        return commit_file_modifications

    def _collect_parents(self, order, commit_mapping, by_hash):
        commit_parents = []
        with alive_progress.alive_bar(len(order)) as bar:
            for a_i, commit_hash in enumerate(order):
                seq, commit = commit_mapping[commit_hash]
                bar()
                parents_for_commit = []
                first = True
                for h in commit.parents:
                    if h in by_hash:
                        if any(x[0] == h for x in parents_for_commit):
                            raise ValueError(f'Duplicate parent {h} for commit {commit.hash}')
                        parents_for_commit.append((by_hash[h], first))
                        first = False
                    else:
                        raise ValueError(f'Parent {h} not found for commit {commit.hash}')
                commit_parents.append(parents_for_commit)
        return commit_parents

