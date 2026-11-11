"""Unit tests for data contracts and time-index handling."""

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
    load_snapshot,
    longest_contiguous_segment,
    prepare_monthly_data,
)
from diagnostic_workflow import build_change_dataset  # noqa: E402
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

    def test_bundled_snapshot_loads_and_has_regular_monthly_index(self) -> None:
        snapshot = ROOT / "data/raw/fred_snapshot.csv"
        loaded = load_snapshot(snapshot)
        self.assertGreater(len(loaded.dropna()), 400)
        self.assertTrue(loaded.index.is_monotonic_increasing)
        self.assertFalse(loaded.index.has_duplicates)


if __name__ == "__main__":
    unittest.main()
