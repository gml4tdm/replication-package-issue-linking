import contextlib
import functools
import random
import shlex
import string
import subprocess
import warnings

from . import process_runner


class GitCmdClient:

    def __init__(self, repo: str):
        self.repo = repo
        self._cached_symlink_state = None

    def _execute(self, args, *, strict=True):
        errors = 'strict' if strict else 'ignore'
        with contextlib.chdir(self.repo):
            return process_runner.run_process(args,
                                              stream_stdout=False,
                                              stream_stderr=False,
                                              capture_stdout=True,
                                              error_handling=errors)[0]

    def _call(self, cmd: list[str], *, strict=True) -> str:
        return self._execute(cmd, strict=strict)

    def _call_shell(self, cmd: str, *, strict=True) -> str:
        return self._execute(shlex.split(cmd), strict=strict)

    def current_branch(self) -> str:
        return self._call(['git', 'branch', '--show-current'])

    def checkout(self, commit_hash: str):
        self._call(['git', 'checkout', commit_hash])

    @contextlib.contextmanager
    def checked_out(self, commit_hash: str, *, symlinks=True):
        if self._cached_symlink_state is None:
            out = self._call_shell('git config get core.symlinks')
            self._cached_symlink_state = out.strip() != 'false'
        if self._cached_symlink_state != symlinks:
            self._call_shell('git config core.symlinks %s' % ('true' if symlinks else 'false'))
        current = self.current_branch()
        try:
            self.checkout(commit_hash)
            yield
        finally:
            self._call_shell(
                'git config set core.symlinks %s' % ('true' if self._cached_symlink_state else 'false')
            )
            self.checkout(current)

    def tags(self) -> list[tuple[str, str]]:
        output = self._call_shell('git show-ref --tags')
        result = []
        for line in output.splitlines(keepends=False):
            commit_hash, tag_name = line.split()
            result.append((commit_hash, tag_name))
        return result

    @functools.lru_cache(maxsize=100_000)
    def merge_base(self, first: str, second: str = 'HEAD') -> str | None:
        output = self._call(['git', 'merge-base', first, second])
        if not output:
            return None
        return output

    def in_main_branch(self, commit_hash: str) -> bool:
        return self.merge_base(commit_hash) == commit_hash

    def count_commits(self) -> int:
        return int(self._call_shell('git rev-list --count HEAD'))

    def last_modified(self, commit_hash: str, filename: str) -> str | None:
        output = self._call(['git', 'rev-list', '-2', commit_hash, '--', filename])
        if not output:
            return None
        hashes = output.splitlines(keepends=False)
        assert hashes[0] == commit_hash
        return hashes[-1]

    def file_at_commit(self, commit_hash: str, filename: str) -> str:
        output = self._call(['git', 'show', f'{commit_hash}:{filename}'], strict=False)
        return output

    def files_at_commit(self, commit_hash: str) -> list[str]:
        output = self._call([
            'git', 'ls-tree', '--name-only', '--full-tree', '-r', commit_hash
        ])
        assert output
        return output.splitlines(keepends=False)

    def files_in_commit(self, commit_hash: str) -> list[str]:
        output = self._call(['git', 'ls-tree', '-r', commit_hash, '--name-only'])
        if not output:
            return []
        return output.splitlines(keepends=False)

    def previous_commit(self, commit_hash: str) -> str | None:
        output = self._call(['git', 'log', '--pretty=%P', '-1', commit_hash])
        if not output:
            return None
        return output.strip()

    def patch_id(self, commit_hash: str) -> str:
        with contextlib.chdir(self.repo):
            p_c = subprocess.Popen(
                ['git', 'show', commit_hash],
                stdout=subprocess.PIPE
            )
            p_p = subprocess.Popen(
                ['git', 'patch-id', '--stable'],
                stdin=p_c.stdout,
                stdout=subprocess.PIPE
            )
            p_c.wait()
            p_c.stdout.close()
            out, _err = p_p.communicate()
        try:
            return out.decode().split()[0]
        except IndexError:
            if self._different_from_parent(commit_hash):
                raise ValueError(
                    f'Empty Patch ID for commit {commit_hash}'
                )
            warnings.warn(
                f'Commit {commit_hash} is equal to its parent. Returning dummy ID.'
            )
            return ''.join(random.choices(string.ascii_letters, k=20))

    def _different_from_parent(self, commit_hash: str):
        out = self._call(['git', 'diff', commit_hash, f'{commit_hash}^1'])
        return bool(out)
