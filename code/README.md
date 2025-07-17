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

Arguments:
- `--files`: List of paths to analyse. Generally a list of files corresponding to a single set of experiments meant to evaluate a particular parameter or setting.
- `--row-pattern`: Regular expression pattern to extract a variable being tested from the filename. Must be specified as `--row-pattern=<pattern>`. Regex must contain exactly on capture group (in brackets), which will be used as the variable name. Set to `@` to disable.
- `--col-pattern`: Regular expression pattern to extract a variable being tested from the filename. Must be specified as `--col-pattern=<pattern>`. Regex must contain exactly on capture group (in brackets), which will be used as the variable name. Set to `@` to disable.
- `--out-dir`: Path to the output directory. Will be created if it does not exist.

Analyse all given performance files. The row and column patterns are usd to extract row and column keys from filenames.
For example, if the filenames are `experiment-{bm25,tfidf}-{project}.json`, then the row pattern could be used to extract the pattern, and the column pattern could be used to extract the project name. By only specifying one, only one of the two could be extracted.

The command generates two outputs. First of all, it generates a plot for every performance metric. If both the row and column patterns are specified, the plot will be a (2D) matrix/heatmpa, where the rows and columns corresponds to the keys extracted from the given patterns. If only a row or a column pattern is specified, the matrix will instead be a "1D heatmap" (row).

A JSON file, `stats.json`, with all aggregated performance metrics (aggregated over categories; median and mean) is also generated. This file is used for downstream performance analysis. This file is only generated if either the row or the column pattern is specified; not if both are specified.

### `python -m linker analyse-commit-sizes`

Arguments:
- `--files`: List of directories generated by the `generate-feature-plan-from-db` command.
- `--output`: Path to the output directory. Will be created if it does not exist.
- `--include-unit-commits` (flag): if given, issues with a single commit are included in the analysis.

Analyse the size of commits (in terms of the numbers of files changed) for all issues with more than 1 associated commits,
across all given projects.

### `python -m linker correlate-identifiers`

Arguments:
- `--files`: Performance files to compute correlations for. Generally a list of files corresponding to a single set of experiments meant to evaluate a particular parameter or setting. Should all correspond to the same project.
- `--data-directory`: Data directory corresonding to the project from which the performance files were generated.
- `--issue-directory`: Directory from which issue features were loaded. Must be a subdirectory of `data-directory`. (e.g. `issue-features-cleaned`)
- `--split`: Split used when obtaining the performance files.
- `--run-on`: Which split to run on. Must be the one used to obtain the performance files.
- `--output`: Path to the output directory. Will be created if it does not exist.
- `--postgres-url`: URL to the PostgreSQL database. (example: `postgres://postgres:pw@localhost:5432/issues`)
- `--no-plots` (flag): If given, no plots are generated. Should always be used if `mode` != `normal`
- `--mode`: Should be one of `normal` or `issue-type-restricted`. See below.
- `--metrics`: List of metrics to include in the analysis. If not given, sensible defaults are used.
-- `--restricted-issue-types`: For `--mode issue-type-restricted`, a list of issue types (groups) to include in the analysis. Example value: `"Bug:Bug,Defect;Task:Task,Sub-task;Improvement:Improvement,Suggestion;New Feature:New Feature,Feature Request"` (format: `Group Name:Issue Types`)

Perform correlation analsis between the number of identifiers in issues and the performance of the retrieval model.

Requires performance files generated with the `--detailed-performance` flag.

See the explanations of the different modes for more details.

#### Mode: `normal`
Spearman correlation between the number of identifiers in all issues (regardless of type) and model performance.

#### Mode: `issue-type-restricted`
Spearman correlation between the number of identifiers in issues which match one of the types in the `--restricted-issue-types` argument, and model performance.


### `python -m linker issue-type-ablation`

Arguments:
- `--config`: Path to the configuration file. See below.

Analyses the performance of the retrieval model in the context of specific issue types. Specifically
1. In case the model is only evaluated on a particular issue type
2. In case the model is evaluated on all issue types except a particular (held out) one.

The output can be pretty-printed using the `scripts/analyse_issue_ablation.py` script.

#### Configuration File
Configuration for the `issue-type-ablation` command is stored in a JSON file. The file must contain the following fields:

- `files`: list of glob patterns used to find perfomance files
- `file_filter`: regex pattern used to filter the glob result. The pattern is applied to the files matched by the globs, with all parent directories stripped. If the pattern does not match, the file is ignored.
- `project_regex`: regex pattern used to extract the project name from the file name. The pattern must contain exactly one capture group (in brackets), which will be used as the project name.
- `data_directory`: directory containing all directories of from which the performance files were generated. (i.e. a directory of containing one of multiple output directories from the `generate-feature-plan-from-db` command)
- `data_dir_suffix`: Every directory in the `data_directory` directory must be of the format `<project-name>-<data_dir_suffix>`. This field specifies the suffix.
- `split`: split used when obtaining the performance files.
- `run_on`: which split to run on. (integer)
- `postgres_url`: URL to the PostgreSQL database. (example: `postgres://postgres:pw@localhost:5432/issues`)
- `repo_mapping`: mapping of project names to their repos/organisation. E.g. it should map `avro` to `Apache`
- `output`: path to the output directory. Will be created if it does not exist.
- `method_regex`: regex pattern used to extract the method name from the file name. The pattern must contain exactly one capture group (in brackets), which will be used as the method name.
- `plot`: List of strings (methods); currently ignored in favour of the `scripts/analyse_issue_ablation.py` script.
- `type_groups`: List of objects, where each object is a dictionary with a fields `name` defining the name of a category of issue types, and `types`, a list of isse types contained in that category.


## Loose Sripts

### `scripts/mat_to_latex.py`
Utility script to transform `stats.json` (from  the `make-matrix` command) into a markdown or text table.

Arguments:
- `--files`: list of files to be transformed into a table. If multiple files are given, the performance scores for each metric/column combination are placed into the same cell (separated by slashes)
- `--columns`: List of column name. Should be the extracted keys from the `make-matrix` command. May be given in the format `key:value`. In this case, the original `key` is printed as `value` in the table.
- `metrics`: list of metrics to be printed. Usually not necessary to specify; sensible defaults are used.
- `--average-column`: If a name is given, a column with the given name containing the per-row average is added to the table.
- `--kind`: table type. Either `markdown` or `latex`

### `scripts/analyse_commit_hist.py`
Generate a figure from the output of the `analyse-commit-sizes` command.

Arguments:
- `--filename`: File to generate the plot from.

Output is stored in `out.png`

### `scripts/analyse_correlations.py`
Generate tables from the output of the `correlate-identifiers` command. (`--mode normal` or `--mode issue-type-restricted`)

Stores tables for all methods in markdown format in the given output directory. Prints the table for BM25 in LaTeX format to the console.

Arguments:
- `--file`: Output file from the `correlate-identifiers` command.
- `--out`: Output directory. Will be created if it does not exist.
- `--key`: obsolete. Do not use.
- `--levels`: obsolete. Do not use.

### `scripts/analyse_issue_ablation.py`
Generate tables and figures from the ouptput of the `issue-type-ablation` command.

Generates a bar chart of performance score per included and held out issue type, per method.

Generates tables with result of the Kruskal-Wallis test to compare performance scores between issue types and held out issue types.

Generates tables with the results from Conover's post-hoc test for pairwise comparisons between issue types.

Arguments (positional):
- Output file from the `issue-type-ablation` command to generate plots and tables from.
- Output directory. Will be created if it does not exist.

### `scripts/analyse_separated_correlations.py`
Generates tables and figures from the output of the `correlate-identifiers` command, for `--mode issue-type-restricted`.

Contrary to the `scripts/analyse_correlations.py` script, this
script expects multiple input files from multiple invocations of the `correlate-identifiers` command. The directory structure must be in the following format:

```
<directory>
├── issue-type-1
│   ├── project-1
│   │   └── <correlate-identifiers outoput>
│   └── project-2
│       └── <correlate-identifiers outoput>
└── issue-type-2
    ├── project-1
    │   └── <correlate-identifiers outoput>
    └── project-2
        └── <correlate-identifiers outoput>
```

Generates a table containing correlation coefficients per issue type for each metric/dataset combination, for each method.
Each cell in the table contains /-separated values, each number corresponding to the issue type as given in the `--issue-types` argument.

Also outputs the table for BM25 in LaTeX format to the console.

Also outputs a heatmap of the magnitude of correlations (bucketed) for each issue type for BM25.

Arguments:
- `--directory`: Output directory from the `correlate-identifiers` command.
- `--out`: Output directory. Will be created if it does not exist.
- `--projects`: List of projects to incluede in the generated tables and plots. If given in the `key:value` format, the original `key` is printed as `value` in the tables/plots.
- `--metrics`: List of metrics to be printed. Usually not necessary to specify; sensible defaults are used. If given in the `key:value` format, the original `key` is printed as `value` in the tables/plots.
-- `--issue-types`: List of issue types to include in the generated tables and plots. If given in the `key:value` format, the original `key` is printed as `value` in the tables/plots.
