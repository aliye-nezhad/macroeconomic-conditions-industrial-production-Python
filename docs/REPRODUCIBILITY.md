# Reproducibility record

- Default mode: offline.
- Input: `data/raw/fred_snapshot.csv`.
- Input SHA-256: `95858e9ef24985d4a55bc698739da272882986a7d75a80396d96d2e16b1f53e4`.
- Reference runtime used to regenerate the attached outputs: Python 3.13.5, NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, Matplotlib 3.10.8, Statsmodels 0.14.6.
- Dependencies are pinned in `requirements.txt`.
- The runner executes unit tests before estimation and validates all expected output files.
- The data snapshot is frozen; the default run does not query FRED.

To reproduce:

```bash
python -m pip install -r requirements.txt
python replication/run_all.py
```

A successful execution reports the number of validated outputs and writes the input hash and sample metadata to `outputs/diagnostics/reproducibility_manifest.json`.
