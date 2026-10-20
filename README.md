# koe-zukan (声図鑑)

A multilingual animal onomatopoeia search site. Search and compare animal sounds through their onomatopoeia in Japanese, English, Korean and Chinese.

> 日本語版は [README.ja.md](README.ja.md) を参照してください.

## Features

- Animal data and onomatopoeia (4 languages)
- Fuzzy search (covers Japanese names, English names, scientific names and onomatopoeia)
- Filter by class (Birds, Mammals, Insects, Amphibians, Reptiles, Fish and more)
- Switchable display language (日本語 / English / 한국어 / 中文)
- Image references to Wikimedia Commons, sound references to xeno-canto / Macaulay Library
- Fully static site — no backend needed, published on GitHub Pages (https://koe-zukan.semnil.com)

## Quick Start

```bash
# Install dependencies
pip3 install --user --break-system-packages openpyxl Pillow

# Build (Excel → static site)
python3 scripts/build.py

# Local preview
python3 -m http.server 8080 --directory dist
# Open http://localhost:8080
```

## Project Structure

```
koe-zukan/
├── .github/workflows/            # Deploy to GitHub Pages and the workflow checks
├── assets/
│   └── favicon.svg               # Site icon (source of the PWA icons)
├── data/
│   ├── animal-sounds-data.xlsx   # Master data
│   └── no-audio.json             # taxonCodes with no audio in the Macaulay Library
├── scripts/
│   └── build.py                  # Generates JSON + HTML from Excel
├── templates/
│   ├── index.html                # Main page template
│   └── species.html              # Species page template
├── tests/                        # pytest and node --test tests
├── docs/                         # Verification and audit reports
├── dist/                         # Build output (deployed, not tracked by git)
│   ├── index.html
│   ├── animals.json
│   ├── regions.json
│   └── species/{ID}/index.html
├── CLAUDE.md                     # Detailed technical specification
├── README.md
└── README.ja.md
```

## Deploy

Pushing to `master` runs `.github/workflows/deploy.yml`, which runs the tests, builds the site with `python scripts/build.py` and deploys `dist/` to GitHub Pages. The site is published at https://koe-zukan.semnil.com.

## Data Editing

The master data is kept in `data/animal-sounds-data.xlsx`. After editing the Excel file, run `python3 scripts/build.py` to regenerate `dist/`.

See [CLAUDE.md](CLAUDE.md) for the details of the data structure.

## License

TBD
