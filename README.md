# Macroeconomic Conditions and Industrial Production

This project examines how U.S. industrial production moves with the effective federal funds rate and the unemployment rate. The analysis compares a descriptive regression in levels with a supplementary model of monthly changes, using monthly data from the Federal Reserve Bank of St. Louis (FRED).

## Data

| FRED series | Measure | Units |
| --- | --- | --- |
| [`INDPRO`](https://fred.stlouisfed.org/series/INDPRO) | Industrial production | Index (2017 = 100), seasonally adjusted |
| [`FEDFUNDS`](https://fred.stlouisfed.org/series/FEDFUNDS) | Effective federal funds rate | Percent, not seasonally adjusted |
| [`UNRATE`](https://fred.stlouisfed.org/series/UNRATE) | Civilian unemployment rate | Percent, seasonally adjusted |

The committed snapshot covers January 1990 through October 2026 (442 monthly observations). Four months have at least one missing observation. The baseline regression uses 438 complete observations. Time-series diagnostics use the longest uninterrupted complete segment, January 1990 through September 2025 (429 observations); the later segment contains nine observations. The snapshot's SHA-256 digest is recorded in [data/raw.sha256](data/raw.sha256). Additional details are in [data/README.md](data/README.md).

## Levels specification

The baseline OLS regression relates the industrial production index to the federal funds rate and unemployment rate. Both slope coefficients are negative in the full sample, and the model's $R^2$ is 0.5721. In the uninterrupted 429-month sample, the residual Durbin–Watson statistic is 0.06. The residual tests also indicate heteroskedasticity and departures from linearity. Newey–West standard errors with 12 lags are reported alongside HC1 estimates for the uninterrupted sample. The levels regression is descriptive; its coefficients should not be interpreted as causal effects.

[Baseline coefficients](outputs/tables/baseline_coefficients.csv) · [Inference comparison](outputs/tables/inference_comparison.csv) · [Residual diagnostics](outputs/tables/diagnostic_tests.csv)

## Stationarity and cointegration

The ADF and KPSS tests provide evidence consistent with a unit root in industrial production and stationarity in unemployment. Their results for the federal funds rate conflict. Since the standard Engle–Granger procedure assumes that all variables in the proposed long-run relationship are integrated of order one, the cointegration test is not reported.

[Stationarity tests](outputs/tables/stationarity_tests.csv) · [Cointegration decision](outputs/tables/cointegration_test_decision.csv) · [Methodology](docs/METHODOLOGY.md)

## Monthly-change specification

The supplementary model regresses monthly industrial production growth (`100 × Δlog(INDPRO)`) on current and one-month-lagged changes in the two interest-rate variables. Differencing and lagging leave 427 observations. A one-percentage-point increase in unemployment is associated with industrial production growth 1.37 percentage points lower in the same month, conditional on the other regressors. The 95% Newey–West confidence intervals for both federal funds rate coefficients include zero. The estimates describe conditional associations, not causal effects.

[Monthly-change estimates](outputs/tables/changes_model_coefficients_hac12.csv)

## Reproducing the results

The reference environment is Python 3.13.15. Package versions are pinned in `requirements.txt`.

Create and activate a virtual environment from the repository root.

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

Install the dependencies and verify the committed data snapshot:

```bash
python -m pip install -r requirements.txt
sha256sum --check data/raw.sha256
```

On Windows PowerShell, use `Get-FileHash .\data\raw\fred_snapshot.csv -Algorithm SHA256` and compare the result with the digest in `data/raw.sha256`.

Run the complete analysis:

```bash
python replication/run_all.py
```

The runner executes ten unit tests, estimates both specifications, generates the tables and figures, and validates all 20 expected outputs. The default workflow uses the committed snapshot and runs offline after package installation. To use another CSV or write results to a separate directory, pass `--data` or `--output-dir`, respectively.

See the [reproducibility guide](docs/REPRODUCIBILITY.md) for the full procedure and the [output inventory](outputs/README.md) for the generated files. An optional FRED downloader is provided separately; it saves a new snapshot and does not replace the committed input.

## Continuous integration

GitHub Actions verifies the snapshot checksum, installs the pinned environment, runs the tests and replication workflow, and compares all 20 regenerated outputs with the committed results. Numeric CSV values are compared within tight floating-point tolerances, figures by decoded pixel values, and text and JSON files exactly.

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
