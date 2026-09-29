# Macroeconomic Conditions and Industrial Production

## Overview

This repository implements a reproducible Python workflow for retrieving
monthly US macroeconomic data from Federal Reserve Economic Data (FRED),
preparing the series, estimating a baseline regression, running diagnostic
checks, and exporting tables and figures in a reviewer-friendly structure.

The project is intended as a compact empirical workflow and coding sample. Its
regression estimates describe conditional associations and should not be
interpreted as causal effects.

## Research Question

How are short-term monetary policy conditions and labor-market slack associated
with movements in US industrial production?

## Data

The scripts download three monthly series directly from FRED:

| FRED code | Variable | Units |
| --- | --- | --- |
| `INDPRO` | Industrial Production: Total Index | Index, 2017 = 100; seasonally adjusted |
| `FEDFUNDS` | Effective Federal Funds Rate | Percent; not seasonally adjusted |
| `UNRATE` | Civilian Unemployment Rate | Percent; seasonally adjusted |

The sample begins on `1990-01-01` and ends at the latest observation available
when the workflow is run. Raw data are not committed because they are retrieved
programmatically. See [`data/README.md`](data/README.md) for series definitions,
processing steps, and the reproducibility caveat.

## Baseline Specification

The descriptive baseline model is:

```text
INDPRO ~ FEDFUNDS + UNRATE
```

The workflow performs:

- date alignment, numeric conversion, missing-value removal, and validation;
- ordinary least squares estimation;
- HC1 heteroskedasticity-robust standard errors;
- fitted-value and residual analysis;
- Rainbow and Breusch-Pagan tests;
- Ljung-Box residual-autocorrelation tests;
- variance inflation factors;
- an AR(3) model for the baseline residuals;
- conventional-versus-HC1 standard-error comparison;
- joint and individual coefficient tests; and
- a partial-regression plot for `FEDFUNDS`.

## Repository Structure

```text
us-macro-regression-python/
├── README.md
├── requirements.txt
├── .gitignore
├── code/
│   ├── macro_regression_workflow.py
│   └── diagnostic_workflow.py
├── data/
│   └── README.md
├── replication/
│   └── run_all.py
└── outputs/
    ├── diagnostics/
    │   ├── coefficient_hypothesis_tests.txt
    │   └── residual_autoregression_summary.txt
    ├── figures/
    │   ├── actual_vs_fitted.png
    │   ├── baseline_residuals.png
    │   ├── macro_series.png
    │   └── partial_regression_fedfunds.png
    └── tables/
        ├── baseline_regression_summary.txt
        ├── correlation_matrix.csv
        ├── descriptive_statistics.csv
        ├── diagnostic_tests.csv
        ├── fitted_values.csv
        ├── ljung_box_tests.csv
        ├── standard_error_comparison.csv
        └── variance_inflation_factors.csv
```

## Installation

The code requires Python 3.10 or newer and an internet connection for FRED.
From the repository root, create a virtual environment and install the pinned
dependency ranges:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Reproduction

Run the full analysis from the repository root:

```bash
python replication/run_all.py
```

The runner executes both workflows in order and verifies that all 14 expected
output files were created and are nonempty.

The stages can also be run separately:

```bash
python code/macro_regression_workflow.py
python code/diagnostic_workflow.py
```

Both commands should be launched from the repository root. Generated figures
are written to `outputs/figures/`, tabular results to `outputs/tables/`, and the
two longer diagnostic reports to `outputs/diagnostics/`.

## Output Guide

| Location | Contents |
| --- | --- |
| `outputs/figures/` | Time-series, fitted-value, residual, and partial-regression figures |
| `outputs/tables/` | Descriptive statistics, correlations, regression output, fitted values, and diagnostic test tables |
| `outputs/diagnostics/` | Coefficient-test and residual-autoregression text reports |

## Interpretation and Limitations

This is a deliberately compact demonstration of a reproducible econometric
workflow, not a causal monetary-policy design. The variables enter the baseline
model contemporaneously and in levels. The saved diagnostics indicate
substantial residual serial correlation and additional specification concerns.
HC1 standard errors address heteroskedasticity but do not correct serial
correlation.

The coefficient tests should therefore be treated as baseline descriptive
results. A substantive empirical extension would examine stationarity,
transformations and lags, dynamic specifications, and HAC or other
time-series-appropriate inference.

Because FRED observations can be revised and the scripts request the latest
available data, future runs may differ slightly from the committed outputs.

## Skills Demonstrated

- automated public-data acquisition;
- data cleaning and validation;
- modular Python workflow design;
- econometric estimation and inference comparison;
- model diagnostics and hypothesis testing;
- reproducible output generation; and
- transparent documentation of empirical limitations.

## Author

Aliye Nezhad

## License

The code and documentation are released under the MIT License. No separate license is asserted over the historical input workbook.
