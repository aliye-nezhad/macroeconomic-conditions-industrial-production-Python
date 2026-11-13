# Macroeconomic Conditions and Industrial Production

How do the federal funds rate and unemployment move with U.S. industrial production? I compare a regression in levels with a model of monthly changes using data from the Federal Reserve Bank of St. Louis.

## Data

| FRED series | Measure | Units |
| --- | --- | --- |
| [`INDPRO`](https://fred.stlouisfed.org/series/INDPRO) | Industrial production | Index (2017 = 100), seasonally adjusted |
| [`FEDFUNDS`](https://fred.stlouisfed.org/series/FEDFUNDS) | Effective federal funds rate | Percent, not seasonally adjusted |
| [`UNRATE`](https://fred.stlouisfed.org/series/UNRATE) | Civilian unemployment rate | Percent, seasonally adjusted |

The saved [FRED snapshot](data/raw/fred_snapshot.csv) covers January 1990 through October 2026. Four of the 442 months have at least one missing series. The levels regression uses all 438 complete observations. The time-series diagnostics use the longest uninterrupted stretch of complete months, January 1990 through September 2025 (429 observations). The later complete segment contains nine observations. The snapshot's expected SHA-256 digest is stored in [data/raw.sha256](data/raw.sha256). See the [data notes](data/README.md).

## Levels regression

I regress the industrial production index on the federal funds and unemployment rates by OLS. Both coefficients are negative in the full sample, and the baseline (R^2) is 0.5721. On the consecutive-month sample, the residual Durbin–Watson statistic is 0.06, and Newey–West standard errors with 12 lags are larger than HC1 standard errors for both slopes. The residual tests also indicate heteroskedasticity and departures from linearity. I use the levels regression as a descriptive benchmark, not as a causal specification. [Baseline estimates](outputs/tables/baseline_coefficients.csv) · [Standard-error comparison](outputs/tables/inference_comparison.csv) · [Residual tests](outputs/tables/diagnostic_tests.csv)

I read the ADF and KPSS results together. They are consistent with a unit root in industrial production and stationarity in unemployment. The two tests give conflicting results for the federal funds rate. The standard Engle–Granger test assumes the three series are integrated of order one. Given the mixed evidence, I leave the test out. [Stationarity tests](outputs/tables/stationarity_tests.csv) · [Methods](docs/METHODOLOGY.md)

## Monthly changes

I regress monthly industrial production growth (`100 × Δlog(INDPRO)`) on current and one-month-lagged changes in the two rates. Differencing and lagging leave 427 observations. A one-percentage-point rise in unemployment is associated with industrial production growth 1.37 percentage points lower in the same month, holding the other regressors fixed. The 95% Newey–West confidence intervals for both federal funds rate coefficients include zero. Estimating a causal effect would require isolating exogenous changes in the policy rate. [Monthly-change estimates](outputs/tables/changes_model_coefficients_hac12.csv)

## Run the analysis

The reference environment is Python 3.13.15. Package versions are pinned in `requirements.txt`. From the repository root, create and activate a virtual environment.

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

Install the pinned dependencies and verify the bundled input before running the analysis:

```bash
python -m pip install -r requirements.txt
sha256sum --check data/raw.sha256
python replication/run_all.py
```

On Windows PowerShell, compare the output of `Get-FileHash .\data\raw\fred_snapshot.csv -Algorithm SHA256` with the digest in `data/raw.sha256`. The runner executes ten unit tests, loads the bundled snapshot once, estimates the baseline and supplementary specifications, writes the tables and figures, and validates all 20 expected outputs. The run record includes the input hash, sample information, and package versions. To write results to another directory, pass `--output-dir path/to/results`. [Reproducibility guide](docs/REPRODUCIBILITY.md) · [Output inventory](outputs/README.md)

The default analysis is offline after package installation. It does not request live FRED observations or require an API key. The optional downloader is separate and writes a new file rather than replacing the committed snapshot; see the [data and reproduction notes](docs/REPRODUCIBILITY.md#optional-fred-download).

## Automated reproduction

GitHub Actions checks the frozen input checksum, installs the pinned Python environment, runs the unit tests and complete analysis, and compares all 20 regenerated outputs with the committed reference files. Numeric CSV values are compared within tight floating-point tolerances, figures are compared by decoded pixel values, and text and JSON files are compared exactly. This verifies the computational workflow on a clean runner without treating harmless last-decimal floating-point variation as a failed replication.

## Repository structure

```text
├── .github/workflows/replication.yml
├── .gitattributes
├── .python-version
├── code/
│   ├── macro_regression_workflow.py
│   └── diagnostic_workflow.py
├── data/
│   ├── raw/fred_snapshot.csv
│   ├── raw.sha256
│   └── README.md
├── docs/
│   ├── METHODOLOGY.md
│   └── REPRODUCIBILITY.md
├── outputs/
│   ├── diagnostics/
│   ├── figures/
│   ├── tables/
│   └── README.md
├── replication/
│   ├── compare_outputs.py
│   └── run_all.py
├── scripts/download_fred_snapshot.py
├── tests/test_workflow.py
├── requirements.txt
├── requirements-fred-download.txt
└── LICENSE
```

## Author

Aliye Nezhad

## License

The code is available under the [MIT License](LICENSE).
