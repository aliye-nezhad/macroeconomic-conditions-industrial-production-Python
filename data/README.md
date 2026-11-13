# Data

The analysis uses the saved FRED export [fred_snapshot.csv](raw/fred_snapshot.csv), containing monthly observations for industrial production, the effective federal funds rate, and civilian unemployment. The series are identified by their FRED codes: [INDPRO](https://fred.stlouisfed.org/series/INDPRO), [FEDFUNDS](https://fred.stlouisfed.org/series/FEDFUNDS), and [UNRATE](https://fred.stlouisfed.org/series/UNRATE).

The CSV does not contain a download timestamp. FRED may revise historical observations, so a new download can differ from the snapshot used here. No retrieval date is asserted. The exact committed file is identified by its SHA-256 digest in [raw.sha256](raw.sha256), which is checked by the GitHub Actions workflow and can be checked locally before reproduction.

## Sample and missing observations

The snapshot has 442 monthly rows from January 1990 through October 2026. Unemployment is missing in October 2025. Industrial production is missing in August, September, and October 2026.

The baseline regression uses 438 complete observations, from January 1990 through July 2026. The time-series tests use January 1990 through September 2025, the longest uninterrupted segment with all three series (429 observations). The later segment, November 2025 through July 2026, has nine complete observations. [Missing months](../outputs/tables/missing_data_report.csv) · [Monthly segments](../outputs/tables/complete_monthly_segments.csv)

## Variables and units

| FRED code | Variable | Units |
| --- | --- | --- |
| INDPRO | Industrial production: total index | Index, 2017 = 100; seasonally adjusted |
| FEDFUNDS | Effective federal funds rate | Percent; not seasonally adjusted |
| UNRATE | Civilian unemployment rate | Percent; seasonally adjusted |

## Input integrity

The SHA-256 digest of the committed CSV is recorded in [raw.sha256](raw.sha256). The replication runner records the input hash in [the reproducibility manifest](../outputs/diagnostics/reproducibility_manifest.json). The manifest records which file was used; the checksum file separately identifies the expected bundled snapshot.
