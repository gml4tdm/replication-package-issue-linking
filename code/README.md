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

Results are stored in the `commits`, `commit_file_modifcations`, `commit_parents`, and `commit_issue_link_raw` tables in the database.

If the issues linked to by commits are not present in the database, a file is created with the name `<Organisation>-<Project>-link-failures.json`, containing a list like the follwing:

```json
[[2486, ["TIKA-6000"]]]
```

Each entry in the list if a length-two list, where the
first element is the ID of the commit, and the second element
a list of all the issue keys that could not be found in the database.

### `python -m linker refine-commit-links`

Arguments:
- `--postgres-url`: URL to the PostgreSQL database. (example: `postgres://postgres:pw@localhost:5432/issues`)
- `--repo`: Name of the organisation to import commits from. Same as `--organisation` for `import-commits` (example: `Apache`)
- `--project`: Name of the project to import commits from. (Example: `Thrift`). Note that this name must match the exact name of the project in Jira. Some projects might have unexpected names, such as Maven, whose Jira name is `Maven (Moved to GitHub Issues)`.
- `--path`: Path to the local repository from which the commits were imported.

After running the `import-commits` command, this command can be used to refine the linking of commits to issues. This command implements steps 2-4 from the commit to issue linking process described in the paper.

Results are stored in the `commit_issue_link_refined` table in the database.


### `python -m linker generate-feature-plan-from-db`

Arguments:
- `--database-url`: URL to the PostgreSQL database. (example: `postgres://postgres:pw@localhost:5432/issues`)
- `--repo-name`: Name of the organisation to import commits from. Same as `--organisation` for `import-commits` (example: `Apache`)
- `--project-name`: Name of the project to import commits from. (Example: `Thrift`). Note that this name must match the exact name of the project in Jira. Some projects might have unexpected names, such as Maven, whose Jira name is `Maven (Moved to GitHub Issues)`.
- `--repo-path`: Path to the local repository from which the commits were imported.
- `--output-directory`: Path to the output directory. Will be created if it does not exist.

This command generates a set of files importable by our data loader. A file `index.json` is generated, containing ground truths, a dense encoding of changes per commits and other commit information, and information about where to find the content of issues and source files. Contents of issues is stored in the `issue-features` directory; contents of files in the `source-code` directory, and file names in the `filenames` directory. All text content is stored in dense JSON files of roughly 1GB each. The easiest way to load this data is to use the data loader.

### `python -m linker clean-text`

Arguments:
- `--input-directory`: Path to the input directory containing the text features for issues.
- `--output-directory`: Path to the output directory. Will be created if it does not exist.
- `--issue-type`: Type of the issue. Must be `jira`
- `--mode`: Mode of cleaning. `raw` leaves text as-is. `remove-formatting` removes formatting (e.g. block syntax) from text, but keeps block content. `remove-formatting-and-blocks` fully removes block content. `remove-formatting-and-replace blocks` removes formatting and replaces blocks with special marker tokens.

Preprocecesses the text of issues.

The output directory should be in the same directory as the `issue-features` directory. E.g. if `--input-directory` is `a/b/c/issue-features`, the output directory should be `a/b/c/issue-features-clean`. This is not enforced in the code,
but not doing so will lead to downstream errors.

### `python -m linker vsm`

Arguments:
- `--input-directory`: Path to the input directory containing the `index.json`  file and all feature/text directories.
- `--output-directory`: Path to the output directory. Will be created if it does not exist.
- `--issue-directory`: directory from which issue features will be loaded. Must be a subdirectory of `input-directory`. (e.g. `issue-features-cleaned`)
- `--corpus-source`: obsolete. Must be `source`
- `--mode`: obsolete. Must be `user`
- `--kind`: which retrieval model to use. Must be `bm25-rank` (!not `bm25`!), `tfidf`, or `rvsm`
- `--sep` (flag): Obsolete. Must always be given
- `--split`: data split for validation/test. Must be integers separated by a slash. All numbers must sum to 100 (e.g. `50/50`)
- `--run-on`: specify which dataset split to run on. `0` -> run on first split, `1` -> run on second split, etc.
- `--lsa-components`: Must be used with `--mode tfidf`. Turns the model into a LSI model. Must be an integer specifying the target dimension.
- `--stemming` (flag): if given, enable stemming
- `--lower-case` (flag): if given, enable lowercasing
- `--sub-token-splitting` (flag): if given, enable sub-token splitting
- `--detailed-performance` (flag): if given, performance output will contain performance scores per issue, alongside the usual global agregate scores.
- `--extra-options`: string specifying extra mode specific options. See below

Evaluate a specific information retrieval model on a given dataset, storing the performance metrics in the given output directory.

#### Extra Options

##### `--mode tfidf`
- `tf`: which term frequency to use. Can be `binary` (0 if term not present, 1 otherwise), `log` (log of term frequency + 1), `count` (use absolute term count), `freq` (use length-normalisd term frequency), or `norm` (double normalisation 0.5)
- `idf`: which inverse document frequency to use. Can be `unary` (1), `idf` (IDF as in sklearn), `max` (log of max frequency over all documents, divided by number of documents containing the term), or `prob` (log(N - n_t) / n_t)), where N is the total number of documents and n_t the number of documents containign the given term)

Example: `--extra-options "tf=freq,idf=prob"`

##### `--mode bm25-rank`
- `k1`: BM25 parameter k1
- `b`: BM25 parameter b
- `delta`: BM25+ parameter delta
- `component_weigthts`: BM25F field weights.

Example (assumuing documents with two fields): `--extra-options "k1=1.2,b=0.75,delta=1.0,component_weigthts=0.2;0.8"`



### `python -m linker make-matrix`

### `python -m linker evaluate`

### `python -m linker analyse-stats-matrix`

### `python -m linker analyse-commit-sizes`

### `python -m linker correlate-identifiers`

### `python -m linker issue-type-ablation`
