# Repair and validation log

## Source snapshot

- Frozen FRED CSV SHA-256: `95858e9ef24985d4a55bc698739da272882986a7d75a80396d96d2e16b1f53e4`
- Analysis window: January 1990 onward.
- Complete observations: 438.
- Longest uninterrupted complete segment: January 1990–September 2025 (429 observations).
- Second uninterrupted segment: November 2025–July 2026 (9 observations).
- Missing months/series are retained in the missing-data report and are not silently compressed for time-series inference.

## Repairs made

1. Replaced the two-stage, independent live-download design with one offline-first runner that loads a single frozen snapshot once and passes the same in-memory data to every analysis stage.
2. Preserved missing months in the monthly calendar and split complete observations into uninterrupted segments before monthly lag and HAC calculations.
3. Removed the unsupported `result_object=False` argument from the partial-regression plot call.
4. Corrected coefficient-table handling for both pandas-backed and NumPy-backed Statsmodels result objects.
5. Added ADF and KPSS tests for levels and first differences, Engle–Granger tests, Rainbow and Breusch–Pagan tests, Durbin–Watson, Ljung–Box, VIF, and HAC inference comparisons.
6. Added a clearly labeled first-difference short-run association model with HAC(12) inference. It is not described as causal.
7. Added a reproducibility manifest with input hash, sample window, missing months, contiguous segments, and package versions.
8. Added unit tests, strict output validation, pinned core dependencies, a separate optional FRED-download dependency, and a GitHub Actions workflow.

## Validation performed in the reference environment

- Python 3.13.5
- NumPy 2.3.5
- pandas 2.2.3
- SciPy 1.17.0
- Matplotlib 3.10.8
- Statsmodels 0.14.6

Result:
- Unit tests: 5 passed.
- Full offline pipeline: completed successfully.
- Expected output files: 20 of 20 validated.
- Baseline sample: 438 observations; R-squared approximately 0.5721.
- Time-series diagnostic sample: 429 consecutive monthly observations.

## Known interpretation limits

The original levels regression remains a descriptive benchmark. The tests identify substantial specification concerns; neither HAC standard errors nor first differences establish causal identification. The new short-run model is exploratory. Further substantive work would require a theory-motivated dynamic specification and a defensible identification strategy.
