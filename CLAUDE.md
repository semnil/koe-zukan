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
│   ├── verification-report.md   ← ソフトウェア検証レポート (V001-V012 + V013 以降の監査ラウンド追記)
│   ├── ux-audit-report.md       ← UI/UX 監査レポート (ラウンド 1-3、WCAG 2.1 AA / 2.2 AA 適合確認)
│   └── quality-audit-report.md  ← 品質監査レポート (ラウンド 1-3、契約/構文/ピクセル検査)
└── dist/                  ← ビルド出力（GitHub Pages デプロイ対象、gitignore）
    ├── index.html         ← テンプレートから生成（プレースホルダー置換済み）
    ├── animals.json
    ├── regions.json
    ├── sitemap.xml        ← Google 用サイトマップ (トップページのみ)
    ├── ogp.png            ← トップページ OGP 画像 (1200x630, Pillow で動的生成)
    ├── icon-192.png       ← PWA アイコン 192x192 (Pillow 動的生成, maskable)
    ├── icon-512.png       ← PWA アイコン 512x512 (Pillow 動的生成, maskable)
    ├── manifest.json      ← PWA マニフェスト
    ├── sw.js              ← Service Worker (キャッシュファースト)
    ├── favicon.svg
    ├── CNAME              ← GitHub Pages カスタムドメイン
    └── species/{ID}/      ← 個別種ページ (305 ディレクトリ)
        ├── index.html     ← 種ページ HTML (JSON-LD, OGP, 共有ボタン, hreflang)
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
- `species/{ID}/index.html` — 個別種ページ (305 ページ、JSON-LD + OGP + 共有ボタン + hreflang 5 本)
- `species/{ID}/ogp.png` — 種別 OGP 画像 (オノマトペ 4 言語表示、CJK 言語別フォント)
- `sitemap.xml` — トップページのみ (種ページはインデックス効率のため除外)
- `ogp.png` — トップページ OGP 画像 (Pillow で動的生成、種数・言語数を反映)
- `icon-192.png` / `icon-512.png` — PWA 用 PNG アイコン (Pillow で `favicon.svg` から動的生成、`purpose: "any maskable"`)
- `manifest.json` — PWA マニフェスト (`lang`, `scope`, `icons` 配列に SVG + 192/512 PNG を登録)
- `sw.js` — Service Worker (バージョン付きキャッシュ、cache-first、navigate は `/` にフォールバック)
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
| `{{CLASS_CSS}}`, `{{CLASS_ICON}}` | 綱別のタグ CSS クラス・絵文字 (トップページと色/アイコン統一) |
| `{{VOICE_METHOD}}` | 発声方法 (なければ「—」) |
| `{{CONSERVATION}}` | 保全状況 (IUCN コード + 日本語ラベル) |
| `{{REGIONS}}` | 生息地域 (読点区切り) |
| `{{NOTE}}` | 備考 HTML (なければ空) |
| `{{DESCRIPTION}}` | meta description |
| `{{ONO_SECTION}}` | オノマトペセクション HTML (各 `ono-cell-text` に `lang` 属性付与) |
| `{{LINKS}}` | 外部リンク HTML (`aria-label`, `rel="noopener"`, 視覚的 `↗` マーク付き) |
| `{{SHARE_BUTTONS}}` | 共有ボタン HTML (X/Facebook/LINE/URL コピー) |
| `{{RELATED_SPECIES}}` | 同じ仲間の動物セクション HTML (family→order→class→phylum の 4 段フォールバック、最大 4 件、ID 昇順) |
| `{{JSON_HEADLINE}}`, `{{JSON_DESCRIPTION}}` | JSON-LD 用に `<`/`>`/`&` を `\u003c` 等にエスケープした文字列 |
| `{{SPECIES_DATA_JSON}}` | 種ページ用 i18n ペイロード (name/class/order/family/voiceMethod/regions の ja+en、conservation コード、4 言語 onomatopoeia 等)。インライン `<script>` 用に `<`/`>`/`&` を `\u003c` 等にエスケープした JSON リテラル |
| `{{RELATED_DATA_JSON}}` | 関連種の i18n ペイロード (各種の ja/en 名前 + ja/en/ko/zh オノマトペ)。同様に `<script>` 安全な JSON リテラル |

未置換プレースホルダーはビルド時に警告出力される (`_apply_placeholders`)。`SHARE_BUTTONS` は警告対象から除外し、後段で個別注入する (`RELATED_SPECIES` は `_build_related_html` 経由で値を渡すため通常置換)。

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
- ブラウザ言語自動検出: `navigator.language` で初期表示言語を ja/en/ko/zh から自動選択 (URL `?lang=` パラメータが最優先)。**非対応ロケールのフォールバックは英語** (フランス語・ドイツ語等の非 CJK 訪問者が読めない漢字を見ないため)。index.html / species.html の両方で同じ判定ロジック
- 詳細ページの多言語化: `/species/{ID}/` も 4 言語対応。`SPECIES_DATA` (build.py が name/class/order/family/voiceMethod/regions の ja+en、4 言語 onomatopoeia 等を埋め込み) と `I18N` 辞書 (ラベル + IUCN 保全状況訳) を組み合わせて DOM を書き換え。初期 HTML は日本語のまま (SEO / no-JS 訪問者向け)、JS が選択言語で上書き
- 言語タブの位置 (両ページ統一): index.html はヘッダー (`.header-inner` の右側)、species.html は top-bar の `←` リンクの右側。緑グラデーション帯上の半透明枠スタイルで揃え、`min-height: 44px` でタップターゲットも統一
- index↔species 間で表示言語を引き継ぐ: モーダルの「詳細ページで見る」「← 動物の鳴き声図鑑」「← 図鑑で表示」「同じ仲間の動物」内リンクに `?lang=<xx>` を付与 (ja のときは canonical 維持で付けない)
- データ: ビルド時にExcel→JSON変換、ページロード時にfetchしてインメモリ検索
- レスポンシブ対応（モバイル含む）
- OGP / Twitter Card 対応（トップページ + 個別種ページ、CJK 言語別フォント）
- 個別種ページ: `/species/{ID}/` (305 ページ、JSON-LD 構造化データ、canonical URL、hreflang ja/en/ko/zh/x-default は自身の `/species/{ID}/?lang=*` を指す)
- 共有ボタン: X (Twitter), Facebook, LINE, URLコピー（種ページのみ。各 aria-label とコピーフィードバックは表示言語に追従）
- PWA 対応: manifest.json + Service Worker (キャッシュファースト、192/512 PNG アイコン maskable)
- URL パラメータ `?id=` でカード直接リンク、`?q=` で初期検索クエリ (`WebSite` JSON-LD の SearchAction `urlTemplate` 契約)
- Google Search Console 連携 (サイトマップ + 所有権確認メタタグ)
- 関連種リンク: 種ページに「同じ仲間の動物」セクション (family→order→class→phylum の 4 段フォールバック、最大 4 件) — SEO 内部リンク強化

### コンテンツ差別化設計 (カード / モーダル / 種ページ)

| 項目 | カード | モーダル (プレビュー) | 種ページ (詳細) |
|---|---|---|---|
| 名前 | 和名 or 表示言語 | 表示言語 | 和名 + 英名 + 学名 |
| 綱/目/科 タグ | 綱のみ (アイコン付き) | 綱のみ | 綱/目/科 全階層 |
| オノマトペ | 表示言語 main のみ | 表示言語 (場面なし) | 4 言語 + 場面 |
| 外部リンク | なし | なし | あり (Wikipedia / xeno-canto / ML) |
| 共有ボタン | なし | なし | あり (X/Facebook/LINE/URLコピー) |
| 保全状況 | — | コードのみ | コード + 日本語ラベル |
| 関連種 | なし | なし | あり |
| 詳細リンク | あり (モーダル内) | あり (「詳細ページで見る →」) | — (自ページ) |

### 多言語 UI 定数 (index.html)

- `NO_VOICE_LABEL` — 「鳴き声なし」4 言語
- `NO_ONO_LABEL` — 「データなし」4 言語
- `MODAL_LABELS` — モーダル内ラベル (ono / info / voiceMethod / conservation / regions) 4 言語
- `MODAL_HINT` / `CLOSE_LABEL` — モーダル操作ヒント 4 言語
- `DETAIL_LINK_LABEL` — モーダル内「詳細ページで見る →」のテキスト 4 言語
- `VOICE_METHOD_EN` — 発声方法の日本語→英語マップ (27 エントリ。`scripts/build.py` の同名定数とミラー)
- `ALL_LABEL` — フィルタ「すべて」4 言語
- `SEARCH_LABELS` — 検索ボックス全要素 (label / placeholder / hint / clear / filters / langTabs / noResults / loading / loadError) 4 言語
- `getDisplayName(a)` — `displayLang` に応じた名前返却
- `getClassLabel(ci, a)` — `displayLang` に応じた綱ラベル
- `getVoiceMethod(vm)` — `displayLang` に応じた発声方法
- `getRegionName(r)` — `displayLang` に応じた地域名
- `updateFilterLabels()` / `updateSearchLabels()` — `applyDisplayLang` から呼び出される UI 更新

### 多言語 UI 定数 (species.html)

詳細ページは自己完結型で 4 言語切替できる。`applyLang(code)` が呼ばれると下記すべてを再適用する。

- `I18N[code]` — 1 言語あたり以下を持つ:
  - `htmlLang`, `siteName`, `title(name, alt)` — `<html lang>`、サイト名、`<title>` ビルダー
  - `skipLink`, `topBar`, `backLink` — ナビゲーション系テキスト
  - `onoSection`, `infoSection`, `linksSection`, `shareSection`, `related`, `note` — セクション見出し
  - `voiceMethod`, `conservation`, `regions` — `.detail-label` のテキスト
  - `langTabsLabel`, `siteNav`, `silentDash`, `noVoice` — その他ラベル
  - `copyLabel`, `copyOk`, `copyFail` — URL コピーボタンの 3 状態
  - `shareX`, `shareFB`, `shareLINE` — 共有ボタン aria-label
  - `ariaCommons`, `ariaXC`, `ariaML`, `ariaWikiJA`, `ariaWikiEN` — 外部リンク aria-label
  - `iucnLabel` — IUCN 保全状況 9 コードの訳辞書 (LC/NT/VU/EN/CR/DD/NE/EW/EX)
- `SPECIES_DATA` — 種固有データ (build.py 由来、上記プレースホルダー参照)。`applyLang` 時の値ソース
- `RELATED_DATA` — 関連種データ。`applyLang` 時に `.related-grid` を再描画
- DOM マーカー (build.py 側で付与):
  - `data-i18n="<key>"` — テキスト書き換え対象 (`L[key]` で textContent 置換)
  - `data-link-kind="commons|xc|ml|wiki-ja|wiki-en"` — 外部リンクの aria-label 切替対象
  - `data-share-kind="x|fb|line|copy"` — 共有ボタンの aria-label 切替対象 (`copy` は内部の `.copy-label` span を書き換え)
- ヘルパー: `detectLang()` (`?lang=` → `navigator.language` → en フォールバック)、`withLang(path, code)` (リンクへの lang 付与、ja のときは canonical 維持で無付与)、`renderLangTabs()` (top-bar 内の言語タブ生成)

### SEO 設定

- canonical URL:
  - トップページ: `<link rel="canonical" href="https://koe-zukan.semnil.com/">` — `?lang=` / `?id=` / `?q=` の各バリエーションを `/` に正規化
  - 種ページ: `<link rel="canonical" href=".../species/{ID}/">` — `?lang=` 付き URL を正規化
- 構造化データ (JSON-LD):
  - トップページ: `@type: WebSite` (name / alternateName / url / description / `inLanguage: [ja, en, ko, zh]` / `potentialAction: SearchAction`)。Google の Sitelinks Search Box 対象
  - SearchAction の `urlTemplate` は `https://koe-zukan.semnil.com/?q={search_term_string}` で、index.html の JS が `?q=` を受けて検索ボックスに投入 + `onSearch()` を実行
  - 種ページ: `@type: Article` (headline / description / url / publisher)。文字列は `_json_for_script()` で `<`/`>`/`&` を `<` 等にエスケープ済み
- サイトマップ: `dist/sitemap.xml` はトップページ 1 URL のみ。種ページは内部リンク (モーダル → 種ページ + 関連種) で発見可能だがサイトマップ非掲載
  - 理由: 種ページは「クロール済み - インデックス未登録」が大量発生したため除外 (コミット `8f76bf3` の方針)
- meta description / OGP / Twitter Card は両ページに設定。og:locale は初期 HTML が `ja_JP`、JS が選択言語に応じて `ja_JP` / `en_US` / `ko_KR` / `zh_CN` に書き換え (Bot は初期 HTML を参照するため SEO 影響は限定的)

### アクセシビリティ

- WCAG 2.1 AA および WCAG 2.2 追加 AA SC 適合 (UX 監査ラウンド 3 で全項目 Pass 判定)
- `<main id="main">` ランドマーク + `.skip-link`「コンテンツへスキップ」(index + species 両テンプレート)
- `<html lang>` は両ページとも表示言語切替に JS で同期 (初期値は `ja`)
- 局所 `lang` 属性: 英名に `lang="en"`、学名に `lang="la"`、オノマトペ `ono-cell-text` は言語別 (`ja`/`en`/`ko`/`zh`)、種ページの「alt-name」要素は表示言語に応じて `lang="ja"`/`lang="en"` に切替
- hreflang: トップページ (`/?lang=*`) + 全種ページ (`/species/{ID}/?lang=*`) の 5 本 (ja/en/ko/zh/x-default)。両ページの `x-default` は canonical URL (パラメータなし) を指す
- タップターゲット 44x44 以上: `.filter-btn`, `.lang-tab`, `.modal-close`, `.search-clear` に `min-height: 44px` / 固定 44x44 を明示
- フォーカス視覚指標: `:focus-visible` に `outline: 2px solid var(--accent)` をグローバル適用。検索ボックスは `.search-input-wrap:focus-within` で枠線 + 3px 半透明リングの二重指標 (SC 2.4.11 Focus Appearance)
- モーダル: `role="dialog"` + `aria-modal="true"` + `aria-labelledby` + focus trap + `_modalOpener` への前焦点復帰
- 検索結果件数は `aria-live="polite" aria-atomic="true"` で告知 (4 言語対応)
- 外部リンク: `rel="noopener"` + `aria-label="... (新しいタブで開く)"` + 視覚的 `↗` マーク
- フォーム: `<form role="search">` ランドマーク + `<label class="sr-only">` + SVG アイコンは `aria-hidden="true"`
- IME 対応: `compositionstart`/`compositionend` で検索 debounce をブロック

### セキュリティ

- HTML エスケープ: JS 側は `esc()` (V001 で `'` → `&#39;` を追加)、Python 側は `html.escape()`
- JSON-LD エスケープ: `_json_for_script()` (scripts/build.py) が `<`/`>`/`&` を `\u003c` `\u003e` `\u0026` に変換し、`</script>` ペイロードによるスクリプトブロック脱出を防止 (OWASP 推奨)
- 外部リンクは全て `rel="noopener"` 付与
- URL 構築は `encodeURIComponent()` (JS 側) / `urllib.parse.quote(..., safe="")` (Python 側) で統一
- Wikipedia リンクは Python / JS いずれも同じエンコード規則を使用 (V011 修正)

### PWA / Service Worker

- `manifest.json`: `lang: "ja"`, `scope: "/"`, `start_url: "/"`, `display: "standalone"`, `theme_color: "#047857"`, icons に `favicon.svg` + 192/512 PNG (`purpose: "any maskable"`)
- `sw.js`: バージョン名 `koe-zukan-v{YYYY-MM-DD}-{species_count}` で install 時にキャッシュ一掃。fetch は cache-first、ミス時は network-fallback + `resp.ok && GET` のみ遅延キャッシュ
- navigate リクエストがオフラインでヒットしない場合は `caches.match("/")` にフォールバック (SPA 的挙動)
- PNG アイコンは precache ではなく fetch 時の遅延キャッシュ (manifest 参照時に Chrome が自動取得)

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
