#!/usr/bin/env python3

"""
Download at least 1000 EEG EDF recordings from the
Harvard Electroencephalography Database (HEEDB).

Requirements:
    - Authorized HEEDB/BDSP access
    - AWS CLI configured with appropriate credentials/access
    - Python 3.10+

The script:
    1. Queries the HEEDB S3 access point
    2. Finds EDF files
    3. Downloads them sequentially
    4. Skips files that already exist
    5. Logs successful/failed downloads
    6. Stops after MIN_FILES successful EDF downloads
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

MIN_FILES = 1000

OUTPUT_DIR = Path("data")

LOG_DIR = Path("logs")

DOWNLOAD_LOG = LOG_DIR / "downloaded.txt"
FAILED_LOG = LOG_DIR / "failed.txt"

# Harvard EEG Database AWS access point
S3_PATH = (
    "s3://arn:aws:s3:us-east-1:184438910517:"
    "accesspoint/bdsp-eeg-access-point/EEG"
)


# ============================================================
# SETUP
# ============================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_message(message):
    """Print timestamped message."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{timestamp}] {message}")


def load_downloaded():
    """Load previously downloaded S3 paths."""

    if not DOWNLOAD_LOG.exists():
        return set()

    with open(DOWNLOAD_LOG, "r") as f:
        return {
            line.strip()
            for line in f
            if line.strip()
        }


def save_downloaded(s3_file):
    """Record successfully downloaded file."""

    with open(DOWNLOAD_LOG, "a") as f:
        f.write(s3_file + "\n")


def save_failed(s3_file, error):
    """Record failed download."""

    with open(FAILED_LOG, "a") as f:
        f.write(
            f"{s3_file}\t{error}\n"
        )


# ============================================================
# CHECK AWS CLI
# ============================================================

def check_aws():

    try:
        result = subprocess.run(
            ["aws", "--version"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                "AWS CLI is not working."
            )

        log_message(
            f"AWS detected: "
            f"{result.stdout.strip() or result.stderr.strip()}"
        )

    except FileNotFoundError:

        print(
            "\nERROR: AWS CLI was not found.\n"
            "Install/configure AWS CLI first.\n"
        )

        sys.exit(1)


# ============================================================
# FIND EDF FILES
# ============================================================

def get_edf_files():

    log_message(
        "Searching Harvard EEG Database for EDF files..."
    )

    command = [
        "aws",
        "s3",
        "ls",
        S3_PATH,
        "--recursive"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print("\nAWS ERROR:")
        print(result.stderr)

        sys.exit(1)

    edf_files = []

    for line in result.stdout.splitlines():

        parts = line.split()

        if len(parts) < 4:
            continue

        s3_file = parts[-1]

        if s3_file.lower().endswith(".edf"):

            edf_files.append(s3_file)

    return edf_files


# ============================================================
# DOWNLOAD ONE FILE
# ============================================================

def download_file(s3_file):

    destination = OUTPUT_DIR / s3_file

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Skip if file already exists
    if destination.exists():

        if destination.stat().st_size > 0:

            log_message(
                f"Already exists: {s3_file}"
            )

            return True

    command = [
        "aws",
        "s3",
        "cp",
        f"{S3_PATH}/{s3_file}",
        str(destination)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:

        if destination.exists() and destination.stat().st_size > 0:

            save_downloaded(s3_file)

            log_message(
                f"Downloaded: {s3_file}"
            )

            return True

    error = result.stderr.strip()

    save_failed(
        s3_file,
        error
    )

    log_message(
        f"FAILED: {s3_file}"
    )

    return False


# ============================================================
# MAIN
# ============================================================

def main():

    log_message(
        "Starting Harvard EEG downloader"
    )

    log_message(
        f"Target: {MIN_FILES} EDF recordings"
    )

    check_aws()

    already_downloaded = load_downloaded()

    log_message(
        f"Previously recorded downloads: "
        f"{len(already_downloaded)}"
    )

    edf_files = get_edf_files()

    log_message(
        f"EDF recordings discovered: "
        f"{len(edf_files)}"
    )

    if len(edf_files) < MIN_FILES:

        print(
            f"\nERROR: Only {len(edf_files)} EDF files "
            f"were discovered."
        )

        sys.exit(1)

    successful = len(already_downloaded)

    for i, s3_file in enumerate(edf_files, start=1):

        if successful >= MIN_FILES:

            break

        if s3_file in already_downloaded:

            continue

        log_message(
            f"[{successful + 1}/{MIN_FILES}] "
            f"Downloading {s3_file}"
        )

        success = download_file(
            s3_file
        )

        if success:

            successful += 1

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print("\n")
    print("=" * 70)
    print("DOWNLOAD COMPLETE")
    print("=" * 70)

    print(
        f"Successful EDF recordings: {successful}"
    )

    print(
        f"Target: {MIN_FILES}"
    )

    print(
        f"Data directory: "
        f"{OUTPUT_DIR.resolve()}"
    )

    print(
        f"Download log: "
        f"{DOWNLOAD_LOG.resolve()}"
    )

    print(
        f"Failed log: "
        f"{FAILED_LOG.resolve()}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
