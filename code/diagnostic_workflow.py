"""Residual tests, stationarity tests, and the monthly-change model."""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import acorr_ljungbox, het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tsa.stattools import adfuller, coint, kpss

from macro_regression_workflow import (
    SERIES,
    contiguous_complete_segments,
    coefficient_table,
    longest_contiguous_segment,
    stable_summary_text,
)


def run_stationarity_tests(data: pd.DataFrame) -> pd.DataFrame:
    """Run ADF and KPSS tests on levels and first differences.

    INDPRO in levels is tested with a constant and linear trend; the two rate
    variables in levels and all first differences are tested with a constant.
    Deterministic terms and null hypotheses are recorded in the output.
    """
    specifications: list[tuple[str, pd.Series, str]] = [
        ("INDPRO", data["INDPRO"], "ct"),
        ("FEDFUNDS", data["FEDFUNDS"], "c"),
        ("UNRATE", data["UNRATE"], "c"),
        ("dlog_INDPRO_pct", 100.0 * np.log(data["INDPRO"]).diff(), "c"),
        ("d_FEDFUNDS", data["FEDFUNDS"].diff(), "c"),
        ("d_UNRATE", data["UNRATE"].diff(), "c"),
    ]
    rows: list[dict] = []

    for variable, raw_series, regression in specifications:
        series = raw_series.dropna()

        adf = adfuller(series, regression=regression, autolag="AIC")
        rows.append(
            {
                "variable": variable,
                "test": "ADF",
                "deterministic_terms": regression,
                "statistic": float(adf[0]),
                "p_value": float(adf[1]),
                "lags": int(adf[2]),
                "nobs": int(adf[3]),
                "p_value_note": "",
                "null_hypothesis": "unit root",
            }
        )

        note = ""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            kpss_result = kpss(series, regression=regression, nlags="auto")
        warning_text = " ".join(str(item.message).lower() for item in caught)
        if "actual p-value is smaller" in warning_text:
            note = "Actual p-value is below the KPSS table range; interpret as <= 0.01."
        elif "actual p-value is greater" in warning_text:
            note = "Actual p-value is above the KPSS table range; interpret as >= 0.10."

        rows.append(
            {
                "variable": variable,
                "test": "KPSS",
                "deterministic_terms": regression,
                "statistic": float(kpss_result[0]),
                "p_value": float(kpss_result[1]),
                "lags": int(kpss_result[2]),
                "nobs": int(len(series)),
                "p_value_note": note,
                "null_hypothesis": "stationarity",
            }
        )

    return pd.DataFrame(rows)

def run_cointegration_tests(
    data: pd.DataFrame,
    stationarity_results: pd.DataFrame,
) -> pd.DataFrame:
    """Run Engle-Granger only when preliminary tests support I(1) in every series.

    The standard Engle-Granger procedure assumes the variables in the
    cointegrating relationship are I(1). If ADF and KPSS results do not
    jointly support that classification for every level series, the test is
    not run and the reason is recorded.
    """
    assessments: dict[str, str] = {}
    for variable in SERIES:
        level_rows = stationarity_results[
            (stationarity_results["variable"] == variable)
            & (stationarity_results["test"].isin(["ADF", "KPSS"]))
        ]
        adf_rows = level_rows[level_rows["test"] == "ADF"]
        kpss_rows = level_rows[level_rows["test"] == "KPSS"]
        if adf_rows.empty or kpss_rows.empty:
            assessments[variable] = "inconclusive"
            continue

        adf_p = float(adf_rows.iloc[0]["p_value"])
        kpss_p = float(kpss_rows.iloc[0]["p_value"])

        if adf_p >= 0.05 and kpss_p < 0.05:
            assessments[variable] = "I(1)-consistent"
        elif adf_p < 0.05 and kpss_p >= 0.05:
            assessments[variable] = "I(0)-consistent"
        elif adf_p < 0.05 and kpss_p < 0.05:
            assessments[variable] = "conflicting"
        else:
            assessments[variable] = "inconclusive"

    assessment_text = "; ".join(
        f"{variable}: {assessments[variable]}" for variable in SERIES
    )

    if not all(assessments[variable] == "I(1)-consistent" for variable in SERIES):
        return pd.DataFrame(
            [
                {
                    "test": "Engle-Granger",
                    "status": "not_run",
                    "reason": (
                        "The level-series ADF and KPSS results do not support "
                        "classifying all variables as I(1). The standard "
                        "Engle-Granger test is therefore not reported."
                    ),
                    "series_assessment": assessment_text,
                    "deterministic_terms": np.nan,
                    "statistic": np.nan,
                    "p_value": np.nan,
                    "critical_value_1pct": np.nan,
                    "critical_value_5pct": np.nan,
                    "critical_value_10pct": np.nan,
                    "nobs": int(len(data)),
                }
            ]
        )

    rows = []
    y = data["INDPRO"].to_numpy()
    x = data[["FEDFUNDS", "UNRATE"]].to_numpy()

    for trend in ("c", "ct"):
        statistic, p_value, critical_values = coint(
            y, x, trend=trend, autolag="aic"
        )
        rows.append(
            {
                "test": "Engle-Granger",
                "status": "run",
                "reason": "",
                "series_assessment": assessment_text,
                "deterministic_terms": trend,
                "statistic": float(statistic),
                "p_value": float(p_value),
                "critical_value_1pct": float(critical_values[0]),
                "critical_value_5pct": float(critical_values[1]),
                "critical_value_10pct": float(critical_values[2]),
                "nobs": int(len(data)),
            }
        )
    return pd.DataFrame(rows)


def compute_vif(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate VIFs for the two baseline regressors."""
    regressors = sm.add_constant(
        data[["FEDFUNDS", "UNRATE"]], has_constant="add"
    )
    values = regressors.to_numpy()
    return pd.DataFrame(
        [
            {
                "variable": variable,
                "vif": float(variance_inflation_factor(values, index)),
            }
            for index, variable in enumerate(regressors.columns)
            if variable != "const"
        ]
    )


def build_change_dataset(data: pd.DataFrame) -> pd.DataFrame:
    """Pair monthly industrial production growth with current and lagged rate changes."""
    frame = data.copy()
    frame["ip_growth_pct"] = 100.0 * np.log(frame["INDPRO"]).diff()
    frame["d_fedfunds"] = frame["FEDFUNDS"].diff()
    frame["d_unrate"] = frame["UNRATE"].diff()
    frame["d_fedfunds_l1"] = frame["d_fedfunds"].shift(1)
    frame["d_unrate_l1"] = frame["d_unrate"].shift(1)
    return frame.dropna()


def run_diagnostics(data: pd.DataFrame, output_dir: Path) -> dict:
    """Run diagnostics on the longest uninterrupted monthly complete-case segment."""
    output_dir = Path(output_dir)
    tables = output_dir / "tables"
    figures = output_dir / "figures"
    diagnostics = output_dir / "diagnostics"
    for directory in (tables, figures, diagnostics):
        directory.mkdir(parents=True, exist_ok=True)

    segments = contiguous_complete_segments(data)
    contiguous = longest_contiguous_segment(data)
    if len(contiguous) < 50:
        raise ValueError("The longest uninterrupted sample is too short for time-series diagnostics.")

    # Use the same consecutive months for the HC1 and Newey–West comparison.
    levels_ols = smf.ols(
        "INDPRO ~ FEDFUNDS + UNRATE", data=contiguous
    ).fit()
    levels_hc1 = levels_ols.get_robustcov_results(cov_type="HC1")
    levels_hac = levels_ols.get_robustcov_results(
        cov_type="HAC", maxlags=12, use_correction=True
    )

    inference_rows = []
    for label, result, covariance in (
        ("all_complete_observations_HC1", smf.ols(
            "INDPRO ~ FEDFUNDS + UNRATE", data=data.dropna()
        ).fit(cov_type="HC1"), "HC1"),
        ("longest_contiguous_segment_HC1", levels_hc1, "HC1"),
        ("longest_contiguous_segment_HAC12", levels_hac, "HAC(12)"),
    ):
        table = coefficient_table(result, covariance)
        table.insert(0, "sample", label)
        inference_rows.append(table)
    pd.concat(inference_rows, ignore_index=True).to_csv(
        tables / "inference_comparison.csv", index=False
    )

    rainbow_stat, rainbow_p = sm.stats.linear_rainbow(levels_ols)
    bp_lm, bp_lm_p, bp_f, bp_f_p = het_breuschpagan(
        levels_ols.resid, levels_ols.model.exog
    )
    dw = sm.stats.stattools.durbin_watson(levels_ols.resid)
    diagnostics_table = pd.DataFrame(
        [
            {"test": "Rainbow linearity", "statistic": rainbow_stat, "p_value": rainbow_p},
            {"test": "Breusch-Pagan LM", "statistic": bp_lm, "p_value": bp_lm_p},
            {"test": "Breusch-Pagan F", "statistic": bp_f, "p_value": bp_f_p},
            {"test": "Durbin-Watson", "statistic": dw, "p_value": np.nan},
        ]
    )
    diagnostics_table.to_csv(tables / "diagnostic_tests.csv", index=False)

    ljung_box = acorr_ljungbox(
        levels_ols.resid, lags=[6, 12], return_df=True
    )
    ljung_box.index.name = "lag"
    ljung_box.to_csv(tables / "ljung_box_tests.csv")
    compute_vif(contiguous).to_csv(
        tables / "variance_inflation_factors.csv", index=False
    )

    stationarity = run_stationarity_tests(contiguous)
    stationarity.to_csv(tables / "stationarity_tests.csv", index=False)
    cointegration = run_cointegration_tests(contiguous, stationarity)
    cointegration.to_csv(tables / "cointegration_test_decision.csv", index=False)

    change_data = build_change_dataset(contiguous)
    change_formula = (
        "ip_growth_pct ~ d_fedfunds + d_unrate + "
        "d_fedfunds_l1 + d_unrate_l1"
    )
    change_ols = smf.ols(change_formula, data=change_data).fit()
    change_hac = change_ols.get_robustcov_results(
        cov_type="HAC", maxlags=12, use_correction=True
    )
    coefficient_table(change_hac, "HAC(12)").to_csv(
        tables / "changes_model_coefficients_hac12.csv", index=False
    )
    (diagnostics / "changes_model_hac12_summary.txt").write_text(
        stable_summary_text(change_hac.summary().as_text()), encoding="utf-8"
    )
    (diagnostics / "contiguous_levels_hac12_summary.txt").write_text(
        stable_summary_text(levels_hac.summary().as_text()), encoding="utf-8"
    )

    segment_rows = [
        {
            "segment": number,
            "n": int(len(segment)),
            "start": segment.index.min().strftime("%Y-%m"),
            "end": segment.index.max().strftime("%Y-%m"),
        }
        for number, segment in enumerate(segments, start=1)
    ]
    pd.DataFrame(segment_rows).to_csv(
        tables / "complete_monthly_segments.csv", index=False
    )

    fig = sm.graphics.plot_partregress(
        endog="INDPRO",
        exog_i="FEDFUNDS",
        exog_others=["UNRATE"],
        data=contiguous,
        obs_labels=False,
    )
    fig.set_size_inches(8, 5)
    fig.tight_layout()
    fig.savefig(figures / "partial_regression_fedfunds.png", dpi=180)
    plt.close(fig)

    return {
        "diagnostic_sample_n": int(len(contiguous)),
        "diagnostic_sample_start": contiguous.index.min().strftime("%Y-%m"),
        "diagnostic_sample_end": contiguous.index.max().strftime("%Y-%m"),
        "changes_model_n": int(len(change_data)),
        "changes_model_r_squared": float(change_ols.rsquared),
        "cointegration_test_status": str(cointegration.iloc[0]["status"]),
    }
