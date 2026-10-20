# koe-zukan (声図鑑)

A multilingual animal onomatopoeia search site. Search and compare animal sounds through their onomatopoeia in Japanese, English, Korean and Chinese.

> 日本語版は [README.ja.md](README.ja.md) を参照してください.

## Features

- Data for 258 animal species, 572 onomatopoeia entries (4 languages)
- Fuzzy search (covers Japanese names, English names, scientific names and onomatopoeia)
- Filter by class (Birds, Mammals, Insects, Amphibians, Reptiles, Fish and more)
- Switchable display language (日本語 / English / 한국어 / 中文)
- Image references to Wikimedia Commons, sound references to xeno-canto / Macaulay Library
- Fully static site — no backend needed, runs on the Cloudflare Pages Free plan

## Quick Start

```bash
# Install dependencies
pip install openpyxl

# Build (Excel → static site)
python scripts/build.py

# Local preview
cd dist && python -m http.server 8080
# Open http://localhost:8080
```

## Project Structure

```
koe-zukan/
├── data/
│   └── animal-sounds-data.xlsx   # Master data
├── scripts/
│   └── build.py                  # Generates JSON + HTML from Excel
├── templates/
│   └── index.html                # HTML template
├── dist/                         # Build output (deployed)
│   ├── index.html
│   ├── animals.json
│   └── regions.json
├── CLAUDE.md                     # Detailed technical specification
└── README.md
```

## Deploy to Cloudflare Pages

1. Push this repository to GitHub
2. [Cloudflare Dashboard](https://dash.cloudflare.com) → Workers & Pages → Create → Pages → Connect to Git
3. Build settings:
   - Build command: `pip install openpyxl && python scripts/build.py`
   - Build output directory: `dist`
4. When the deploy finishes → published at `https://<project>.pages.dev`

## Data Editing

The master data is kept in `data/animal-sounds-data.xlsx`. After editing the Excel file, run `python scripts/build.py` to regenerate `dist/`.

See [CLAUDE.md](CLAUDE.md) for the details of the data structure.

## License

TBD
