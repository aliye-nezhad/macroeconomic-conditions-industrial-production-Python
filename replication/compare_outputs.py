"""Compare regenerated outputs with committed reference results.

CSV numeric values are compared within tight floating-point tolerances.
Figures are compared as decoded pixels, not compressed PNG bytes.
Text and JSON outputs must match exactly.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

from run_all import EXPECTED_OUTPUTS

NUMERIC_RTOL = 1e-9
NUMERIC_ATOL = 1e-14
PIXEL_ATOL = 1


def compare_csv(reference_path: Path, generated_path: Path) -> None:
    reference = pd.read_csv(reference_path)
    generated = pd.read_csv(generated_path)

    if reference.shape != generated.shape:
        raise AssertionError(
            f"CSV shape differs: reference={reference.shape}, generated={generated.shape}"
        )
    if list(reference.columns) != list(generated.columns):
        raise AssertionError("CSV column names or order differ.")

    for column in reference.columns:
        reference_values = reference[column]
        generated_values = generated[column]
        reference_numeric = pd.api.types.is_numeric_dtype(reference_values)
        generated_numeric = pd.api.types.is_numeric_dtype(generated_values)

        if reference_numeric and generated_numeric:
            left = reference_values.to_numpy(dtype=float)
            right = generated_values.to_numpy(dtype=float)
            if not np.allclose(
                left,
                right,
                rtol=NUMERIC_RTOL,
                atol=NUMERIC_ATOL,
                equal_nan=True,
            ):
                difference = np.abs(left - right)
                finite = difference[np.isfinite(difference)]
                maximum = float(finite.max()) if finite.size else float("nan")
                raise AssertionError(
                    f"Numeric values differ in column {column!r}; "
                    f"maximum absolute difference={maximum:.6g}."
                )
        elif not reference_values.equals(generated_values):
            raise AssertionError(f"Non-numeric values differ in column {column!r}.")


def compare_png(reference_path: Path, generated_path: Path) -> None:
    with Image.open(reference_path) as reference_image:
        reference = np.asarray(reference_image.convert("RGB"), dtype=np.int16)
    with Image.open(generated_path) as generated_image:
        generated = np.asarray(generated_image.convert("RGB"), dtype=np.int16)

    if reference.shape != generated.shape:
        raise AssertionError(
            f"Image dimensions differ: reference={reference.shape}, generated={generated.shape}"
        )

    maximum_difference = int(np.abs(reference - generated).max(initial=0))
    if maximum_difference > PIXEL_ATOL:
        raise AssertionError(
            f"Image pixels differ by up to {maximum_difference} intensity levels "
            f"(allowed: {PIXEL_ATOL})."
        )


def compare_outputs(reference_dir: Path, generated_dir: Path) -> None:
    failures: list[str] = []

    for relative in EXPECTED_OUTPUTS:
        reference_path = reference_dir / relative
        generated_path = generated_dir / relative

        if not reference_path.is_file():
            failures.append(f"Reference output is missing: {relative}")
            continue
        if not generated_path.is_file():
            failures.append(f"Generated output is missing: {relative}")
            continue

        try:
            if relative.endswith(".csv"):
                compare_csv(reference_path, generated_path)
            elif relative.endswith(".png"):
                compare_png(reference_path, generated_path)
            elif reference_path.read_bytes() != generated_path.read_bytes():
                raise AssertionError("File content differs.")
        except Exception as error:
            failures.append(f"{relative}: {error}")
        else:
            print(f"PASS {relative}")

    if failures:
        raise SystemExit(
            "Reference-output comparison failed:\n"
            + "\n".join(f"- {failure}" for failure in failures)
        )

    print(
        f"SUCCESS: all {len(EXPECTED_OUTPUTS)} outputs match their committed "
        "references within the documented comparison rules."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare regenerated outputs with committed reference results."
    )
    parser.add_argument(
        "--reference-dir",
        type=Path,
        required=True,
        help="Directory containing the saved reference outputs.",
    )
    parser.add_argument(
        "--generated-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "outputs",
        help="Directory containing the newly generated outputs.",
    )
    args = parser.parse_args()
    compare_outputs(args.reference_dir.resolve(), args.generated_dir.resolve())


if __name__ == "__main__":
    main()
