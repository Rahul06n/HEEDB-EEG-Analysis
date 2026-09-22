# HEEDB-EEG-Analysis

Exploratory EEG signal analysis and Harvard EEG Database (HEEDB) metadata analysis.

## Project Overview

This repository contains the computational work performed during the initial exploration of EEG data from the Harvard EEG Database (HEEDB).

The current work focuses on understanding the EEG recording, exploring its spectral and temporal characteristics, evaluating signal quality, and examining available HEEDB neurological and clinical metadata.

The final research question, cohort definition, and statistical methodology will be established with supervisor guidance.

## Current Analysis Workflow

1. EEG dataset and metadata inspection
2. Initial EEG signal inspection using MNE
3. PSD and frequency-band power analysis
4. Temporal band-power analysis
5. Artifact-based quality-control analysis
6. EEG scalp topographic analysis
7. Time-frequency analysis
8. HEEDB ICD-10 and neurological metadata analysis
9. Figure and result generation

## EEG Analysis

### Recording

Example recording: sub-S0001123604493

Key recording characteristics:

- Sampling frequency: 512 Hz
- Original recording: 46 channels
- EEG channels analyzed: 22
- Frequency range analyzed: 1–40 Hz
- Frequency bands:
  - Delta
  - Theta
  - Alpha
  - Beta
  - Gamma

### Methods

- Welch PSD
- Temporal band-power analysis using 5-minute windows
- Artifact-based quality assessment
- 10–20 scalp topography
- Morlet-wavelet time-frequency analysis

## HEEDB Metadata Analysis

The repository also contains exploratory analysis of HEEDB neurological and clinical metadata, including:

- Neurological category distribution
- ICD-10 code distribution
- Site distribution
- Sex distribution
- Age distribution

The ICD-10 metadata contains a mixture of diseases, symptoms, signs, and other clinical codes, so these exploratory results should not be interpreted as simple disease prevalence.

## Repository Structure

analysis_record/
  00_environment/
  01_dataset_metadata/
  02_initial_inspection/
  03_psd_band_power/
  04_temporal_analysis/
  05_quality_control/
  06_topography/
  07_time_frequency/
  08_disease_statistics/
  09_figures/
  10_logs/

scripts/
figures/
results/
harvard_eeg_1000/
pixi.toml
pixi.lock

### analysis_record/

Contains the organized record of the exploratory analysis, including scripts, intermediate results, figures, metadata references, environment information, and research documentation.

### scripts/

Contains the original analysis scripts used during the project.

### results/

Contains generated numerical analysis results.

### figures/

Contains generated plots and visualizations.

## Reproducibility

The project uses an existing Pixi environment.

Environment configuration and software versions are preserved in:

analysis_record/00_environment/

The chronological research record is available at:

analysis_record/10_logs/RESEARCH_LOG.md

The complete analysis pipeline is documented in:

analysis_record/ANALYSIS_PIPELINE.md

## Data Privacy

Raw EEG recordings, large processed EEG files, and restricted patient-level HEEDB metadata are kept outside the publicly tracked repository according to the project's .gitignore configuration.

The repository is intended to contain analysis code, documentation, figures, and non-restricted results suitable for collaborative development and review.


## Exploratory HEEDB Results

The initial HEEDB neurological/clinical metadata analysis included 108,666 unique patients.

Key exploratory findings:

- Patients with at least one neurological category: 64,532 (59.39%)
- Patients without a recorded neurological category: 44,134 (40.61%)

Most frequent neurological/clinical categories:

- Miscellaneous: 53,242 (49.00%)
- Seizure Disorders: 30,221 (27.81%)
- Headache Disorders: 21,318 (19.62%)
- Sleep Disorders: 17,630 (16.22%)
- Cerebral Degeneration: 15,091 (13.89%)

Additional outputs include:

- ICD-10 code distribution
- Site-wise neurological/clinical statistics
- Neurological category statistics
- Top ICD-10 codes
- Corresponding figures and summary reports

These results are exploratory. The ICD-10 metadata contains a mixture of
diseases, symptoms, signs, and miscellaneous clinical codes, so these
frequencies should not be interpreted as simple disease prevalence.

The detailed outputs are preserved in:

`analysis_record/08_disease_statistics/`

and the visualizations are preserved in:

`analysis_record/09_figures/`

## Project Status

Current stage: Exploratory analysis / pre-research-question phase.

The next stage is to discuss the exploratory findings and available HEEDB data with the supervisor and define:

- Research question
- Study cohort
- Inclusion/exclusion criteria
- Outcome variables
- Statistical analysis plan
- Final EEG analysis pipeline
