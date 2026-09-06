from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

# Local-first configuration.
#
# By default this points at the same Google Drive archive used by the Colab
# notebooks, assuming Google Drive for Desktop is mounted as G: on Windows.
#
# You can override it without editing code:
#   $env:HOUSE_PTR_ROOT="D:\some\other\folder"
#
DEFAULT_ROOT = r"G:\My Drive\Congressional Trading Data\House_PTRs"

ROOT = Path(os.environ.get("HOUSE_PTR_ROOT", DEFAULT_ROOT))

START_YEAR = int(os.environ.get("HOUSE_PTR_START_YEAR", "2021"))
END_YEAR = int(os.environ.get("HOUSE_PTR_END_YEAR", str(datetime.now().year)))

YEAR_INTS = list(range(START_YEAR, END_YEAR + 1))
YEARS = [str(year) for year in YEAR_INTS]
YEAR_LABEL = f"{START_YEAR}_{END_YEAR}"

PDF_ROOT = ROOT / "01 Official House PTR PDFs"
XML_ROOT = ROOT / "02 Official House XML Indexes"
VERIFICATION_ROOT = ROOT / "03 PDF Archive Verification Reports"
DATA_ROOT = ROOT / "04 Parsed PTR Transaction Data"
STATUS_ROOT = ROOT / "05 Parser Checkpoints and Status"
WORKFLOW_NOTEBOOK_ROOT = ROOT / "06 Workflow Notebooks"

V81_TRANSACTIONS = DATA_ROOT / f"PTR_transactions_GEOMETRY_V8_1_{YEAR_LABEL}.csv"
V81_FALLBACK = DATA_ROOT / f"PTR_GEOMETRY_V8_1_needs_fallback_{YEAR_LABEL}.csv"
V81_EXCEL = DATA_ROOT / f"PTR_GEOMETRY_V8_1_{YEAR_LABEL}.xlsx"
V81_CHECKPOINT = STATUS_ROOT / f"PTR_GEOMETRY_V8_1_checkpoint_{YEAR_LABEL}.csv"

V82_TRANSACTIONS = DATA_ROOT / f"PTR_transactions_GEOMETRY_V8_2_{YEAR_LABEL}.csv"

PUBLIC_ROOT = ROOT / "07 Public Website Data"
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
        WORKFLOW_NOTEBOOK_ROOT,
        PUBLIC_ROOT,
    ]:
        folder.mkdir(parents=True, exist_ok=True)

    for year in YEARS:
        (PDF_ROOT / year).mkdir(parents=True, exist_ok=True)
