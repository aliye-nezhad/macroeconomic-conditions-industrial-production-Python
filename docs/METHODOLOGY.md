# Methodology

## Sample and baseline model

The data are aligned to a monthly calendar. The baseline regression uses every month with observations for all three series, including the months after the October 2025 gap. I estimate the following equation by OLS and report HC1 standard errors.

$$
\mathrm{INDPRO}_t = \beta_0 + \beta_1 \mathrm{FEDFUNDS}_t + \beta_2 \mathrm{UNRATE}_t + u_t.
$$

The time-series diagnostics use the longest stretch of consecutive complete months, January 1990 through September 2025. On that sample, I fit the same levels model and compare HC1 and Newey–West standard errors with 12 lags and a small-sample correction. The residual diagnostics include the Rainbow, Breusch–Pagan, and Ljung–Box tests and the Durbin–Watson statistic. The standard-error comparison addresses how residual dependence affects inference. Questions about nonstationarity and the specification still apply. [Results](../outputs/tables/inference_comparison.csv)

## Stationarity and cointegration

The ADF test takes a unit root as its null hypothesis. The KPSS test takes stationarity as its null. Both tests include a constant and linear trend for industrial production in levels. The rate series in levels and all transformed series use a constant. The transformations are the first difference of log industrial production and the first differences of the two rates. [Test results and lags](../outputs/tables/stationarity_tests.csv)

At the 5% level, the results for industrial production are consistent with a unit root, both tests reject their respective nulls for the federal funds rate, and the unemployment results are consistent with stationarity. The standard Engle–Granger test assumes that the series in the proposed long-run relationship are each integrated of order one. Given the mixed evidence, I report the stationarity tests and leave out the cointegration estimate. [Cointegration test decision](../outputs/tables/cointegration_test_decision.csv)

## Monthly-change model

The dependent variable is 100 times the monthly log change in industrial production. The regressors are current and one-month-lagged changes in the two rates, measured in percentage points. I estimate the model by OLS and report Newey–West standard errors with 12 lags and a small-sample correction. The coefficients describe short-run conditional associations in 427 months. [Monthly-change estimates](../outputs/tables/changes_model_coefficients_hac12.csv)
