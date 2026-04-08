# koe-zukan

多言語対応の動物オノマトペ検索サイト。Excelマスターデータから静的サイトを生成し、Cloudflare Pagesでホスティングする。

## ディレクトリ構成

```
koe-zukan/
├── CLAUDE.md              ← このファイル
├── data/
│   └── animal-sounds-data.xlsx  ← マスターデータ（唯一の真のソース）
├── scripts/
│   └── build.py           ← Excel → dist/ 変換スクリプト
├── templates/
│   └── index.html         ← HTMLテンプレート（fetchでJSON読み込み）
└── dist/                  ← ビルド出力（Cloudflare Pagesデプロイ対象）
    ├── index.html
    ├── animals.json
    └── regions.json
```

## ビルド

```bash
python scripts/build.py
```

依存: `openpyxl`（`pip install openpyxl`）

`data/animal-sounds-data.xlsx` を読み込み、`dist/` に静的サイトを出力する。
Cloudflare Pages のデプロイ対象は `dist/` ディレクトリのみ。

## Excel シート構成（7シート）

| シート | 内容 | 主キー |
|---|---|---|
| メインデータ | 258種の基本情報（14列） | ID |
| 名称マッピング | 和名・学名・英名・別名 | ID |
| 分類マッピング | 門/綱/目/科の多言語名称 | (分類レベル, 和名) |
| オノマトペマッピング | 4言語のオノマトペ+場面 | (ID, 言語コード) |
| 凡例・定義 | IUCN区分・発声方法等の定義 | — |
| 地域マスター | 26地域の正規化マスター | 地域ID |
| 地域マッピング | 動物×地域の多対多マッピング | (ID, 地域ID) |

### メインデータ列（A〜N）

ID, 和名, 門, 綱, 目, 科, 鳴き声の有無, オノマトペ（日本語）, 発声方法, 生息地域, 保全状況, 画像参照, 備考, 音声参照

### ID体系

- A: 初期サンプル（A001〜A003）
- B: 鳥類（B001〜B095、B002欠番）
- M: 哺乳類（M001〜M068）
- I: 昆虫（I001〜I033）
- F: 両生類（F001〜F029）
- R: 爬虫類（R001〜R015）
- S: 魚類（S001〜S012）
- V: 無脊椎動物（V001〜V006）

### 言語コード

- `ja`: 日本語（252件）
- `en`: English（250件）
- `ko`: 한국어（35件、パイロット）
- `zh`: 中文（35件、パイロット）

## サイト技術構成

- 完全静的サイト（バックエンド不要）
- フロントエンド検索: Fuse.js（CDN読み込み）
- データ: ビルド時にExcel→JSON変換、ページロード時にfetchしてインメモリ検索
- レスポンシブ対応（モバイル含む）
- Cloudflare Pages Free プラン（月額0円、独自ドメインのみ年額約1,500円）

## 検索対象フィールド

Fuse.jsインデックスに含まれるフィールドと重み:

| フィールド | weight | 説明 |
|---|---|---|
| nameJA | 3.0 | 和名（最優先） |
| onomatopoeiaJA | 2.5 | 日本語オノマトペ |
| onomatopoeia.onomatopoeia | 2.5 | 全言語のオノマトペ |
| nameEN | 2.0 | 英名 |
| scientificName | 1.5 | 学名 |
| altJA, altEN | 1.0 | 別名 |
| voiceMethod | 0.5 | 発声方法 |
| family, order | 0.5 | 分類（科・目） |

## 外部リンク参照

- 画像参照: `https://commons.wikimedia.org/wiki/Category:{学名}`
- 音声参照（鳥類）: `https://xeno-canto.org/species/{学名}`
- 音声参照（その他）: `https://search.macaulaylibrary.org/catalog?...q={学名}`

## データ編集時の注意

- マスターデータは `data/animal-sounds-data.xlsx` のみ。`dist/` 内のJSONを直接編集しない。
- 種を追加する際は全関連シート（メインデータ、名称マッピング、オノマトペマッピング、地域マッピング）に整合的に追加すること。
- IDは各カテゴリの連番を維持する（欠番は埋めない）。
- 編集後は `python scripts/build.py` で再ビルドする。

## 今後の拡張候補

- 韓国語・中国語オノマトペの拡充（現在35種ずつ→全種へ）
- 第5言語以降の追加（オノマトペマッピングに行を追加するだけで対応可能）
- 個別種ページの生成（SEO対策）
- OGP / メタデータの動的生成
- PWA対応（オフライン閲覧）
