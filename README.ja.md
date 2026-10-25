# koe-zukan（声図鑑）

多言語対応の動物オノマトペ検索サイト。動物の鳴き声を日本語・英語・韓国語・中国語のオノマトペで検索・比較できます。

> For the English version, see [README.md](README.md).

## Features

- 動物データとオノマトペ（4言語）
- あいまい検索（和名・英名・学名・オノマトペすべて対象）
- 綱別フィルタ（鳥綱・哺乳綱・昆虫綱・両生綱・爬虫綱・魚綱 他）
- 言語切り替え表示（日本語 / English / 한국어 / 中文）
- Wikimedia Commons 画像参照、xeno-canto / Macaulay Library 音声参照
- 完全静的サイト — バックエンド不要、GitHub Pages で公開（https://koe-zukan.semnil.com）

## Quick Start

```bash
# 依存インストール
pip3 install --user --break-system-packages openpyxl Pillow

# ビルド（Excel → 静的サイト）
python3 scripts/build.py

# ローカルプレビュー
python3 -m http.server 8080 --directory dist
# http://localhost:8080 を開く
```

## Project Structure

```
koe-zukan/
├── .github/workflows/            # テストと GitHub Pages へのデプロイ、workflow の検査、Dependabot の自動マージ
├── assets/
│   └── favicon.svg               # サイトアイコン（PWA アイコンの元）
├── data/
│   ├── animal-sounds-data.xlsx   # マスターデータ
│   └── no-audio.json             # Macaulay Library に音声がない taxonCode
├── scripts/
│   └── build.py                  # Excel → JSON + HTML 生成
├── templates/
│   ├── index.html                # メインページのテンプレート
│   └── species.html              # 種ページのテンプレート
├── tests/                        # pytest と node --test のテスト
├── docs/                         # 検証・監査レポート
├── dist/                         # ビルド出力（デプロイ対象、git 管理外）
│   ├── index.html
│   ├── animals.json
│   ├── regions.json
│   └── species/{ID}/index.html
├── CLAUDE.md                     # 詳細な技術仕様
├── README.md
└── README.ja.md
```

## Deploy

pull request と `master` への push のたびに `.github/workflows/deploy.yml` がテストを実行し、`python scripts/build.py` でサイトをビルドします。`master` への push では、続けて `dist/` を GitHub Pages へデプロイします。公開先は https://koe-zukan.semnil.com です。

Dependabot の pull request のうち patch か minor の更新は、必須チェックが通ると自動でマージされます (`.github/workflows/dependabot-auto-merge.yml`)。

## Data Editing

マスターデータは `data/animal-sounds-data.xlsx` で管理しています。Excel ファイルの編集後に `python3 scripts/build.py` を実行すると `dist/` が再生成されます。

データ構造の詳細は [CLAUDE.md](CLAUDE.md) を参照してください。

## License

TBD
