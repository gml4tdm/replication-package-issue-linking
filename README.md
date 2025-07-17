# Towards Issue Change Impact Prediction -- Replication Package

## Supplementary Reading

- [Extensions](docs/extensions.md)
- [Regexes for Identifiers and File Names](docs/regexes.md)
- [Issue Type Details](docs/issue_types.md)


## Directory Structure

### `results` Directory

Contains the raw results of all experiments.

- `results/ir-1`: Contains the results for tuning the formatting handling
- `results/ir-2`: Contains the results for tuning the remainder of the preprocessing
- `results/ir-3`: Contains the results for the actual experiments presented in the paper

### `tuning` Directory

Containt the tables summarising the results for the tuning of the formatting handling and preprocessing. Specifically:

- [`tuning/formatting.md`](tuning/formatting.md): Contains the results for tuning the formatting handling
- [`tuning/preprocessing.md`](tuning/preprocessing.md): Contains the results for tuning the other preprocessing steps

### `analysis` Directory

Contains the statistical analysis for the results presented in the paper.

- [`analysis/identifier-count`](analysis/identifier-count): Contains the results for the identifier count analysis. It contains a breakdown of the number of identifiers per issue type (over all projects), and by project (over all issue types). For both, we provide a box plot, and the results of a statistical analysis using Kruskal-Wallis and Conover's Post-Hoc test.

- [`analysis/rq-1/performance.md`](analysis/rq-1/performance.md): Contains the results for RQ 1 (performance). Contains both tables included in the paper, as well as the results for the `Lower, Stemming, Sub Tokens` option.

- [`analysis/rq-2/uncontrolled`](analysis/rq-2/uncontrolled): Contains various results for RQ 2. One directory contains the results for the methods without sub-tokens; the other contains the results for the methods with sub-tokens. Each directory contains bar charts showing the performance of each method for each separate issue type (`<METHOD>_specific.png`) and with each specific issue type held out (`<METHOD>_holdout.png`). The `tables.md` file contains the results of the Kruskal-Wallis test (for difference between issue types) for each method. The `pairwise.md` file contains the results of Conover's Post-Hoc test for difference between the individual issue types.

- [`analysis/rq-3/uncontrolled`](analysis/rq-3/uncontrolled): Contains the results for RQ 3. The `no-sub-tokens` and `sub-tokens` directories contain tables of the Spearman correlation coefficients between performance and number of identifiers for each method. The `no-sub-tokens-restricted` and `sub-tokens-restricted` directories contain the same tables, but restricted to the four main issue types. These tables show that the patterns from the tables containing all issue types (also those not in the four main categories) still hold up when restricting to the four main types. The tables in `no-sub-tokens-by-type` and `sub-tokens-by-type` show the correlation coefficients for each issue type separately.
