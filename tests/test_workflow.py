"""Tests for monthly data preparation and regression diagnostics."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from macro_regression_workflow import (  # noqa: E402
    DataValidationError,
    coefficient_table,
    contiguous_complete_segments,
    estimate_baseline_model,
    load_snapshot,
    longest_contiguous_segment,
    prepare_monthly_data,
    sha256_file,
    stable_summary_text,
)
from diagnostic_workflow import build_change_dataset, run_cointegration_tests  # noqa: E402
import statsmodels.formula.api as smf  # noqa: E402


class DataContractTests(unittest.TestCase):
    def setUp(self) -> None:
        index = pd.date_range("2000-01-01", periods=60, freq="MS")
        self.frame = pd.DataFrame(
            {
                "INDPRO": np.linspace(80, 100, 60),
                "FEDFUNDS": np.linspace(5, 2, 60),
                "UNRATE": np.linspace(4, 6, 60),
            },
            index=index,
        )

    def test_prepare_preserves_missing_month_as_explicit_nan(self) -> None:
        broken = self.frame.drop(pd.Timestamp("2002-06-01"))
        prepared = prepare_monthly_data(broken)
        self.assertEqual(len(prepared), 60)
        self.assertTrue(pd.isna(prepared.loc["2002-06-01", "INDPRO"]))

    def test_contiguous_segments_split_at_missing_month(self) -> None:
        broken = self.frame.drop(pd.Timestamp("2002-06-01"))
        prepared = prepare_monthly_data(broken)
        segments = contiguous_complete_segments(prepared)
        self.assertEqual([len(segment) for segment in segments], [29, 30])
        self.assertEqual(len(longest_contiguous_segment(prepared)), 30)

    def test_duplicate_months_are_rejected(self) -> None:
        broken = pd.concat([self.frame, self.frame.iloc[[0]]])
        with self.assertRaises(DataValidationError):
            prepare_monthly_data(broken)

    def test_nonpositive_indpro_is_rejected(self) -> None:
        broken = self.frame.copy()
        broken.iloc[0, 0] = 0
        with self.assertRaises(DataValidationError):
            prepare_monthly_data(broken)

    def test_change_dataset_has_expected_lags_and_no_missing_values(self) -> None:
        result = build_change_dataset(self.frame)
        self.assertEqual(len(result), 58)
        self.assertFalse(result.isna().any().any())
        self.assertIn("ip_growth_pct", result.columns)
        self.assertIn("d_fedfunds_l1", result.columns)

    def test_coefficient_table_supports_numpy_backed_robust_results(self) -> None:
        model = smf.ols(
            "INDPRO ~ FEDFUNDS + UNRATE", data=self.frame
        ).fit()
        robust = model.get_robustcov_results(cov_type="HAC", maxlags=2)
        table = coefficient_table(robust, "HAC(2)")
        self.assertEqual(
            table["term"].tolist(),
            ["Intercept", "FEDFUNDS", "UNRATE"],
        )
        self.assertTrue(np.isfinite(table["coefficient"]).all())

    def test_cointegration_is_not_run_when_level_series_are_not_all_i1(self) -> None:
        stationarity = pd.DataFrame(
            [
                {"variable": "INDPRO", "test": "ADF", "p_value": 0.80},
                {"variable": "INDPRO", "test": "KPSS", "p_value": 0.01},
                {"variable": "FEDFUNDS", "test": "ADF", "p_value": 0.01},
                {"variable": "FEDFUNDS", "test": "KPSS", "p_value": 0.01},
                {"variable": "UNRATE", "test": "ADF", "p_value": 0.03},
                {"variable": "UNRATE", "test": "KPSS", "p_value": 0.10},
            ]
        )
        result = run_cointegration_tests(self.frame, stationarity)
        self.assertEqual(result.iloc[0]["status"], "not_run")
        self.assertIn("FEDFUNDS: conflicting", result.iloc[0]["series_assessment"])
        self.assertIn("UNRATE: I(0)-consistent", result.iloc[0]["series_assessment"])

    def test_bundled_snapshot_loads_and_has_regular_monthly_index(self) -> None:
        snapshot = ROOT / "data/raw/fred_snapshot.csv"
        loaded = load_snapshot(snapshot)
        self.assertEqual(len(loaded), 442)
        self.assertEqual(len(loaded.dropna()), 438)
        self.assertTrue(loaded.index.is_monotonic_increasing)
        self.assertFalse(loaded.index.has_duplicates)
        self.assertEqual(loaded.index[0], pd.Timestamp("1990-01-01"))
        self.assertEqual(loaded.index[-1], pd.Timestamp("2026-10-01"))

    def test_bundled_snapshot_matches_checksum_and_documented_results(self) -> None:
        snapshot = ROOT / "data/raw/fred_snapshot.csv"
        expected_hash = (ROOT / "data/raw.sha256").read_text(encoding="utf-8").split()[0]
        self.assertEqual(sha256_file(snapshot), expected_hash)

        loaded = load_snapshot(snapshot)
        segments = contiguous_complete_segments(loaded)
        self.assertEqual([len(segment) for segment in segments], [429, 9])

        baseline = estimate_baseline_model(loaded)
        self.assertEqual(int(baseline.nobs), 438)
        self.assertAlmostEqual(float(baseline.rsquared), 0.5721, places=4)

    def test_stable_summary_removes_runtime_fields_but_preserves_statistics(self) -> None:
        summary = (
            "Date: Fri Nov 13 2026   Prob (F-statistic): 1.23e-45\n"
            "Time: 05:19:56   Log-Likelihood: -123.456\n"
        )
        stable = stable_summary_text(summary)
        self.assertNotIn("Fri Nov 13 2026", stable)
        self.assertNotIn("05:19:56", stable)
        self.assertIn("Prob (F-statistic): 1.23e-45", stable)
        self.assertIn("Log-Likelihood: -123.456", stable)


if __name__ == "__main__":
    unittest.main()
