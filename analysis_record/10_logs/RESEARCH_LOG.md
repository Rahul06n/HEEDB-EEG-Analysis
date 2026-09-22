# EEG Analysis Research Log

## Project Status
Exploratory EEG analysis and HEEDB metadata analysis.
Final research question and study design are pending supervisor guidance.

---

## 1. Environment Setup

### Objective
Set up the computational environment for EEG analysis.

### Environment
- Existing pixi environment: `eeg-analysis`
- MNE
- NumPy
- SciPy
- Matplotlib

### Record
Software versions are stored in:

`00_environment/software_versions.txt`

The project environment files are preserved as:

`00_environment/pixi.toml`  
`00_environment/pixi.lock`

---

## 2. Dataset Acquisition and Metadata

### Objective
Obtain EEG data and inspect HEEDB metadata.

### Dataset
- HEEDB EEG data
- Example recording: `sub-S0001123604493`
- Sampling frequency: 512 Hz
- Original EDF contains 46 channels
- 22 EEG channels were retained for analysis

### Metadata preserved
- EEG JSON
- EEG channels TSV
- HEEDB patient metadata
- HEEDB ICD-10 metadata

---

## 3. Initial EEG Inspection

### Objective
Inspect the raw EEG recording and identify signal-quality issues.

### Processing
- EEG recording loaded using MNE
- Recording duration inspected
- Channel information inspected
- BAD_artifact annotations inspected
- Raw waveform visually inspected at multiple time points

### Processed file
`sub-S0001123604493_clean_raw.fif`

---

## 4. PSD and Frequency-Band Analysis

### Objective
Characterize EEG spectral power.

### Method
Welch PSD was used.

### Frequency range
1–40 Hz

### Bands
- Delta
- Theta
- Alpha
- Beta
- Gamma

### Script
The PSD calculation is part of:

`04_temporal_analysis/temporal_band_analysis.py`

No separate standalone PSD script was used.

---

## 5. Temporal Band-Power Analysis

### Objective
Examine how EEG band power changes throughout the recording.

### Method
The recording was divided into non-overlapping 5-minute windows.

### Result
58 complete 5-minute windows were analyzed.

The final partial window was excluded.

### Output
`temporal_band_power.csv`

---

## 6. Quality-Control Analysis

### Objective
Investigate the effect of annotated artifacts on spectral measurements.

### Method
Artifact percentage was calculated for each 5-minute window.

Exploratory thresholds:
- Clean: <=20%
- Moderate: 20–50%
- Poor: >50%

These thresholds are project-specific exploratory thresholds and are not clinical standards.

### Output
`temporal_qc_results.csv`

---

## 7. Topographic Analysis

### Objective
Examine the spatial distribution of EEG band power.

### Method
A standard 10–20 montage was applied.

20 scalp channels were used for topographic visualization; A1 and A2 were excluded.

### Bands
- Delta
- Theta
- Alpha
- Beta
- Gamma

### Outputs
Band-specific topography CSV files and PNG figures.

---

## 8. Time-Frequency Analysis

### Objective
Examine changes in spectral activity over time.

### Method
Morlet-wavelet time-frequency analysis was performed using Cz.

A relative-power dB representation was used for interpretation.

### Correction
An initial absolute dB calculation produced uninformative extremely negative values.
The analysis was subsequently represented using frequency-wise relative power.

### Outputs
Time-frequency frequency, time, and power arrays plus figures.

---

## 9. HEEDB Disease / Clinical Metadata Analysis

### Objective
Explore the clinical and neurological metadata available in HEEDB.

### Analysis
- Neurological category distribution
- ICD-10 code distribution
- Site distribution
- Sex distribution
- Age distribution

### Important interpretation limitation
The ICD-10 table contains diseases, symptoms, signs, and miscellaneous clinical codes.
Therefore, these results should not be interpreted as simple disease prevalence.

### Outputs
- Neurological category statistics
- Site statistics
- Top ICD-10 codes
- Summary report
- Detailed report

---

## 10. Current Scientific Status

The work completed so far is exploratory.

No final:
- disease-vs-control cohort
- machine-learning model
- diagnostic classifier
- hypothesis test
- final statistical model

has been established.

The final research question, cohort definition, inclusion/exclusion criteria,
and statistical methodology will be determined with supervisor guidance.

---

## 11. Reproducibility

Analysis scripts, intermediate results, figures, metadata references,
environment information, and terminal history are preserved in this folder.

Original project data remain in the main project directories.

Restricted patient-level data should remain local and should not be uploaded
to a public GitHub repository.

---

## 12. Next Step

Discuss the exploratory findings and available HEEDB data with the supervisor
and define the final research question and analysis plan.
