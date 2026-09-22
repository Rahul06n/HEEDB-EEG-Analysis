# PSD and Band-Power Analysis

## Method
Power spectral density (PSD) was calculated using MNE's Welch method.

## Frequency range
1–40 Hz

## Frequency bands
- Delta
- Theta
- Alpha
- Beta
- Gamma

## Script
The PSD calculation used for the temporal analysis is implemented in:

scripts/temporal_band_analysis.py

The preserved copy is:

analysis_record/04_temporal_analysis/temporal_band_analysis.py

## Note
No separate standalone PSD script was used. The PSD/Welch calculation is
part of the temporal band-power analysis pipeline.

The original terminal history is preserved in:

analysis_record/10_logs/terminal_history.txt
