import argparse
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SRC = HERE / "src"

STAGES = [
    ("Stage 1 — download missing official PTR PDFs", SRC / "stage1_download.py"),
    ("Stage 2 — archive XML and verify PDF completeness", SRC / "stage2_verify.py"),
    ("Stage 3 — extract V8.1 transaction data", SRC / "stage3_extract.py"),
    ("Stage 4 — resolve tickers and save V8.2", SRC / "stage4_clean.py"),
    ("Publish — create stable website CSV + metadata", SRC / "publish_latest.py"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-stage",
        type=int,
        default=1,
        choices=[1, 2, 3, 4, 5],
        help="Start at this stage (5 means publish-only).",
    )
    args = parser.parse_args()

    for index, (title, script) in enumerate(STAGES, start=1):
        if index < args.from_stage:
            continue

        print()
        print("=" * 88)
        print(title)
        print("=" * 88)

        subprocess.run(
            [sys.executable, str(script)],
            check=True,
        )

    print()
    print("HOUSE PTR PIPELINE FINISHED")


if __name__ == "__main__":
    main()
