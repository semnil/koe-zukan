#!/usr/bin/env python3
"""
check_audio.py — Macaulay Library に音声が存在するか確認し、スキップリストを生成

taxonCode ごとに ML API を叩き、音声 0 件の taxonCode を
data/no-audio.json に書き出す。build.py はこのファイルを参照して
audioRef 生成をスキップする。

使い方:
    python scripts/check_audio.py
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

try:
    import openpyxl
except ImportError:
    print("Error: openpyxl required. pip install openpyxl")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "animal-sounds-data.xlsx"
OUTPUT_FILE = PROJECT_ROOT / "data" / "no-audio.json"

API_URL = "https://search.macaulaylibrary.org/api/v1/search"
DELAY = 0.3


def check_audio(taxon_code):
    """Return number of audio results for a taxonCode."""
    url = f"{API_URL}?taxonCode={taxon_code}&mediaType=audio"
    req = urllib.request.Request(url, headers={"User-Agent": "koe-zukan-build/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return len(data.get("results", {}).get("content", []))
    except Exception as e:
        print(f"  ERROR {taxon_code}: {e}")
        return -1


def main():
    wb = openpyxl.load_workbook(DATA_FILE, data_only=True)
    ws = wb["メインデータ"]

    # Collect all taxonCodes (column O = index 14)
    entries = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        aid = str(row[0])
        taxon_code = str(row[14]) if len(row) > 14 and row[14] else ""
        if taxon_code:
            entries.append((aid, taxon_code))

    print(f"Checking {len(entries)} taxonCodes...")

    no_audio = []
    has_audio = 0
    errors = 0

    for aid, code in entries:
        count = check_audio(code)
        if count == 0:
            no_audio.append(code)
            print(f"  {aid} {code}: NO AUDIO")
        elif count < 0:
            errors += 1
        else:
            has_audio += 1
        time.sleep(DELAY)

    print(f"\nHas audio: {has_audio}, No audio: {len(no_audio)}, Errors: {errors}")

    # Write skip list
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(no_audio), f, indent=2)
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
