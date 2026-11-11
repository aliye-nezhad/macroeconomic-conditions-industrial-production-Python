# Methodology

## Baseline model

The main descriptive specification is:

\[
INDPRO_t = \beta_0 + \beta_1 FEDFUNDS_t + \beta_2 UNRATE_t + u_t.
\]

It is estimated by OLS on all complete monthly observations from January 1990 onward. HC1 standard errors are reported for the baseline. They account for heteroskedasticity, but not serial correlation.

## Monthly sample construction

The data are aligned to a complete monthly index before estimation. Missing observations remain explicit. The baseline regression uses all complete observations, including observations after the October 2025 gap. Time-series diagnostics and lagged specifications use the longest uninterrupted complete segment so that a lag always refers to the preceding calendar month.

## Diagnostics

The project reports ADF and KPSS tests for the level variables and their first differences. The tests use different null hypotheses and are interpreted together rather than treated as automatic model-selection rules. Deterministic terms and lag choices are saved in the output table.

The standard Engle–Granger test is run only if the level-series ADF and KPSS results jointly support treating all variables as I(1). In the supplied sample, that condition is not met, so the repository records that the test was not run. This avoids reporting cointegration p-values under an unsupported integration-order assumption.

The baseline residuals are also checked for linearity, heteroskedasticity, and autocorrelation. HAC(12) standard errors are reported on the uninterrupted sample as an inference comparison. HAC covariance estimation does not correct nonstationarity or a misspecified regression.

## Supplementary change model

The supplementary specification relates monthly log growth in industrial production to current and one-month-lagged changes in FEDFUNDS and UNRATE. It is estimated by OLS with Newey–West HAC(12) standard errors. The specification is exploratory and does not identify exogenous monetary-policy shocks.

## Interpretation

The baseline and supplementary regressions estimate conditional associations. Neither is a causal design. The levels model is retained as a descriptive benchmark, not presented as a stable long-run relationship. A stronger substantive study would require a theory-motivated dynamic specification and a defensible identification strategy.
