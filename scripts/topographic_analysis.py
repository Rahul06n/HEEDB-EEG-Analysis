#!/usr/bin/env python3

from pathlib import Path

import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


EEG_FILE = "data/processed/sub-S0001123604493_clean_raw.fif"

RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")

RESULTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

BANDS = {
    "Delta": (1, 4),
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta": (13, 30),
    "Gamma": (30, 40),
}

# Scalp channels only
SCALP_CHANNELS = [
    "Fp1", "F7", "T3", "T5", "O1",
    "F3", "C3", "P3", "Fz", "Cz",
    "Fp2", "F8", "T4", "T6", "O2",
    "F4", "C4", "P4", "Fpz", "Pz"
]


# ============================================================
# LOAD EEG
# ============================================================

print("Loading EEG...")

raw = mne.io.read_raw_fif(
    EEG_FILE,
    preload=False,
    verbose=False
)

# Use standard 10-20 montage.
# match_case=False allows Fp1 etc.
montage = mne.channels.make_standard_montage("standard_1020")

raw.set_montage(
    montage,
    match_case=False,
    on_missing="warn"
)

# Keep only scalp channels
available = [
    ch for ch in SCALP_CHANNELS
    if ch in raw.ch_names
]

raw_scalp = raw.copy().pick(available)

print("\nScalp channels:")
print(raw_scalp.ch_names)

print(f"\nNumber of scalp channels: {len(raw_scalp.ch_names)}")


# ============================================================
# SELECT RELATIVELY CLEAN WINDOWS
# ============================================================

csv_file = RESULTS_DIR / "temporal_qc_results.csv"

df = pd.read_csv(csv_file)

clean_windows = df[
    df["bad_percent"] <= 20
]

print(
    f"\nClean windows available: "
    f"{len(clean_windows)}"
)


# ============================================================
# ACCUMULATE BAND POWER
# ============================================================

band_channel_values = {
    band: [] for band in BANDS
}


for _, row in clean_windows.iterrows():

    start = row["start_min"] * 60
    end = row["end_min"] * 60

    segment = raw_scalp.copy().crop(
        tmin=start,
        tmax=end,
        include_tmax=False
    )

    spectrum = segment.compute_psd(
        method="welch",
        fmin=1,
        fmax=40,
        picks="eeg",
        exclude="bads",
        n_fft=2048,
        n_per_seg=2048,
        n_overlap=1024,
        verbose=False
    )

    psds, freqs = spectrum.get_data(
        return_freqs=True
    )

    for band, (low, high) in BANDS.items():

        mask = (
            (freqs >= low) &
            (freqs < high)
        )

        power = np.trapezoid(
            psds[:, mask],
            freqs[mask],
            axis=1
        )

        band_channel_values[band].append(power)


# ============================================================
# AVERAGE ACROSS CLEAN WINDOWS
# ============================================================

for band in BANDS:

    values = np.asarray(
        band_channel_values[band]
    )

    mean_power = np.nanmean(
        values,
        axis=0
    )

    output = pd.DataFrame({
        "channel": raw_scalp.ch_names,
        "power": mean_power
    })

    output.to_csv(
        RESULTS_DIR / f"{band.lower()}_topography.csv",
        index=False
    )

    # --------------------------------------------------------
    # Topomap
    # --------------------------------------------------------

    info = mne.create_info(
        raw_scalp.ch_names,
        sfreq=raw.info["sfreq"],
        ch_types="eeg"
    )

    info.set_montage(
        montage,
        match_case=False,
        on_missing="ignore"
    )

    fig, ax = plt.subplots(
        figsize=(7, 6)
    )

    mne.viz.plot_topomap(
        mean_power,
        info,
        axes=ax,
        show=False
    )

    ax.set_title(
        f"{band} power\n"
        f"Average across clean windows"
    )

    fig.tight_layout()

    filename = (
        FIGURES_DIR /
        f"{band.lower()}_topomap.png"
    )

    fig.savefig(
        filename,
        dpi=200
    )

    plt.close(fig)

    print(f"Saved: {filename}")


print("\n============================================================")
print("TOPOGRAPHIC ANALYSIS COMPLETE")
print("============================================================")
