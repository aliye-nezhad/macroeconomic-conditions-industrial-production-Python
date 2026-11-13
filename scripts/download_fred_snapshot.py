"""Save a new copy of the three monthly FRED series."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas_datareader.data as web

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the three monthly series from FRED.")
    parser.add_argument("--start", default="1990-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/raw/fred_snapshot_new.csv",
        help="CSV path (defaults to data/raw/fred_snapshot_new.csv).",
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


if __name__ == "__main__":
    main()
