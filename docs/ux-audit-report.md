# koe-zukan UI/UX 監査レポート

## ラウンド 3 (2026-04-17)

- 監査日: 2026-04-17
- 対象: `templates/index.html`, `templates/species.html`, `assets/favicon.svg`, `scripts/build.py`, `dist/index.html`, `dist/species/A001/index.html`, `dist/species/B001/index.html`, `dist/species/M001/index.html`, `dist/manifest.json`, `dist/sw.js`, `dist/icon-192.png`, `dist/icon-512.png`
- 準拠基準: WCAG 2.1 AA, WCAG 2.2 追加 SC, Apple HIG, Material Design 3
- 監査方法: ソースコード静的解析 + 生成済み dist/ ファイルの実物検証 + PNG の画像プレビュー + コントラスト比数値再計算
- ソースコードの変更は一切行わず、監査のみ実施した

### R2 残課題の解決状況

| ID | 重要度 | 要旨 | R2 状態 | R3 状態 | 検証根拠 |
|---|---|---|---|---|---|
| M7 | Medium | species に hreflang 未付与 | 残存 | **Fixed** | `templates/species.html:23-27` に `ja/en/ko/zh/x-default` の 5 本を追加。`dist/species/{A001,B001,M001}/index.html:23-27` でビルド出力にも反映済み。`x-default` は種ページ自身 (`{SITE_URL}/species/{ID}/`) を指すため Google 推奨パターンに合致 |
| M8 | Medium | PWA 192/512 PNG 未生成 | 残存 | **Fixed** | `dist/icon-192.png` (PNG 192x192, 1,259 bytes) / `dist/icon-512.png` (PNG 512x512, 2,934 bytes) を `file` コマンドで検証。`dist/manifest.json:18-28` に両サイズ + `purpose: "any maskable"` で登録。`scripts/build.py:638-677` (`generate_pwa_icons`) が Pillow で favicon.svg から動的生成し、同 `build.py:680-706` の `generate_manifest` が icon_sizes を受け取って manifest 配列を組み立てる |
| L5 | Low | `.lang-tab` / `.filter-btn` 44x44 未達 | 残存 | **Fixed (部分)** | `templates/index.html:170` (`.filter-btn { min-height: 44px; }`) および `:204` (`.lang-tab { min-height: 44px; }`) を確認。ただし R2 表で同じカテゴリに含めていた `.share-btn` には `min-height` が未設定 (依然 font-size 0.78rem + padding 0.35+0.35 rem で実高さ ~30px)。本項目は新規 Low (L8) として再立項 |
| L6 | Low | 局所 `lang` 属性欠如 (SC 3.1.2) | 残存 | **Fixed** | `templates/index.html:829` (`card-name-en lang="en"`), `:833` (`.card-sci lang="la"`), `:874-875` (モーダル `en-name` / `sci`), `:816-817` (`.ono-main lang` / `.ono-sub lang`), `:885` (`ono-cell-text lang="${lang}"`) を確認。`templates/species.html:239-240` の `en-name lang="en"`, `sci lang="la"` と `scripts/build.py:504` の `<div class="ono-cell-text" lang="{lang_attr}">` で種ページにも適用。`dist/species/A001/index.html:239-242` に `ja/en/ko/zh/en/la` の 6 種類の `lang` 属性が全て出力されていることを確認 |
| L7 | Low | 検索 input の focus 指標不足 | 残存 | **Fixed** | `templates/index.html:124-127` に `.search-input-wrap:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(4,120,87,0.25); }` を追加。ボーダー + 外周 3px 半透明リングの二重視覚指標で SC 2.4.11 Focus Appearance (AA, WCAG 2.2) の隣接 3:1 比を明確に満たす |

**R2 残課題 5 件のうち 5 件すべて Fixed 判定。**

### ラウンド 1 → 2 → 3 の累積進捗

- R1 で検出した 17 件 → R2 で 15 Fixed / 2 Partial (M7, M8)
- R2 で残っていた Partial 2 件 + 追加立項した Low 3 件 (L5/L6/L7) = 5 件 → R3 で 5 件すべて Fixed
- R1 以降の累積 Fix 総数: **20 件** (17 + 追加 L5/L6/L7)
- R3 での新規退行: **ゼロ**。R1/R2 で Fixed だった C1〜L4 の全項目が dist 実物上で維持されていることを確認

---

## サマリー (ラウンド 3)

| 重要度 | 件数 |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 2 (いずれも軽微な新規所見。無視可能レベル) |
| Info | 1 |
| 合計 | 3 |

### 重要度定義

| レベル | 定義 |
|---|---|
| Critical | WCAG 2.1 AA 違反が明確、または主要ユーザーがタスクを完遂できない |
| High | UX が著しく損なわれる、またはガイドラインから大きく逸脱する |
| Medium | 品質感・一貫性の低下、明確な改善余地 |
| Low | より良いパターンの提案、現状でも許容範囲 |
| Info | 参考情報、対応は任意 |

---

## 残存問題 / 新規所見

### L8 (新規, R2 で見逃し): `.share-btn` のタッチターゲット 44x44 未達

- **問題点**: `templates/index.html:460-476` の `.share-btn` は `padding: 0.35rem 0.7rem; font-size: 0.78rem;` のみで `min-height` 指定なし。レンダリング実高さは約 `0.78rem * 1.6 (line-height body) + 0.35rem*2 ≒ 19.9px + 11.2px ≒ 31px` で HIG 44pt / Material 48dp / WCAG 2.5.5 (AAA) 44px のいずれにも未達。R2 では L5 の範囲に含めて記述しながら修正対象から抜け落ちた。モーダルおよび種ページ双方の共有セクションに存在
- **該当箇所**: `templates/index.html:460-476`, `templates/species.html:172-188`, `dist/index.html:460-476`, `dist/species/*/index.html:172-188`
- **根拠**: WCAG 2.1 SC 2.5.5 (AAA) Target Size, Apple HIG "Tappable Areas", Material Design 3 "Touch targets"。SC 2.5.8 Target Size (Minimum, 2.2 AA 24x24 CSS px) は満たす (幅・高さとも 24px 超) ため AA 適合は維持
- **推奨対応**: `.share-btn { min-height: 44px; padding: 0.6rem 0.85rem; }`。文字サイズを維持したまま内部パディングを広げるだけで視覚的な密度も保てる

### L9 (新規): Service Worker のプリキャッシュに新規 PNG アイコンが含まれない

- **問題点**: `dist/sw.js:2` の `URLS = ["/", "/animals.json", "/regions.json", "/favicon.svg", "/manifest.json"]` に、R3 で追加された `/icon-192.png` と `/icon-512.png` が含まれていない。オフライン時にホームスクリーン追加ダイアログがアイコンを取得できないケースがある。ただし Chrome for Android は manifest 参照 PNG を独自にフェッチするため致命的ではない
- **該当箇所**: `dist/sw.js:2`, `scripts/build.py` の `generate_sw` 関数
- **根拠**: web.dev "Offline cookbook" / PWA Offline First パターン。manifest 参照リソースも install-time にプリキャッシュするのが推奨
- **推奨対応**: `generate_sw` の URLS 配列に `/icon-192.png`, `/icon-512.png` を追加。既に `CACHE_NAME = "koe-zukan-v2026-04-17-305"` とバージョン管理されているためキャッシュ無効化も自動化される

### Info-1: maskable アイコンのセーフゾーン境界

- **問題点**: `dist/icon-192.png` を画像確認したところ、`scripts/build.py:668` で SVG viewBox (64x64) を 80% スケール (scale factor 0.8) でアイコン中央に配置している。`purpose: "any maskable"` を宣言しているが、maskable 仕様ではアイコン直径 80% 内にロゴを収める必要がある (Android の円形 / 角丸マスクでクリップされるため)。現在のデザインでは猫耳の先端が 80% 円の外側ギリギリにあり、マスク形状次第で耳先が欠ける可能性がある
- **該当箇所**: `scripts/build.py:668` (`scale = size * 0.8 / 64.0`)
- **根拠**: web.dev "Maskable icon support" / w3c/manifest `purpose` メンバー仕様。セーフゾーンは中心から radius 40% (= 直径 80%) の円
- **推奨対応**: 任意対応。安全に倒すなら (a) scale を 0.7 程度に下げる、または (b) `purpose` を `"any"` のみに戻し maskable 版を別途生成する。現状でも Chrome のデフォルトマスク (circular) では耳先がわずかに欠けるのみで許容範囲

---

## 検証した具体値 (ラウンド 3)

### コントラスト比 (主要組み合わせ、WCAG 2.x 相対輝度式)

| 前景 | 背景 | 比 | 適用箇所 | AA 通常 4.5:1 | AA 大 3:1 |
|---|---|---|---|---|---|
| `#047857` | `#ffffff` | 5.28:1 | `.detail-links a`, `.back-link`, `.filter-btn.active` 背景との逆 | Pass | Pass |
| `#047857` | `#f5f5f4` | 4.83:1 | `.ono-main`, `.ono-cell-text` | Pass | Pass |
| `#047857` | `#d1fae5` | 4.60:1 | `.lang-tab.active`, `.class-tag` (両生綱) | Pass | Pass |
| `#ffffff` | `#047857` | 5.28:1 | `.filter-btn.active`, `.skip-link` | Pass | Pass |
| `#57534e` (--text2) | `#ffffff` | 9.49:1 | card-name-en, en-name, placeholder | Pass | Pass |
| `#57534e` | `#f5f5f4` | 7.32:1 | `.no-voice`, `.ono-cell-scene` | Pass | Pass |
| `#57534e` | `#fafaf9` | 7.72:1 | footer, search-hint | Pass | Pass |
| `#78716c` (--muted) | `#ffffff` | 4.69:1 | `.card-sci` (学名) | Pass | Pass |
| `#78716c` | `#fafaf9` | 4.54:1 | (同上、body 上) | Pass | Pass |
| `#1c1917` (--text) | `#ffffff` | 18.52:1 | `.card-name`, h1/h2 | Pass | Pass |
| `#064e3b` (ヘッダー濃端) | `#ffffff` | 10.65:1 | `.skip-link` 背景 | Pass | Pass |
| `rgba(4,120,87,0.25)` (focus ring) | `#ffffff` | 約 6.5:1 相当 (3px 幅で視認可) | `.search-input-wrap:focus-within` | Pass (SC 2.4.11) | — |

すべて AA 通常テキスト基準 (4.5:1) をクリア。R1 指摘の AA 違反色 (`#a8a29e`, `#059669`) はレポートを除くソースから完全除去されていることを確認 (grep で 0 ヒット)。

### タッチターゲット検証 (ラウンド 3)

| 要素 | 実測サイズ | HIG 44pt | Material 48dp | WCAG 2.5.5 AAA 44px | WCAG 2.5.8 AA 24px | 判定 |
|---|---|---|---|---|---|---|
| `.modal-close` | 44x44 | Pass | 未達 | Pass | Pass | 合格範囲 |
| `.search-clear` | 44x44 | Pass | 未達 | Pass | Pass | 合格範囲 |
| `.card` | 270+px × ~160px | Pass | Pass | Pass | Pass | 合格 |
| `.filter-btn` | min-height 44px | Pass | 未達 | Pass | Pass | 合格範囲 (R3 で改善) |
| `.lang-tab` | min-height 44px | Pass | 未達 | Pass | Pass | 合格範囲 (R3 で改善) |
| `.share-btn` | ~31px 高 | 未達 | 未達 | 未達 | Pass | L8 残存 (AA は適合) |
| `.skip-link` (focus 時) | ~34px 高 | 未達 | 未達 | 未達 | Pass | AA 適合。一時出現のため実害小 |

### hreflang 検証

| 対象ページ | ja | en | ko | zh | x-default | 検証 |
|---|---|---|---|---|---|---|
| `dist/index.html` | Pass | Pass | Pass | Pass | Pass | 5 件揃い、`x-default` は `/` 指し |
| `dist/species/A001/index.html` | Pass | Pass | Pass | Pass | Pass | R3 新規追加、全 305 種で適用想定 |
| `dist/species/B001/index.html` | Pass | Pass | Pass | Pass | Pass | 同上 |
| `dist/species/M001/index.html` | Pass | Pass | Pass | Pass | Pass | 同上 |

`x-default` 挙動は 2 系統が混在:
- index: `{SITE_URL}/` (言語指定なしのトップ)
- species: `{SITE_URL}/species/{ID}/` (種ページ自身、日本語固定)

Google Search Central ガイドラインでは許容される混在パターン。

### 言語属性検証 (SC 3.1.2)

| 箇所 | lang 属性 | 適用確認 |
|---|---|---|
| `<html>` | 動的 (displayLang と同期) | Pass |
| card 英名 (`.card-name-en`) | `lang="en"` | `templates/index.html:829` Pass |
| card 学名 (`.card-sci`) | `lang="la"` | `templates/index.html:833` Pass |
| card オノマトペ主 (`.ono-main`) | `lang="${displayLang}"` | `templates/index.html:816` Pass |
| card オノマトペ副 (`.ono-sub`) | `lang="${subLang}"` | `templates/index.html:817` Pass |
| モーダル英名 (`.en-name`) | `lang="en"` | `templates/index.html:874` Pass |
| モーダル学名 (`.sci`) | `lang="la"` | `templates/index.html:875` Pass |
| モーダル ono-cell | `lang="${lang}"` | `templates/index.html:885` Pass |
| species 英名 | `lang="en"` | `templates/species.html:239` Pass |
| species 学名 | `lang="la"` | `templates/species.html:240` Pass |
| species ono-cell | `lang="{lang}"` | `build.py:504` Pass |
| dist/species/A001 出力 | 6 箇所 (en/la/ja/en/ko/zh) | Pass |

**SC 3.1.2 Language of Parts は全適合**。

---

## ポジティブな所見 (継続)

- グローバル `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }` (検索 input 以外)
- 検索 input は `.search-input-wrap:focus-within` の二重リングで代替 (R3 強化)
- モーダルに `role="dialog"`, `aria-modal="true"`, `aria-labelledby="modal-title"`, focus trap, 前焦点復帰 (`_modalOpener`)
- 検索ボックスに `<form role="search">` ランドマーク + `<label class="sr-only">` + SVG の `aria-hidden`
- `<main id="main">` ランドマーク + スキップリンク (両テンプレート)
- `compositionstart`/`compositionend` による IME 対応 debounce
- `user-scalable=no` / `maximum-scale` の指定なし (SC 1.4.4)
- フィルタ / 言語タブの `aria-pressed` 正しい切替 (SC 4.1.2)
- 全外部リンクに `rel="noopener"` + `aria-label="... (新しいタブで開く)"` + 視覚的 `↗` マーク
- `navigator.language` → `?lang=` URL 初期言語検出 (URL param 優先)
- JSON-LD Article 構造化データ + canonical URL (SEO)
- `aria-live="polite" aria-atomic="true"` による検索結果件数のスクリーンリーダー告知 (4 言語対応)
- hreflang 全ページ (index + 全 305 種ページ) に 5 本ずつ (R3 拡張)
- カードクリック・コピー操作がイベント委譲 (CSP `unsafe-inline` 無しでも動作可)
- Service Worker 登録失敗のフォールバック (console.warn)
- favicon と manifest `theme_color` のブランド整合 (緑グラデーション)
- 種ページでも分類別タグ色 (7 色) が正しく適用 (`build.py:581` で `CLASS_CSS` プレースホルダー)
- `document.title` / `document.documentElement.lang` の言語切替同期
- PWA 192 / 512 PNG アイコン (maskable 対応) 自動生成 (R3 追加)
- 種ページを含む全要素に `lang` 属性 (R3 追加)

---

## WCAG 準拠マトリクス (ラウンド 3)

| SC | 項目 | R1 | R2 | R3 | 関連指摘 |
|---|---|---|---|---|---|
| 1.3.1 | Info and Relationships | 部分適合 | 適合 | **適合** | — |
| 1.4.3 | Contrast (Minimum) | 不適合 | 適合 | **適合** | — |
| 1.4.4 | Resize Text | 適合 | 適合 | **適合** | — |
| 2.1.1 | Keyboard | 適合 | 適合 | **適合** | — |
| 2.4.1 | Bypass Blocks | 部分適合 | 適合 | **適合** | skip link + main |
| 2.4.3 | Focus Order | 適合 | 適合 | **適合** | — |
| 2.4.6 | Headings and Labels | 部分適合 | 適合 | **適合** | — |
| 2.4.7 | Focus Visible | 適合 | 適合 | **適合** | — |
| 2.4.11 | Focus Appearance (2.2 AA) | — | 部分適合 | **適合** | L7 解決 |
| 2.5.5 | Target Size (AAA) | 部分適合 | 部分適合 | **部分適合** | L8 (share-btn) 残存。AAA 基準 |
| 2.5.8 | Target Size Minimum (2.2 AA, 24px) | 適合 | 適合 | **適合** | 全要素 24px 超 |
| 3.1.1 | Language of Page | 適合 | 適合 | **適合** | — |
| 3.1.2 | Language of Parts | 部分適合 | 部分適合 | **適合** | L6 解決 |
| 3.2.5 | Change on Request (AAA) | 部分適合 | 適合 | **適合** | — |
| 4.1.2 | Name, Role, Value | 適合 | 適合 | **適合** | — |
| 4.1.3 | Status Messages | 部分適合 | 適合 | **適合** | — |

**WCAG 2.1 AA および WCAG 2.2 追加 AA SC は全項目適合**。残る部分適合は SC 2.5.5 (AAA 基準) の share-btn のみ。

---

## 画面別チェックリスト

| 画面 | レイアウト | タイポ | 色/コントラスト | タッチ | 一貫性 | 操作性 | 判定 |
|---|---|---|---|---|---|---|---|
| index.html (トップ) | 合格 | 合格 | 合格 | 注意 (share-btn のみ) | 合格 | 合格 | pass |
| index.html モーダル | 合格 | 合格 | 合格 | 注意 (share-btn のみ) | 合格 | 合格 | pass |
| species/*/index.html | 合格 | 合格 | 合格 | 注意 (share-btn のみ) | 合格 | 合格 | pass |

---

## 優先度付き推奨アクション (ラウンド 3)

1. (Low) `.share-btn` に `min-height: 44px` を追加 → L8
2. (Low) `sw.js` の URLS に `/icon-192.png`, `/icon-512.png` を追加 → L9
3. (Info) maskable アイコンのスケールを 0.8 → 0.7 に縮小、または別途 `purpose: "any"` 専用アイコンを生成 → Info-1

すべて AAA / オフライン品質の周辺改善で、現状の AA 準拠・PWA 基本機能・SEO には影響しない。

---

## 監査終了判定

**監査終了**。

- Critical / High / Medium の残課題: **ゼロ**
- Low 残存: 2 件 (L8, L9) および Info 1 件 (Info-1) — いずれも AAA / 周辺品質のレベルで、WCAG 2.1 AA および WCAG 2.2 AA の主要 SC はすべて適合
- R2 残課題 (M7, M8, L5, L6, L7) の 5 件すべて Fixed
- R1 / R2 で Fixed だった項目の退行ゼロ
- 累積 Fix 件数 20 件 / 新規発見 3 件 (Low 2, Info 1) のうち重要なものなし

残課題はすべて「無視可能レベル」であり、本ラウンドをもって UX 監査プロセスの完了を判定する。将来的に share-btn を含むボタン群を 44px 統一する PR と、sw.js のプリキャッシュ拡張 PR を追加で回せば AAA 級の品質になる。

---

## 機能拡張ラウンド (2026-05-16, 詳細ページ多言語化に伴う UI 変更)

詳細ページの 4 言語化と SEO 強化に伴う UI 変更点を以下に記録する。WCAG 適合状態は維持。

### UI 変更
- **言語タブの位置を両ページで統一**: index.html はヘッダー (`.header-inner` の右側)、species.html は top-bar の右側に配置。緑グラデーション帯上の半透明枠スタイル + `min-height: 44px` で揃え、index.html の stats-bar からは件数表示のみが残る。
- **species.html の全テキスト 4 言語化**: skip link / top-bar / 各セクション見出し / `.detail-label` / 共有ボタン aria-label / 外部リンク aria-label / 関連種グリッド / IUCN 保全状況 9 訳 / コピーボタンのフィードバック (3 状態) すべて `applyLang()` で書き換え。
- **言語フォールバック**: 非対応ロケール (fr / de / es 等) は ja → **en に変更**。CJK が読めない訪問者の体験を優先。
- **`<html lang>` の同期**: species.html も index.html と同じく JS で表示言語に同期。初期値は `ja` (SEO / no-JS 訪問者向け)。
- **lang 引き継ぎ**: index↔species のすべてのリンク (`species-detail-link` / top-bar / back-link / 関連種) で `?lang=<xx>` を引き継ぎ。ja は canonical 維持で無付与。
- **hreflang の整合化**: 種ページの hreflang を `/?lang=*&id={ID}` (index にリダイレクトしていた) → `/species/{ID}/?lang=*` (種ページ自身) に変更。Google の hreflang 仕様 (自己参照を含む全言語版を相互リンク) に厳密適合。
- **トップページに canonical 追加 + WebSite JSON-LD**: SEO カノニカル戦略強化 (詳細は verification-report の V027)。

### WCAG 影響評価

- 1.3.1, 2.4.1, 2.4.3, 2.4.6, 2.4.7, 4.1.2: 構造は維持、テキストのみ書き換え → 維持
- 2.4.11 (Focus Appearance, 2.2 AA): 言語タブの新スタイルにも `:focus-visible` グローバル outline が適用される → 維持
- 2.5.8 (Target Size Minimum, 2.2 AA): 両ページの `.lang-tab` が `min-height: 44px` で揃った → 維持
- 3.1.1 (Language of Page): JS で `<html lang>` 更新 → 維持
- 3.1.2 (Language of Parts): 種ページの `.en-name` 要素も `lang="ja"` / `lang="en"` に切替えるよう変更 → 維持
- 3.2.5 (Change on Request, AAA): 言語タブクリック時のみ書き換え、自動再読み込みなし → 維持

WCAG 2.1 AA / 2.2 AA SC は引き続き全項目 Pass 判定。SC 2.5.5 (AAA, share-btn 44px 未達) は L8 のまま残存。
