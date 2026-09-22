#!/usr/bin/env python3

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


# ============================================================
# FILES
# ============================================================

INPUT = Path("results/temporal_band_power.csv")

RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")

RESULTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT)

print("\n============================================================")
print("TEMPORAL EEG QUALITY CONTROL ANALYSIS")
print("============================================================")

print(f"Windows loaded: {len(df)}")


# ============================================================
# QUALITY FLAGS
# ============================================================

def quality_class(x):

    if x <= 20:
        return "Clean"

    elif x <= 50:
        return "Moderate"

    else:
        return "Poor"


df["quality"] = df["bad_percent"].apply(quality_class)


print("\n================ QUALITY DISTRIBUTION =================\n")

print(
    df["quality"]
    .value_counts()
    .reindex(["Clean", "Moderate", "Poor"])
    .fillna(0)
    .astype(int)
)


# ============================================================
# QUALITY SUMMARY
# ============================================================

bands = [
    "Delta_relative",
    "Theta_relative",
    "Alpha_relative",
    "Beta_relative",
    "Gamma_relative",
]

print("\n================ BAND POWER BY QUALITY =================\n")

for quality in ["Clean", "Moderate", "Poor"]:

    subset = df[df["quality"] == quality]

    print(f"\n--- {quality} windows: n={len(subset)} ---")

    if len(subset) == 0:
        continue

    for band in bands:

        print(
            f"{band:20s} "
            f"Mean={subset[band].mean():6.2f}% "
            f"SD={subset[band].std():6.2f}%"
        )


# ============================================================
# CLEAN-WINDOW SUMMARY
# ============================================================

clean = df[df["bad_percent"] <= 20].copy()

print("\n================ CLEAN WINDOWS =================\n")

print(f"Clean windows: {len(clean)} / {len(df)}")

if len(clean) > 0:

    for band in bands:

        values = clean[band].dropna()

        print(
            f"{band:20s} "
            f"Mean={values.mean():6.2f}% "
            f"SD={values.std():6.2f}% "
            f"Min={values.min():6.2f}% "
            f"Max={values.max():6.2f}%"
        )

    clean["dominant_band"] = (
        clean[bands]
        .idxmax(axis=1)
        .str.replace(
            "_relative",
            "",
            regex=False
        )
    )

    print("\nDominant band among clean windows:")

    print(
        clean["dominant_band"]
        .value_counts()
        .to_string()
    )


# ============================================================
# MOST ARTIFACT-CONTAMINATED WINDOWS
# ============================================================

print("\n================ WORST WINDOWS =================\n")

worst = (
    df.sort_values(
        "bad_percent",
        ascending=False
    )
    [
        [
            "window",
            "start_min",
            "end_min",
            "bad_percent",
            "Delta_relative",
            "Theta_relative",
            "Alpha_relative",
            "Beta_relative",
            "Gamma_relative"
        ]
    ]
    .head(10)
)

print(worst.to_string(index=False))


# ============================================================
# HIGHEST BETA / GAMMA WINDOWS
# ============================================================

print("\n================ HIGHEST BETA WINDOWS =================\n")

high_beta = (
    df.sort_values(
        "Beta_relative",
        ascending=False
    )
    [
        [
            "window",
            "start_min",
            "end_min",
            "bad_percent",
            "Beta_relative",
            "Gamma_relative"
        ]
    ]
    .head(10)
)

print(high_beta.to_string(index=False))


print("\n================ HIGHEST GAMMA WINDOWS =================\n")

high_gamma = (
    df.sort_values(
        "Gamma_relative",
        ascending=False
    )
    [
        [
            "window",
            "start_min",
            "end_min",
            "bad_percent",
            "Beta_relative",
            "Gamma_relative"
        ]
    ]
    .head(10)
)

print(high_gamma.to_string(index=False))


# ============================================================
# ARTIFACT VS BAND POWER
# ============================================================

print("\n================ ARTIFACT CORRELATIONS =================\n")

for band in bands:

    x = df["bad_percent"]
    y = df[band]

    valid = (
        np.isfinite(x) &
        np.isfinite(y)
    )

    rho, p = spearmanr(
        x[valid],
        y[valid]
    )

    print(
        f"{band:20s} "
        f"Spearman rho={rho: .3f} "
        f"p={p:.4g}"
    )


# ============================================================
# SAVE QC TABLE
# ============================================================

output = RESULTS_DIR / "temporal_qc_results.csv"

df.to_csv(
    output,
    index=False
)

print(f"\nSaved QC table: {output}")


# ============================================================
# PLOT 1 — ARTIFACT OVER TIME
# ============================================================

plt.figure(figsize=(12, 5))

plt.plot(
    df["midpoint_min"],
    df["bad_percent"],
    marker="o",
    markersize=3
)

plt.axhline(
    20,
    linestyle="--",
    label="20% flag"
)

plt.axhline(
    50,
    linestyle="--",
    label="50% flag"
)

plt.xlabel("Time (minutes)")
plt.ylabel("Artifact (%)")
plt.title("Artifact Burden Across EEG Recording")
plt.legend()
plt.tight_layout()

plot1 = FIGURES_DIR / "qc_artifact_over_time.png"

plt.savefig(
    plot1,
    dpi=200
)

plt.close()

print(f"Saved: {plot1}")


# ============================================================
# PLOT 2 — BETA/GAMMA VS ARTIFACT
# ============================================================

plt.figure(figsize=(7, 6))

plt.scatter(
    df["bad_percent"],
    df["Beta_relative"],
    alpha=0.7,
    label="Beta"
)

plt.scatter(
    df["bad_percent"],
    df["Gamma_relative"],
    alpha=0.7,
    label="Gamma"
)

plt.xlabel("Artifact (%)")
plt.ylabel("Relative power (%)")
plt.title("High-Frequency Power vs Artifact Burden")
plt.legend()
plt.tight_layout()

plot2 = FIGURES_DIR / "qc_high_frequency_vs_artifact.png"

plt.savefig(
    plot2,
    dpi=200
)

plt.close()

print(f"Saved: {plot2}")


# ============================================================
# PLOT 3 — CLEAN VS POOR WINDOWS
# ============================================================

colors = {
    "Clean": "tab:green",
    "Moderate": "tab:orange",
    "Poor": "tab:red",
}

plt.figure(figsize=(12, 6))

for quality in ["Clean", "Moderate", "Poor"]:

    subset = df[df["quality"] == quality]

    plt.scatter(
        subset["midpoint_min"],
        subset["Delta_relative"],
        label=quality,
        alpha=0.8
    )

plt.xlabel("Time (minutes)")
plt.ylabel("Delta relative power (%)")
plt.title("Delta Power Across Recording by Signal Quality")
plt.legend()
plt.tight_layout()

plot3 = FIGURES_DIR / "qc_delta_by_quality.png"

plt.savefig(
    plot3,
    dpi=200
)

plt.close()

print(f"Saved: {plot3}")


print("\n============================================================")
print("QC ANALYSIS COMPLETE")
print("============================================================")
