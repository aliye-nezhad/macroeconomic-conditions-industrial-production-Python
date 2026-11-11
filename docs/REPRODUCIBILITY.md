# Reproducibility

The default analysis runs offline using the CSV snapshot in `data/raw/fred_snapshot.csv`.

## Reference environment

- Python 3.13.5
- NumPy 2.3.5
- pandas 2.2.3
- Matplotlib 3.10.8
- SciPy 1.17.0
- Statsmodels 0.14.6

The direct dependencies and required transitive packages are pinned in `requirements.txt`. The optional FRED download utility has its own dependency file, `requirements-fred-download.txt`.

## Run

From the repository root:

```bash
python -m pip install -r requirements.txt
python replication/run_all.py
```

The runner executes eight unit tests before estimating the models. It then generates the output tables and figures and writes `outputs/diagnostics/reproducibility_manifest.json`. Before finishing, it checks that the manifest hash matches the input file and that the fitted-value row count matches the recorded sample size. The manifest records the data hash, sample dates, missing months, contiguous sample segments, and package versions.

The committed data snapshot has SHA-256:

```text
95858e9ef24985d4a55bc698739da272882986a7d75a80396d96d2e16b1f53e4
```

The GitHub Actions workflow uses Python 3.13.5 and runs the same replication command on pushes and pull requests.
