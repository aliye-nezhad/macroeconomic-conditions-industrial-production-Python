"""Optional helper to create a new FRED snapshot; never used by the default run."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas_datareader.data as web

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a fresh FRED snapshot.")
    parser.add_argument("--start", default="1990-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/raw/fred_snapshot_new.csv",
        help="Output CSV path. The frozen default snapshot is never overwritten.",
    )
    args = parser.parse_args()

    frame = web.DataReader(
        ["INDPRO", "FEDFUNDS", "UNRATE"],
        "fred",
        args.start,
        args.end,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index_label="observation_date")
    print(f"Saved {len(frame)} rows to {args.output}")
    print("Review the new snapshot and its SHA-256 before replacing the frozen input.")


if __name__ == "__main__":
    main()
