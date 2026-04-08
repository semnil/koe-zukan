# koe-zukan（声図鑑）

多言語対応の動物オノマトペ検索サイト。動物の鳴き声を日本語・英語・韓国語・中国語のオノマトペで検索・比較できます。

## Features

- 258種の動物データ、572件のオノマトペ（4言語）
- あいまい検索（和名・英名・学名・オノマトペすべて対象）
- 綱別フィルタ（鳥綱・哺乳綱・昆虫綱・両生綱・爬虫綱・魚綱 他）
- 言語切り替え表示（日本語 / English / 한국어 / 中文）
- Wikimedia Commons 画像参照、xeno-canto / Macaulay Library 音声参照
- 完全静的サイト — バックエンド不要、Cloudflare Pages Free プランで運用

## Quick Start

```bash
# 依存インストール
pip install openpyxl

# ビルド（Excel → 静的サイト）
python scripts/build.py

# ローカルプレビュー
cd dist && python -m http.server 8080
# http://localhost:8080 を開く
```

## Project Structure

```
koe-zukan/
├── data/
│   └── animal-sounds-data.xlsx   # マスターデータ
├── scripts/
│   └── build.py                  # Excel → JSON + HTML 生成
├── templates/
│   └── index.html                # HTMLテンプレート
├── dist/                         # ビルド出力（デプロイ対象）
│   ├── index.html
│   ├── animals.json
│   └── regions.json
├── CLAUDE.md                     # 詳細な技術仕様
└── README.md
```

## Deploy to Cloudflare Pages

1. このリポジトリを GitHub に push
2. [Cloudflare Dashboard](https://dash.cloudflare.com) → Workers & Pages → Create → Pages → Connect to Git
3. ビルド設定:
   - Build command: `pip install openpyxl && python scripts/build.py`
   - Build output directory: `dist`
4. デプロイ完了 → `https://<project>.pages.dev` で公開

## Data Editing

マスターデータは `data/animal-sounds-data.xlsx` で管理しています。Excel ファイルの編集後に `python scripts/build.py` を実行すると `dist/` が再生成されます。

データ構造の詳細は [CLAUDE.md](CLAUDE.md) を参照してください。

## License

TBD
