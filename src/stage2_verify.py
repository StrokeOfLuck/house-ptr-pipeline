import json
import xml.etree.ElementTree as ET

import pandas as pd
import requests
from openpyxl.styles import PatternFill

from config import (
    PDF_ROOT,
    XML_ROOT,
    VERIFICATION_ROOT,
    VERIFICATION_SUMMARY_JSON,
    V81_CHECKPOINT,
    YEAR_INTS,
    ensure_folders,
)


HEADERS = {"User-Agent": "Mozilla/5.0"}


def load_checkpoint_status_by_docid():
    """Map doc_id -> {parser_status, geometry_error} from Stage 3's checkpoint,
    so the completeness audit can flag PDFs that exist but didn't actually
    parse cleanly -- not just files that are missing outright."""
    if not V81_CHECKPOINT.exists():
        return {}

    checkpoint = pd.read_csv(V81_CHECKPOINT, low_memory=False)

    # fillna("") before astype(str) -- otherwise missing values become the
    # literal (truthy) string "nan" instead of an empty string.
    checkpoint["filing_id"] = checkpoint["filing_id"].fillna("").astype(str).str.strip()
    checkpoint["parser_status"] = checkpoint.get("parser_status", "").fillna("").astype(str).str.strip()
    checkpoint["geometry_error"] = checkpoint.get("geometry_error", "").fillna("").astype(str).str.strip()

    status_by_docid = {}
    for _, row in checkpoint.iterrows():
        doc_id = row["filing_id"]
        if not doc_id:
            continue
        status_by_docid[doc_id] = {
            "parser_status": row["parser_status"],
            "geometry_error": row["geometry_error"],
        }

    return status_by_docid


def run() -> pd.DataFrame:
    ensure_folders()
    summary = []
    checkpoint_status = load_checkpoint_status_by_docid()

    for year in YEAR_INTS:
        print(f"\n===== STAGE 2: {year} =====")

        xml_url = (
            "https://disclosures-clerk.house.gov/"
            f"public_disc/financial-pdfs/{year}FD.xml"
        )

        response = requests.get(
            xml_url,
            headers=HEADERS,
            timeout=60,
        )
        response.raise_for_status()

        xml_path = XML_ROOT / f"{year}FD.xml"
        xml_path.write_bytes(response.content)

        root = ET.parse(xml_path).getroot()

        all_rows = []
        for member in root.iter("Member"):
            all_rows.append({
                child.tag: child.text
                for child in member
            })

        full_index_df = pd.DataFrame(all_rows)

        if "DocID" in full_index_df.columns:
            full_index_df["DocID"] = (
                full_index_df["DocID"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        ptr_mask = (
            full_index_df["FilingType"]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("P")
        )

        ptr_df = full_index_df.loc[ptr_mask].copy()

        year_folder = PDF_ROOT / str(year)
        year_folder.mkdir(parents=True, exist_ok=True)

        pdf_docids = {
            pdf.stem
            for pdf in year_folder.glob("*.pdf")
        }

        full_index_df["PDF in Drive?"] = ""
        full_index_df["Parser status"] = ""

        for row_number in full_index_df.index:
            filing_type = str(
                full_index_df.loc[row_number, "FilingType"]
            ).strip()
            doc_id = str(
                full_index_df.loc[row_number, "DocID"]
            ).strip()

            if filing_type == "P":
                has_pdf = doc_id in pdf_docids
                full_index_df.loc[
                    row_number,
                    "PDF in Drive?"
                ] = "YES" if has_pdf else "NO"

                if has_pdf:
                    status = checkpoint_status.get(doc_id, {})
                    parser_status = status.get("parser_status", "")
                    geometry_error = status.get("geometry_error", "")

                    if not parser_status:
                        full_index_df.loc[row_number, "Parser status"] = "not_yet_parsed"
                    elif geometry_error:
                        full_index_df.loc[row_number, "Parser status"] = f"error: {geometry_error}"
                    else:
                        full_index_df.loc[row_number, "Parser status"] = parser_status

        expected_docids = set(ptr_df["DocID"].astype(str))
        missing_docids = sorted(expected_docids - pdf_docids)
        extra_docids = sorted(pdf_docids - expected_docids)

        # PDFs present but flagged by the parser (needs_fallback or an
        # outright geometry error) -- present, but not necessarily usable.
        present_and_expected = expected_docids & pdf_docids
        parser_flagged_docids = sorted(
            doc_id
            for doc_id in present_and_expected
            if checkpoint_status.get(doc_id, {}).get("parser_status") == "needs_fallback"
            or checkpoint_status.get(doc_id, {}).get("geometry_error")
        )
        not_yet_parsed_docids = sorted(
            doc_id
            for doc_id in present_and_expected
            if doc_id not in checkpoint_status
        )

        expected_count = len(expected_docids)
        pdf_count = len(pdf_docids)
        matched_count = len(expected_docids & pdf_docids)
        missing_count = len(missing_docids)
        extra_count = len(extra_docids)
        parser_flagged_count = len(parser_flagged_docids)
        not_yet_parsed_count = len(not_yet_parsed_docids)

        complete = missing_count == 0 and extra_count == 0

        verification_df = pd.DataFrame({
            "Check": [
                "Year",
                "PTRs in official House XML",
                "PDF files in Drive",
                "Matched PTR PDFs",
                "Missing PTR PDFs",
                "Extra PDFs not in XML",
                "PDFs present but parser-flagged (needs_fallback/error)",
                "PDFs present but not yet parsed",
                "Complete (download)?",
            ],
            "Result": [
                year,
                expected_count,
                pdf_count,
                matched_count,
                missing_count,
                extra_count,
                parser_flagged_count,
                not_yet_parsed_count,
                "YES" if complete else "NO",
            ],
        })

        excel_path = VERIFICATION_ROOT / f"House_PTR_Verification_{year}.xlsx"

        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            full_index_df.to_excel(
                writer,
                sheet_name="House XML Index",
                index=False,
            )
            verification_df.to_excel(
                writer,
                sheet_name="Verification",
                index=False,
            )

            if missing_count:
                pd.DataFrame({
                    "Missing DocID": missing_docids
                }).to_excel(
                    writer,
                    sheet_name="Missing PTRs",
                    index=False,
                )

            if extra_count:
                pd.DataFrame({
                    "Extra PDF DocID": extra_docids
                }).to_excel(
                    writer,
                    sheet_name="Extra PDFs",
                    index=False,
                )

            if parser_flagged_count:
                pd.DataFrame({
                    "Parser-flagged DocID": parser_flagged_docids
                }).to_excel(
                    writer,
                    sheet_name="Parser Flagged",
                    index=False,
                )

            worksheet = writer.book["House XML Index"]

            headers_in_sheet = {
                cell.value: cell.column
                for cell in worksheet[1]
            }

            filing_col = headers_in_sheet["FilingType"]
            drive_col = headers_in_sheet["PDF in Drive?"]

            green_fill = PatternFill(
                fill_type="solid",
                fgColor="C6EFCE",
            )
            red_fill = PatternFill(
                fill_type="solid",
                fgColor="FFC7CE",
            )

            for excel_row in range(2, worksheet.max_row + 1):
                filing_type = worksheet.cell(
                    excel_row,
                    filing_col,
                ).value
                drive_status = worksheet.cell(
                    excel_row,
                    drive_col,
                ).value

                if filing_type == "P":
                    fill = (
                        green_fill
                        if drive_status == "YES"
                        else red_fill
                    )
                    for cell in worksheet[excel_row]:
                        cell.fill = fill

        summary.append({
            "Year": year,
            "House PTRs": expected_count,
            "PDFs in Drive": pdf_count,
            "Matched": matched_count,
            "Missing": missing_count,
            "Extra": extra_count,
            "Parser flagged": parser_flagged_count,
            "Not yet parsed": not_yet_parsed_count,
            "Complete": complete,
        })

        print("House PTRs:", expected_count)
        print("PDFs in Drive:", pdf_count)
        print("Matched:", matched_count)
        print("Missing:", missing_count)
        print("Extra:", extra_count)
        print("Parser flagged:", parser_flagged_count)
        print("Not yet parsed:", not_yet_parsed_count)
        print("Complete:", complete)
        print("Excel:", excel_path)

    summary_df = pd.DataFrame(summary)
    print("\n===== ALL YEARS =====")
    print(summary_df.to_string(index=False))

    # Machine-readable summary -- so a GitHub Action can act on regressions
    # (annotate the run, or fail loudly if missing/error counts increase)
    # instead of the audit being Excel-only/human-only.
    summary_payload = {
        "years": summary,
        "totals": {
            "house_ptrs": int(summary_df["House PTRs"].sum()) if len(summary_df) else 0,
            "pdfs_in_drive": int(summary_df["PDFs in Drive"].sum()) if len(summary_df) else 0,
            "missing": int(summary_df["Missing"].sum()) if len(summary_df) else 0,
            "extra": int(summary_df["Extra"].sum()) if len(summary_df) else 0,
            "parser_flagged": int(summary_df["Parser flagged"].sum()) if len(summary_df) else 0,
            "not_yet_parsed": int(summary_df["Not yet parsed"].sum()) if len(summary_df) else 0,
            "all_years_complete": bool(summary_df["Complete"].all()) if len(summary_df) else True,
        },
    }

    VERIFICATION_SUMMARY_JSON.write_text(
        json.dumps(summary_payload, indent=2),
        encoding="utf-8",
    )
    print("\nSaved machine-readable summary:", VERIFICATION_SUMMARY_JSON)

    return summary_df


if __name__ == "__main__":
    run()
