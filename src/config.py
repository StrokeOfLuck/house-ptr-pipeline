from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

# Git-based configuration.
#
# Data lives in a local `data/` folder inside this repo (committed to git),
# not on Google Drive. This keeps the automated GitHub Actions pipeline
# self-contained -- no Drive API / service-account credentials needed.
#
# Override the root without editing code if you ever want to point this
# somewhere else:
#   $env:HOUSE_PTR_ROOT="D:\some\other\folder"
#
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = str(REPO_ROOT / "data")

ROOT = Path(os.environ.get("HOUSE_PTR_ROOT", DEFAULT_ROOT))

START_YEAR = int(os.environ.get("HOUSE_PTR_START_YEAR", "2021"))
END_YEAR = int(os.environ.get("HOUSE_PTR_END_YEAR", str(datetime.now().year)))

YEAR_INTS = list(range(START_YEAR, END_YEAR + 1))
YEARS = [str(year) for year in YEAR_INTS]

# Overridable safety valve for automated/incremental runs -- caps how many
# *new* PDFs Stage 3 processes in a single run. None = no cap (used for a
# local backfill). The GitHub Action sets this to a conservative default.
MAX_NEW_PDFS_THIS_RUN = (
    int(os.environ["HOUSE_PTR_MAX_NEW_PDFS"])
    if os.environ.get("HOUSE_PTR_MAX_NEW_PDFS")
    else None
)

PDF_ROOT = ROOT / "01_pdfs"
XML_ROOT = ROOT / "02_xml_indexes"
VERIFICATION_ROOT = ROOT / "03_verification"
DATA_ROOT = ROOT / "04_transactions"
STATUS_ROOT = ROOT / "05_status"
PUBLIC_ROOT = ROOT / "06_public"

# Clean, version-suffix-free filenames -- versioning is left to git history
# instead of being baked into the filename (previously
# PTR_transactions_GEOMETRY_V8_1_2021_2026.csv, etc.).
V81_TRANSACTIONS = DATA_ROOT / "transactions_raw.csv"
V81_FALLBACK = DATA_ROOT / "needs_fallback.csv"
V81_EXCEL = DATA_ROOT / "transactions_raw.xlsx"
V81_CHECKPOINT = STATUS_ROOT / "checkpoint.csv"

V82_TRANSACTIONS = DATA_ROOT / "transactions_resolved.csv"

VERIFICATION_SUMMARY_JSON = VERIFICATION_ROOT / "completeness_summary.json"

PUBLIC_LATEST_CSV = PUBLIC_ROOT / "house_ptr_transactions_latest.csv"
PUBLIC_METADATA_JSON = PUBLIC_ROOT / "house_ptr_metadata.json"


def ensure_folders() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)

    for folder in [
        PDF_ROOT,
        XML_ROOT,
        VERIFICATION_ROOT,
        DATA_ROOT,
        STATUS_ROOT,
        PUBLIC_ROOT,
    ]:
        folder.mkdir(parents=True, exist_ok=True)

    for year in YEARS:
        (PDF_ROOT / year).mkdir(parents=True, exist_ok=True)
