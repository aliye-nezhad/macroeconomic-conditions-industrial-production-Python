"""Prepare the monthly FRED data and estimate the baseline regression."""

from __future__ import annotations

import hashlib
import json
import logging
import platform
import re
import warnings
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels
import scipy
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import RegressionResultsWrapper

LOGGER = logging.getLogger(__name__)

SERIES: tuple[str, ...] = ("INDPRO", "FEDFUNDS", "UNRATE")
START_DATE = "1990-01-01"
BASELINE_FORMULA = "INDPRO ~ FEDFUNDS + UNRATE"
MIN_OBSERVATIONS = 30


class DataValidationError(ValueError):
    """Raised when the input is unsuitable for the monthly regression."""


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_summary_text(summary_text: str) -> str:
    """Leave out the run date and time while keeping the model statistics."""
    return re.sub(
        r"^(?:Date|Time):[^\n]*?(?= +(?:Prob \(F-statistic\)|Log-Likelihood):)",
        lambda prefix: " " * len(prefix[0]),
        summary_text,
        flags=re.MULTILINE,
    )


def load_snapshot(path: Path, start_date: str = START_DATE) -> pd.DataFrame:
    """Load a FRED CSV snapshot with an explicit observation-date column."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Data snapshot not found: {path}")

    frame = pd.read_csv(path)
    date_column = next(
        (column for column in ("observation_date", "DATE", "date") if column in frame.columns),
        None,
    )
    if date_column is None:
        raise DataValidationError(
            "The CSV must contain an observation_date, DATE, or date column."
        )

    frame[date_column] = pd.to_datetime(frame[date_column], errors="raise")
    frame = frame.set_index(date_column)
    return prepare_monthly_data(frame, start_date=start_date)


def prepare_monthly_data(
    raw_data: pd.DataFrame,
    start_date: str = START_DATE,
) -> pd.DataFrame:
    """Align the series to a monthly calendar so gaps remain visible."""
    if raw_data.empty:
        raise DataValidationError("The input data set is empty.")

    missing_columns = sorted(set(SERIES) - set(raw_data.columns))
    if missing_columns:
        raise DataValidationError(f"Missing required series: {missing_columns}")

    data = raw_data.loc[:, list(SERIES)].copy()
    dates = pd.to_datetime(data.index, errors="raise")
    data.index = dates.to_period("M").to_timestamp(how="start")
    data.index.name = "observation_date"

    if data.index.has_duplicates:
        duplicates = data.index[data.index.duplicated()].strftime("%Y-%m").tolist()
        raise DataValidationError(f"Duplicate monthly observations: {duplicates}")

    data = data.apply(pd.to_numeric, errors="coerce").sort_index()
    data = data.loc[pd.Timestamp(start_date):]

    if data.empty:
        raise DataValidationError(f"No observations remain from {start_date} onward.")

    full_index = pd.date_range(data.index.min(), data.index.max(), freq="MS")
    data = data.reindex(full_index)
    data.index.name = "observation_date"

    if data.dropna(how="all").empty:
        raise DataValidationError("All observations are missing after date alignment.")

    complete = data.dropna()
    if len(complete) < MIN_OBSERVATIONS:
        raise DataValidationError(
            f"Only {len(complete)} complete observations remain; "
            f"at least {MIN_OBSERVATIONS} are required."
        )

    if (complete["INDPRO"] <= 0).any():
        raise DataValidationError("INDPRO must be strictly positive for log transformations.")

    return data


def contiguous_complete_segments(data: pd.DataFrame) -> list[pd.DataFrame]:
    """Split complete observations into uninterrupted monthly segments."""
    complete = data.dropna().sort_index()
    if complete.empty:
        return []

    month_number = complete.index.year * 12 + complete.index.month
    split_points = np.where(np.diff(month_number) != 1)[0] + 1
    boundaries = np.r_[0, split_points, len(complete)]
    return [
        complete.iloc[boundaries[i]:boundaries[i + 1]].copy()
        for i in range(len(boundaries) - 1)
    ]


def longest_contiguous_segment(data: pd.DataFrame) -> pd.DataFrame:
    """Return the longest uninterrupted complete monthly segment."""
    segments = contiguous_complete_segments(data)
    if not segments:
        raise DataValidationError("No uninterrupted complete monthly segment exists.")
    return max(segments, key=len)


def missing_observation_report(data: pd.DataFrame) -> pd.DataFrame:
    """Describe months with one or more missing series."""
    missing = data.loc[data.isna().any(axis=1)].copy()
    if missing.empty:
        return pd.DataFrame(columns=["date", "missing_series", "missing_count"])
    return pd.DataFrame(
        {
            "date": missing.index.strftime("%Y-%m-%d"),
            "missing_series": [
                ";".join(column for column in SERIES if pd.isna(row[column]))
                for _, row in missing.iterrows()
            ],
            "missing_count": missing.isna().sum(axis=1).to_numpy(),
        }
    )


def estimate_baseline_model(data: pd.DataFrame) -> RegressionResultsWrapper:
    """Fit the levels regression by OLS with HC1 standard errors."""
    complete = data.dropna()
    if len(complete) < MIN_OBSERVATIONS:
        raise DataValidationError("Insufficient complete observations for baseline OLS.")
    return smf.ols(BASELINE_FORMULA, data=complete).fit(cov_type="HC1")


def coefficient_table(result, covariance_label: str) -> pd.DataFrame:
    """Build a consistent coefficient table from a statsmodels result."""
    confidence = np.asarray(result.conf_int())
    parameter_names = (
        list(result.params.index)
        if hasattr(result.params, "index")
        else list(result.model.exog_names)
    )
    return pd.DataFrame(
        {
            "term": parameter_names,
            "coefficient": np.asarray(result.params),
            "standard_error": np.asarray(result.bse),
            "p_value": np.asarray(result.pvalues),
            "ci_lower": confidence[:, 0],
            "ci_upper": confidence[:, 1],
            "covariance": covariance_label,
        }
    )


def build_fitted_values(
    data: pd.DataFrame,
    model: RegressionResultsWrapper,
) -> pd.DataFrame:
    """Return actual, fitted, and residual values with their original dates."""
    fitted = pd.DataFrame(index=data.index)
    fitted.index.name = "observation_date"
    fitted["INDPRO_actual"] = data["INDPRO"]
    fitted["INDPRO_fitted"] = model.fittedvalues
    fitted["residual"] = model.resid
    return fitted


def save_baseline_outputs(
    data: pd.DataFrame,
    model: RegressionResultsWrapper,
    output_dir: Path,
) -> None:
    """Save baseline descriptive statistics, coefficients, fitted values, and plots."""
    tables = output_dir / "tables"
    figures = output_dir / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    complete = data.dropna()
    complete.describe().T.to_csv(tables / "descriptive_statistics.csv")
    complete.corr().to_csv(tables / "correlation_matrix.csv")
    build_fitted_values(complete, model).to_csv(tables / "fitted_values.csv")
    coefficient_table(model, "HC1").to_csv(tables / "baseline_coefficients.csv", index=False)
    (tables / "baseline_regression_summary.txt").write_text(
        stable_summary_text(model.summary().as_text()), encoding="utf-8"
    )

    missing_observation_report(data).to_csv(
        tables / "missing_data_report.csv", index=False
    )

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    for axis, variable in zip(axes, SERIES):
        axis.plot(data.index, data[variable], linewidth=1.0)
        axis.set_ylabel(variable)
        axis.grid(True, alpha=0.25)
    axes[-1].set_xlabel("Month")
    fig.suptitle("US Macroeconomic Series (FRED snapshot)")
    fig.tight_layout()
    fig.savefig(figures / "macro_series.png", dpi=180)
    plt.close(fig)

    fitted = build_fitted_values(complete, model)
    fig, axis = plt.subplots(figsize=(10, 5))
    axis.plot(fitted.index, fitted["INDPRO_actual"], label="Actual INDPRO", linewidth=1.1)
    axis.plot(fitted.index, fitted["INDPRO_fitted"], label="Fitted INDPRO", linewidth=1.1)
    axis.set_title("Descriptive Levels OLS: Actual vs. Fitted")
    axis.set_xlabel("Month")
    axis.set_ylabel("Industrial production index")
    axis.grid(True, alpha=0.25)
    axis.legend()
    fig.tight_layout()
    fig.savefig(figures / "actual_vs_fitted.png", dpi=180)
    plt.close(fig)


def build_manifest(
    snapshot_path: Path,
    data: pd.DataFrame,
    output_dir: Path,
    source_label: str = "FRED CSV snapshot included with the repository",
) -> dict:
    """Record the input file, sample dates, and software versions."""
    segments = contiguous_complete_segments(data)
    complete = data.dropna()
    snapshot_path = Path(snapshot_path).resolve()
    project_root = Path(__file__).resolve().parents[1]
    try:
        input_label = snapshot_path.relative_to(project_root).as_posix()
    except ValueError:
        input_label = snapshot_path.name
    manifest = {
        "project": "Macroeconomic Conditions and Industrial Production",
        "project_version": "1.0.2",
        "input_source": source_label,
        "input_file": input_label,
        "input_sha256": sha256_file(snapshot_path),
        "baseline_formula": BASELINE_FORMULA,
        "analysis_start": START_DATE,
        "snapshot_first_month": data.index.min().strftime("%Y-%m"),
        "snapshot_last_month": data.index.max().strftime("%Y-%m"),
        "complete_case_observations": int(len(complete)),
        "complete_case_first_month": complete.index.min().strftime("%Y-%m"),
        "complete_case_last_month": complete.index.max().strftime("%Y-%m"),
        "missing_months": data.index[data.isna().any(axis=1)].strftime("%Y-%m").tolist(),
        "contiguous_complete_segments": [
            {
                "n": int(len(segment)),
                "start": segment.index.min().strftime("%Y-%m"),
                "end": segment.index.max().strftime("%Y-%m"),
            }
            for segment in segments
        ],
        "python_version": platform.python_version(),
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
        "statsmodels_version": statsmodels.__version__,
        "scipy_version": scipy.__version__,
        "matplotlib_version": matplotlib.__version__,
        "reproduction_mode": "offline; frozen input snapshot",
    }
    destination = output_dir / "diagnostics" / "reproducibility_manifest.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
