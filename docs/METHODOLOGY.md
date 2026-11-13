# Methodology

## Sample and baseline model

The data are aligned to a monthly calendar. The baseline regression uses every month with observations for all three series, including the months after the October 2025 gap. The equation is estimated by OLS, with HC1 standard errors.

$$
\mathrm{INDPRO}_t = \beta_0 + \beta_1 \mathrm{FEDFUNDS}_t + \beta_2 \mathrm{UNRATE}_t + u_t.
$$

Time-series diagnostics use the longest stretch of consecutive complete months, January 1990 through September 2025. The same levels specification is estimated on this sample, with HC1 and Newey–West standard errors using 12 lags and a small-sample correction. Residual diagnostics include the Rainbow, Breusch–Pagan, and Ljung–Box tests and the Durbin–Watson statistic. The standard-error comparison illustrates how residual dependence affects inference; it does not resolve the specification's other limitations. [Results](../outputs/tables/inference_comparison.csv)

## Stationarity and cointegration

The ADF test takes a unit root as its null hypothesis; the KPSS test takes stationarity as its null. Both tests include a constant and linear trend for industrial production in levels. The rate series in levels and all transformed series use a constant. The transformations are the first difference of log industrial production and the first differences of the two rates. [Test results and lags](../outputs/tables/stationarity_tests.csv)

At the 5% level, the results for industrial production are consistent with a unit root. Both tests reject their respective nulls for the federal funds rate, while the unemployment results are consistent with stationarity. The standard Engle–Granger test assumes that the variables in the proposed long-run relationship are each integrated of order one. Given the mixed evidence, the stationarity results are reported without a cointegration estimate. [Cointegration test decision](../outputs/tables/cointegration_test_decision.csv)

## Monthly-change model

The dependent variable is 100 times the monthly log change in industrial production. The regressors are current and one-month-lagged changes in the two rates, measured in percentage points. The model is estimated by OLS, with Newey–West standard errors using 12 lags and a small-sample correction. The coefficients describe short-run conditional associations in 427 months. [Monthly-change estimates](../outputs/tables/changes_model_coefficients_hac12.csv)
