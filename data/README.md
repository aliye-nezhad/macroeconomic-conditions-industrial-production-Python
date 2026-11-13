# Data

The saved FRED export contains monthly observations for industrial production, the effective federal funds rate, and civilian unemployment. The file has no download timestamp. FRED can revise past observations, so a new download can differ from the file used here. The download script saves a separate CSV by default. [Saved CSV](raw/fred_snapshot.csv) · [Download script](../scripts/download_fred_snapshot.py) · [INDPRO](https://fred.stlouisfed.org/series/INDPRO) · [FEDFUNDS](https://fred.stlouisfed.org/series/FEDFUNDS) · [UNRATE](https://fred.stlouisfed.org/series/UNRATE)

## Sample and missing observations

The CSV has 442 monthly rows from January 1990 through October 2026. Unemployment is missing in October 2025. Industrial production is missing in August, September, and October 2026.

The baseline regression uses 438 complete observations through July 2026. The time-series tests use January 1990 through September 2025, the longest stretch of consecutive months with all three series (429 observations). The later stretch, November 2025 through July 2026, has nine complete months. [Missing months](../outputs/tables/missing_data_report.csv)

## File checksum

```text
95858e9ef24985d4a55bc698739da272882986a7d75a80396d96d2e16b1f53e4
```

The [run record](../outputs/diagnostics/reproducibility_manifest.json) includes the SHA-256 checksum for the file used in the analysis.
