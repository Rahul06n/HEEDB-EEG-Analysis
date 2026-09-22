#!/usr/bin/env python3

from pathlib import Path

import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mne.time_frequency import tfr_array_morlet


EEG_FILE = "data/processed/sub-S0001123604493_clean_raw.fif"

RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")

RESULTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

CHANNEL = "Cz"

SEGMENT_SEC = 120

FMIN = 1
FMAX = 40
N_FREQS = 40


# ============================================================
# LOAD
# ============================================================

raw = mne.io.read_raw_fif(
    EEG_FILE,
    preload=False,
    verbose=False
)

qc = pd.read_csv(
    RESULTS_DIR / "temporal_qc_results.csv"
)

# Select the lowest-artifact complete 5-min window
best = qc.sort_values("bad_percent").iloc[0]

window_start = best["start_min"] * 60
window_end = best["end_min"] * 60

print("\n============================================================")
print("CORRECTED TIME-FREQUENCY ANALYSIS")
print("============================================================")

print(
    f"Selected 5-min window: "
    f"{best['start_min']:.2f}–{best['end_min']:.2f} min"
)

print(
    f"Artifact burden: "
    f"{best['bad_percent']:.2f}%"
)


# ============================================================
# FIND CLEANEST 2-MINUTE SUBWINDOW
# ============================================================

bad_intervals = []

for ann in raw.annotations:

    if ann["description"] == "BAD_artifact":

        start = float(ann["onset"])
        end = start + float(ann["duration"])

        bad_intervals.append((start, end))


def bad_overlap(start, end):

    total = 0.0

    for bstart, bend in bad_intervals:

        overlap_start = max(start, bstart)
        overlap_end = min(end, bend)

        if overlap_end > overlap_start:
            total += overlap_end - overlap_start

    return total


candidate_starts = np.arange(
    window_start,
    window_end - SEGMENT_SEC + 0.1,
    5
)

candidates = []

for start in candidate_starts:

    end = start + SEGMENT_SEC

    candidates.append(
        (
            bad_overlap(start, end),
            start,
            end
        )
    )

bad_duration, start, end = min(
    candidates,
    key=lambda x: x[0]
)

print(
    f"Selected 2-min segment: "
    f"{start/60:.2f}–{end/60:.2f} min"
)

print(
    f"Artifact in segment: "
    f"{100 * bad_duration / SEGMENT_SEC:.2f}%"
)


# ============================================================
# LOAD CZ
# ============================================================

segment = raw.copy().pick([CHANNEL]).crop(
    tmin=start,
    tmax=end,
    include_tmax=False
)

segment.load_data()

data = segment.get_data()

sfreq = raw.info["sfreq"]


# ============================================================
# MORLET
# ============================================================

freqs = np.linspace(
    FMIN,
    FMAX,
    N_FREQS
)

n_cycles = np.maximum(
    3,
    freqs / 2
)

power = tfr_array_morlet(
    data[np.newaxis, :, :],
    sfreq=sfreq,
    freqs=freqs,
    n_cycles=n_cycles,
    output="power",
    decim=4,
    n_jobs=1
)

power = power[0, 0]

times = segment.times[::4]


# ============================================================
# RELATIVE TIME-FREQUENCY POWER
# ============================================================

# Frequency-wise median baseline across time
baseline = np.median(
    power,
    axis=1,
    keepdims=True
)

relative_power_db = (
    10 *
    np.log10(
        np.maximum(
            power,
            np.finfo(float).tiny
        )
        /
        np.maximum(
            baseline,
            np.finfo(float).tiny
        )
    )
)


# ============================================================
# SAVE
# ============================================================

np.save(
    RESULTS_DIR /
    "time_frequency_relative_power_db.npy",
    relative_power_db
)

np.save(
    RESULTS_DIR /
    "time_frequency_relative_frequencies.npy",
    freqs
)

np.save(
    RESULTS_DIR /
    "time_frequency_relative_times.npy",
    times
)


# ============================================================
# PLOT
# ============================================================

plt.figure(figsize=(12, 7))

vmax = np.nanpercentile(
    np.abs(relative_power_db),
    98
)

plt.pcolormesh(
    times,
    freqs,
    relative_power_db,
    shading="auto",
    vmin=-vmax,
    vmax=vmax
)

plt.xlabel("Time (seconds)")
plt.ylabel("Frequency (Hz)")

plt.title(
    f"Relative Time-Frequency Power — {CHANNEL}\n"
    f"{start/60:.2f}–{end/60:.2f} min"
)

plt.colorbar(
    label="Power relative to frequency-wise median (dB)"
)

# EEG-band guide lines
for f in [4, 8, 13, 30]:
    plt.axhline(
        f,
        linestyle="--",
        linewidth=0.7
    )

plt.tight_layout()

output = (
    FIGURES_DIR /
    "time_frequency_Cz_relative.png"
)

plt.savefig(
    output,
    dpi=200
)

plt.close()

print(
    f"\nSaved: {output}"
)

print("\n============================================================")
print("CORRECTED TIME-FREQUENCY ANALYSIS COMPLETE")
print("============================================================")
