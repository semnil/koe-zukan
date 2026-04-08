#!/usr/bin/env python3
"""
build.py — Excel → 静的サイト生成スクリプト

data/animal-sounds-data.xlsx を読み込み、dist/ に静的サイトを出力する。
依存: openpyxl, Pillow (pip install openpyxl Pillow)

使い方:
    python scripts/build.py
"""

import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path

try:
    import openpyxl
except ImportError:
    print("Error: openpyxl is required. Install with: pip install openpyxl")
    sys.exit(1)

# ── Paths ─────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "animal-sounds-data.xlsx"
DIST_DIR = PROJECT_ROOT / "dist"
TEMPLATE_FILE = PROJECT_ROOT / "templates" / "index.html"
ASSETS_DIR = PROJECT_ROOT / "assets"
NO_AUDIO_FILE = PROJECT_ROOT / "data" / "no-audio.json"
SITE_URL = "https://koe-zukan.semnil.com"


def _load_no_audio():
    """Load taxonCodes with no audio on Macaulay Library."""
    if NO_AUDIO_FILE.exists():
        with open(NO_AUDIO_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


_NO_AUDIO = _load_no_audio()


def _build_audio_ref(aid, scientific_name, taxon_code):
    """Build audio reference URL from taxonCode.

    Birds use xeno-canto (by scientific name).
    Others use Macaulay Library (by taxonCode), skipped if no audio.
    """
    if not scientific_name:
        return ""
    if aid.startswith("B"):
        # xeno-canto: Genus-species format
        parts = scientific_name.split()
        if len(parts) >= 2:
            return f"https://xeno-canto.org/species/{parts[0]}-{parts[1]}"
        return ""
    if taxon_code and taxon_code not in _NO_AUDIO:
        return f"https://search.macaulaylibrary.org/catalog?taxonCode={taxon_code}&mediaType=audio"
    return ""


def extract_data(wb):
    """Excel workbook → Python dicts"""

    # ── 名称マッピング ──
    ws_name = wb["名称マッピング"]
    name_map = {}
    for row in ws_name.iter_rows(min_row=2, values_only=True):
        if row[0]:
            name_map[str(row[0])] = {
                "scientificName": row[2] or "",
                "englishName": row[3] or "",
                "altJA": row[4] or "",
                "altEN": row[5] or "",
            }

    # ── オノマトペマッピング ──
    ws_ono = wb["オノマトペマッピング"]
    ono_map = {}
    for row in ws_ono.iter_rows(min_row=2, values_only=True):
        if row[0]:
            aid = str(row[0])
            if aid not in ono_map:
                ono_map[aid] = []
            ono_map[aid].append({
                "lang": row[2] or "",
                "langName": row[3] or "",
                "onomatopoeia": row[4] or "",
                "scene": row[5] or "",
                "note": row[6] or "",
            })

    # ── 地域マスター ──
    ws_rm = wb["地域マスター"]
    region_master = {}
    for row in ws_rm.iter_rows(min_row=2, values_only=True):
        if row[0]:
            region_master[str(row[0])] = {
                "nameJA": row[1] or "",
                "nameEN": row[2] or "",
                "areaCode": row[3] or "",
            }

    # ── 地域マッピング ──
    ws_reg = wb["地域マッピング"]
    region_map = {}
    for row in ws_reg.iter_rows(min_row=2, values_only=True):
        if row[0]:
            aid = str(row[0])
            rid = str(row[2]) if row[2] else ""
            if aid not in region_map:
                region_map[aid] = []
            if rid:
                region_map[aid].append(rid)

    # ── 分類マッピング ──
    ws_tax = wb["分類マッピング"]
    tax_map = {}
    for row in ws_tax.iter_rows(min_row=2, values_only=True):
        if row[0] and row[1]:
            tax_map[(str(row[0]), str(row[1]))] = {
                "scientificName": row[2] or "",
                "englishName": row[3] or "",
            }

    # ── メインデータ → animals ──
    ws = wb["メインデータ"]
    animals = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        aid = str(row[0])
        names = name_map.get(aid, {})
        onos = ono_map.get(aid, [])
        regions = region_map.get(aid, [])

        resolved_regions = []
        for rid in regions:
            rm = region_master.get(rid, {})
            resolved_regions.append({
                "id": rid,
                "nameJA": rm.get("nameJA", ""),
                "nameEN": rm.get("nameEN", ""),
            })

        class_en = tax_map.get(("綱", str(row[3])), {}).get("englishName", "") if row[3] else ""
        order_en = tax_map.get(("目", str(row[4])), {}).get("englishName", "") if row[4] else ""
        family_en = tax_map.get(("科", str(row[5])), {}).get("englishName", "") if row[5] else ""

        animal = {
            "id": aid,
            "nameJA": row[1] or "",
            "scientificName": names.get("scientificName", ""),
            "nameEN": names.get("englishName", ""),
            "altJA": names.get("altJA", ""),
            "altEN": names.get("altEN", ""),
            "phylum": row[2] or "",
            "class": row[3] or "",
            "classEN": class_en,
            "order": row[4] or "",
            "orderEN": order_en,
            "family": row[5] or "",
            "familyEN": family_en,
            "hasVoice": row[6] or "",
            "onomatopoeiaJA": row[7] or "",
            "voiceMethod": row[8] or "",
            "habitat": row[9] or "",
            "conservation": row[10] or "",
            "imageRef": row[11] or "",
            "note": row[12] or "",
            "audioRef": _build_audio_ref(aid, names.get("scientificName", ""),
                                         row[14] if len(row) > 14 else ""),
            "onomatopoeia": onos,
            "regions": resolved_regions,
        }
        animals.append(animal)

    # ── 地域マスター (flat) ──
    regions_data = []
    for rid, rm in sorted(region_master.items()):
        regions_data.append({"id": rid, **rm})

    return animals, regions_data


def build_stats(animals):
    """Generate stats for template injection."""
    total = len(animals)
    ono_count = sum(len(a["onomatopoeia"]) for a in animals)
    langs = set()
    for a in animals:
        for o in a["onomatopoeia"]:
            if o["lang"]:
                langs.add(o["lang"])
    return {
        "total_species": total,
        "total_onomatopoeia": ono_count,
        "languages": sorted(langs),
        "language_count": len(langs),
    }


def write_json(data, filepath):
    """Write JSON with UTF-8, no ASCII escaping."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(filepath)
    print(f"  {filepath.name}: {size:,} bytes")


def generate_html(animals, template_path, output_path):
    """Read HTML template and inject data if template exists."""
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        # Fallback: copy from dist if template doesn't exist yet
        fallback = output_path
        if fallback.exists():
            print(f"  Using existing {fallback.name} (no template found)")
            return
        print(f"  WARNING: No template at {template_path} and no existing {output_path.name}")
        return

    # Inject stats into HTML
    stats = build_stats(animals)
    html = html.replace(
        "258 species / 4 languages",
        f"{stats['total_species']} species / {stats['language_count']} languages"
    )
    html = html.replace(
        "Data: 258 species, 572 onomatopoeia entries across 4 languages",
        f"Data: {stats['total_species']} species, {stats['total_onomatopoeia']} onomatopoeia entries across {stats['language_count']} languages"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(output_path)
    print(f"  {output_path.name}: {size:,} bytes")


def generate_ogp(stats, output_path):
    """Generate OGP image (1200x630) with dynamic stats."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  WARNING: Pillow not installed, skipping OGP image generation")
        return

    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (42, 38, 52))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(H):
        r = int(42 + (58 - 42) * y / H)
        g = int(38 + (48 - 38) * y / H)
        b = int(52 + (68 - 52) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Cat silhouette from favicon.svg
    raw_points = [
        (32.0, 15.0), (36.1, 15.1), (38.6, 15.5), (40.6, 15.8),
        (42.1, 15.5), (43.3, 14.2), (45.0, 12.4), (46.6, 11.0),
        (50.8, 7.1), (53.4, 4.8), (56.9, 3.3), (59.0, 3.2),
        (60.6, 4.8), (61.3, 7.0), (61.8, 9.6), (62.0, 12.9),
        (61.9, 17.6), (61.4, 23.6), (60.2, 29.6), (60.4, 32.1),
        (61.2, 35.0), (61.8, 38.9), (61.0, 44.9), (58.5, 50.4),
        (55.2, 54.1), (52.3, 56.2), (49.2, 57.8), (45.9, 59.1),
        (42.9, 59.9), (39.7, 60.5), (36.6, 60.7), (34.0, 60.8),
        (32.0, 60.8),
        (30.0, 60.8), (27.4, 60.7), (24.3, 60.5),
        (21.1, 59.9), (18.1, 59.1), (14.8, 57.8), (11.7, 56.2),
        (8.8, 54.1), (5.5, 50.4), (3.0, 44.9), (2.2, 38.9),
        (2.8, 35.0), (3.6, 32.1), (3.8, 29.6), (2.6, 23.6),
        (2.1, 17.6), (2.0, 12.9), (2.2, 9.6), (2.7, 7.0),
        (3.4, 4.8), (5.0, 3.2), (7.1, 3.3), (10.6, 4.8),
        (13.2, 7.1), (17.4, 11.0), (19.0, 12.4), (20.7, 14.2),
        (21.9, 15.5), (23.4, 15.8), (25.4, 15.5), (27.9, 15.1),
        (32.0, 15.0),
    ]
    cx, cy, size = 200, 315, 280
    scale = size / 64.0
    points = [(cx + (x - 32) * scale, cy + (y - 38) * scale) for x, y in raw_points]
    draw.polygon(points, fill=(91, 74, 122))

    # Fonts
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 52)
        sub_font = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 24)
        en_font = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 20)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        en_font = ImageFont.load_default()

    white = (255, 255, 255)
    light = (200, 195, 210)
    draw.text((440, 200), "動物の鳴き声図鑑", fill=white, font=title_font)
    draw.text((440, 280), "Animal Sound Encyclopedia", fill=light, font=en_font)
    draw.text((440, 340),
              f"{stats['total_species']}種 × {stats['language_count']}言語のオノマトペを収録",
              fill=light, font=sub_font)
    draw.rectangle([(440, 380), (750, 383)], fill=(5, 150, 105))

    img.save(output_path, "PNG", optimize=True)
    size = os.path.getsize(output_path)
    print(f"  {output_path.name}: {size:,} bytes")


def generate_sitemap(animals, output_path):
    """Generate sitemap.xml with top page and deep links for each species."""
    today = date.today().isoformat()
    urls = [f'  <url><loc>{SITE_URL}/</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>']
    for a in animals:
        urls.append(f'  <url><loc>{SITE_URL}/?id={a["id"]}</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n"
           '</urlset>\n')
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml)
    size = os.path.getsize(output_path)
    print(f"  {output_path.name}: {size:,} bytes ({len(urls)} URLs)")


def main():
    print(f"=== koe-zukan build ===")
    print(f"Data source: {DATA_FILE}")
    print(f"Output dir:  {DIST_DIR}")
    print()

    if not DATA_FILE.exists():
        print(f"Error: Data file not found: {DATA_FILE}")
        sys.exit(1)

    # Load Excel
    print("Loading Excel...")
    wb = openpyxl.load_workbook(DATA_FILE, data_only=True)
    print(f"  Sheets: {wb.sheetnames}")

    # Extract data
    print("Extracting data...")
    animals, regions = extract_data(wb)
    stats = build_stats(animals)
    print(f"  Species: {stats['total_species']}")
    print(f"  Onomatopoeia: {stats['total_onomatopoeia']}")
    print(f"  Languages: {', '.join(stats['languages'])}")

    # Ensure dist directory
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Write JSON
    print("Writing JSON...")
    write_json(animals, DIST_DIR / "animals.json")
    write_json(regions, DIST_DIR / "regions.json")

    # Generate HTML
    print("Generating HTML...")
    generate_html(animals, TEMPLATE_FILE, DIST_DIR / "index.html")

    # Generate sitemap
    print("Generating sitemap...")
    generate_sitemap(animals, DIST_DIR / "sitemap.xml")

    # CNAME for GitHub Pages custom domain
    cname_domain = SITE_URL.replace("https://", "").replace("http://", "").rstrip("/")
    with open(DIST_DIR / "CNAME", "w") as f:
        f.write(cname_domain + "\n")
    print(f"  CNAME: {cname_domain}")

    # Generate OGP image
    print("Generating OGP image...")
    generate_ogp(stats, DIST_DIR / "ogp.png")

    # Copy assets
    if ASSETS_DIR.exists():
        print("Copying assets...")
        for src in ASSETS_DIR.iterdir():
            if src.is_file():
                dst = DIST_DIR / src.name
                shutil.copy2(src, dst)
                print(f"  {src.name}: {os.path.getsize(dst):,} bytes")

    print()
    print(f"Build complete! {stats['total_species']} species → {DIST_DIR}/")
    print(f"Deploy the contents of {DIST_DIR}/ to Cloudflare Pages.")


if __name__ == "__main__":
    main()
