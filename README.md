# House PTR Scraper

Collects and parses official U.S. House Periodic Transaction Reports (PTRs) into structured transaction data for analysis and web use.

The pipeline starts with the House Clerk's official annual disclosure indexes, downloads the corresponding PTR PDFs, checks archive completeness, extracts transactions from born-digital filings, resolves ticker edge cases, and publishes stable CSV files for downstream projects.

## Official source

House financial disclosure data is retrieved from the Clerk of the U.S. House of Representatives:

https://disclosures-clerk.house.gov/

The annual XML indexes identify PTR filings, and every parsed transaction retains a link back to the original House PDF.

## What the pipeline does

1. Downloads missing official PTR PDFs listed in the House annual XML indexes.
2. Archives the official XML indexes and verifies that expected PDFs are present.
3. Parses born-digital PTR PDFs with the V8.1 geometry-based extraction pipeline.
4. Resolves ticker and asset-name edge cases with the V8.2 cleanup stage.
5. Publishes stable full and web-facing datasets plus metadata.

The pipeline is resumable. Existing PDFs and completed parser checkpoint records are reused on later runs.

## Repository data

The automated pipeline keeps its working archive in the repository under `data/`:

```text
data/
├── 01_pdfs/           official House PTR PDFs by year
├── 02_xml_indexes/    archived annual House disclosure indexes
├── 03_verification/   completeness checks and summaries
├── 04_transactions/   parsed and cleaned transaction tables
├── 05_status/         parser checkpoints and review state
└── 06_public/         stable downstream datasets
```

The main published files are:

```text
data/06_public/house_ptr_transactions_latest.csv
data/06_public/house_ptr_transactions_web.csv
data/06_public/house_ptr_metadata.json
```

`house_ptr_transactions_latest.csv` preserves the full resolved transaction table. The smaller `house_ptr_transactions_web.csv` contains the fields used by the public-facing site.

## Automation

The repository includes a GitHub Actions workflow at `.github/workflows/scrape.yml`.

It runs daily at approximately **9:30 AM America/New_York**, processes newly available filings, commits changes under `data/`, and can notify the `sean-data-portfolio` repository to rebuild when new House data is published.

A manual workflow run can also override the maximum number of new PDFs processed in one run.

## Run locally

Create a virtual environment and install the requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the full pipeline:

```powershell
python run_pipeline.py
```

Start at a later stage:

```powershell
python run_pipeline.py --from-stage 4
```

Publish only:

```powershell
python run_pipeline.py --from-stage 5
```

## Configuration

The default archive is `data/` inside the repository. Environment variables can override the main runtime settings without editing code.

Common options include:

```text
HOUSE_PTR_ROOT
HOUSE_PTR_START_YEAR
HOUSE_PTR_END_YEAR
HOUSE_PTR_MAX_NEW_PDFS
```

For example:

```powershell
$env:HOUSE_PTR_START_YEAR="2025"
$env:HOUSE_PTR_MAX_NEW_PDFS="100"
python run_pipeline.py
```

## Data quality and review

House PTRs are PDFs, so document layout and extraction quality vary. The parser records review fields and checkpoint status rather than treating every file as equally reliable.

Filings that cannot be parsed cleanly are tracked for fallback or manual review. The published transaction data also retains the original House PDF URL so questionable rows can be checked against the source disclosure.

## Original notebooks

The `notebooks/` directory preserves the original Colab research and development workflow that preceded the automated Python pipeline.

The current scripts in `src/` are the production version used by local runs and GitHub Actions.
