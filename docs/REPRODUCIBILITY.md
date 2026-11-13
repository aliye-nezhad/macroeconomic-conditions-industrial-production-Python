# Reproducing the results

## Reference environment

The committed results use Python 3.13.15, NumPy 2.3.5, pandas 2.2.3, Matplotlib 3.10.8, SciPy 1.17.0, and Statsmodels 0.14.6. The complete set of pinned packages is in [requirements.txt](../requirements.txt), and [.python-version](../.python-version) records the Python version used by GitHub Actions.

## Obtain the repository

Clone the repository and change into its root directory:

```bash
git clone https://github.com/aliye-nezhad/macroeconomic-conditions-industrial-production-Python.git
cd macroeconomic-conditions-industrial-production-Python
```

## Verify the frozen input

The analysis uses the committed [FRED CSV snapshot](../data/raw/fred_snapshot.csv), not live observations. On Linux or macOS, verify it with:

```bash
sha256sum --check data/raw.sha256
```

On Windows PowerShell, calculate the digest with:

```powershell
Get-FileHash .\data\raw\fred_snapshot.csv -Algorithm SHA256
```

The calculated digest must match the value in [data/raw.sha256](../data/raw.sha256):

```text
95858e9ef24985d4a55bc698739da272882986a7d75a80396d96d2e16b1f53e4
```

The runner records the actual input hash in the reproducibility manifest and checks it against the input used for that run. The checksum file identifies the expected bundled snapshot independently.

## Create the environment and run the workflow

Create and activate a virtual environment using Python 3.13.15, then install the pinned dependencies:

```bash
python -m pip install -r requirements.txt
```

From the repository root, run:

```bash
python replication/run_all.py
```

The runner executes the nine unit tests, loads the fixed CSV snapshot once, estimates the levels regression, performs the time-series diagnostics and supplementary monthly-change model, writes the results, and validates all 20 expected output files. The output validator checks file presence and non-empty content, fitted-value fields, the manifest's input hash and sample size, the cointegration decision, and the baseline coefficient table.

The default output directory is `outputs/`. To preserve the committed reference outputs while writing a separate run, use:

```bash
python replication/run_all.py --output-dir path/to/results
```

The unit tests can also be run separately:

```bash
python -m unittest discover -s tests -v
```

The runner supports `--data path/to/file.csv` for a different snapshot. In that case, the manifest records the selected file and its hash; the committed checksum applies only to the bundled snapshot. The `--skip-tests` option is available for troubleshooting but is not recommended for a reviewer reproduction.

## Optional FRED download

The default workflow does not access the internet or request current FRED observations. To use the separate download utility, install its optional dependencies:

```bash
python -m pip install -r requirements-fred-download.txt
python scripts/download_fred_snapshot.py --start 1990-01-01
```

The utility saves a separate file at `data/raw/fred_snapshot_new.csv` by default. It does not overwrite the frozen input. A refreshed snapshot is a different dataset: review its sample and missing observations, update the checksum and reference outputs deliberately, and document the new snapshot before treating it as the project input.

## What GitHub Actions verifies

On pushes to `main` and pull requests targeting `main`, GitHub Actions:

1. checks out the repository on a clean Ubuntu runner;
2. installs the Python version recorded in `.python-version`;
3. verifies the frozen CSV against `data/raw.sha256`;
4. installs the pinned dependencies;
5. runs the unit tests and the complete replication workflow;
6. compares all 20 generated files with the committed reference outputs.

The comparison uses tight numerical tolerances for numeric CSV columns, pixel-level comparison for figures, and exact comparison for text and JSON files. This accommodates harmless floating-point and image-encoding variation while still detecting changes to the sample, model results, output structure, or substantive content.

The workflow therefore executes the analysis; it is not a static file-presence check. A successful run demonstrates that the committed code, fixed input, and pinned environment regenerate results consistent with the committed references on the CI runner.

## Generated outputs

The full inventory and purpose of the 20 expected result files are documented in [outputs/README.md](../outputs/README.md). The machine-readable [reproducibility manifest](../outputs/diagnostics/reproducibility_manifest.json) records the input checksum, sample dates, missing months, contiguous segments, software versions, and supplementary-model sample information.
