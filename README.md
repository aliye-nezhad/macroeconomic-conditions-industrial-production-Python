# Macroeconomic Conditions and Industrial Production

An offline-first, reproducible Python workflow for examining the association between US industrial production, the effective federal funds rate, and the unemployment rate.

## Research question

How are short-term monetary-policy conditions and labor-market slack associated with movements in US industrial production?

This repository is an empirical programming and econometrics sample. Its regression estimates describe conditional associations. They are **not causal effects**.

## Reproduce the project

The repository includes a frozen FRED CSV snapshot. The default workflow does not call the internet and does not depend on the current state of FRED.

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python replication/run_all.py
```

### Windows (Git Bash)

```bash
py -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python replication/run_all.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python replication/run_all.py
```

The runner:
1. executes the unit tests;
2. loads the bundled frozen data snapshot;
3. validates the monthly date index and missing observations;
4. estimates the original descriptive levels regression;
5. runs diagnostics on the longest uninterrupted monthly sample;
6. estimates a supplementary first-difference specification with HAC(12) inference;
7. writes tables, figures, and a reproducibility manifest; and
8. validates that all expected outputs exist and contain usable data.

A successful run ends with `SUCCESS` and reports the number of validated output files.

## Data

The three FRED series are:

| Series | Description | Units |
|---|---|---|
| `INDPRO` | Industrial Production: Total Index | Index, 2017 = 100; seasonally adjusted |
| `FEDFUNDS` | Effective Federal Funds Rate | Percent; not seasonally adjusted |
| `UNRATE` | Civilian Unemployment Rate | Percent; seasonally adjusted |

The analysis begins in January 1990. The frozen input is `data/raw/fred_snapshot.csv`. Its source and SHA-256 digest are documented in [`data/README.md`](data/README.md).

The snapshot contains 442 monthly rows from January 1990 through October 2026. Four rows have at least one missing series: October 2025 and August–October 2026. Complete-case estimation therefore uses 438 observations. Time-series diagnostics use the longest uninterrupted complete segment, January 1990–September 2025 (429 observations), rather than treating observations on opposite sides of a missing month as adjacent.

## Models and interpretation

### 1. Historical descriptive benchmark

```text
INDPRO ~ FEDFUNDS + UNRATE
```

This levels OLS model is retained to make the original sample and estimates transparent. HC1 standard errors address heteroskedasticity but do not address serial correlation or nonstationarity. The levels regression should not be interpreted as a causal or necessarily stable long-run relationship.

### 2. Time-series diagnostics

The workflow reports:
- ADF and KPSS tests for each series in levels and for the first-difference series;
- Engle–Granger residual-based cointegration tests under constant and constant-plus-trend specifications;
- Rainbow linearity and Breusch–Pagan heteroskedasticity tests;
- Durbin–Watson and Ljung–Box residual-autocorrelation statistics;
- variance inflation factors; and
- inference comparisons using HC1 and Newey–West HAC(12) covariance estimates on a strictly consecutive monthly sample.

The ADF and KPSS tests have different null hypotheses. Their deterministic terms are documented in the output table. Test outcomes are evidence, not an automatic instruction to difference every series.

### 3. Supplementary short-run change specification

The workflow estimates:

```text
100 × Δlog(INDPRO)
    ~ ΔFEDFUNDS + ΔUNRATE
    + ΔFEDFUNDS(t-1) + ΔUNRATE(t-1)
```

This is an exploratory short-run association model, estimated on the longest uninterrupted monthly segment with Newey–West HAC(12) standard errors. It is not a causal design. Its specification and results are reported separately from the original levels benchmark.

## Output files

All generated files are written under `outputs/`.

| Folder | Contents |
|---|---|
| `outputs/tables/` | Descriptive statistics, correlations, fitted values, coefficient tables, missing-data report, inference comparison, diagnostics, stationarity and cointegration tests |
| `outputs/figures/` | Macro series, actual-versus-fitted plot, partial-regression plot |
| `outputs/diagnostics/` | HAC summaries and machine-readable reproducibility manifest |

The manifest records the input file hash, sample dates, missing months, contiguous segments, and software versions.

## Tests

Run the unit tests independently:

```bash
python -m unittest discover -s tests -v
```

The GitHub Actions workflow also runs the tests and the complete offline replication pipeline on each push and pull request.

## Optional: download a newer FRED snapshot

The default replication never downloads data. To create a separate newer snapshot, first install the optional downloader dependency:

```bash
python -m pip install -r requirements-fred-download.txt
python scripts/download_fred_snapshot.py --start 1990-01-01 --output data/raw/fred_snapshot_new.csv
```

Review the new file, update its provenance and hash, and deliberately replace the frozen input only when you intend to create a new data vintage. Do not silently overwrite the snapshot used for a published or submitted result.

## Limitations

- The baseline levels regression is descriptive and has substantial time-series diagnostic concerns.
- HC1 does not correct serial correlation.
- The change specification is a transparent robustness exercise, not a structural monetary-policy model.
- FRED can revise historical observations. The frozen snapshot prevents silent changes to the input data, but it does not guarantee that a later FRED download will match this vintage.
- Numerical reproducibility is strongest when the pinned dependencies and Python version documented in `requirements.txt` are used.
