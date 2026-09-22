#!/usr/bin/env python3

from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE = Path("scripts/Harvard-EEG-Database-Tools")

FILE = BASE / "HEEDB_ICD10_for_Neurology_statistics.xlsx"

OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUTPUT_DIR / "HEEDB_disease_statistics_summary.txt"


# ============================================================
# CHECK FILE
# ============================================================

if not FILE.exists():
    raise FileNotFoundError(
        f"\nERROR: File not found:\n{FILE}\n"
    )

print("\n============================================================")
print("HEEDB DISEASE / ICD-10 STATISTICS INSPECTION")
print("============================================================")

print(f"\nInput file:\n{FILE}")


# ============================================================
# INSPECT EXCEL WORKBOOK
# ============================================================

xls = pd.ExcelFile(FILE)

print("\nSheets found:")
for sheet in xls.sheet_names:
    print(f"  - {sheet}")


# ============================================================
# LOAD EACH SHEET
# ============================================================

summary_lines = []

summary_lines.append(
    "HEEDB ICD-10 Neurology Statistics Inspection"
)
summary_lines.append("=" * 60)
summary_lines.append(f"Input file: {FILE}")
summary_lines.append("")
summary_lines.append("Sheets:")
summary_lines.extend(
    [f"  - {s}" for s in xls.sheet_names]
)
summary_lines.append("")


for sheet in xls.sheet_names:

    print("\n============================================================")
    print(f"SHEET: {sheet}")
    print("============================================================")

    df = pd.read_excel(
        FILE,
        sheet_name=sheet
    )

    print(f"Shape: {df.shape}")

    print("\nColumns:")
    for col in df.columns:
        print(f"  {col}")

    print("\nFirst rows:")
    print(
        df.head(10).to_string(index=False)
    )

    print("\nData types:")
    print(df.dtypes.to_string())

    summary_lines.append(
        f"\n{'=' * 60}"
    )
    summary_lines.append(
        f"SHEET: {sheet}"
    )
    summary_lines.append(
        f"Shape: {df.shape}"
    )
    summary_lines.append("")
    summary_lines.append(
        "Columns:"
    )

    for col in df.columns:
        summary_lines.append(
            f"  {col}"
        )

    summary_lines.append("")
    summary_lines.append(
        "First rows:"
    )
    summary_lines.append(
        df.head(10).to_string(index=False)
    )


# ============================================================
# SAVE SUMMARY
# ============================================================

OUTPUT.write_text(
    "\n".join(summary_lines),
    encoding="utf-8"
)

print("\n============================================================")
print("DONE")
print("============================================================")
print(f"Saved summary to:\n{OUTPUT}")
