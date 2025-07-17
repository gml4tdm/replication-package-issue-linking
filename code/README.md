# Code

## Setup
In this section, we describe how to setup the environment to run our code.
We will be assuming the use of a Linux system.

### Prerequisites
- Working Conda Installlation (wordking `conda` command)
- Working Rust Installation (working `cargo` command)
- Working `docker` installation

### Setup Conda Environment
Create a new conda environment from the `environment.yml` file:

```bash
conda env create -f environment.yml
```

Activate the environment:

```bash
conda activate issue-linking
```

### Building Rust Extension Module
The Python code uses a Rust extension module to speed
up a number of computations. It must be built before
the code can be used.

To build it, `cd` into the `linker/` directory and run:

```bash
maturin develop --release
```

This will locally install the Rust extension module,
and allow all Python code to be imported through
`import linker`.

## Database
The issue information is currently stored in a PostgreSQL database. The database must be active for all commands that
take a URL to it as a parameter.

The `services/docker-compose.yaml` file can be used to start a local PostgreSQL database.

```bash
docker-compose up -d
```

The URL for this database is `postgres://postgres:pw@localhost:5432/issues`.

If the database is started for the first time,
it will need to be initialised. At a minimum, the schema
should be created. This can be done with the following command:

```bash
docker exec -it services-postgres-1 pg_restore -d issues -U postgres /archives/issues/schema.sql
```

Alternatively, our entire pre-downloaded database can also be loaded. To do this, download the `issue-dump.zip` file,
`unzip` it, and place its contents in the `services/archives/issues` directory. Once the docker container is started, it can be loaded with the following command:

```bash
docker exec -it services-postgres-1 pg_restore -d issues -U postgres /archives/issues/issue-dump.sql
```

## Commands
The `linker` package is callable and can be used to
run a number of different commands. Below, we describe
each command and its arguments.

### `python -m linker update-issues`

Arguments:
- `--postgres-url`: URL to the PostgreSQL database. (example: `postgres://postgres:pw@localhost:5432/issues`)
- `--jira-name`: Name of the Jira instance to update (example: `Apache`)
- `--username` (optional): Username to use for authentication.
- `--password` (optional): Password to use for authentication.

Updates the database of issues with the latest available
data from the specified Jira instance.


### `python -m linker import-commits`

Arguments:
- `--repository-path`: Path to the local repository to import commits from.
- `--postgres_url`: URL to the PostgreSQL database. (example: `postgres://postgres:pw@localhost:5432/issues`)
- `--organisation`: Name of the organisation to import commits from. Same as `--jira-name` for `update-issues` (example: `Apache`)
- `--project`: Name of the project to import commits from. (Example: `Thrift`). Note that this name must match the exact name of the project in Jira. Some projects might have unexpected names, such as Maven, whose Jira name is `Maven (Moved to GitHub Issues)`.
- `--key-pattern`: Regular expression pattern to match commit keys.
- `--multiple-key-handling`: How to handle multiple keys in a single commit. Options are: `first` -- use the first key. `last` --- use the last key. `ignore` -- ignore all keys in the commit. `all` -- use all keys in the commit.
- `--extract-from`: Part of the commit message to extract the issue key from. Options are: `title` -- extract from the title (first line). `body` -- extract from the entire commit message.

This imports commits from the specified repository into the database, and performs the raw linking of commits to known issues in the database based on the provided regular expression pattern.

Results are stored in the `commits`, `commit_file_modifcations`, `commit_parents`, and `commit_issue_links_raw` tables in the database.

If the issues linked to by commits are not present in the database, a file is created with the name `<Organisation>-<Project>-link-failures.json`, containing a list like the follwing:

```json
[[2486, ["TIKA-6000"]]]
```

Each entry in the list if a length-two list, where the
first element is the ID of the commit, and the second element
a list of all the issue keys that could not be found in the database.

### `python -m linker refine-commit-links`

### `python -m linker clean-text`

### `python -m linker generate-feature-plan-from-db`

### `python -m linker vsm`

### `python -m linker make-matrix`

### `python -m linker analyse-stats-matrix`

### `python -m linker analyse-commit-sizes`

### `python -m linker correlate-identifiers`

### `python -m linker issue-type-ablation`
