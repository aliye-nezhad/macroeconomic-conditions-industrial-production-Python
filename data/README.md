# Data provenance and contract

## Source and input

The input file `raw/fred_snapshot.csv` is a FRED CSV snapshot supplied for this project audit on 2026-11-11. The original file does not embed a download timestamp, so the exact time at which it was retrieved cannot be independently established from the file alone.

Series:
- `INDPRO`: Industrial Production: Total Index.
- `FEDFUNDS`: Effective Federal Funds Rate.
- `UNRATE`: Civilian Unemployment Rate.

The downloaded file has an `observation_date` column and three series columns. The repository preserves this input snapshot unchanged.

## Analysis window and missingness

The analysis starts in January 1990. The file has 442 monthly rows through October 2026. Four months have at least one missing value:
- 2025-10: one or more series missing.
- 2026-08: INDPRO unavailable in the supplied snapshot.
- 2026-09: INDPRO unavailable in the supplied snapshot.
- 2026-10: INDPRO unavailable in the supplied snapshot.

The complete-case sample has 438 observations, January 1990–July 2026. Because October 2025 is an interior gap, the time-series diagnostics use the longest uninterrupted complete segment, January 1990–September 2025 (429 observations). The later November 2025–July 2026 segment contains nine observations and is not used for monthly HAC diagnostics.

## Integrity

SHA-256 of the supplied frozen snapshot:

```text
95858e9ef24985d4a55bc698739da272882986a7d75a80396d96d2e16b1f53e4
```

The generated `outputs/diagnostics/reproducibility_manifest.json` records this hash again alongside the analysis sample and software versions.

## Important

Do not replace the frozen input file without:
1. recording the new source and retrieval date;
2. recording the new SHA-256;
3. regenerating every output; and
4. committing the updated data and outputs together.
