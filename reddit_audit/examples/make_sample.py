"""
make_sample.py — Build a SAMPLE workbook from SYNTHETIC fixtures.

⚠️  The rows in the produced workbook are HAND-WRITTEN, INVENTED examples — NOT
real Reddit data. Their only purpose is to show what the 9-tab output looks like
once populated. Do NOT use this file for any analysis or decision. Real output
comes only from running collect.py against Reddit.

Run:  python reddit_audit/examples/make_sample.py
Writes: reddit_audit/examples/SAMPLE_workbook_synthetic.xlsx
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import pandas as pd  # noqa: E402
import classify, build_dataset, config  # noqa: E402
from tests.test_pipeline import FIXTURES  # reuse the same invented fixtures  # noqa: E402


def main():
    rows = [classify.classify_observation(f, i + 1) for i, f in enumerate(FIXTURES)]
    df = pd.DataFrame(rows)
    for c in classify.MASTER_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    # redirect the workbook writer to the examples dir
    out = HERE / "SAMPLE_workbook_synthetic.xlsx"
    config.MASTER_XLSX = out
    build_dataset.write_workbook(df)
    print(f"Sample (SYNTHETIC data) written to {out}")


if __name__ == "__main__":
    main()
