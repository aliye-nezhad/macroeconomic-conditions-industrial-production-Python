# Macroeconomic Conditions and Industrial Production

## Overview

This project examines the relationship between US industrial production, the effective federal funds rate, and the unemployment rate using monthly data from the Federal Reserve Bank of St. Louis's FRED database.

The analysis starts with a descriptive OLS regression and then checks whether its assumptions are reasonable for these time series. A supplementary model uses monthly changes to examine short-run associations. The results should not be interpreted as causal effects.

## Research question

How are monetary conditions and labor-market conditions associated with movements in US industrial production?

## Data

The analysis uses three FRED series:

| Series | Description | Units |
| --- | --- | --- |
| `INDPRO` | Industrial Production: Total Index | Index, 2017 = 100; seasonally adjusted |
| `FEDFUNDS` | Effective Federal Funds Rate | Percent; not seasonally adjusted |
| `UNRATE` | Civilian Unemployment Rate | Percent; seasonally adjusted |

A CSV snapshot is included at `data/raw/fred_snapshot.csv`. The main workflow reads this file and does not connect to FRED, so the results can be reproduced without an API key or an internet connection.

The snapshot covers January 1990 to October 2026 (442 monthly rows). Four months contain at least one missing value. The baseline regression uses the 438 complete observations. For time-series diagnostics, the code uses the longest uninterrupted monthly segment, January 1990 to September 2025 (429 observations). October 2025 is incomplete, and the later complete segment is too short for the monthly diagnostics used here. The missing observations are documented in `outputs/tables/missing_data_report.csv`.

Series definitions, the data snapshot's SHA-256 hash, and the missing-data details are recorded in `data/README.md`.

## Empirical approach

### Baseline regression

The original descriptive specification is retained:

```text
INDPRO ~ FEDFUNDS + UNRATE
```

It is estimated by OLS using all complete observations. HC1 standard errors are reported for comparison with the original analysis. These standard errors account for heteroskedasticity, but not serial correlation.

### Diagnostics

The workflow examines residual autocorrelation, heteroskedasticity, linearity, and multicollinearity. It also reports ADF and KPSS tests for the level series and their first differences.

An Engle–Granger cointegration test is not reported for this sample. The preliminary ADF and KPSS results do not support treating all three level series as I(1): the evidence differs across variables. Applying the standard test without that qualification would give the result more meaning than the data support.

For the baseline model, the code compares HC1 standard errors with Newey–West HAC(12) standard errors on the uninterrupted monthly sample. HAC inference does not, by itself, resolve nonstationarity or model misspecification.

### Short-run specification

A supplementary model relates monthly log growth in industrial production to current and one-month-lagged changes in the federal funds and unemployment rates:

```text
100 × Δlog(INDPRO)
    ~ ΔFEDFUNDS + ΔUNRATE
    + ΔFEDFUNDS(t-1) + ΔUNRATE(t-1)
```

It is estimated on the uninterrupted sample with HAC(12) standard errors. This is an exploratory specification, not a structural monetary-policy model or a causal design.

## Reproducing the results

The repository includes the data snapshot and pinned package versions. The main analysis runs offline.

Python 3.13.5 is the reference version used for the committed results.

### Windows (PowerShell)

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python replication/run_all.py
```

### Windows (Git Bash)

```bash
py -3.13 -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python replication/run_all.py
```

### macOS or Linux

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python replication/run_all.py
```

The replication script runs the unit tests, loads the bundled CSV, estimates the models, generates the tables and figures, and writes a reproducibility manifest. It also checks that the manifest hash matches the input file and that the fitted-value sample size is consistent. A successful run ends with a `SUCCESS` message and confirms that all expected outputs were checked.

To run the tests separately:

```bash
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs the same tests and replication script when changes are pushed or a pull request is opened.

## Repository contents

```text
.
├── code/                  # Data preparation, estimation, and diagnostics
├── data/
│   ├── raw/                # Frozen FRED data snapshot
│   └── README.md           # Data sources and provenance
├── docs/                   # Methodology and reproducibility notes
├── outputs/
│   ├── diagnostics/        # Model summaries and reproducibility manifest
│   ├── figures/            # Generated figures
│   └── tables/             # Regression and diagnostic results
├── replication/
│   └── run_all.py          # Main replication entry point
├── scripts/                # Optional data-download utility
├── tests/                  # Unit tests
├── requirements.txt
└── README.md
```

## Outputs

The main outputs are saved under `outputs/`:

- `tables/` contains descriptive statistics, correlations, regression estimates, fitted values, missing-data information, and diagnostic results.
- `figures/` contains the time-series plots, fitted-versus-actual plot, and partial-regression plot.
- `diagnostics/` contains model summaries and a JSON manifest recording the input hash, sample information, and package versions.

## Limitations

The levels regression is a descriptive benchmark. The diagnostics show substantial residual autocorrelation and heteroskedasticity, while the stationarity tests raise concerns about the time-series properties of the variables. Its coefficients should therefore not be read as stable long-run effects.

The supplementary change specification is exploratory. It does not identify exogenous monetary-policy shocks, and none of the reported regressions establishes causality. A more complete empirical study would need a theory-motivated dynamic specification and a defensible identification strategy.

FRED may revise historical observations. For that reason, the default workflow uses the included data snapshot. The optional download script creates a separate file rather than overwriting the snapshot used for the committed results.


## Author

Aliye Nezhad


## License

The code is released under the MIT License. See `LICENSE`.
