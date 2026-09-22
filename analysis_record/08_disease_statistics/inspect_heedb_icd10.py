#!/usr/bin/env python3

from pathlib import Path
import pandas as pd


BASE = Path("scripts/Harvard-EEG-Database-Tools")

FILES = [
    BASE / "HEEDB_ICD10_for_Neurology.xlsx",
    BASE / "HEEDB_ICD10_for_Neurology_statistics.xlsx",
]


for file in FILES:

    print("\n" + "=" * 70)
    print(f"FILE: {file.name}")
    print("=" * 70)

    if not file.exists():
        print("NOT FOUND")
        continue

    xls = pd.ExcelFile(file)

    print("\nSheets:")
    for sheet in xls.sheet_names:
        print(f"  - {sheet}")

        df = pd.read_excel(
            file,
            sheet_name=sheet
        )

        print(f"\nShape: {df.shape}")

        print("\nColumns:")
        for col in df.columns:
            print(f"  {col}")

        print("\nFirst 10 rows:")
        print(
            df.head(10).to_string(index=False)
        )


print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)
