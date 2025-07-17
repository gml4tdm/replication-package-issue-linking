from __future__ import annotations

import asyncio
import collections
import dataclasses
import datetime
import itertools
import typing
import warnings

import psycopg


def _make_sync(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@dataclasses.dataclass
class Issue:
    key: str
    summary: str
    description: str
    uid: int
    other_fields: dict[str, typing.Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(slots=True)
class Commit:
    uid: int
    commit_hash: str
    sequence_number: int
    timestamp: datetime.datetime
    message: str
    modified_files: list[ModifiedFile] | None = None
    parents: list[int] | None = None
    diff_point: str | None = None

    def _with_diff_point(self, dp: str | None) -> typing.Self:
        self.diff_point = dp
        return self


@dataclasses.dataclass(frozen=True, slots=True)
class ModifiedFile:
    old_path: str
    new_path: str
    change_type: str


@dataclasses.dataclass(frozen=True)
class Repo:
    name: str
    url: str
    last_downloaded: str
    wait_time: int


# noinspection PyTypeChecker
class IssueDatabaseWrapper:

    def __init__(self, connection: psycopg.AsyncConnection, url):
        self._url = url
        self._connection = connection

    async def _reconnect(self):
        if self._connection.closed:
            self._connection = await psycopg.AsyncConnection.connect(self._url)

    @classmethod
    async def from_url(cls, database_url):
        return cls(
            await psycopg.connection_async.AsyncConnection.connect(database_url),
            database_url
        )

    @classmethod
    def from_url_sync(cls, database_url) -> typing.Self:
        return _make_sync(cls.from_url(database_url))

    async def close(self):
        await self._connection.close()

    def close_sync(self):
        _make_sync(self.close())

    # async def get_main_branch_commits(self, repo: str, project: str, *, return_modified_files: bool = False):
    #     commits = await self.get_commits(repo, project, return_modified_files=return_modified_files)
    #     commits_by_id = {c.uid: c for c in commits}
    #     async with self._connection.cursor() as cursor:
    #         await cursor.execute(
    #             'SELECT commit_id, parent_id FROM commit_parents WHERE commit_id = ANY(%S) WHERE is_main;',
    #             [list(commits_by_id)]
    #         )
    #         main_parents = {}
    #         for child, parent in main_parents:
    #             if child in main_parents:
    #                 raise ValueError(f'Commit {child} has multiple main parents!')
    #             main_parents[child] = parent
    #         root_commits = set(commits_by_id) - set(main_parents)
    #         if not root_commits:
    #             raise ValueError('No root commit found')
    #         if len(root_commits) > 1:
    #             warnings.warn(f'Found {len(root_commits)} root commits. Picking oldest one.')
    #         candidates = [commits_by_id[uid] for uid in root_commits]
    #         root = min(candidates, key=lambda c: c.timestamp)


    def get_commits_sync(self,
                         repo: str,
                         project: str, *,
                         return_modified_files: bool = False,
                         merge_commits_only: bool = False,
                         return_parents: bool = False):
        return _make_sync(
            self.get_commits(repo,
                             project,
                             return_modified_files=return_modified_files,
                             merge_commits_only=merge_commits_only,
                             return_parents=return_parents)
        )

    async def get_commits(self,
                          repo: str,
                          project: str, *,
                          return_modified_files: bool = False,
                          merge_commits_only: bool = False,
                          return_parents: bool = False):
        if True:
            async with self._connection.cursor() as cursor:
                if merge_commits_only:
                    await cursor.execute(
                        f'SELECT commit.id, commit.sha, commit.sequence_number, commit.timestamp_utc, commit.message '
                        f'FROM commit '
                        f'INNER JOIN project ON commit.project_id = project.id '
                        f'INNER JOIN issue_repo ON project.repo_id = issue_repo.id '
                        f'WHERE issue_repo.name = %s AND project.name = %s '
                        f'AND commit.is_merge = true '
                        f'ORDER BY commit.analysis_seq_nr ASC;',
                        [repo, project]
                    )
                else:
                    await cursor.execute(
                        f'SELECT commit.id, commit.sha, commit.sequence_number, commit.timestamp_utc, commit.message '
                        f'FROM commit '
                        f'INNER JOIN project ON commit.project_id = project.id '
                        f'INNER JOIN issue_repo ON project.repo_id = issue_repo.id '
                        f'WHERE issue_repo.name = %s AND project.name = %s '
                        f'ORDER BY commit.analysis_seq_nr ASC;',
                        [repo, project]
                    )
                commits = [
                    Commit(
                        uid=row[0],
                        commit_hash=row[1],
                        sequence_number=row[2],
                        timestamp=row[3],
                        message=row[4]
                    )
                    for row in await cursor.fetchall()
                ]
                if return_modified_files:
                    await self._add_modified_files(commits)
                if return_parents:
                    await self._add_parents(commits)
                return commits

    async def _add_parents(self, commits: list[Commit]):
        commit_ids = [c.uid for c in commits]
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                'SELECT commit_id, parent_id, is_main FROM commit_parents WHERE commit_id = ANY(%s);',
                [commit_ids]
            )
            parents_by_id = {}
            main_parents_by_id = {}
            for commit_id, parent_id, is_main in await cursor.fetchall():
                mapping = main_parents_by_id if is_main else parents_by_id
                mapping.setdefault(commit_id, []).append(parent_id)

        for commit in commits:
            parents = main_parents_by_id.get(commit.uid, [])
            assert len(parents) <= 1
            parents += parents_by_id.get(commit.uid, [])
            commit.parents = parents

    async def get_repos(self) -> list[Repo]:
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                'SELECT name, url, last_downloaded_utc, query_wait_time_in_minutes FROM issue_repo;'
            )
            return [
                Repo(
                    name=row[0],
                    url=row[1],
                    last_downloaded=row[2],
                    wait_time=row[3]
                )
                for row in await cursor.fetchall()
            ]

    def get_repos_sync(self) -> list[Repo]:
        return _make_sync(self.get_repos())

    async def get_repo(self, name: str) -> Repo:
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                'SELECT name, url, last_downloaded_utc, query_wait_time_in_minutes '
                'FROM issue_repo WHERE issue_repo.name = %s;',
                [name]
            )
            row = await cursor.fetchone()
            if row is None:
                raise ValueError(f'Repo {name} not found')
            return Repo(
                name=row[0],
                url=row[1],
                last_downloaded=row[2],
                wait_time=row[3]
            )

    def get_repo_sync(self, name: str) -> Repo:
        return _make_sync(self.get_repo(name))

    def fetch_issue_fields_sync(self, issues: list[Issue], *fields: str) -> list[Issue]:
        return _make_sync(self.fetch_issue_fields(issues, *fields))

    async def fetch_issue_fields(self, issues: list[Issue], *fields: str) -> list[Issue]:
        async with self._connection.cursor() as cursor:
            fields_fmt = ', '.join(f'issue.{f}' for f in fields)
            await cursor.execute(
                f'SELECT issue.id, {fields_fmt} FROM issue WHERE issue.id = ANY(%s);',
                [[issue.uid for issue in issues]]
            )
            issues_by_id = {issue.uid: issue for issue in issues}
            for uid, *field_values in await cursor.fetchall():
                issue = issues_by_id[uid]
                for field, value in zip(fields, field_values):
                    issue.other_fields[field] = value
            return [issues_by_id[issue.uid] for issue in issues]

    async def get_issues_by_key(self, repo: str, *keys: str) -> dict[str, Issue]:
        # SELECT COUNT(*) FROM issue INNER JOIN project on issue.project_id = project.id WHERE project.key = 'CAMEL'
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                'SELECT issue.key, issue.summary, issue.description, issue.id FROM ('
                'SELECT issue.key, issue.summary, issue.description, issue.id FROM issue '
                'INNER JOIN project ON issue.project_id = project.id '
                'INNER JOIN issue_repo ON project.repo_id = issue_repo.id '
                'WHERE issue_repo.name = %s'
                ') AS issue WHERE issue.key = ANY(%s)',
                [repo, list(keys)]
            )
            return {
                row[0]: Issue(
                    key=row[0],
                    summary=row[1],
                    description=row[2],
                    uid=row[3],
                )
                for row in await cursor.fetchall()
            }

    def get_issues_by_key_sync(self, *keys: str) -> dict[str, Issue]:
        return _make_sync(self.get_issues_by_key(*keys))

    def get_issues_by_db_id_sync(self, ids: list[int]) -> dict[int, Issue]:
        return _make_sync(self.get_issues_by_db_id(ids))

    async def get_issues_by_db_id(self, ids: list[int]) -> dict[int, Issue]:
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                'SELECT id, key, summary, description FROM issue WHERE id = ANY(%s);',
                [ids]
            )
            return {
                row[0]: Issue(
                    key=row[1],
                    summary=row[2],
                    description=row[3],
                    uid=row[0]
                )
                for row in await cursor.fetchall()
            }

    def update_issues_by_jira_id_sync(self,
                                      repo: str,
                                      issues: dict[str, Issue], *,
                                      add_missing_projects: bool = False):
        coro = self.update_issues_by_jira_id(repo,
                                             issues,
                                             add_missing_projects=add_missing_projects)
        return _make_sync(coro)

    async def update_issues_by_jira_id(self,
                                       repo: str,
                                       issues: dict[str, Issue], *,
                                       add_missing_projects: bool = False):
        projects, repos = await self._project_information()
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                'SELECT issue.jira_id, issue.id, issue.key, issue.project_id FROM '
                '(SELECT issue.jira_id, issue.id, issue.key, issue.project_id FROM issue '
                'INNER JOIN project ON issue.project_id = project.id '
                'INNER JOIN issue_repo ON project.repo_id = issue_repo.id '
                'WHERE issue_repo.name = %s) AS issue '
                'WHERE issue.jira_id = ANY(%s);',
                [repo, list(issues.keys())]
            )
            result = {
                jira_id: (issue_id, key, project_id)
                for jira_id, issue_id, key, project_id in await cursor.fetchall()
            }

        async with self._connection:
            new_projects = []
            for jira_id, issue in issues.items():
                project_key = issue.key.split('-')[0]
                if project_key not in projects[repo]:
                    if not add_missing_projects:
                        raise ValueError(f'Project {repo} does not have project {project_key}')
                    new_projects.append((repos[repo], project_key, ''))
            if new_projects:
                async with self._connection.cursor() as cursor:
                    await cursor.executemany(
                        'INSERT INTO project (repo_id, key, name) VALUES (%s, %s, %s);',
                        new_projects
                    )
                projects, repos = await self._project_information()

            to_update = []
            to_insert = []
            for jira_id, issue in issues.items():
                if jira_id not in result:
                    project_key = issue.key.split('-')[0]
                    project_id = projects[repo][project_key][1]
                    values = (issue.key, issue.summary, issue.description, project_id, jira_id)
                    extra_fields = list(issue.other_fields)
                    to_insert.append((values + tuple(issue.other_fields.values()), extra_fields))
                else:
                    extra_fields = list(issue.other_fields)
                    values = (issue.key, issue.summary, issue.description)
                    to_update.append(
                        (result[jira_id][0],
                        values + tuple(issue.other_fields.values()),
                        extra_fields
                    ))

            if to_update:
                async with self._connection.cursor() as cursor:
                    for uid, values, extra_fields in to_update:
                        fields = ['key', 'summary', 'description']
                        fields.extend(extra_fields)
                        fillers = ", ".join(["%s"] * len(fields))
                        await cursor.execute(
                            f'UPDATE issue SET ({", ".join(fields)}) = ({fillers}) WHERE id = %s;',
                            (values + (uid,))
                        )
            if to_insert:
                async with self._connection.cursor() as cursor:
                    for values, extra_fields in to_insert:
                        fields = ['key', 'summary', 'description', 'project_id', 'jira_id']
                        fields.extend(extra_fields)
                        fillers = ", ".join(["%s"] * len(fields))
                        await cursor.execute(
                            f'INSERT INTO issue ({", ".join(fields)}) VALUES ({fillers});',
                            values
                        )
        await self._reconnect()

    async def _project_information(self):
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                'SELECT project.id, repo.id, project.key, repo.name FROM project '
                'INNER JOIN issue_repo AS repo ON project.repo_id = repo.id;'
            )
            result = {}
            repos = {}
            for p_id, r_id, p_key, r_name in await cursor.fetchall():
                result.setdefault(r_name, {})[p_key] = (r_id, p_id)
                repos[r_name] = r_id
            return result, repos

    async def update_repo(self, name: str, last_downloaded: datetime.datetime):
        #ts = last_downloaded.strftime('%Y-%m-%d %H:%M:%S')
        async with self._connection:
            async with self._connection.cursor() as cursor:
                await cursor.execute(
                    f'UPDATE issue_repo SET last_downloaded_utc = %s WHERE name = %s;',
                    (last_downloaded, name),
                )

    def update_repo_sync(self, name: str, last_downloaded: datetime.datetime):
        return _make_sync(self.update_repo(name, last_downloaded))

    def insert_commit_information_sync(self,
                                       repo_name: str,
                                       project_name: str,
                                       commits: list[tuple[str, int, datetime.datetime, str, bool, int]],
                                       file_modifications: list[list[tuple[str, str | None, str | None]]],
                                       parent_ids: list[list[tuple[int, bool]]],
                                       issue_links: dict[int, list[str]]):
        return _make_sync(self.insert_commit_information(
            repo_name,
            project_name,
            commits,
            file_modifications,
            parent_ids,
            issue_links
        ))

    async def insert_commit_information(self,
                                        repo_name: str,
                                        project_name: str,
                                        commits: list[tuple[str, int, datetime.datetime, str, bool, int]],
                                        file_modifications: list[list[tuple[str, str | None, str | None]]],
                                        parent_ids: list[list[tuple[int, bool]]],
                                        issue_links: dict[int, list[str]]):
        async with self._connection:
            async with self._connection.cursor() as cursor:
                await cursor.execute('SELECT project.id FROM project '
                                     'INNER JOIN issue_repo ON project.repo_id = issue_repo.id '
                                     'WHERE issue_repo.name = %s AND project.name = %s;',
                                     [repo_name, project_name])
                project_id = (await cursor.fetchone())[0]
                if project_id is None:
                    raise ValueError(f'Project {project_name} not found in repo {repo_name}')
                ids = []
                for commit in commits:
                    await cursor.execute(
                        'INSERT INTO commit (project_id, sha, sequence_number, timestamp_utc, message, is_merge, analysis_seq_nr) VALUES (%s, %s, %s, %s, %s, %s, %s) '
                        'RETURNING id;',
                        (project_id,) + commit,
                    )
                    ids.append((await cursor.fetchone())[0])
                id_mapping = {i: uid for i, uid in enumerate(ids)}
                await cursor.executemany(
                    'INSERT INTO commit_parents (commit_id, parent_id, is_main) VALUES (%s, %s, %s);',
                    [(id_mapping[i], id_mapping[p], m) for i, parents in enumerate(parent_ids) for p, m in parents]
                )
                await cursor.executemany(
                    'INSERT INTO commit_file_modification (commit_id, action_type, old_path, new_path) VALUES (%s, %s, %s, %s);',
                    [
                        (id_mapping[i], action_type, old_path, new_path)
                        for i, modifications in enumerate(file_modifications)
                        for old_path, new_path, action_type in modifications
                    ]
                )
                all_keys = set()
                for keys in issue_links.values():
                    all_keys |= set(keys)
                issues = await self.get_issues_by_key(repo_name, *all_keys)
                payload = []
                link_failures = []
                for commit_nr, keys in issue_links.items():
                    for key in keys:
                        if key not in issues:
                            link_failures.append((commit_nr, keys))
                            warnings.warn(f'Commit {commit_nr} links to issue {key} which is not in the database')
                        else:
                            payload.append((id_mapping[commit_nr], issues[key].uid))
                await cursor.executemany(
                    'INSERT INTO commit_issue_link_raw (commit_id, issue_id) VALUES (%s, %s);',
                    payload
                )

        await self._reconnect()
        return link_failures

    def insert_refined_commit_issue_links_sync(self, links: list[list[tuple[int, int, int, int | None]]]):
        return _make_sync(self.insert_refined_commit_issue_links(links))

    async def insert_refined_commit_issue_links(self, links: list[list[tuple[int, int, int, int | None]]]):
        async with self._connection:
            async with self._connection.cursor() as cursor:
                flattened = []
                for x in links:
                    flattened.extend(x)
                await cursor.executemany(
                    'INSERT INTO commit_issue_link_refined (issue_id, commit_id, sequence_nr, diff_point) VALUES (%s, %s, %s, %s);',
                    flattened
                )
        await self._reconnect()

    def get_commit_issue_links_sync(self, repo: str, project: str) -> list[tuple[int, int]]:
        return _make_sync(self.get_commit_issue_links(repo, project))

    async def get_commit_issue_links(self, repo: str, project: str) -> list[tuple[int, int]]:
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                'SELECT project.id FROM project '
                'INNER JOIN issue_repo ON project.repo_id = issue_repo.id '
                'WHERE issue_repo.name = %s AND project.name = %s;',
                [repo, project]
            )
            project_id = (await cursor.fetchone())[0]
            await cursor.execute(
                'SELECT commit_id, issue_id FROM commit_issue_link_raw '
                'JOIN commit ON commit.id = commit_issue_link_raw.commit_id '
                'WHERE commit.project_id = %s;',
                [project_id]
            )
            return [
                (row[0], row[1])
                for row in await cursor.fetchall()
            ]

    def get_linked_issues_and_commits_sync(self,
                                           repo: str,
                                           project: str, *,
                                           return_modified_files: bool = False) -> list[tuple[Issue, list[Commit]]]:
        return _make_sync(
            self.get_linked_issues_and_commits(repo,
                                               project,
                                               return_modified_files=return_modified_files)
        )

    async def get_linked_issues_and_commits(self,
                                            repo: str,
                                            project: str, *,
                                            return_modified_files: bool = False) -> list[tuple[Issue, list[Commit]]]:
        async with (self._connection.cursor() as cursor):
            await cursor.execute(
                'SELECT link.issue_id, link.commit_id, link.sequence_nr, link.diff_point '
                'FROM commit_issue_link_refined AS link '
                'JOIN commit ON commit.id = link.commit_id '
                'JOIN project ON commit.project_id = project.id '
                'JOIN issue_repo ON issue_repo.id = project.repo_id '
                'WHERE issue_repo.name = %s AND project.name = %s;',
                [repo, project]
            )

            commit_ids_by_issue_ids = collections.defaultdict(list)
            diff_points = []
            for issue_id, commit_id, sequence_nr, diff_point in await cursor.fetchall():
                commit_ids_by_issue_ids[issue_id].append((sequence_nr, commit_id, diff_point))
                if diff_point is not None:
                    diff_points.append(diff_point)
            for uids in commit_ids_by_issue_ids.values():
                uids.sort()

            if diff_points:
                await cursor.execute(
                    'SELECT id, sha FROM commit WHERE id = ANY(%s);',
                    [diff_points]
                )
                diff_point_mapping = {
                    row[0]: row[1]
                    for row in await cursor.fetchall()
                }
            else:
                diff_point_mapping = {}

            issues = await self.get_issues_by_db_id(list(commit_ids_by_issue_ids))

            all_commit_ids = [
                pair[1] for pair in itertools.chain.from_iterable(commit_ids_by_issue_ids.values())
            ]
            await cursor.execute(
                'SELECT id, sha, sequence_number, timestamp_utc, message FROM commit '
                'WHERE id = ANY(%s);',
                [all_commit_ids]
            )
            commits = {
                row[0]: Commit(
                    uid=row[0],
                    commit_hash=row[1],
                    sequence_number=row[2],
                    timestamp=row[3],
                    message=row[4]
                )
                for row in await cursor.fetchall()
            }
            if return_modified_files:
                await self._add_modified_files(list(commits.values()))

            return [
                (
                    issues[issue_id],
                    [commits[commit_id]._with_diff_point(diff_point_mapping.get(diff_point, None))
                     for _, commit_id, diff_point in commit_ids]
                )
                for issue_id, commit_ids in commit_ids_by_issue_ids.items()
            ]

    async def _add_modified_files(self, commits: list[Commit]):
        commit_ids = [c.uid for c in commits]
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                'SELECT commit_id, old_path, new_path, action_type FROM commit_file_modification '
                'WHERE commit_id = ANY(%s);',
                [commit_ids]
            )
            mapping = collections.defaultdict(list)
            for commit_id, old_path, new_path, action_type in await cursor.fetchall():
                mapping[commit_id].append(ModifiedFile(old_path, new_path, action_type))
            for commit in commits:
                commit.modified_files = mapping[commit.uid]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_sync()

    def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def __del__(self):
        self.close_sync()
