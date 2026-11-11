# Data

The analysis uses three monthly series from the Federal Reserve Bank of St. Louis's FRED database:

- `INDPRO`: Industrial Production: Total Index (2017 = 100, seasonally adjusted).
- `FEDFUNDS`: Effective Federal Funds Rate (percent, not seasonally adjusted).
- `UNRATE`: Civilian Unemployment Rate (percent, seasonally adjusted).

The CSV snapshot is stored at `raw/fred_snapshot.csv`. It is a static FRED export provided with the project; the original retrieval timestamp is not embedded in the file. The main replication uses this saved file and does not download updated observations.

## Sample and missing observations

The analysis window is January 1990–October 2026, with 442 monthly rows. Four months contain at least one missing series:

- October 2025: `UNRATE` is missing.
- August, September, and October 2026: `INDPRO` is missing.

The baseline regression uses 438 complete observations, from January 1990 through July 2026. The longest uninterrupted complete segment is January 1990–September 2025 (429 observations). The later segment, November 2025–July 2026, contains nine observations and is not used for the monthly time-series diagnostics.

## File integrity

SHA-256:

```text
95858e9ef24985d4a55bc698739da272882986a7d75a80396d96d2e16b1f53e4
```

The same hash is written to `outputs/diagnostics/reproducibility_manifest.json` whenever the replication script runs. If the data file changes, the hash in the manifest will change as well.
