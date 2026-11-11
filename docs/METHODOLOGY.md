# Methodology and interpretation notes

## Historical benchmark

The original descriptive model is preserved:

\[
INDPRO_t = \beta_0 + \beta_1 FEDFUNDS_t + \beta_2 UNRATE_t + u_t.
\]

The model is estimated by OLS on all complete monthly observations from January 1990 onward. HC1 standard errors are reported to preserve the original benchmark. This does not correct serial correlation or solve nonstationarity.

## Time-index discipline

The data are first reindexed to a complete monthly calendar. Missing observations remain explicit. Complete-case observations are split into uninterrupted segments before any monthly lag, HAC covariance, Ljung–Box, or autoregressive operation is performed. This avoids treating dates on opposite sides of a missing month as adjacent observations.

## Stationarity and cointegration

ADF and KPSS tests are reported together for the level series and their first differences because their null hypotheses differ. The deterministic terms used for each series are stored in `stationarity_tests.csv`. Engle–Granger tests are reported under constant and constant-plus-trend specifications. These tests are sensitive to deterministic terms, lag selection, breaks, and sample choice; they should not be read as definitive proof of an economic relationship.

## Inference comparison

The repository reports:
- HC1 on the full complete-case benchmark sample;
- HC1 on the longest uninterrupted monthly sample; and
- Newey–West HAC(12) on the longest uninterrupted monthly sample.

The HAC estimates use a consecutive monthly index. HAC is a covariance estimator, not a cure for a misspecified or spurious levels regression.

## Short-run change specification

The supplementary model uses monthly log growth in industrial production and current plus one-month-lagged changes in the federal funds and unemployment rates. It is estimated on the longest uninterrupted sample with HAC(12) covariance. This specification is exploratory and associational. It does not identify exogenous monetary-policy shocks and must not be described as a causal effect.

## Research interpretation

The project demonstrates data acquisition, validation, regression, diagnostic testing, and reproducible output generation. It does not claim to be a complete empirical investigation of monetary policy and industrial production. A stronger substantive study would require a clearly motivated identification strategy, a more developed dynamic specification, treatment of structural breaks, and economic interpretation grounded in the relevant literature.
