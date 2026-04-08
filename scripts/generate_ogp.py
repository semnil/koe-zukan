#!/usr/bin/env python3
"""
generate_ogp.py — OGP画像 (1200x630) を生成

favicon.svg の猫シルエットをモチーフに、サイト名とタグラインを配置した
OGP画像を assets/ogp.png として出力する。build.py が dist/ にコピーする。

依存: Pillow (pip install Pillow)
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "assets" / "ogp.png"

WIDTH, HEIGHT = 1200, 630


def draw_cat_silhouette(draw, cx, cy, size, color):
    """Draw simplified cat head silhouette as a filled polygon."""
    # Simplified cat outline from favicon.svg, scaled to `size`
    # Original viewBox: 0 0 64 64, center at (32, 32)
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
    scale = size / 64.0
    points = [(cx + (x - 32) * scale, cy + (y - 38) * scale) for x, y in raw_points]
    draw.polygon(points, fill=color)


def main():
    # Background: dark gradient-like solid
    bg_color = (42, 38, 52)
    img = Image.new("RGB", (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)

    # Subtle gradient effect with rectangles
    for y in range(HEIGHT):
        r = int(42 + (58 - 42) * y / HEIGHT)
        g = int(38 + (48 - 38) * y / HEIGHT)
        b = int(52 + (68 - 52) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Cat silhouette (semi-transparent effect via lighter color)
    cat_color = (91, 74, 122)  # #5b4a7a from favicon gradient
    draw_cat_silhouette(draw, 200, 315, 280, cat_color)

    # Text
    white = (255, 255, 255)
    light = (200, 195, 210)

    # Try system fonts
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 52)
        sub_font = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 24)
        en_font = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 20)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        en_font = ImageFont.load_default()

    # Title
    draw.text((440, 200), "動物の鳴き声図鑑", fill=white, font=title_font)

    # Subtitle
    draw.text((440, 280), "Animal Sound Encyclopedia", fill=light, font=en_font)

    # Stats line
    draw.text((440, 340), "305種 × 4言語のオノマトペを収録", fill=light, font=sub_font)

    # Accent line
    draw.rectangle([(440, 380), (750, 383)], fill=(5, 150, 105))  # --accent color

    # URL
    draw.text((440, 400), "koe-zukan.muddy-forest-7547.workers.dev", fill=(150, 145, 160), font=en_font)

    img.save(OUTPUT_FILE, "PNG", optimize=True)
    print(f"OGP image saved: {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
