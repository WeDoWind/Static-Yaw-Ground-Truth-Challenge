#!/usr/bin/env python3
"""Structural validation for a Static Yaw challenge submission.

Runs in the PUBLIC repo's PR workflow, so it has NO access to the ground-truth
labels. It can only check that a submission is well-formed; the actual score is
computed later, after merge, by the private evaluation repo.

Two kinds of submission, distinguished by the filename suffix:
  - Results_NN_x.csv     (x = submission number)  -> PUBLIC  test split (pub_)
  - Results_NN_final.csv (the final submission)   -> PRIVATE test split (priv_)

A valid submission file:
  - is named Results_NN_x.csv or Results_NN_final.csv
  - has exactly the header: row_id,yaw_offset
  - has exactly the split's row count
  - contains every row_id of that split exactly once (contiguous, 0-based)
  - has a finite float yaw_offset on every row (no NaN/empty/inf)

Usage:
    python validate_submission.py path/to/Results_NN_x.csv
Exit code 0 = valid, 1 = invalid (reasons printed to stderr).
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# --- Test-set shapes (NOT secret: row_ids ship with the test data) ---
SPLITS = {
    "public": {"prefix": "pub_", "n": 1_064_641, "width": 8},
    "private": {"prefix": "priv_", "n": 3_627_380, "width": 8},
}
FILENAME_RE = re.compile(r"^Results_(\d+)_(\d+|final)\.csv$")


def split_for(suffix: str) -> str:
    """'final' -> private split; a number -> public split."""
    return "private" if suffix == "final" else "public"


def fail(msg: str) -> None:
    print(f"::error::{msg}", file=sys.stderr)


def validate(path: Path) -> list[str]:
    errors: list[str] = []

    m = FILENAME_RE.match(path.name)
    if not m:
        errors.append(
            f"Filename '{path.name}' must match Results_NN_x.csv or "
            "Results_NN_final.csv (NN = participant id, x = submission number)."
        )
        # We can't know which split to check against; stop here.
        return errors

    cfg = SPLITS[split_for(m.group(2))]
    n, prefix, width = cfg["n"], cfg["prefix"], cfg["width"]

    try:
        df = pd.read_csv(path, dtype={"row_id": str})
    except Exception as e:  # noqa: BLE001
        errors.append(f"Could not parse CSV: {e}")
        return errors

    if list(df.columns) != ["row_id", "yaw_offset"]:
        errors.append(
            f"Header must be exactly 'row_id,yaw_offset'; got {list(df.columns)}."
        )
        return errors

    if len(df) != n:
        errors.append(f"Expected {n:,} data rows for this split; found {len(df):,}.")

    if df["row_id"].duplicated().any():
        dups = df["row_id"][df["row_id"].duplicated()].unique()[:5]
        errors.append(f"Duplicate row_id values (e.g. {list(dups)}).")
    expected = {f"{prefix}{i:0{width}d}" for i in range(n)}
    actual = set(df["row_id"])
    if actual != expected:
        missing = sorted(expected - actual)[:5]
        extra = sorted(actual - expected)[:5]
        if missing:
            errors.append(f"Missing required row_id(s), e.g. {missing}.")
        if extra:
            errors.append(f"Unexpected row_id(s), e.g. {extra} (wrong test split?).")

    yaw = pd.to_numeric(df["yaw_offset"], errors="coerce")
    n_bad = int(yaw.isna().sum())
    if n_bad:
        errors.append(f"{n_bad} yaw_offset value(s) are empty or non-numeric.")
    finite = np.isfinite(yaw.to_numpy(dtype=float))
    if not finite.all():
        errors.append(f"{int((~finite).sum())} yaw_offset value(s) are NaN or infinite.")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        fail("usage: validate_submission.py <Results_NN_x.csv>")
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        fail(f"File not found: {path}")
        return 1

    errors = validate(path)
    if errors:
        fail(f"{path.name} is INVALID:")
        for e in errors:
            fail(f"  - {e}")
        return 1
    print(f"✅ {path.name} is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
