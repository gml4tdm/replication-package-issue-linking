# This file is based on the following code:
# https://github.com/mining-design-decisions/maestro-issues-db/blob/85a27071adf3fe0f31c4aad73d15fb352c4867f2/issues-db-api/app/jirarepos_download.py
import asyncio
import collections
import datetime
import json
import os
import time
import warnings

import alive_progress
import psycopg
import requests
import tap

from jira import JIRA

from ..base import BaseCommand, register

from ...utils.issue_db import IssueDatabaseWrapper, Issue


class UpdateIssuesConfig(tap.Tap):
    postgres_url: str
    jira_name: str
    username: str | None = None
    password: str | None = None


@register('update-issues')
class UpdateIssuesCommand(BaseCommand):

    @staticmethod
    def config_type() -> type[tap.Tap]:
        return UpdateIssuesConfig

    def execute(self):
        assert isinstance(self.config, UpdateIssuesConfig)
        db = IssueDatabaseWrapper.from_url_sync(self.config.postgres_url)
        repo = db.get_repo_sync(self.config.jira_name)
        os.makedirs('temp', exist_ok=True)
        username = self.config.username
        password = self.config.password
        if (username is not None) != (password is not None):
            raise ValueError('Both username and password must be provided or not provided')

        checkpoint_time = datetime.datetime.now(datetime.timezone.utc)

        jira_server = get_jira_server(
            self.config.jira_name,
            repo.url,
            enable_auth=username is not None,
            username=username,
            password=password
        )
        num_available_results = get_response(jira_server, repo.last_downloaded, 0, 0)["total"]
        print(f"Total issues to download from {self.config.jira_name}: {num_available_results}")
        batch_size = 500
        coro = download_and_write_data_mongo(
            self.config.jira_name,
            self.config.postgres_url,
            jira_server,
            repo.last_downloaded,
            num_desired_results=None,
            iteration_max=batch_size,
            start_index=0,
            num_available_results=num_available_results,
        )
        asyncio.get_event_loop().run_until_complete(coro)

        # Update last updated for the repo
        db = IssueDatabaseWrapper.from_url_sync(self.config.postgres_url)
        db.update_repo_sync(self.config.jira_name,
                            checkpoint_time)


# Apache projects requiring authentication
APACHE_AUTH_PROJECTS = [
    "DATALAB",
    "CLOUDSTACK",
    "COUCHDB",
    "DAYTRADER",
    "DELTASPIKE",
    "GERONIMO",
    "GSHELL",
    "INFRA",
    "MYNEWT",
    "RIVER",
    "SANTUARIO",
    "SOLR",
    "XALANJ",
    "YOKO",
]


def check_jira_url(jira_url):
    try:
        requests.head(jira_url)
    except ConnectionError as e:
        raise RuntimeError(f'Jira URL {jira_url} not reachable') from e

    # CHECK PROVIDED JIRA URL API AVAILABILITY
    response = requests.get(jira_url + "/rest/api/2/issuetype")
    if response.status_code >= 300:
        try:
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f'Jira URL {jira_url} returned error status code') from e

    # CHECK NUMBER OF ISSUES
    response = requests.get(jira_url + "/rest/api/2/search?jql=&maxResults=0")
    if response.status_code >= 300:
        try:
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f'Jira URL {jira_url} returned error status code') from e


def format_duration(start_time, end_time):
    # Get the total seconds of the duration
    seconds = end_time - start_time
    # Calculate the other time
    milliseconds = int((seconds % 1) * 10000)
    minutes = int(seconds / 60)
    hours = int(minutes / 60)
    # Trim the values to fit in their appopriate slots
    display_minutes = int(minutes % 60)
    display_seconds = int(seconds % 60)

    return f"{hours:02}:{display_minutes:02}:{display_seconds:02}.{milliseconds:04}"


def get_jira_server(jira_name, url, enable_auth=False, username=None, password=None):
    check_jira_url(url)
    if enable_auth and jira_name == "Apache":
        return JIRA(url, basic_auth=(username, password))
    return JIRA(url)


def get_response(jira, download_date, start_index, iteration_max=100):
    if download_date is None:
        query = f"order by created asc"
    else:
        d = download_date
        query = f'updated>="{d.year}-{d.month:02}-{d.day:02}" order by created asc'
    filename = f'temp/{start_index}-{iteration_max}.json'
    if not os.path.exists(filename):
        result = jira.search_issues(
            query,
            startAt={start_index},
            maxResults={iteration_max},
            expand="changelog",
            json_result=True,
        )
        with open(filename, 'w') as f:
            json.dump(result, f)
        return result
    else:
        with open(filename, 'r') as f:
            return json.load(f)


async def download_and_write_data_mongo(
        jira_name,
        postgres_url,
        jira_server,
        download_date,
        num_desired_results=None,  # Leave as "None" to download all, otherwise specify a number
        iteration_max=250,  # Recommended to keep at or below 500
        start_index=0,  # This allows you to start back up from a different place
        num_available_results=None):

    # iteration_max is the number of issues the script will attempt to get at one time.
    # The Jira default max is 1000. Trying with 1000 consistently returned errors after a short while
    # as the object being returned was likely too large. Values of 500 or less serve no particular issue
    # to the script except that more calls (of smaller size) have to be made.

    # How many issues to collect before writing to MongoDB
    num_issues_per_write = 10000

    last_write_start_index = start_index
    issues = []

    if num_available_results is None:
        # Available and requested number of results
        num_available_results = get_response(jira_server, download_date, 0, 0)["total"]
        print(
            f'Number of Desired Results   : {num_desired_results if num_desired_results else "All"}'
        )
        print(f"Number of Available Results : {num_available_results}")
        print("")

    # Set the number of results to retrieve based on information from Jira server
    if not num_desired_results:
        num_remaining_results = num_available_results
    else:
        num_remaining_results = min(int(num_desired_results), num_available_results)
    # Adjust remaining results based on their start index
    num_remaining_results -= start_index

    # Collect results while there are more results to gather
    issues_downloaded = 0
    max_count_width = len(str(num_remaining_results)) + 1
    print(f"Total Remaining:{num_remaining_results:< {max_count_width}}")


    connection = await psycopg.connection_async.AsyncConnection.connect(
        postgres_url
    )

    async with connection:
        async with connection.cursor() as cursor:
            writer = JiraToPostgresWriter(cursor, jira_name)

            while num_remaining_results > 0:
                # Start a timer for this particular chunk
                start_time = time.time()

                # Number of items to retrieve
                num_items_to_retrieve = min(iteration_max, num_remaining_results)

                # Get issues from Jira
                response_json = get_response(
                    jira_server, download_date, start_index, num_items_to_retrieve
                )
                if "issues" in response_json:
                    # Add issues to program list
                    issues.extend(response_json["issues"])
                    num_returned_issues = len(response_json["issues"])
                else:
                    raise Exception("No issues found in response")

                # Adjust the remaining results to get
                num_remaining_results -= num_returned_issues

                # Print progress for user
                end_index = start_index + num_returned_issues - 1
                print(
                    f"Total Remaining:{num_remaining_results:< {max_count_width}}  "
                    f"Retrieved Items: {start_index:< {max_count_width}} - {end_index:< {max_count_width}}  "
                    f"Duration: {format_duration(start_time, time.time())}"
                )

                # Move the start index
                start_index += num_returned_issues

                # Write the issues to file IF there are enough of them. This is a nice way to save state and start over at a
                # certain place if there are too many to download in one go.
                if (
                    len(issues) >= num_issues_per_write
                    or num_remaining_results == 0
                    or num_returned_issues == 0
                ):
                    # db = IssueDatabaseWrapper.from_url_sync(postgres_url)
                    # payload = {
                    #     issue['id']: Issue(
                    #         key=issue['key'],
                    #         summary=issue['fields']['summary'],
                    #         description=issue['fields']['description']
                    #     )
                    #     for issue in issues
                    # }
                    # db.update_issues_by_jira_id_sync(jira_name, payload, add_missing_projects=True)

                    await writer.start_batch()
                    with alive_progress.alive_bar(len(issues)) as bar:
                        for issue in issues:
                            bar()
                            await writer.write_issue(issue)
                    print('Writing batch data...')
                    await writer.end_batch()

                    print("... Issues written to database ...")
                    last_write_start_index = start_index

                    issues_downloaded += len(issues)
                    issues = []  # Clear the issues so that our memory doesn't get too full

                # If we have for some reason run out of results, we may want to react to this in some way
                if num_returned_issues == 0:
                    print(
                        "Number of Returned Issues is 0. This is strange and should not happen. Investigate."
                    )
                    return

            print("Writing deferred data to database...")
            await writer.finish()
            print("... Issues written to database ...")

            print("")
            print(f"Number of Downloaded Issues: {issues_downloaded}")


class JiraToPostgresWriter:

    def __init__(self, cursor, repo: str):
        self._cursor = cursor
        self._deferred_insertions = []
        self._repo = repo
        self._repo_id = None
        self._existing_issue_mapping = None
        self._existing_projects = None
        self._existing_categories = None
        self._cached_projects = {}
        self._batch = []

    async def finish(self):
        assert self._existing_issue_mapping is not None

        by_type = collections.defaultdict(list)
        for type_, values in self._deferred_insertions:
            by_type[type_].append(values)
        assert set(by_type.keys()) <= {'parent', 'issuelink', 'subtask'}, set(by_type.keys())

        await self._finish_list(
            table='issue_subtask',
            fields=['parent_issue', 'child_issue'],
            kind='subtask',
            values=list(set(by_type['subtask']))
        )
        await self._finish_list(
            table='issue_to_issue_link',
            fields=['lhs_issue', 'rhs_issue', 'link_type',
                    'link_name_lhs_to_rhs', 'link_name_rhs_to_lhs'],
            kind='issuelink',
            values=list(set(by_type['issuelink']))
        )

        for self_id, parent_jira_id in by_type['parent']:
            if parent_jira_id not in self._existing_issue_mapping:
                warnings.warn(f'Issue {self_id} references Jira ID {parent_jira_id} '
                              '(parent) which is not in the existing issue mapping.')
                continue
            await self._cursor.execute(
                'UPDATE issue SET parent_id = %s WHERE id = %s;',
                (self._existing_issue_mapping[parent_jira_id], self_id)
            )

    async def _finish_list(self, table, fields, kind, values):
        assert self._existing_issue_mapping is not None

        ids = [item[0] for item in values]
        if table == 'issue_subtask':
            await self._cursor.execute(
                'DELETE FROM issue_subtask WHERE parent_issue = ANY(%s);',
                [ids]
            )
        else:
            await self._cursor.execute(
                'DELETE FROM issue_to_issue_link WHERE lhs_issue = ANY(%s);',
                [ids]
            )

        payload = []
        for self_id, other_jira_id, *rest in values:
            if other_jira_id not in self._existing_issue_mapping:
                warnings.warn(f'Issue {self_id} references Jira ID {other_jira_id} '
                              f'({kind}) which is not present in the database.')
            else:
                payload.append(
                    (self_id, self._existing_issue_mapping[other_jira_id], *rest)
                )
        if payload:
            fillers = ', '.join(['%s'] * len(fields))
            await self._cursor.executemany(
                f'INSERT INTO {table} ({", ".join(fields)}) VALUES ({fillers});',
                payload
            )

    async def start_batch(self):
        self._batch = []

    async def end_batch(self):
        ids = [issue_id for document, issue_id in self._batch]

        if len(ids) != len(set(ids)):
            counts = collections.Counter(ids)
            multiple = {k: v for k, v in counts.items() if v > 1}
            import warnings
            warnings.warn(f'Duplicate issues in batch: {multiple}')
        else:
            multiple = {}


        print('Deleting batch data...')
        with alive_progress.alive_bar(6) as bar:
            await self._cursor.execute(
                'DELETE FROM issue_comment WHERE issue_id = ANY(%s);', [ids]
            )
            bar()
            await self._cursor.execute(
                'DELETE FROM issue_affected_versions WHERE issue_id = ANY(%s);', [ids]
            )
            bar()
            await self._cursor.execute(
                'DELETE FROM issue_fix_versions WHERE issue_id = ANY(%s);', [ids]
            )
            bar()
            await self._cursor.execute(
                'DELETE FROM issue_components WHERE issue_id = ANY(%s);', [ids]
            )
            bar()
            await self._cursor.execute(
                'DELETE FROM issue_labels WHERE issue_id = ANY(%s);', [ids]
            )
            bar()
            await self._cursor.execute(
                'DELETE FROM issue_time_tracking WHERE issue_id = ANY(%s);', [ids]
            )
            bar()

        print('Inserting batch data...')
        with alive_progress.alive_bar(len(self._batch)) as bar:
            for document, issue_id in self._batch:
                if issue_id in multiple:
                    multiple[issue_id] -= 1
                    if multiple[issue_id] > 0:
                        print(f'Skipping duplicate issue ({issue_id})')
                        bar()
                        continue
                await self._insert_comments(document, issue_id)
                await self._insert_affected_versions(document, issue_id)
                await self._insert_fix_versions(document, issue_id)
                await self._insert_components(document, issue_id)
                await self._insert_labels(document, issue_id)
                await self._insert_time_tracking(document, issue_id)
                bar()

        assert all(x == 0 for x in multiple.values())

    async def write_issue(self, document):
        if self._existing_issue_mapping is None:
            await self._fetch_existing_issues()

        assert self._existing_issue_mapping is not None

        project_id = await self._ensure_project(
            document['project'] if 'project' in document else document['fields']['project']
        )

        jira_id = document['id']
        existing = jira_id in self._existing_issue_mapping

        fields = self._gather_issue_fields(document)
        if existing:
            fields['project_id'] = project_id  # Account for possible project change
            fields['key'] = document['key']  # Account for possible key change
            val_updates = ', '.join([f'{key} = %s' for key in fields])
            await self._cursor.execute(
                f'UPDATE issue SET {val_updates} WHERE id = %s;',
                tuple(fields.values()) + (self._existing_issue_mapping[jira_id],)
            )
            issue_id = self._existing_issue_mapping[jira_id]
        else:
            all_fields = ['jira_id', 'project_id', 'key', 'summary', 'description']
            all_fields.extend(list(fields.keys()))
            key = document['key']
            if 'summary' not in document:
                summary = ''
            else:
                summary = document['summary'] if document['summary'] is not None else ''
            if 'description' not in document:
                description = ''
            else:
                description = document['description'] if document['description'] is not None else ''
            filler = ', '.join(['%s'] * len(all_fields))
            await self._cursor.execute(
                f'INSERT INTO issue ({", ".join(all_fields)}) VALUES ({filler}) RETURNING id;',
                (jira_id, project_id, key, summary, description, *fields.values())
            )
            issue_id = (await self._cursor.fetchone())[0]
            self._existing_issue_mapping[jira_id] = issue_id

        self._deferred_insertions.extend(
            self._get_deferred_insertions(document, issue_id)
        )

        self._batch.append((document, issue_id))


    async def _ensure_project(self, project):
        if self._existing_projects is None:
            await self._cursor.execute(
                'SELECT project.jira_id, project.id, project.project_category_id, project.name, project.project_type_key FROM project '
                'WHERE project.repo_id = %s;',
                [self._repo_id]
            )
            self._existing_projects = {
                row[0]: row[1:]
                for row in await self._cursor.fetchall()
            }
            await self._cursor.execute(
                'SELECT jira_id, id, name, description FROM project_category;'
            )
            self._existing_categories = {
                row[0]: row[1:]
                for row in await self._cursor.fetchall()
            }

        if 'projectCategory' in project and project['projectCategory'] is not None:
            category = project['projectCategory']
            if category['id'] not in self._existing_categories:
                name = category['name'] if category['name'] is not None else ''
                if 'description' in category:
                    description = category['description'] if category['description'] is not None else ''
                else:
                    description = ''
                await self._cursor.execute(
                    'INSERT INTO project_category (jira_id, name, description, repo_id) VALUES (%s, %s, %s, %s) '
                    'RETURNING id;',
                    (category['id'], name, description, self._repo_id)
                )
                db_id = await self._cursor.fetchone()
                self._existing_categories[category['id']] = (db_id[0], name, description)
            category_id = self._existing_categories[category['id']][0]
        else:
            category_id = None

        jira_id = project['id']
        if jira_id not in self._existing_projects:
            await self._cursor.execute(
                'INSERT INTO project (jira_id, repo_id, project_category_id, name, key, project_type_key) VALUES (%s, %s, %s, %s, %s, %s) '
                'RETURNING id;',
                (jira_id, self._repo_id, category_id, project['name'], project['key'], project['projectTypeKey'])
            )
            db_id = (await self._cursor.fetchone())[0]
            self._existing_projects[jira_id] = (db_id, category_id, project['name'], project['projectTypeKey'])
            if category_id is not None:
                await self._cursor.execute(
                    'UPDATE project SET project_category_id = %s WHERE id = %s;',
                    (category_id, db_id)
                )
        else:
            # Check if update is required
            # SELECT project.jira_id, project.id, project.project_category_id, project.name, project.project_type_key FROM project
            # 0 -> jira id
            # 1 -> db id
            # 2 -> category_id
            # 3 -> name
            # 4 -> project_type_key
            name_changed = project['name'] != self._existing_projects[jira_id][2]
            if 'projectCategory' in project:
                category_changed = project['projectCategory']['id'] != self._existing_projects[jira_id][1]
            else:
                category_changed = False
            if 'projectTypeKey' in project:
                type_changed = project['projectTypeKey'] != self._existing_projects[jira_id][3]
            else:
                type_changed = False
            if name_changed or category_changed or type_changed:
                db_id = self._existing_projects[jira_id][0]
                changed = []
                new_values = []
                if name_changed:
                    changed.append('name')
                    new_values.append(project['name'])
                if category_changed:
                    changed.append('project_category_id')
                    new_values.append(category_id)
                if type_changed:
                    changed.append('project_type_key')
                    new_values.append(project['projectTypeKey'])
                if len(changed) > 1:
                    await self._cursor.execute(
                        f'UPDATE project SET ({", ".join(changed)}) = ({", ".join("%s" for _ in changed)}) WHERE id = %s;',
                        tuple(new_values) + (db_id,)
                    )
                else:
                    await self._cursor.execute(
                        f'UPDATE project SET {changed[0]} = %s WHERE id = %s;',
                        (new_values[0], db_id)
                    )
                self._existing_projects[jira_id] = (db_id, category_id, project['name'], project['projectTypeKey'])


        return self._existing_projects[jira_id][0]

    async def _fetch_existing_issues(self):
        self._existing_issue_mapping = {}
        await self._cursor.execute(
            'SELECT issue.jira_id, issue.id FROM issue '
            'INNER JOIN project ON issue.project_id = project.id '
            'INNER JOIN issue_repo ON project.repo_id = issue_repo.id '
            'WHERE issue_repo.name = %s;',
            [self._repo]
        )
        for jira_id, issue_id in await self._cursor.fetchall():
            self._existing_issue_mapping[jira_id] = issue_id

        await self._cursor.execute(
            'SELECT id FROM issue_repo WHERE name = %s;',
            [self._repo]
        )
        self._repo_id = (await self._cursor.fetchone())[0]

    def _gather_issue_fields(self, document):
        updates = {}
        maybe_copy(updates, 'issue_type', document, 'issuetype', 'name')
        maybe_copy(updates, 'resolution', document, 'resolution', 'name')
        maybe_copy(updates, 'date_resolved', document, 'resolutiondate', None)
        def_copy(updates, 'date_created', document, 'created', None)
        def_copy(updates, 'date_updated', document, 'updated', None)
        maybe_copy(updates, 'date_archived', document, 'archiveddate', None)
        maybe_copy(updates, 'status', document, 'status', 'name')
        maybe_copy(updates, 'status_category_change_date', document, 'statuscategorychangedate', None)
        maybe_copy(updates, 'priority', document, 'priority', 'name')
        maybe_copy(updates, 'environment', document, 'environment', None)
        def_copy(updates, 'watches', document, 'watches', 'watchCount')
        maybe_copy(updates, 'votes', document, 'votes', 'votes')

        updates = {
            k: v if not isinstance(v, str) else v.replace('\x00', '')
            for k, v in updates.items()
        }

        return updates

    async def _insert_comments(self, document, self_id):
        comments = []
        comment_lists = [
            document['fields'].get('comments', []),
            document['fields'].get('comment', {'comments': []})['comments']
        ]
        for comment_list in comment_lists:
            for comment in comment_list:
                comments.append(
                    {
                        'body': comment['body'].replace('\x00', ''),
                        'date_created': comment['created'],
                        'date_updated': comment['updated'],
                        'issue_id': self_id
                    }
                )
        comments.sort(
            key=lambda x: datetime.datetime.strptime(x['date_created'], '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()
        )
        for i, c in enumerate(comments):
            c['sequence_number'] = i
        await self._cursor.executemany(
            'INSERT INTO issue_comment (issue_id, sequence_number, date_created, date_updated, body) VALUES (%s, %s, %s, %s, %s);',
            [(c['issue_id'], c['sequence_number'], c['date_created'], c['date_updated'], c['body']) for c in comments]
        )

    async def _insert_affected_versions(self, document, self_id):
        affected_versions = []
        for version in self._dedup(document['fields'].get('affectedVersions', []), 'name'):
            affected_versions.append(
                (
                    self_id,
                    version['name'],
                    version.get('description', None)
                )
            )
        await self._cursor.executemany(
            'INSERT INTO issue_affected_versions (issue_id, version, description) VALUES (%s, %s, %s);',
            affected_versions
        )

    async def _insert_fix_versions(self, document, self_id):
        fix_versions = []
        for version in self._dedup(document['fields'].get('fixVersions', []), 'name'):
            fix_versions.append(
                (
                    self_id,
                    version['name'],
                    version.get('description', None)
                )
            )
        try:
            await self._cursor.executemany(
                'INSERT INTO issue_fix_versions (issue_id, version, description) VALUES (%s, %s, %s);',
                fix_versions
            )
        except psycopg.errors.UniqueViolation:
            print(document, self_id, fix_versions)
            raise

    async def _insert_components(self, document, self_id):
        components = []
        for component in self._dedup(document['fields'].get('components', []), 'name'):
            components.append(
                (
                    self_id,
                    component['name'],
                    component.get('description', None)
                )
            )
        await self._cursor.executemany(
            'INSERT INTO issue_components (issue_id, component, description) VALUES (%s, %s, %s);',
            components
        )

    async def _insert_labels(self, document, self_id):
        issue_labels = []
        for label in self._dedup(document['fields'].get('labels', []), None):
            issue_labels.append(
                (
                    self_id,
                    label
                )
            )
        await self._cursor.executemany(
            'INSERT INTO issue_labels (issue_id, label) VALUES (%s, %s);',
            issue_labels
        )

    def _dedup(self, items, key):
        seen = set()
        for item in items:
            if key is None:
                check = item
            else:
                check = item[key]
            if check in seen:
                warnings.warn(f'Duplicate {key}: {check} (in {items})')
                continue
            seen.add(check)
            yield item

    async def _insert_time_tracking(self, document, self_id):
        tt_present = {}
        if 'timetracking' in document['fields']:
            maybe_copy2(tt_present, 'tt_original_estimate_seconds', document, 'originalEstimateSeconds')
            maybe_copy2(tt_present, 'tt_remaining_estimate', document, 'remainingEstimate')
            maybe_copy2(tt_present, 'tt_original_estimate', document, 'originalEstimate')
            maybe_copy2(tt_present, 'tt_remaining_estimate_seconds', document, 'remainingEstimateSeconds')
            maybe_copy2(tt_present, 'tt_time_spent_seconds', document, 'timeSpentSeconds')
            maybe_copy2(tt_present, 'tt_time_spent', document, 'timeSpent')
        maybe_copy(tt_present, 'aggregate_time_original_estimate', document, 'aggregatetimeoriginalestimate', None)
        maybe_copy(tt_present, 'aggregate_time_estimate', document, 'aggregatetimeestimate', None)
        maybe_copy(tt_present, 'time_original_estimate', document, 'timeoriginalestimate', None)
        maybe_copy(tt_present, 'aggregate_time_spent', document, 'aggregatetimespent', None)
        maybe_copy(tt_present, 'time_estimate', document, 'timeestimate', None)
        maybe_copy(tt_present, 'time_spent', document, 'timespent', None)
        maybe_copy(tt_present, 'work_ratio', document, 'workratio', None)

        if tt_present:
            tt_present['issue_id'] = self_id
            fmt_provided = f'({", ".join(f"{k}" for k in tt_present.keys())})'
            fmt_exp = f'({", ".join(f"%s" for k in tt_present.keys())})'
            await self._cursor.execute(
                f'INSERT INTO issue_time_tracking {fmt_provided} VALUES {fmt_exp};',
                tuple(tt_present.values())
            )

    def _get_deferred_insertions(self, document, self_id):
        deferred = []

        # parent
        if 'parent' in document and document['parent'] is not None:
            deferred.append(('parent', (self_id, document['parent']['id'])))

        # issuelink
        for link in document['fields'].get('issuelinks', []):
            assert 'outwardIssue' in link or 'inwardIssue' in link
            assert not ('outwardIssue' in link and 'inwardIssue' in link)
            if 'outwardIssue' in link:
                sql_link = (
                    self_id,
                    link['outwardIssue']['id'],
                    link['type']['name'],
                    link['type']['outward'],
                    link['type']['inward']
                )
                deferred.append(('issuelink', sql_link))
            else:
                pass  # Should be handled by reverse direction

        # issue_subtask
        for subtask in document['fields'].get('subtasks', []):
            deferred.append(('subtask', (self_id, subtask['id'])))

        return deferred


def maybe_copy2(updates, name, document, field):
    if field not in document['fields']['timetracking']:
        return
    updates[name] = document['fields']['timetracking'][field]


def maybe_copy(updates, name, document, field, value):
    if field not in document['fields']:
        return
    if document['fields'][field] is None:
        return
    def_copy(updates, name, document, field, value)


def def_copy(updates, name, document, field, value):
    if value is None:
        updates[name] = document['fields'][field]
    else:
        updates[name] = document['fields'][field][value]
