# House PTR Pipeline

Automated pipeline for official U.S. House Periodic Transaction Reports (PTRs).

This repository is the code side of the project. The large source archive and
persistent parser state remain in the existing Google Drive folder:

`Congressional Trading Data/House_PTRs`

## Pipeline

1. Download missing official House PTR PDFs from the annual House XML indexes.
2. Archive the official XML indexes and independently verify PDF completeness.
3. Parse born-digital PTR PDFs with the V8.1 geometry parser.
4. Resolve ticker edge cases with the V8.2 cleanup layer.
5. Copy the current final dataset to a stable website filename and write metadata.

## Current local setup

The default path is:

`G:\My Drive\Congressional Trading Data\House_PTRs`

Override it in PowerShell if Google Drive uses another location:

```powershell
$env:HOUSE_PTR_ROOT="G:\My Drive\Congressional Trading Data\House_PTRs"
```

## Set up Python

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the full workflow

```powershell
python run_pipeline.py
```

Because the original workflow is resumable, normal reruns should skip source
PDFs and parser checkpoint records already completed.

## Run only later stages

Start with Stage 4:

```powershell
python run_pipeline.py --from-stage 4
```

Publish only:

```powershell
python run_pipeline.py --from-stage 5
```

## Website outputs

After a successful run:

`07 Public Website Data/house_ptr_transactions_latest.csv`

`07 Public Website Data/house_ptr_metadata.json`

Those stable filenames are what the portfolio site should consume.

## Original notebooks

The `notebooks/` folder preserves the original five Colab notebooks as the
documented research/development version of the workflow.

## Next phase

The current starter is intentionally local-first so the conversion can be
tested against the exact existing Google Drive archive before introducing
cloud credentials.

After that works, the next step is GitHub Actions:
- authenticate the persistent Google Drive archive for the runner
- run daily at 9:30 AM America/New_York
- copy the public CSV/metadata into a web-accessible location
- trigger the Quarto portfolio rebuild
