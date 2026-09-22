#!/usr/bin/env python3

from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

BASE = Path("scripts/Harvard-EEG-Database-Tools")

INPUT = BASE / "HEEDB_ICD10_for_Neurology.xlsx"

RESULTS = Path("results")
FIGURES = Path("figures")

RESULTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD
# ============================================================

print("\n============================================================")
print("HEEDB PATIENT-LEVEL NEUROLOGICAL DISEASE STATISTICS")
print("============================================================")

print(f"\nInput: {INPUT}")

df = pd.read_excel(INPUT)

print(f"Rows   : {len(df):,}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# PATIENT UNIQUENESS
# ============================================================

n_rows = len(df)

n_unique_patients = df["BDSPPatientID"].nunique()

print("\n================ PATIENT STRUCTURE =================\n")

print(f"Rows                     : {n_rows:,}")
print(f"Unique BDSPPatientID      : {n_unique_patients:,}")
print(
    f"Duplicate patient rows   : "
    f"{n_rows - n_unique_patients:,}"
)

if n_rows != n_unique_patients:
    print(
        "\nWARNING: Multiple rows per patient detected."
        "\nDisease prevalence must then be calculated at patient level."
    )


# ============================================================
# METADATA SUMMARY
# ============================================================

print("\n================ DEMOGRAPHICS =================\n")

print("\nSex:")
print(
    df["SexDSC"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nSite:")
print(
    df["SiteID"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nAge summary:")
print(
    df["AgeAtVisitAvg"]
    .describe()
    .to_string()
)


# ============================================================
# DISEASE CATEGORY COLUMNS
# ============================================================

metadata_columns = [
    "BDSPPatientID",
    "SiteID",
    "SexDSC",
    "VisitCount",
    "AgeAtVisitAvg",
]

disease_columns = [
    c for c in df.columns
    if c not in metadata_columns
]


print("\n================ DISEASE COLUMNS =================\n")

print(f"Number of disease categories: {len(disease_columns)}")

for c in disease_columns:
    print(f"  {c}")


# ============================================================
# CATEGORY PATIENT COUNTS
# ============================================================

category_rows = []

for category in disease_columns:

    nonempty = (
        df[category]
        .notna()
        &
        (df[category].astype(str).str.strip() != "")
        &
        (df[category].astype(str).str.lower() != "nan")
    )

    patient_count = int(nonempty.sum())

    percentage = (
        100 * patient_count / n_unique_patients
    )

    category_rows.append({
        "Category": category,
        "Patients": patient_count,
        "Percentage_of_disease_dataset": percentage
    })


category_df = pd.DataFrame(category_rows)

category_df = category_df.sort_values(
    "Patients",
    ascending=False
).reset_index(drop=True)

category_df.insert(
    0,
    "Rank",
    range(1, len(category_df) + 1)
)


print("\n================ CATEGORY STATISTICS =================\n")

print(
    category_df.to_string(
        index=False,
        formatters={
            "Percentage_of_disease_dataset":
            "{:.2f}".format
        }
    )
)


# Save
category_df.to_csv(
    RESULTS / "HEEDB_neurological_category_statistics.csv",
    index=False
)


# ============================================================
# PATIENTS WITH ANY NEUROLOGICAL DIAGNOSIS
# ============================================================

has_any = np.zeros(
    len(df),
    dtype=bool
)

for category in disease_columns:

    present = (
        df[category]
        .notna()
        &
        (df[category].astype(str).str.strip() != "")
        &
        (df[category].astype(str).str.lower() != "nan")
    )

    has_any |= present.to_numpy()


n_with_any = int(has_any.sum())
n_without_any = int((~has_any).sum())

print("\n================ OVERALL NEUROLOGICAL STATUS =================\n")

print(
    f"Patients with >=1 neurological category: "
    f"{n_with_any:,} "
    f"({100*n_with_any/n_unique_patients:.2f}%)"
)

print(
    f"Patients without neurological category: "
    f"{n_without_any:,} "
    f"({100*n_without_any/n_unique_patients:.2f}%)"
)


# ============================================================
# ICD-10 CODE FREQUENCIES
# ============================================================

code_counter = Counter()

code_category = {}

for category in disease_columns:

    for value in df[category].dropna():

        codes = str(value).split()

        for code in codes:

            code = code.strip()

            if not code or code.lower() == "nan":
                continue

            code_counter[code] += 1

            code_category.setdefault(
                code,
                set()
            ).add(category)


# ============================================================
# DESCRIPTION LOOKUP
# ============================================================

stats_file = (
    BASE /
    "HEEDB_ICD10_for_Neurology_statistics.xlsx"
)

description_map = {}

if stats_file.exists():

    stats_df = pd.read_excel(
        stats_file
    )

    if {
        "Code",
        "Descriptions",
        "Category"
    }.issubset(stats_df.columns):

        for _, row in stats_df.iterrows():

            code = str(row["Code"]).strip()

            description_map[code] = (
                row["Descriptions"]
            )


# ============================================================
# TOP ICD CODES
# ============================================================

code_rows = []

for code, count in code_counter.items():

    category = "; ".join(
        sorted(
            code_category.get(
                code,
                set()
            )
        )
    )

    description = description_map.get(
        code,
        ""
    )

    percentage = (
        100 * count / n_unique_patients
    )

    code_rows.append({
        "Code": code,
        "Description": description,
        "Category": category,
        "Patient_records": count,
        "Percentage_of_disease_dataset": percentage
    })


code_df = pd.DataFrame(
    code_rows
).sort_values(
    "Patient_records",
    ascending=False
).reset_index(drop=True)

code_df.insert(
    0,
    "Rank",
    range(1, len(code_df) + 1)
)


print("\n================ TOP 30 ICD-10 CODES =================\n")

print(
    code_df.head(30).to_string(
        index=False,
        formatters={
            "Percentage_of_disease_dataset":
            "{:.2f}".format
        }
    )
)


code_df.to_csv(
    RESULTS / "HEEDB_top_ICD10_codes.csv",
    index=False
)


# ============================================================
# SITE × DISEASE CATEGORY
# ============================================================

site_rows = []

for site in sorted(
    df["SiteID"].dropna().unique()
):

    subset = df[
        df["SiteID"] == site
    ]

    row = {
        "SiteID": site,
        "Patients": subset["BDSPPatientID"].nunique(),
    }

    for category in disease_columns:

        present = (
            subset[category]
            .notna()
            &
            (
                subset[category]
                .astype(str)
                .str.strip() != ""
            )
        )

        row[category] = int(
            present.sum()
        )

    site_rows.append(row)


site_df = pd.DataFrame(site_rows)

site_df.to_csv(
    RESULTS / "HEEDB_site_disease_statistics.csv",
    index=False
)


# ============================================================
# PLOT 1 — TOP DISEASE CATEGORIES
# ============================================================

top_category = category_df.head(15).copy()

plt.figure(figsize=(10, 7))

plt.barh(
    top_category["Category"][::-1],
    top_category["Patients"][::-1]
)

plt.xlabel("Patients")
plt.ylabel("Neurological category")
plt.title("Top Neurological Disease Categories in HEEDB")
plt.tight_layout()

plt.savefig(
    FIGURES / "HEEDB_top_neurological_categories.png",
    dpi=200
)

plt.close()


# ============================================================
# PLOT 2 — TOP ICD CODES
# ============================================================

top_codes = code_df.head(20).copy()

labels = (
    top_codes["Code"]
    + " — "
    + top_codes["Description"].fillna("")
    .astype(str)
    .str[:50]
)

plt.figure(figsize=(11, 8))

plt.barh(
    labels[::-1],
    top_codes["Patient_records"][::-1]
)

plt.xlabel("Patient records")
plt.ylabel("ICD-10 code")
plt.title("Top ICD-10 Neurological Codes")
plt.tight_layout()

plt.savefig(
    FIGURES / "HEEDB_top_ICD10_codes.png",
    dpi=200
)

plt.close()


# ============================================================
# SAVE TEXT REPORT
# ============================================================

report = RESULTS / "HEEDB_disease_statistics_report.txt"

with open(report, "w", encoding="utf-8") as f:

    f.write(
        "HEEDB PATIENT-LEVEL NEUROLOGICAL DISEASE STATISTICS\n"
    )

    f.write("=" * 70 + "\n\n")

    f.write(
        f"Rows: {n_rows:,}\n"
    )

    f.write(
        f"Unique patients: {n_unique_patients:,}\n\n"
    )

    f.write(
        "Patients with >=1 neurological category: "
        f"{n_with_any:,} "
        f"({100*n_with_any/n_unique_patients:.2f}%)\n"
    )

    f.write(
        "Patients without neurological category: "
        f"{n_without_any:,} "
        f"({100*n_without_any/n_unique_patients:.2f}%)\n\n"
    )

    f.write(
        "CATEGORY STATISTICS\n"
    )

    f.write(
        category_df.to_string(index=False)
    )

    f.write(
        "\n\nTOP ICD-10 CODES\n"
    )

    f.write(
        code_df.head(50).to_string(index=False)
    )


print("\n============================================================")
print("DISEASE STATISTICS COMPLETE")
print("============================================================")

print("\nGenerated files:")

for file in [
    RESULTS / "HEEDB_neurological_category_statistics.csv",
    RESULTS / "HEEDB_top_ICD10_codes.csv",
    RESULTS / "HEEDB_site_disease_statistics.csv",
    RESULTS / "HEEDB_disease_statistics_report.txt",
    FIGURES / "HEEDB_top_neurological_categories.png",
    FIGURES / "HEEDB_top_ICD10_codes.png",
]:
    print(f"  {file}")

print("\n============================================================")
