import collections
import copy
import datetime
import functools
import itertools
import json
import logging
import pathlib
import sys
import traceback
import warnings

import alive_progress
import pydriller
import tap

from ...utils.calc_size import calculate_object_size
from ...utils.git_utils import GitCmdClient
from ...utils.resources import resolve_resource_path
from ...utils.issue_db import IssueDatabaseWrapper
from ...utils import logs
from ..base import BaseCommand, register


def _json_dump(o, f):
    json.dump(o, f, separators=(',', ':'))


class GenerateFeaturePlanFromDbConfig(tap.Tap):
    repo_name: str
    repo_path: str
    project_name: str
    database_url: str
    output_directory: pathlib.Path
    dump_extensions: bool = False
    strip_extensions: bool = True


@register('generate-feature-plan-from-db')
class GenerateFeaturePlanFromDbCommand(BaseCommand):

    _extensions = resolve_resource_path('extensions.json')

    @staticmethod
    def config_type() -> type[tap.Tap]:
        return GenerateFeaturePlanFromDbConfig

    def execute(self):
        assert isinstance(self.config, GenerateFeaturePlanFromDbConfig)
        logger = logs.get_logger(self.__class__.__qualname__)
        self.config.output_directory.mkdir(parents=True, exist_ok=True)

        db = IssueDatabaseWrapper.from_url_sync(self.config.database_url)

        with logs.measure_time(logger, 'Fetching commits'):
            all_commits = db.get_commits_sync(self.config.repo_name,
                                              self.config.project_name,
                                              return_modified_files=True)
            logger.info('Fetched %s commits', len(all_commits))

        packer = SourceFilePacker(self.config.repo_path,
                                  source_output_directory=self.config.output_directory / 'source-code',
                                  filename_output_directory=self.config.output_directory / 'filenames',
                                  logger=logger,
                                  extension_file=self._extensions,
                                  strip_extensions=self.config.strip_extensions,
                                  max_restoration_length=500)
        index = packer.pack_commits([c.commit_hash for c in all_commits])
        packer.close()

        commit_registry = index['commit_registry']
        file_registry = index['file_registry']
        extensions = index.pop('extensions')
        pairings, diff_points = self._generate_pairings(db, commit_registry, file_registry, packer)
        payload = {
            'pairings': pairings,
            'diff_points': diff_points,
            **index
        }

        with open(self.config.output_directory / 'index.json', 'w') as f:
            _json_dump(payload, f)

        if self.config.dump_extensions:
            with open(self.config.output_directory / 'extensions.json', 'w') as f:
                _json_dump(list(extensions), f)

    @staticmethod
    def _get_source_slow(repo_path: str, commit_hash, filename: str):
        client = GitCmdClient(repo_path)
        return client.file_at_commit(commit_hash, filename)

    def _generate_pairings(self,
                           db: IssueDatabaseWrapper,
                           commit_registry,
                           file_registry,
                           packer):
        assert isinstance(self.config, GenerateFeaturePlanFromDbConfig)
        pairs = db.get_linked_issues_and_commits_sync(self.config.repo_name,
                                                      self.config.project_name,
                                                      return_modified_files=True)

        writer = FileWriter(self.config.output_directory / 'issue-features')
        pairings = []
        diff_points = {}
        #with alive_progress.alive_bar(len(pairs)) as bar:
        if True:
            for issue, commits in pairs:
                #bar()
                payload = {
                    'issue_key': issue.key,
                    'resolving_commits': [],
                    'files_changed_for_commits': [],     # changed_files
                    'issue-data': writer.add_file({
                        'summary': issue.summary,
                        'description': issue.description,
                    })
                }
                for commit in commits:
                    payload['resolving_commits'].append(commit_registry[commit.commit_hash])
                    if (diff_point := commit.diff_point) is not None:
                        diff_points[commit_registry[commit.commit_hash]] = commit_registry[diff_point]
                payload['files_changed_for_commits'] = packer.get_clean_modified_files(
                    [commit.commit_hash for commit in commits]
                )
                if not any(bool(x) for x in payload['files_changed_for_commits']):
                    continue
                pairings.append(payload)
        writer.flush()
        return pairings, diff_points

    @staticmethod
    def _find_commit(commits, ts: datetime.datetime):
        low = 0
        high = len(commits)
        while low < high:
            mid = (low + high) // 2
            commit = commits[mid]
            if commit.timestamp < ts:
                low = mid + 1
            else:
                high = mid
        assert commits[low].timestamp >= ts
        assert low == 0 or commits[low - 1].timestamp < ts
        return commits[low].commit_hash


class QueryDefaultDict(dict):

    def __init__(self, default_factory):
        super().__init__()
        self._factory = default_factory

    def __missing__(self, key):
        value = self._factory(key)
        self[key] = value
        return value


class SourceFilePacker:

    def __init__(self,
                 repository_path: str, *,
                 source_output_directory: pathlib.Path,
                 filename_output_directory: pathlib.Path,
                 logger: logging.Logger,
                 extension_file: pathlib.Path | None = None,
                 strip_extensions: bool = True,
                 max_restoration_length: int = 500):
        self._logger = logger
        self._max_restoration_length = max_restoration_length

        # Repository Interactions
        self._git_client = GitCmdClient(repository_path)
        self._repository_path = repository_path

        # Registries
        self._commit_registry = collections.defaultdict(
            lambda: str(len(self._commit_registry))
        )
        self._file_registry = QueryDefaultDict(
            self._register_filename_helper
        )

        # Tracking of commits
        #   * _packed_commits
        #       Fixed list of files, for merge commits (and the root commit)
        #   * _delta_by_commit
        #       List of changes per commit, or None in case of a merge commit.
        #   * _checkpoints
        #       Maps for every commit its restoration point;
        #       The algorithm takes the file in that commit,
        #       and fast forwards to the current commit by applying
        #       the deltas listed in all commits in between.
        #       The process may be recursive in case the restoration
        #       point must also be restored from its own restoration point.
        #       Restoration never traces back further than the most
        #       recent merge commit.
        self._delta_by_commit = {}
        self._checkpoints = {}
        self._packed_commits = {}

        self._parked_commits = {}
        self._filenames = {}

        self._source_writer = FileWriter(source_output_directory)
        self._filename_writer = FileWriter(filename_output_directory)

        self._changes_by_commit = {}
        self._merge_commit_diffs = {}
        self._commit_order = {}
        self._rev_order = {}

        # Tracking of file extensions
        self._strip_extensions = strip_extensions
        self._extensions = set()
        if extension_file is None:
            extension_file = resolve_resource_path('extensions.json')
        self._extension_filter = ExtensionFilter(extension_file)

    def close(self):
        self._source_writer.flush()
        self._filename_writer.flush()

    def _register_filename_helper(self, filename):
        if filename not in self._file_registry:
            uid = str(len(self._file_registry))
            self._filenames[uid] = (self._filename_writer.add_file(filename))
        else:
            uid = self._file_registry[filename]
        return uid

    @functools.cached_property
    def _commit_count(self):
        return self._git_client.count_commits()

    def _load_commits(self):
        commit_mapping = {}
        dependents_by_commit = collections.defaultdict(set)
        checkpoints = {}
        parents = {}
        with alive_progress.alive_bar(self._commit_count) as bar:
            bar.title('First pass')
            repo = pydriller.Repository(self._repository_path, order='topo-order')
            for commit in repo.traverse_commits():
                bar()
                commit_mapping[commit.hash] = commit
                for p in commit.parents:
                    dependents_by_commit[p].add(commit.hash)
                # Store parents
                commit_id = self._commit_registry[commit.hash]
                parent_ids = [
                    self._commit_registry[p] for p in commit.parents
                ]
                parents[commit_id] = parent_ids
                if len(parent_ids) == 0:
                    checkpoints[commit_id] = (commit_id, 0)
                elif len(parent_ids) > 1:
                    checkpoints[commit_id] = (commit_id, 0)
                else:
                    cp, dist = checkpoints[parent_ids[0]]
                    if dist + 1 > self._max_restoration_length:
                        checkpoints[commit_id] = (commit_id, 0)
                    else:
                        checkpoints[commit_id] = (cp, dist + 1)
        restoration_points = {
            k: v[0] for k, v in checkpoints.items()
        }
        return commit_mapping, dependents_by_commit, parents, restoration_points

    def get_clean_modified_files(self, commits: list[str]):
        commits = [self._commit_registry[h] for h in commits]
        commits.sort(key=int)
        changes = []
        state = set()
        for i in itertools.count(start=self._commit_order[commits[0]]):
            current = []
            if i > self._commit_order[commits[-1]]:
                break
            key = self._rev_order[i]
            if key in commits:
                for change_tp, old, new in self._changes_by_commit[key]:
                    if change_tp == 'rem':
                        if old not in state:
                            current.append(old)
                    elif change_tp == 'mod':
                        if old not in state:
                            current.append(old)
                        if old != new and old in state:
                            state.remove(old)
                        state.add(new)
                    else:
                        state.add(new)
                changes.append(current)
            else:
                for change_tp, old, new in self._changes_by_commit[key]:
                    if change_tp == 'rem':
                        if old in state:
                            state.remove(old)
                    elif change_tp == 'mod':
                        if old is not None and new is not None and old != new:
                            # Rename
                            if old in state:
                                state.remove(old)
                                state.add(new)
                    elif change_tp == 'add':
                        continue
        if len(changes) != len(commits):
            breakpoint()
        assert len(changes) == len(commits)
        return changes

    def pack_commits(self, hashes: list[str]):
        commit_mapping, dependents_by_commit, parents, restore_point_mapping = self._load_commits()
        restore_points = set(restore_point_mapping.values())
        with alive_progress.alive_bar(len(hashes)) as bar:
            for commit_hash in hashes:
                bar()
                commit = commit_mapping.pop(commit_hash)
                self._pack_commit(commit, dependents_by_commit, restore_points)
        filename_index = [self._filenames[str(i)] for i in range(len(self._filenames))]
        index = {
            'file_registry': self._file_registry,
            'commit_registry': self._commit_registry,
            'delta_by_commit': self._delta_by_commit,
            'packed_commits': self._packed_commits,
            'filename_index': filename_index,
            'restoration_points': restore_point_mapping,
            'parents': parents,
            'extensions': list(self._extensions),
            'changes_by_commit': self._changes_by_commit,
            'merge_commit_changes': self._merge_commit_diffs,
            'commit_order': {self._commit_registry[h]: i for i, h in enumerate(hashes)}
        }
        # self._commit_order.extend([
        #     self._commit_registry[h] for h in hashes
        # ])
        self._commit_order = {self._commit_registry[h]: i
                              for i, h in enumerate(hashes)}
        self._rev_order = {v: k for k, v in self._commit_order.items()}
        return index

    def _pack_commit(self, commit, dependents_by_commit, restore_points):
        commit_id = self._commit_registry[commit.hash]
        self._logger.debug(f'Packing commit {commit.hash} ({commit_id})')
        if len(commit.parents) > 1:
            parents = {
                p: self._parked_commits[p]
                for p in commit.parents
            }
            snapshot = self._pack_merge_commit(commit, parents)
            for parent in commit.parents:
                dependents_by_commit[parent].remove(commit.hash)
                if not dependents_by_commit[parent]:
                    del self._parked_commits[parent]
            self._parked_commits[commit.hash] = snapshot
            self._packed_commits[commit_id] = copy.deepcopy(snapshot)
        elif not commit.parents:
            deltas = self._pack_regular_commit(commit, {})
            assert commit_id in restore_points
            self._packed_commits[commit_id] = self._fast_forward({}, deltas)
            self._parked_commits[commit.hash] = self._fast_forward({}, deltas)
        else:
            try:
                parent = self._parked_commits[commit.parents[0]]
            except KeyError as e:
                print(commit_id, commit.hash)
                raise e 
            deltas = self._pack_regular_commit(commit, parent)
            if commit_id not in restore_points:
                self._delta_by_commit[commit_id] = deltas
            dependents_by_commit[commit.parents[0]].remove(commit.hash)
            if not dependents_by_commit[commit.parents[0]]:
                del self._parked_commits[commit.parents[0]]     # Free memory
                snapshot = self._fast_forward(parent, deltas)
            else:
                snapshot = self._fast_forward(copy.deepcopy(parent), deltas)
            if commit_id in restore_points:
                self._packed_commits[commit_id] = copy.deepcopy(snapshot)
            self._parked_commits[commit.hash] = snapshot
           
    def _pack_merge_commit(self, commit, parents):
        deltas = self._pack_regular_commit(commit,
                                           parents[commit.parents[0]],
                                           alternative_diff=True,
                                           is_merge_commit=True)
        for i in range(1, len(parents)):
            _ = self._pack_regular_commit(
                commit,
                parents[commit.parents[i]],
                alternative_diff=True,
                parent_index=i,
                is_merge_commit=True
            )
        original = copy.deepcopy(parents[commit.parents[0]])
        try:
            return self._fast_forward(copy.deepcopy(parents[commit.parents[0]]), deltas)
        except KeyError as e:
            self._logger.critical('Fast forward after merge failed')
            self._logger.critical(f'Main parent: {commit.parents[0]}')
            self._logger.critical(f'Commit: {commit.hash}')
            self._logger.critical(f'Parents: {commit.parents}')
            fid = e.args[0]
            rev_map = {v: k for k, v in self._file_registry.items()}
            self._logger.critical(f'Offending file: {rev_map[fid]}')
            entries = [delta for delta in deltas if delta[1] == fid]
            self._logger.critical(f'Offending deltas: {entries}')
            with open('deltas.json', 'w') as f:
                json.dump(deltas, f, indent=2)
            with open('original.json', 'w') as f:
                json.dump(original, f, indent=2)
            with open('registry.json', 'w') as f:
                json.dump(self._file_registry, f, indent=2)
            raise e

    def _pydriller_get_modified_files(self, commit: pydriller.Commit, *, parent=0):
        diff_index = commit._c_object.parents[parent].diff(
            other=commit._c_object, paths=None, create_patch=True
        )
        return commit._parse_diff(diff_index)

    def _fast_forward(self, parent, deltas):
        for kind, key, payload in deltas:
            if kind == 'add':
                parent[key] = payload
            elif kind == 'rem':
                if key not in parent:
                    self._logger.debug('%s', parent)
                del parent[key]
            else:
                raise ValueError(f'Unknown delta kind {kind}')
        return parent

    def _pack_regular_commit(self,
                             commit,
                             parent, *,
                             alternative_diff=False,
                             is_merge_commit=False,
                             parent_index=0):
        deltas = []
        if not alternative_diff:
            modified_files = commit.modified_files
        else:
            modified_files = self._pydriller_get_modified_files(commit, parent=parent_index)
        changes_for_commit = []
        for file in modified_files:
            if self._skip(file) and not self._is_special_skip(file):
                self._logger.debug(f'Skipping file %s -> %s', file.old_path, file.new_path)
                continue
            if self._is_special_skip(file):
                mods = (pydriller.ModificationType.MODIFY,
                        pydriller.ModificationType.UNKNOWN,
                        pydriller.ModificationType.RENAME)
                if file.change_type not in mods:
                    raise ValueError(f'Invalid special skip modification type')
            match file.change_type:
                case pydriller.ModificationType.ADD:
                    source = self._get_source_for_file(commit, file)
                    if source is None:
                        continue
                    self._logger.debug('Recording added file %s', file.new_path)
                    deltas.append(
                        ('add', self._file_registry[file.new_path], self._source_writer.add_file(source))
                    )
                    changes_for_commit.append(('add', None, self._file_registry[file.new_path]))
                    self._logger.debug('Added delta: %s', deltas[-1])
                case (pydriller.ModificationType.MODIFY |
                      pydriller.ModificationType.UNKNOWN |
                      pydriller.ModificationType.RENAME):
                    if file.change_type == pydriller.ModificationType.UNKNOWN:
                        self._logger.info(f'Unknown Change: {commit.hash} -- {file.old_path} -> {file.new_path}')
                    renamed = False
                    if self._is_rename(file) and not self._skip_name(file.old_path):
                        self._logger.debug(f'Rename {file.old_path} -> {file.new_path}')
                        deltas.append(('rem', self._file_registry[file.old_path], None))
                        renamed = True
                        self._logger.debug('Added delta: %s', deltas[-1])
                    source = self._get_source_for_file(commit, file)
                    if source is None:
                        if renamed:
                            deltas.pop()
                        continue
                    self._logger.debug('Recording modified file %s', file.new_path)
                    if self._is_special_skip(file):
                        # Special skips are handled as additions
                        changes_for_commit.append(
                            ('mod-special', self._file_registry[file.old_path], self._file_registry[file.new_path])
                        )
                    else:
                        changes_for_commit.append(
                            ('mod', self._file_registry[file.old_path], self._file_registry[file.new_path])
                        )
                    deltas.append(
                        ('add', self._file_registry[file.new_path], self._source_writer.add_file(source))
                    )
                    self._logger.debug('Added delta: %s', deltas[-1])
                case pydriller.ModificationType.DELETE:
                    self._logger.debug('Recording deleted file %s', file.old_path)
                    deltas.append(('rem', self._file_registry[file.old_path], None))
                    changes_for_commit.append(
                        ('rem', self._file_registry[file.old_path], None)
                    )
                    self._logger.debug('Added delta: %s', deltas[-1])
                case pydriller.ModificationType.COPY:
                    self._logger.debug('Recording copied file %s -> %s', file.old_path, file.new_path)
                    deltas.append(
                        ('add', self._file_registry[file.new_path], parent[file.old_path])
                    )
                    changes_for_commit.append(
                        ('add', None, self._file_registry[file.new_path])
                    )
                    self._logger.debug('Added delta: %s', deltas[-1])
                case _:
                    raise ValueError(f'Unknown file change type: {file.change_type}')
        changes_for_commit = self._deduplicate_changes(changes_for_commit)
        if parent_index == 0 or not is_merge_commit:
            self._changes_by_commit[self._commit_registry[commit.hash]] = changes_for_commit
        if is_merge_commit:
            k1 = self._commit_registry[commit.hash]
            k2 = self._commit_registry[commit.parents[parent_index]]
            self._merge_commit_diffs.setdefault(k1, {})[k2] = changes_for_commit
        return deltas

    def _deduplicate_changes(self, changes: list[tuple]) -> list[tuple]:
        # Remove certain weird duplication changes.
        # Currently:
        #   - File removed, then added -> Modified
        removed = set()
        added = set()
        for action, old, new in changes:
            if action == 'rem':
                removed.add(old)
            elif action == 'add':
                added.add(new)

        common = removed & added
        changes = [
            (action, old, new)
            for action, old, new in changes
            if not ((action == 'rem' and old in common) or (action == 'add' and new in common))
        ]
        for c in common:
            changes.append(('mod', c, c))
        return changes

    def _skip(self, file: pydriller.ModifiedFile):
        filenames = []
        if file.old_path is not None:
            filenames.append(file.old_path)
        if file.new_path is not None:
            filenames.append(file.new_path)
        skip = True
        for i, filename in enumerate(filenames, start=1):
            if self._skip_name(filename):
                ext = pathlib.Path(filename).suffix.lower()
                self._extensions.add(ext)
            else:
                skip = False
        return skip and self._strip_extensions

    def _is_special_skip(self, f: pydriller.ModifiedFile) -> bool:
        if f.old_path is None or f.new_path is None:
            return False
        if not self._skip_name(f.old_path):
            return False
        return not self._skip_name(f.new_path)      # SKIP OLD AND NOT NEW

    def _skip_name(self, fn: str):
        return not self._extension_filter.file_is_included(pathlib.Path(fn))

    @staticmethod
    def _is_rename(file: pydriller.ModifiedFile):
        is_rename_only = file.change_type == pydriller.ModificationType.RENAME
        is_rename_and_change = (
                file.old_path is not None and
                file.new_path is not None and
                file.old_path != file.new_path
        )
        return is_rename_only or is_rename_and_change

    def _get_source_for_file(self, commit, file: pydriller.ModifiedFile):
        try:
            source = file.source_code
        except ValueError as e:
            self._logger.error('Failed to load source code for %s', file.new_path)
            self._logger.error('Underling error:')
            for block in traceback.format_exception(e):
                for line in block.splitlines():
                    self._logger.error(line.rstrip())
            return '[SOURCE NOT AVAILABLE]'

        if source is None:
            self._logger.debug('Slow fetch of source code file %s', file.new_path)
            source = self._git_client.file_at_commit(commit.hash, file.new_path)

        return source


class ExtensionFilter:

    def __init__(self, path: pathlib.Path):
        with open(path) as file:
            raw = json.load(file)
        self._included = raw['included']
        self._mapping = {
            k: v['kind'] for k, v in raw['extensions'].items()
        }
        self._mapping |= {
            ext: item['kind']
            for item in raw['bulk']
            for ext in item['items']
        }
        self._mapping = {k.lower(): v for k, v in self._mapping.items()}

    def file_is_included(self, filename: pathlib.Path) -> bool:
        ext = filename.suffix.lower()
        return self.ext_is_included(ext)

    def ext_is_included(self, ext: str) -> bool:
        kind = self._mapping.get(ext, None)
        return kind is not None and kind in self._included


class FileWriter:

    _STR_BASE_SIZE = sys.getsizeof('')

    def __init__(self,
                 output_directory: pathlib.Path, *,
                 max_size: int = 1024 * 1024 * 1024):
        self._output_directory = output_directory
        self._output_directory.mkdir(parents=True, exist_ok=True)
        self._current_batch = []
        self._current_batch_size = 0
        self._batch_number = 0
        self._max_size = max_size
        self._closed = False

    def __del__(self):
        if not self._closed:
            warnings.warn('FileWriter is not closed')

    def report(self, logger: logging.Logger):
        logger.info(f'%s: Current batch: %s, Current batch size: %s (%s)',
                    self.__class__.__name__,
                    self._batch_number,
                    self._current_batch_size,
                    f'{self._current_batch_size / self._max_size:.2f}%'
                    )

    def report_size(self):
        total = 0
        total += calculate_object_size(self._current_batch)
        total += calculate_object_size(self._current_batch_size)
        total += calculate_object_size(self._batch_number)
        total += calculate_object_size(self._max_size)
        total += calculate_object_size(self._closed)
        return total

    def add_file(self, content: object) -> tuple[int, int]:
        if self._closed:
            raise RuntimeError('FileWriter is closed')
        extra = self._calc_json_size(content)
        if self._calc_size() + extra + 1 > self._max_size:
            self._flush()
        self._current_batch.append(content)
        self._current_batch_size += extra
        return self._batch_number, len(self._current_batch) - 1

    def flush(self):
        if self._closed:
            raise RuntimeError('FileWriter is closed')
        self._flush()
        self._closed = True

    def _calc_json_size(self, o):
        if isinstance(o, str):
            return sys.getsizeof(o) - self._STR_BASE_SIZE
        elif isinstance(o, list):
            size = sum(self._calc_json_size(x) for x in o)
            return size + 2 + len(o) - 1
        elif isinstance(o, dict):
            size = 2 + 2*len(o) - 1
            for k, v in o.items():
                size += self._calc_json_size(k)
                size += self._calc_json_size(v)
            return size
        raise NotImplementedError(f'Unknown type {type(o)}')

    def _calc_size(self) -> int:
        size = self._current_batch_size
        size += 2 + len(self._current_batch) - 1
        return size

    def _flush(self):
        with open(self._output_directory / f'{self._batch_number}.json', 'w') as f:
            _json_dump(self._current_batch, f)
        self._current_batch = []
        self._current_batch_size = 0
        self._batch_number += 1
