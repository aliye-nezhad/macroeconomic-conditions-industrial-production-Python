"""Reproduce the industrial production results from the saved FRED data."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "code"
sys.path.insert(0, str(CODE))

from macro_regression_workflow import (  # noqa: E402
    build_manifest,
    estimate_baseline_model,
    load_snapshot,
    save_baseline_outputs,
    sha256_file,
)
from diagnostic_workflow import run_diagnostics  # noqa: E402

EXPECTED_OUTPUTS = (
    "tables/descriptive_statistics.csv",
    "tables/correlation_matrix.csv",
    "tables/fitted_values.csv",
    "tables/baseline_coefficients.csv",
    "tables/baseline_regression_summary.txt",
    "tables/missing_data_report.csv",
    "tables/inference_comparison.csv",
    "tables/diagnostic_tests.csv",
    "tables/ljung_box_tests.csv",
    "tables/variance_inflation_factors.csv",
    "tables/stationarity_tests.csv",
    "tables/cointegration_test_decision.csv",
    "tables/changes_model_coefficients_hac12.csv",
    "tables/complete_monthly_segments.csv",
    "figures/macro_series.png",
    "figures/actual_vs_fitted.png",
    "figures/partial_regression_fedfunds.png",
    "diagnostics/changes_model_hac12_summary.txt",
    "diagnostics/contiguous_levels_hac12_summary.txt",
    "diagnostics/reproducibility_manifest.json",
)


def validate_outputs(output_dir: Path, data_path: Path) -> None:
    """Fail if an expected output is missing, empty, or malformed."""
    missing_or_empty = [
        relative for relative in EXPECTED_OUTPUTS
        if not (output_dir / relative).is_file()
        or (output_dir / relative).stat().st_size == 0
    ]
    if missing_or_empty:
        raise RuntimeError(
            "Replication completed with missing/empty outputs:\n"
            + "\n".join(f"- {item}" for item in missing_or_empty)
        )

    import numpy as np
    import pandas as pd

    fitted = pd.read_csv(output_dir / "tables/fitted_values.csv")
    if fitted.empty or fitted[["INDPRO_actual", "INDPRO_fitted", "residual"]].isna().any().any():
        raise RuntimeError("Fitted-values output failed numeric validation.")

    manifest = json.loads(
        (output_dir / "diagnostics/reproducibility_manifest.json").read_text(encoding="utf-8")
    )
    if manifest.get("input_sha256") != sha256_file(data_path):
        raise RuntimeError("Reproducibility manifest hash does not match the input data.")
    if len(fitted) != int(manifest.get("complete_case_observations", -1)):
        raise RuntimeError("Fitted-values row count does not match the manifest sample size.")

    cointegration = pd.read_csv(output_dir / "tables/cointegration_test_decision.csv")
    if cointegration.empty or cointegration.iloc[0].get("status") not in {"run", "not_run"}:
        raise RuntimeError("Cointegration test decision is missing or invalid.")

    coefficients = pd.read_csv(output_dir / "tables/baseline_coefficients.csv")
    if not {"term", "coefficient", "standard_error", "p_value"}.issubset(coefficients.columns):
        raise RuntimeError("Baseline coefficient table is missing required columns.")
    numeric = coefficients[["coefficient", "standard_error", "p_value"]].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise RuntimeError("Baseline coefficient table contains non-finite values.")


def run(data_path: Path, output_dir: Path, run_tests: bool = True) -> None:
    """Fit the models and write the tables, figures, and diagnostics."""
    data_path = data_path.resolve()
    output_dir = output_dir.resolve()

    if not data_path.is_file():
        raise FileNotFoundError(f"Input snapshot does not exist: {data_path}")

    if run_tests:
        print("Running unit tests...", flush=True)
        subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-v"],
            cwd=ROOT,
            check=True,
        )

    # Protect the project directory before replacing the result folders.
    if output_dir == ROOT or output_dir in ROOT.parents:
        raise ValueError("--output-dir cannot be the project root or one of its parent directories.")
    output_dir.mkdir(parents=True, exist_ok=True)
    for folder in ("tables", "figures", "diagnostics"):
        generated_folder = output_dir / folder
        if generated_folder.exists():
            shutil.rmtree(generated_folder)
        generated_folder.mkdir(parents=True, exist_ok=True)

    print(f"Reading {data_path.name}", flush=True)
    data = load_snapshot(data_path)
    complete = data.dropna()
    print(
        f"Monthly rows: {len(data)} | complete observations: {len(complete)}",
        flush=True,
    )

    print("Estimating the levels regression...", flush=True)
    baseline = estimate_baseline_model(data)
    save_baseline_outputs(data, baseline, output_dir)

    print("Running diagnostics and estimating the monthly-change model...", flush=True)
    diagnostic_info = run_diagnostics(data, output_dir)
    manifest = build_manifest(data_path, data, output_dir)
    manifest["diagnostic_sample"] = diagnostic_info
    (output_dir / "diagnostics/reproducibility_manifest.json").write_text(
        __import__("json").dumps(manifest, indent=2),
        encoding="utf-8",
    )

    validate_outputs(output_dir, data_path)
    print(
        f"SUCCESS: checked {len(EXPECTED_OUTPUTS)} result files.",
        flush=True,
    )
    print(
        f"Levels model: {int(baseline.nobs)} months, R-squared {baseline.rsquared:.4f}. "
        f"Diagnostic sample: {diagnostic_info['diagnostic_sample_n']} consecutive months.",
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Estimate the industrial production models from a saved FRED CSV."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "data/raw/fred_snapshot.csv",
        help="FRED CSV file (defaults to the copy in data/raw).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "outputs",
        help="Directory for tables, figures, and diagnostics.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Run the analysis without the unit tests.",
    )
    args = parser.parse_args()
    run(args.data, args.output_dir, run_tests=not args.skip_tests)


if __name__ == "__main__":
    main()
