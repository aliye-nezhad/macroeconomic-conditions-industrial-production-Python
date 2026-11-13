# Reproducing the results

The results in this repository use Python 3.13.15, NumPy 2.3.5, pandas 2.2.3, Matplotlib 3.10.8, SciPy 1.17.0, and Statsmodels 0.14.6. The full list of package versions is in [`requirements.txt`](../requirements.txt).

Follow the [environment setup](../README.md#run-the-analysis), then run these commands from the repository root.

```bash
python -m pip install -r requirements.txt
python replication/run_all.py
```

The results go to `outputs/`. Use `--output-dir path/to/results` to write them elsewhere. To run the eight tests separately, use `python -m unittest discover -s tests -v`.

The analysis uses the saved [FRED CSV](../data/raw/fred_snapshot.csv). Its SHA-256 checksum is `95858e9ef24985d4a55bc698739da272882986a7d75a80396d96d2e16b1f53e4`. The [run record](../outputs/diagnostics/reproducibility_manifest.json) lists the checksum, sample dates, missing months, and software versions.
