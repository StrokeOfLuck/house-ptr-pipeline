from pathlib import Path
import time
import xml.etree.ElementTree as ET

import requests

from config import PDF_ROOT, YEAR_INTS, ensure_folders


HEADERS = {"User-Agent": "Mozilla/5.0"}


def run() -> None:
    ensure_folders()

    for year in YEAR_INTS:
        print(f"\n===== STAGE 1: {year} =====")

        xml_url = (
            "https://disclosures-clerk.house.gov/"
            f"public_disc/financial-pdfs/{year}FD.xml"
        )

        print("Downloading filing index:", xml_url)

        response = requests.get(
            xml_url,
            headers=HEADERS,
            timeout=60,
        )
        response.raise_for_status()

        root = ET.fromstring(response.content)

        year_folder = PDF_ROOT / str(year)
        year_folder.mkdir(parents=True, exist_ok=True)

        total_ptrs = 0
        downloaded = 0
        skipped = 0
        failed = 0

        for member in root.iter("Member"):
            filing_type = member.findtext("FilingType")
            doc_id = member.findtext("DocID")

            if filing_type != "P" or not doc_id:
                continue

            doc_id = str(doc_id).strip()
            total_ptrs += 1

            pdf_path = year_folder / f"{doc_id}.pdf"

            if pdf_path.exists():
                skipped += 1
                continue

            pdf_url = (
                "https://disclosures-clerk.house.gov/"
                f"public_disc/ptr-pdfs/{year}/{doc_id}.pdf"
            )

            try:
                pdf_response = requests.get(
                    pdf_url,
                    headers=HEADERS,
                    timeout=30,
                )
                pdf_response.raise_for_status()
                pdf_path.write_bytes(pdf_response.content)
                downloaded += 1
                print("Downloaded:", doc_id)
                time.sleep(0.5)
            except Exception as error:
                failed += 1
                print("ERROR:", doc_id, error)

        print("PTRs listed:", total_ptrs)
        print("Downloaded:", downloaded)
        print("Already had:", skipped)
        print("Failed:", failed)
        print("Saved in:", year_folder)


if __name__ == "__main__":
    run()
