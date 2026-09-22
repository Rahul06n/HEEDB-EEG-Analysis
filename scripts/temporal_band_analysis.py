#!/usr/bin/env python3

from pathlib import Path

import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

EEG_FILE = "data/processed/sub-S0001123604493_clean_raw.fif"

RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_SEC = 300.0       # 5 minutes

FMIN = 1.0
FMAX = 40.0

# 4-second Welch windows
N_FFT = 2048
N_PER_SEG = 2048
N_OVERLAP = 1024

BANDS = {
    "Delta": (1, 4),
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta": (13, 30),
    "Gamma": (30, 40),
}


# ============================================================
# LOAD EEG
# ============================================================

print("\nLoading EEG header...")

raw = mne.io.read_raw_fif(
    EEG_FILE,
    preload=False,
    verbose=False
)

sfreq = raw.info["sfreq"]
duration = raw.times[-1]

print("\n============================================================")
print("WHOLE-RECORDING EEG TEMPORAL ANALYSIS")
print("============================================================")
print(f"File              : {EEG_FILE}")
print(f"Sampling frequency: {sfreq} Hz")
print(f"Channels          : {len(raw.ch_names)}")
print(f"Duration          : {duration:.2f} sec")
print(f"Duration          : {duration/60:.2f} min")
print(f"Duration          : {duration/3600:.2f} hours")
print(f"Window size       : {WINDOW_SEC/60:.1f} min")
print("============================================================")


# ============================================================
# BAD ANNOTATIONS
# ============================================================

bad_intervals = []

for ann in raw.annotations:

    if ann["description"] == "BAD_artifact":

        start = float(ann["onset"])
        end = start + float(ann["duration"])

        bad_intervals.append((start, end))


def get_bad_seconds(window_start, window_end):

    bad_seconds = 0.0

    for bad_start, bad_end in bad_intervals:

        overlap_start = max(window_start, bad_start)
        overlap_end = min(window_end, bad_end)

        if overlap_end > overlap_start:
            bad_seconds += overlap_end - overlap_start

    return min(
        bad_seconds,
        window_end - window_start
    )


# ============================================================
# ANALYSIS
# ============================================================

rows = []

# Only analyze complete 5-minute windows.
# The final partial window will be reported separately.
n_complete_windows = int(duration // WINDOW_SEC)

print(f"\nComplete 5-minute windows: {n_complete_windows}")
print("Final partial window will be excluded from temporal PSD analysis.\n")


for i in range(n_complete_windows):

    start = i * WINDOW_SEC
    end = start + WINDOW_SEC

    print(
        f"[{i+1:03d}/{n_complete_windows:03d}] "
        f"{start/60:7.2f} - {end/60:7.2f} min",
        flush=True
    )

    # --------------------------------------------------------
    # Artifact percentage
    # --------------------------------------------------------

    bad_seconds = get_bad_seconds(start, end)

    bad_percent = (
        100.0 * bad_seconds / WINDOW_SEC
    )

    # --------------------------------------------------------
    # Crop
    # --------------------------------------------------------

    segment = raw.copy().crop(
        tmin=start,
        tmax=end,
        include_tmax=False
    )

    # --------------------------------------------------------
    # PSD
    # --------------------------------------------------------

    try:

        spectrum = segment.compute_psd(
            method="welch",
            fmin=FMIN,
            fmax=FMAX,
            picks="eeg",
            exclude="bads",
            n_fft=N_FFT,
            n_per_seg=N_PER_SEG,
            n_overlap=N_OVERLAP,
            verbose=False
        )

    except ValueError as e:

        print(
            f"  WARNING: PSD failed for window {i+1}: {e}"
        )

        continue

    # --------------------------------------------------------
    # PSD data
    # --------------------------------------------------------

    psds, freqs = spectrum.get_data(
        return_freqs=True
    )

    valid_channels = np.all(
        np.isfinite(psds),
        axis=1
    )

    if not np.any(valid_channels):

        print("  WARNING: No valid EEG channels.")
        continue

    psds_valid = psds[valid_channels]

    # --------------------------------------------------------
    # Total power
    # --------------------------------------------------------

    total_power = np.trapezoid(
        psds_valid,
        freqs,
        axis=1
    )

    # Avoid divide-by-zero
    valid_total = total_power > 0

    psds_valid = psds_valid[valid_total]
    total_power = total_power[valid_total]

    if len(total_power) == 0:

        print("  WARNING: No valid power values.")
        continue

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    result = {
        "window": i + 1,
        "start_min": start / 60,
        "end_min": end / 60,
        "midpoint_min": (start + end) / 120,
        "bad_seconds": bad_seconds,
        "bad_percent": bad_percent,
        "valid_channels": len(total_power),
    }

    for band, (low, high) in BANDS.items():

        mask = (
            (freqs >= low) &
            (freqs < high)
        )

        if np.sum(mask) < 2:

            result[f"{band}_absolute"] = np.nan
            result[f"{band}_relative"] = np.nan

            continue

        band_power = np.trapezoid(
            psds_valid[:, mask],
            freqs[mask],
            axis=1
        )

        absolute_power = np.mean(
            band_power
        )

        relative_power = np.mean(
            band_power / total_power
        )

        result[f"{band}_absolute"] = absolute_power

        result[f"{band}_relative"] = (
            relative_power * 100.0
        )

    rows.append(result)


# ============================================================
# FINAL PARTIAL WINDOW
# ============================================================

partial_start = n_complete_windows * WINDOW_SEC

if partial_start < duration:

    partial_duration = duration - partial_start

    partial_bad = get_bad_seconds(
        partial_start,
        duration
    )

    partial_bad_percent = (
        100 * partial_bad / partial_duration
    )

    print("\n============================================================")
    print("FINAL PARTIAL WINDOW")
    print("============================================================")
    print(
        f"Time        : "
        f"{partial_start/60:.2f} - {duration/60:.2f} min"
    )
    print(
        f"Duration    : "
        f"{partial_duration/60:.2f} min"
    )
    print(
        f"Artifact    : "
        f"{partial_bad:.2f} sec "
        f"({partial_bad_percent:.2f}%)"
    )

    print(
        "\nExcluded from the main temporal PSD analysis "
        "because it is shorter than the standard 5-minute window."
    )


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(rows)

csv_file = (
    RESULTS_DIR /
    "temporal_band_power.csv"
)

df.to_csv(
    csv_file,
    index=False
)

print("\n============================================================")
print(f"Saved: {csv_file}")
print("============================================================")


# ============================================================
# SUMMARY
# ============================================================

print("\n================ OVERALL SUMMARY =================\n")

relative_columns = [
    "Delta_relative",
    "Theta_relative",
    "Alpha_relative",
    "Beta_relative",
    "Gamma_relative",
]

for col in relative_columns:

    values = df[col].dropna()

    print(
        f"{col:20s} "
        f"Mean={values.mean():6.2f}%   "
        f"SD={values.std():6.2f}%   "
        f"Min={values.min():6.2f}%   "
        f"Max={values.max():6.2f}%"
    )


# ============================================================
# DOMINANT BAND
# ============================================================

df["dominant_band"] = (
    df[relative_columns]
    .idxmax(axis=1)
    .str.replace(
        "_relative",
        "",
        regex=False
    )
)

print("\n================ DOMINANT BAND =================\n")

print(
    df["dominant_band"]
    .value_counts()
    .to_string()
)


# ============================================================
# ARTIFACT SUMMARY
# ============================================================

print("\n================ ARTIFACT =================\n")

print(
    f"Mean artifact percentage: "
    f"{df['bad_percent'].mean():.2f}%"
)

print(
    f"Minimum artifact percentage: "
    f"{df['bad_percent'].min():.2f}%"
)

print(
    f"Maximum artifact percentage: "
    f"{df['bad_percent'].max():.2f}%"
)


# ============================================================
# PLOT 1 — RELATIVE BAND POWER
# ============================================================

plt.figure(figsize=(12, 6))

for band in BANDS:

    plt.plot(
        df["midpoint_min"],
        df[f"{band}_relative"],
        label=band
    )

plt.xlabel("Time (minutes)")
plt.ylabel("Relative power (%)")
plt.title(
    "EEG Band Power Across Entire Recording"
)

plt.legend()
plt.tight_layout()

plot1 = (
    FIGURES_DIR /
    "temporal_relative_band_power.png"
)

plt.savefig(
    plot1,
    dpi=200
)

plt.close()

print(f"\nSaved: {plot1}")


# ============================================================
# PLOT 2 — ARTIFACT
# ============================================================

plt.figure(figsize=(12, 4))

plt.plot(
    df["midpoint_min"],
    df["bad_percent"]
)

plt.xlabel("Time (minutes)")
plt.ylabel("Artifact (%)")
plt.title(
    "Artifact Burden Across Recording"
)

plt.tight_layout()

plot2 = (
    FIGURES_DIR /
    "temporal_artifact_percentage.png"
)

plt.savefig(
    plot2,
    dpi=200
)

plt.close()

print(f"Saved: {plot2}")


# ============================================================
# PLOT 3 — ABSOLUTE POWER
# ============================================================

plt.figure(figsize=(12, 6))

for band in BANDS:

    plt.plot(
        df["midpoint_min"],
        df[f"{band}_absolute"],
        label=band
    )

plt.xlabel("Time (minutes)")
plt.ylabel(
    "Absolute PSD-integrated power"
)

plt.title(
    "Absolute EEG Band Power Across Recording"
)

plt.legend()
plt.tight_layout()

plot3 = (
    FIGURES_DIR /
    "temporal_absolute_band_power.png"
)

plt.savefig(
    plot3,
    dpi=200
)

plt.close()

print(f"Saved: {plot3}")


print("\n============================================================")
print("TEMPORAL EEG ANALYSIS COMPLETE")
print("============================================================")
print(f"Successfully analyzed {len(df)} windows.")
print("============================================================\n")
