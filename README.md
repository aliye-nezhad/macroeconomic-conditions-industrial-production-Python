# Macroeconomic Conditions and Industrial Production

How do the federal funds rate and unemployment move with U.S. industrial production? I compare a regression in levels with a model of monthly changes using data from the Federal Reserve Bank of St. Louis.

## Data

| FRED series | Measure | Units |
| --- | --- | --- |
| [`INDPRO`](https://fred.stlouisfed.org/series/INDPRO) | Industrial production | Index (2017 = 100), seasonally adjusted |
| [`FEDFUNDS`](https://fred.stlouisfed.org/series/FEDFUNDS) | Effective federal funds rate | Percent, not seasonally adjusted |
| [`UNRATE`](https://fred.stlouisfed.org/series/UNRATE) | Civilian unemployment rate | Percent, seasonally adjusted |

The [saved FRED data](data/raw/fred_snapshot.csv) cover January 1990 through October 2026. Four of the 442 months are missing at least one series. The levels regression uses all 438 complete observations. The time-series tests use the longest stretch of consecutive complete months, January 1990 through September 2025 (429 observations). On that sample, a one-month lag always refers to the preceding calendar month. [Data notes](data/README.md)

## Levels regression

I regress the industrial production index on the federal funds and unemployment rates by OLS. Both coefficients are negative in the full sample. On the consecutive-month sample, the residual Durbin–Watson statistic is 0.06, and Newey–West standard errors with 12 lags are larger than HC1 standard errors for both slopes. The residual tests also indicate heteroskedasticity and departures from linearity. I use the levels regression as a descriptive benchmark. [Baseline estimates](outputs/tables/baseline_coefficients.csv) · [Standard-error comparison](outputs/tables/inference_comparison.csv) · [Residual tests](outputs/tables/diagnostic_tests.csv)

I read the ADF and KPSS results together. They are consistent with a unit root in industrial production and stationarity in unemployment. The two tests give conflicting results for the federal funds rate. The standard Engle–Granger test assumes the three series are integrated of order one. Given the mixed evidence, I leave the test out. [Stationarity tests](outputs/tables/stationarity_tests.csv) · [Methods](docs/METHODOLOGY.md)

## Monthly changes

I regress monthly industrial production growth (`100 × Δlog(INDPRO)`) on current and one-month-lagged changes in the two rates. Differencing and lagging leave 427 observations. A one-percentage-point rise in unemployment is associated with industrial production growth 1.37 percentage points lower in the same month, holding the other regressors fixed. The 95% Newey–West confidence intervals for both federal funds rate coefficients include zero. Estimating a causal effect would require isolating exogenous changes in the policy rate. [Monthly-change estimates](outputs/tables/changes_model_coefficients_hac12.csv)

## Run the analysis

Python 3.13.15 was used for the results in this repository. From the repository root, create and activate a virtual environment.

**macOS or Linux**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows Git Bash**

```bash
py -3.13 -m venv .venv
source .venv/Scripts/activate
```

```bash
python -m pip install -r requirements.txt
python replication/run_all.py
```

After package installation, the analysis reads the included CSV locally. The command writes to `outputs/`. To save a separate copy, pass `--output-dir path/to/results`. [Software versions and data checksum](docs/REPRODUCIBILITY.md)

## Repository structure

```text
├── code/
│   ├── macro_regression_workflow.py
│   └── diagnostic_workflow.py
├── data/
│   ├── raw/fred_snapshot.csv
│   └── README.md
├── docs/
│   ├── METHODOLOGY.md
│   └── REPRODUCIBILITY.md
├── outputs/
│   ├── diagnostics/
│   ├── figures/
│   └── tables/
├── replication/run_all.py
├── scripts/download_fred_snapshot.py
├── tests/test_workflow.py
├── requirements.txt
└── LICENSE
```

## Author

Aliye Nezhad

## License

The code is available under the [MIT License](LICENSE).
