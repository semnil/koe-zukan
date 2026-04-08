# koe-zukan

多言語対応の動物オノマトペ検索サイト。Excelマスターデータから静的サイトを生成し、GitHub Pages でホスティングする。

- サイト URL: https://koe-zukan.semnil.com
- リポジトリ: https://github.com/semnil/koe-zukan (private)

## ディレクトリ構成

```
koe-zukan/
├── CLAUDE.md              ← このファイル
├── .github/
│   ├── FUNDING.yml        ← GitHub Sponsors
│   └── workflows/
│       └── deploy.yml     ← GitHub Pages デプロイ (Python 3.12 + openpyxl + Pillow)
├── data/
│   ├── animal-sounds-data.xlsx  ← マスターデータ（唯一の真のソース）
│   └── no-audio.json      ← Macaulay Library 音声なしリスト (check_audio.py で生成)
├── scripts/
│   ├── build.py           ← Excel → dist/ 変換スクリプト (メイン)
│   ├── add_species.py     ← 種の一括追加スクリプト
│   ├── add_kanji_names.py ← 漢字名の一括追加スクリプト
│   ├── add_ko_zh_onomatopoeia.py ← 韓国語・中国語オノマトペ一括追加
│   ├── fetch_taxon_codes.py ← ML taxonCode 取得スクリプト
│   └── check_audio.py     ← ML 音声有無チェック → no-audio.json 生成
├── assets/
│   └── favicon.svg        ← 猫シルエット (紫グラデーション, 左右対称)
├── templates/
│   ├── index.html         ← メインページテンプレート（プレースホルダー: {{SITE_URL}}, {{SPECIES_COUNT}} 等）
│   └── species.html       ← 個別種ページテンプレート（SEO 用、JSON-LD 構造化データ）
├── tests/
│   ├── test_build.py      ← build.py ユニットテスト (pytest)
│   └── test_frontend.mjs  ← フロントエンドロジックテスト (node --test)
├── docs/
│   └── verification-report.md ← ソフトウェア検証レポート (V001-V012)
└── dist/                  ← ビルド出力（GitHub Pages デプロイ対象、gitignore）
    ├── index.html         ← テンプレートから生成（プレースホルダー置換済み）
    ├── animals.json
    ├── regions.json
    ├── sitemap.xml        ← Google 用サイトマップ (全種 /species/{ID}/ URL)
    ├── ogp.png            ← トップページ OGP 画像 (1200x630, Pillow で動的生成)
    ├── manifest.json      ← PWA マニフェスト
    ├── sw.js              ← Service Worker (キャッシュファースト)
    ├── favicon.svg
    ├── CNAME              ← GitHub Pages カスタムドメイン
    └── species/{ID}/      ← 個別種ページ (305 ディレクトリ)
        ├── index.html     ← 種ページ HTML (JSON-LD, OGP, 共有ボタン)
        └── ogp.png        ← 種別 OGP 画像 (オノマトペ 4 言語表示)
```

## ビルド

```bash
pip install openpyxl Pillow
python scripts/build.py
```

`data/animal-sounds-data.xlsx` を読み込み、`dist/` に静的サイトを出力する。

### ビルド出力物

- `animals.json`, `regions.json` — Excel から変換した JSON データ
- `index.html` — テンプレートからプレースホルダーを置換して生成
- `species/{ID}/index.html` — 個別種ページ (305 ページ、JSON-LD + OGP + 共有ボタン)
- `species/{ID}/ogp.png` — 種別 OGP 画像 (オノマトペ 4 言語表示、CJK 言語別フォント)
- `sitemap.xml` — トップページ + 全種の `/species/{ID}/` ディープリンク
- `ogp.png` — トップページ OGP 画像 (Pillow で動的生成、種数・言語数を反映)
- `manifest.json` — PWA マニフェスト
- `sw.js` — Service Worker (バージョン付きキャッシュ、cache-first 戦略)
- `CNAME` — `SITE_URL` から自動生成

### テンプレートプレースホルダー

#### index.html

| プレースホルダー | 内容 |
|---|---|
| `{{SITE_URL}}` | サイト URL (build.py の `SITE_URL` 定数) |
| `{{SPECIES_COUNT}}` | 種数 |
| `{{LANGUAGE_COUNT}}` | 言語数 |
| `{{ONOMATOPOEIA_COUNT}}` | オノマトペ総数 |

#### species.html

| プレースホルダー | 内容 |
|---|---|
| `{{SITE_URL}}` | サイト URL |
| `{{ID}}` | 種 ID |
| `{{NAME_JA}}`, `{{NAME_EN}}` | 和名、英名 |
| `{{SCIENTIFIC_NAME}}` | 学名 |
| `{{ALT_EN}}` | 英名別名 (括弧付き or 空) |
| `{{CLASS}}`, `{{ORDER}}`, `{{FAMILY}}` | 綱、目、科 |
| `{{VOICE_METHOD}}` | 発声方法 (なければ「—」) |
| `{{CONSERVATION}}` | 保全状況 (IUCN コード + 日本語ラベル) |
| `{{REGIONS}}` | 生息地域 (読点区切り) |
| `{{NOTE}}` | 備考 HTML (なければ空) |
| `{{DESCRIPTION}}` | meta description |
| `{{ONO_SECTION}}` | オノマトペセクション HTML |
| `{{LINKS}}` | 外部リンク HTML |
| `{{SHARE_BUTTONS}}` | 共有ボタン HTML |

未置換プレースホルダーはビルド時に警告出力される (`_apply_placeholders`)。

## デプロイ

GitHub Actions (`.github/workflows/deploy.yml`) が master push 時に自動デプロイ。
GitHub Pages → カスタムドメイン `koe-zukan.semnil.com` (Route 53 CNAME → `semnil.github.io`)。

## Excel シート構成（7シート）

| シート | 内容 | 主キー |
|---|---|---|
| メインデータ | 305種の基本情報（15列、O列=taxonCode） | ID |
| 名称マッピング | 和名・学名・英名・別名・漢字名 | ID |
| 分類マッピング | 門/綱/目/科の多言語名称 | (分類レベル, 和名) |
| オノマトペマッピング | 4言語のオノマトペ+場面 | (ID, 言語コード) |
| 凡例・定義 | IUCN区分・発声方法等の定義 | — |
| 地域マスター | 26地域の正規化マスター | 地域ID |
| 地域マッピング | 動物×地域の多対多マッピング | (ID, 地域ID) |

### メインデータ列（A〜O）

ID, 和名, 門, 綱, 目, 科, 鳴き声の有無, オノマトペ（日本語）, 発声方法, 生息地域, 保全状況, 画像参照, 備考, 音声参照, taxonCode

### ID体系

- A: 初期サンプル（A001〜A005）
- B: 鳥類（B001〜B122、B002欠番）
- M: 哺乳類（M001〜M081）
- I: 昆虫（I001〜I044）
- F: 両生類（F001〜F033）
- R: 爬虫類（R001〜R020）
- S: 魚類（S001〜S018）
- V: 無脊椎動物（V001〜V012）

### 言語コード

- `ja`: 日本語
- `en`: English
- `ko`: 한국어
- `zh`: 中文

## サイト技術構成

- 完全静的サイト（バックエンド不要）
- フロントエンド検索: Fuse.js（CDN読み込み）
- ひらがな検索: カタカナ→ひらがな自動変換で「ねこ」「にゃー」等のひらがな入力に対応
- ブラウザ言語自動検出: `navigator.language` で初期表示言語を ja/en/ko/zh から自動選択
- データ: ビルド時にExcel→JSON変換、ページロード時にfetchしてインメモリ検索
- レスポンシブ対応（モバイル含む）
- OGP / Twitter Card 対応（トップページ + 個別種ページ、CJK 言語別フォント）
- 個別種ページ: `/species/{ID}/` (305 ページ、JSON-LD 構造化データ、canonical URL)
- 共有ボタン: X (Twitter), Facebook, LINE, URLコピー（モーダル + 種ページ両方）
- PWA 対応: manifest.json + Service Worker (キャッシュファースト戦略)
- URL パラメータ `?id=` でカード直接リンク
- Google Search Console 連携 (サイトマップ + 所有権確認メタタグ)

## 検索対象フィールド

Fuse.jsインデックスに含まれるフィールドと重み:

| フィールド | weight | 説明 |
|---|---|---|
| nameJA | 3.0 | 和名（最優先） |
| _hira | 3.0 | 和名ひらがな（カタカナ→ひらがな自動変換） |
| nameEN | 2.0 | 英名 |
| scientificName | 1.5 | 学名 |
| altJA | 1.0 | 別名（漢字名含む） |
| _altHira | 1.0 | 別名ひらがな |
| altEN | 1.0 | 英名別名 |
| onomatopoeiaJA | 2.5 | 日本語オノマトペ |
| _onoHira | 2.5 | 日本語オノマトペひらがな |
| onomatopoeia.onomatopoeia | 2.5 | 全言語のオノマトペ |
| _onoAllHira | 2.5 | 全言語オノマトペひらがな |
| voiceMethod | 0.5 | 発声方法 |
| family, order | 0.5 | 分類（科・目） |

`_hira` / `_altHira` / `_onoHira` / `_onoAllHira` はページロード時に `kataToHira()` で動的生成。「ねこ」で「ネコ」、「にゃー」で「ニャー」を検索可能。

## 外部リンク参照

- 画像参照: `https://commons.wikimedia.org/wiki/Category:{学名}`
- 音声参照（鳥類）: `https://xeno-canto.org/species/{Genus}-{species}`
- 音声参照（その他）: `https://search.macaulaylibrary.org/catalog?taxonCode={taxonCode}&mediaType=audio`
  - `data/no-audio.json` に登録された taxonCode はリンク非生成

## 音声参照の管理

1. `scripts/fetch_taxon_codes.py` — ML taxonomy API から taxonCode を取得し Excel O列に書き込み
2. `scripts/check_audio.py` — 各 taxonCode の音声有無を ML API で確認し `data/no-audio.json` に出力
3. `scripts/build.py` — no-audio.json を読み込み、音声なしの種は audioRef を空にする

手動実行スクリプト (CI では実行しない)。結果は JSON としてコミットする。

## データ編集時の注意

- マスターデータは `data/animal-sounds-data.xlsx` のみ。`dist/` 内のJSONを直接編集しない
- 種を追加する際は全関連シート（メインデータ、名称マッピング、オノマトペマッピング、地域マッピング）に整合的に追加すること
- IDは各カテゴリの連番を維持する（欠番は埋めない）
- 編集後は `python scripts/build.py` で再ビルドする

## テスト

```bash
# Python テスト (build.py)
python -m pytest tests/test_build.py -v

# JavaScript テスト (フロントエンドロジック)
node --test tests/test_frontend.mjs

# Python テスト + カバレッジ
python -m pytest tests/test_build.py --cov=scripts --cov-report=term-missing
```

## 今後の拡張候補

- 第5言語以降の追加（オノマトペマッピングに行を追加するだけで対応可能）
- Fuse.js のローカルバンドル（PWA オフライン完全対応）
