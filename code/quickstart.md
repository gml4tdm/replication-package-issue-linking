# Quickstart Guide

## Using Our Existing Dataset
After the data (in `issue-linking.zip`) is unzipped, a project can be loaded as follows:

```python
from linker._accelerator import LiveIndexLoader

loader = LiveIndexLoader.load('packed/<project>-packed/index.json')
```

Full API documentation for the loader can be found in [`linker/_accelerator.pyi`](code/linker/python/linker/_accelerator.pyi).

The documentation in `_accelerator.pyi` sometimes makes references to indexes for text content. These indexe are 2-tuples of integers.
Suppose that our `index.json` file is located in `/path/to/dataset/index.json`, and we want to find the associated text for the issue with issue index `(1, 231)`. We then have to load the file `1.json` from `/path/to/dataset/issue-features/1.json`, and fetch the content of index `231` from the resulting list. The mechanism is similar for source code and file names, but these use the `source-code` and `filenames` folders, respectively.


### Generating a New Dataset
### Generating Data for a Repository

#### Importing Issues (Jira)
To obtain a list of Jira instances known by the system, you can first enter the postgres command line:

```bash
docker exec -it services-postgres-1 psql -U postgres issues
```

You can then obtain a list of known instances by running the following query:

```sql
SELECT * FROM issue_repo;
```

To enter a new Jira instance, insert a row into the `issue_repo` table. The following minimal example should work:

```sql
INSERT INTO issue_repo (name, url, requires_authentication, last_downloaded_utc, query_wait_time_in_minutes, type) VALUES (
$0, $1, $2, '1970-01-01 00:00:00', 0, 'jira');
```

Here, `$0` should be replaced with the name of the instance, `$1` with the URL of the instance, and `$2` with a boolean value indicating whether the instance requires authentication. If authentication is required, username and passwords should be supplied when calling the `update-issues` command.

Invoke the `update-issues` command to download or update issues from a specific instance.

#### Importing Issues (non-Jira)
Non-Jira issue tracker are not natively supported. However, as long as issues are properly inserted into the database, the system will be able to work with them.

This process is somewhat technical, and we only provide a high level overview here; the user should consult e.g. the schema definition for more details.

First, the user should update the `repo_type` type in the database to add a value for their chosen issue tracker.

Next, the user should should add an enrtrto the `issue_repo` table for their chosen issue tracker.

Next, the user should add entries for the projects corresponding to their issue tracker to the `project` table.

Finally, the user can insert issues into the `issue table`. The fields that should be present are the following:

- `jira_id`: cannot be null, but may be set to any dummy value
- `key`: key/identifier for the issue, which would be used by developers to reference the issue. Used to resolve links.
- `project_i`: foreign key to the `project` table
- `summary`: title of the issue
`description`: description/body of the issue

#### Cloning Repo
Once all necessary issues are stored in the database, clone the repository to be analysed using `git`.

#### Issue Linking
Once the issues and repostory are in place, use the following sequence of commands to links issues to commits, and store the results in the database:

- `import-commits`
- `refine-commit-links`

The full documentation for these command can be found in the [README of the /code directory](code/README.md).

#### Dataset Generation
After linking issues to commits, run the `generate-feature-plan-from-db` command to generate a dataset.

Optionally, use the `clean-text` command to preprocess issue text content.

### Loading the Dataset
Once a dataset is generated, it can be loaded in Python code using our dataset loader.

Assuming all setup steps have been completed, the loader can be imported and invoked as follows:

```python
from linker._accelerator import LiveIndexLoader

dataset = LiveIndexLoader.load('path/to/dataset/index.json')
```

Full API documentation for the loader can be found in [`linker/_accelerator.pyi`](code/linker/python/linker/_accelerator.pyi).

The documentation in `_accelerator.pyi` sometimes makes references to indexes for text content. These indexe are 2-tuples of integers.
Suppose that our `index.json` file is located in `/path/to/dataset/index.json`, and we want to find the associated text for the issue with issue index `(1, 231)`. We then have to load the file `1.json` from `/path/to/dataset/issue-features/1.json`, and fetch the content of index `231` from the resulting list. The mechanism is similar for source code and file names, but these use the `source-code` and `filenames` folders, respectively.
