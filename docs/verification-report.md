# ソフトウェア検証レポート

- 対象: koe-zukan 全ソースコード
- 日付: 2026-04-08
- フェーズ: Code Review (Python + HTML/JS)
- 適用技法: BVA, エラーパス分析, 状態遷移分析, 決定表, セキュリティレビュー, 契約検証

## Findings

### [V001] XSS: openModal の onclick で ID がエスケープされていない
- **Severity**: S1 (CRITICAL) → **修正済み**
- **Phase**: Code
- **Location**: templates/index.html:595
- **Technique**: セキュリティレビュー (入力境界分析)
- **Scenario**: Excel の ID 列に `');alert(1);//` のような値が含まれた場合、`onclick="openModal('');alert(1);//')"` として展開され、任意の JS が実行される。
- **Root Cause**: テンプレートリテラル内で `a.id` を `esc()` せずに直接展開していた
- **Fix**: `esc()` に `'` → `&#39;` エスケープを追加し、`openModal` 引数を `esc(a.id)` に変更

### [V002] フッターの統計値がハードコードで未置換
- **Severity**: S2 (HIGH) → **修正済み**
- **Phase**: Code
- **Location**: templates/index.html:385, 412
- **Technique**: 決定表 (テンプレート注入パス分析)
- **Scenario**: `str.replace()` はマッチしない場合にエラーにならず、テンプレートの文字列が変更されると置換が空振りする。
- **Root Cause**: プレースホルダー方式が未適用だった
- **Fix**: ヘッダー/フッターも `{{PLACEHOLDER}}` 方式に統一

### [V003] `_parse_svg_points` が SVG の M コマンド座標を含む
- **Severity**: S3 (MEDIUM)
- **Phase**: Code
- **Location**: scripts/build.py:256
- **Technique**: BVA (入力フォーマット分析)
- **Scenario**: 正規表現 `re.findall(r"[\d.]+", path_data)` は SVG パスの全数値を抽出する。現在の favicon.svg では問題ないが、パーサーが脆弱。
- **Root Cause**: SVG パスの正式なパーサーではなく正規表現で座標を抽出している
- **Recommendation**: 現状の SVG 構造では問題ないため低優先度。変更時に注意。

### [V004] `row[14]` のインデックスアクセスが安全でない
- **Severity**: S3 (MEDIUM) → **修正済み**
- **Phase**: Code
- **Location**: scripts/build.py:176
- **Technique**: BVA (境界値分析)
- **Scenario**: `row[14]` が `None` の場合、空の taxonCode で ML URL が生成される。
- **Root Cause**: `row[14]` の None チェックがなかった
- **Fix**: `str(row[14]) if len(row) > 14 and row[14] else ""` に変更

### [V005] Wikipedia リンクの `nameEN` に空白を含む名前が正しくエンコードされない可能性
- **Severity**: S4 (LOW)
- **Phase**: Code
- **Location**: templates/index.html:668
- **Technique**: BVA (文字列境界)
- **Scenario**: `encodeURIComponent(a.nameEN)` は空白を `%20` に変換するが、Wikipedia は `_` 区切りを正規とする。リダイレクトされるため実害は少ない。
- **Root Cause**: Wikipedia URL の慣例と `encodeURIComponent` の差異

### [V006] `check_audio.py` の API レスポンスパースが脆弱
- **Severity**: S3 (MEDIUM)
- **Phase**: Code
- **Location**: scripts/check_audio.py:40
- **Technique**: エラーパス分析
- **Scenario**: API がフォーマットを変更した場合に `AttributeError` が発生する。手動実行スクリプトのため低優先度。
- **Root Cause**: 外部 API レスポンスの型検証がない

### [V007] kataToHira がカタカナ「ヷヸヹヺ」(U+30F7-U+30FA) を変換しない
- **Severity**: S4 (LOW)
- **Phase**: Code
- **Location**: templates/index.html:482
- **Technique**: BVA (文字範囲境界分析)
- **Scenario**: 正規表現 `[\u30A1-\u30F6]` はヷ (U+30F7)〜ヺ (U+30FA) を含まない。これらは歴史的カタカナで、現代の動物名には出現しない。
- **Root Cause**: Unicode カタカナブロックの末尾 4 文字が範囲外
- **Recommendation**: 現在のデータセットに該当文字はないため対応不要

### [V008] `_apply_placeholders` が未置換プレースホルダーを検出しない
- **Severity**: S3 (MEDIUM) → **修正済み**
- **Phase**: Code
- **Location**: scripts/build.py:216-220
- **Technique**: エラーパス分析 / 契約検証 (サイレント失敗)
- **Scenario**: テンプレートに `{{NEW_FIELD}}` を追加したが `mapping` に含めなかった場合、そのまま HTML 出力に残るサイレント失敗。
- **Root Cause**: `str.replace()` はマッチしない場合にエラーにならない
- **Fix**: 置換後に `re.findall(r"\{\{[A-Z_]+\}\}", html)` で残存チェックし警告出力

### [V009] `shareButtons` の URL に `a.id` が未エスケープで埋め込まれる
- **Severity**: S3 (MEDIUM)
- **Phase**: Code
- **Location**: templates/index.html:753
- **Technique**: セキュリティレビュー (入力境界分析)
- **Scenario**: `a.id` に `/` や `?` が含まれる場合、意図しない URL が生成される。ただしデータソース (Excel ID列) は `B001` 等の安全なパターンのため実害なし。
- **Root Cause**: URL 構築時のエンコーディング不足
- **Recommendation**: 低優先度。V001 同様、データソースが信頼できるため現時点で実害なし

### [V010] `copyShareUrl` の clipboard API 失敗時にハンドリングなし
- **Severity**: S3 (MEDIUM) → **修正済み**
- **Phase**: Code
- **Location**: templates/index.html:765-771, templates/species.html:227-233
- **Technique**: エラーパス分析
- **Scenario**: `navigator.clipboard.writeText()` は HTTP 環境、iframe、ユーザー権限拒否で失敗する。`.catch()` がないため Promise rejection が未処理。
- **Root Cause**: Promise の reject パスが未処理
- **Fix**: `.catch()` を追加し「コピー失敗」メッセージを表示

### [V011] species.html の Wikipedia リンクで `nameJA` が URL エンコードされていない
- **Severity**: S3 (MEDIUM) → **修正済み**
- **Phase**: Code
- **Location**: scripts/build.py:490
- **Technique**: BVA (URL 文字列境界)
- **Scenario**: `esc()` は HTML エスケープであり URL エンコードではない。`href` 属性値に非 ASCII 文字が直接含まれていた。index.html 側は `encodeURIComponent()` を使用しており不整合。
- **Root Cause**: Python 側と JS 側で Wikipedia URL の構築方法が異なっていた
- **Fix**: build.py 側を `quote(name, safe="")` でエンコードするよう修正

### [V012] SW の fetch ハンドラで opaque レスポンスがキャッシュされる
- **Severity**: S4 (LOW)
- **Phase**: Code
- **Location**: scripts/build.py:613-619 (生成される sw.js)
- **Technique**: エラーパス分析
- **Scenario**: CDN (Fuse.js) からの cross-origin fetch は `resp.ok` が `false` のため実際にはキャッシュされない。Fuse.js CDN がダウンした場合にオフラインでサイトが動作しない。
- **Root Cause**: opaque レスポンスは ok が常に false
- **Recommendation**: PWA のオフライン完全対応を目指すなら Fuse.js をローカルにバンドルする。現状は progressive enhancement として許容可能

## 適用技法のカバレッジ

| 技法 | 対象 | 結果 |
|---|---|---|
| BVA | Excel 行列インデックス, SVG パーサー, URL エンコーディング, kataToHira 文字範囲 | V003, V004, V005, V007, V011 検出 |
| エラーパス分析 | API レスポンス, ファイル I/O, テンプレート置換, clipboard API, SW fetch | V002, V006, V008, V010, V012 検出 |
| セキュリティレビュー | HTML テンプレートリテラル内のユーザー由来データ, URL 構築 | V001, V009 検出 |
| 状態遷移分析 | モーダル open/close, URL パラメータ, popstate, displayLang 初期化, SW lifecycle | 問題なし |
| 決定表 | テンプレート注入パス, フィルタ/検索の組み合わせ, browser language detection | V002 検出 |
| 契約検証 | _apply_placeholders 事前条件/事後条件 | V008 検出 |

## Summary

| 重要度 | 件数 | 修正済み |
|---|---|---|
| S1 (CRITICAL) | 1件 (V001) | 1件 |
| S2 (HIGH) | 1件 (V002) | 1件 |
| S3 (MEDIUM) | 8件 (V003, V004, V006, V008, V009, V010, V011) | 5件 |
| S4 (LOW) | 3件 (V005, V007, V012) | 0件 |

未修正 (対応不要/低優先度): V003, V005, V006, V007, V009, V012

---

## 監査ラウンド 1-3 追加検証 (2026-04-17)

UX / 品質の 2 系統で 3 ラウンドの監査を実施。詳細は `docs/ux-audit-report.md` / `docs/quality-audit-report.md` を参照。
以下は本レポートに V### として統合する主要項目のみ。

### [V013] JSON-LD 文字列に `</script>` 等が未エスケープで埋め込まれる
- **Severity**: S2 (HIGH) → **修正済み**
- **Phase**: Code
- **Location**: scripts/build.py (`_json_for_script`, `generate_species_pages`), templates/species.html:213-225
- **Technique**: セキュリティレビュー (コンテキスト依存エスケープ)
- **Scenario**: `json.dumps()` は `"` と `\` はエスケープするが `<`/`>`/`&` は通す。種名や description に `</script>` が含まれると `<script type="application/ld+json">` ブロックから脱出し XSS につながる可能性
- **Fix**: `_json_for_script()` で `<` → `\u003c`, `>` → `\u003e`, `&` → `\u0026` を追加エスケープ。`JSON_HEADLINE` / `JSON_DESCRIPTION` 経由で注入
- **Test**: `dist/species/**/*.html` の JSON-LD 文字列値に生の `<`/`>`/`&` が含まれないことを実機検証

### [V014] 種別ページに hreflang が未付与
- **Severity**: S3 (MEDIUM) → **修正済み**
- **Phase**: Code
- **Location**: templates/species.html:23-27
- **Technique**: 国際化レビュー (Google Search Central hreflang ガイドライン)
- **Scenario**: 種ページから言語切替したいユーザー・検索エンジンに対して言語バリアントへの参照がなかった
- **Fix**: `ja` / `en` / `ko` / `zh` / `x-default` の 5 本を追加。`ja`〜`zh` はトップページの `/?lang=*&id={ID}` を、`x-default` は種ページ自身の `/species/{ID}/` を指す

### [V015] PWA マニフェストに 192/512 PNG アイコンが未登録
- **Severity**: S3 (MEDIUM) → **修正済み**
- **Phase**: Code
- **Location**: scripts/build.py (`generate_pwa_icons`, `generate_manifest`), dist/icon-192.png, dist/icon-512.png, dist/manifest.json
- **Technique**: PWA Installability 要件検証 (Lighthouse PWA audit)
- **Scenario**: Chrome for Android の「ホーム画面に追加」要件は 192 / 512 サイズの PNG が manifest に存在することを求める。SVG のみでは不足
- **Fix**: `generate_pwa_icons()` が favicon.svg からシルエットを 80% スケールで中央配置した PNG を 192/512 両方生成。`generate_manifest()` が `icons` 配列に `purpose: "any maskable"` 付きで登録

### [V016] `hasVoice=なし` の種に韓国語・中国語オノマトペが残存
- **Severity**: S4 (LOW) → **修正済み**
- **Phase**: Data
- **Location**: data/animal-sounds-data.xlsx (オノマトペマッピングシート) の 6 種 (A005, R012, F022, F026, F028, V011)
- **Technique**: 契約検証 (`hasVoice=あり ⇒ onomatopoeia 非空` の対偶)
- **Scenario**: 「鳴き声なし」と明示されている種で `ko`/`zh` 行が残っており、トップカードと種ページで不整合が発生していた
- **Fix**: 該当 12 行を Excel から削除。`dist/animals.json` 上で `hasVoice != "あり"` かつ `onomatopoeia` が非空の種は 0 件に収束
- **Test**: `tests/test_build.py::test_no_voice_species_have_no_onomatopoeia` で契約を固定

### [V017] Service Worker の fetch ハンドラが構文エラーで登録失敗
- **Severity**: S2 (HIGH) → **修正済み**
- **Phase**: Code
- **Location**: scripts/build.py (`generate_sw`)
- **Technique**: 構文妥当性検査 (`node --check`)
- **Scenario**: R2 修正で fetch ハンドラに `.catch()` を追加した際に括弧バランスが崩れ、`dist/sw.js` 全体が構文エラーになっていた。SW 登録は失敗するがエラーは console に出るだけでアプリは一見動作する (静かな失敗)
- **Fix**: `caches.match(...).then(r => r || fetch(...).then(resp => {...}))` のチェーン後に `.catch(() => { navigate なら / を返し、それ以外は 503 })` を正しく閉じる。括弧バランスを `(` 8 / `)` 8、`{` 11 / `}` 11 に整合
- **Test**: `tests/test_build.py::test_built_sw_is_syntactically_valid` (`node --check` で構文検証) と `test_sw_parens_are_balanced`

### [V018] 孤児オノマトペ (存在しない ID `I033` への参照)
- **Severity**: S3 (MEDIUM) → **修正済み**
- **Phase**: Data
- **Location**: data/animal-sounds-data.xlsx (オノマトペマッピング)
- **Technique**: 契約検証 (FK 整合性)
- **Scenario**: メインデータに存在しない `I033` のオノマトペ行がオノマトペマッピングに残っていた
- **Fix**: 該当行を削除。`animals.json` 内に `I033` 文字列は 0 件

### [V019] 分類マッピング (綱/目/科) の英訳欠落
- **Severity**: S3 (MEDIUM) → **修正済み**
- **Phase**: Data
- **Location**: data/animal-sounds-data.xlsx (分類マッピング)
- **Technique**: 欠損値検出
- **Scenario**: `classEN` / `orderEN` / `familyEN` が空の種があり、英語 UI 表示で「—」になるケースがあった
- **Fix**: 欠落していた全行の英訳を補完。`dist/animals.json` での `classEN`/`orderEN`/`familyEN` 空文字数は全て 0

### [V020] `no-audio.json` に重複エントリ
- **Severity**: S4 (LOW) → **修正済み**
- **Phase**: Data
- **Location**: data/no-audio.json
- **Technique**: 一意性検査
- **Scenario**: 手動実行スクリプトの複数回実行で同じ taxonCode が重複追加されていた
- **Fix**: 重複排除し set 変換後と件数が一致する状態 (110 件) に収束

### [V021] PWA manifest に `lang` / `scope` 未設定
- **Severity**: S4 (LOW) → **修正済み**
- **Phase**: Code
- **Location**: scripts/build.py (`generate_manifest`)
- **Technique**: PWA 仕様レビュー (w3c/manifest)
- **Fix**: `"lang": "ja"` と `"scope": "/"` を追加

### [V022] 共有ボタンのラベルに Unicode 数学記号が混入
- **Severity**: S4 (LOW) → **修正済み**
- **Phase**: Code
- **Location**: scripts/build.py (`generate_species_pages` 内の share_html)
- **Technique**: セキュリティレビュー + A11y レビュー
- **Scenario**: ラベル文字列に U+1D400〜U+1D7FF の数学記号 (太字ラテン等) が紛れ込んでおり、スクリーンリーダー読み上げと検索インデックスに悪影響
- **Fix**: 通常の ASCII ラテン文字に置き換え。`dist/**` から U+1D400-1D7FF を 0 件に

### [V023] UX: WCAG 2.1 AA 適合度改善 (コントラスト比 + タッチターゲット + 言語属性)
- **Severity**: S3 (MEDIUM) 群 → **全項目修正済み**
- **Phase**: Code
- **Location**: templates/index.html, templates/species.html
- **Technique**: WCAG 2.1 AA / 2.2 追加 SC 検査 + コントラスト比数値計算 + タッチターゲット実測
- **Scenario / Fix**:
  - SC 1.4.3 Contrast: `#a8a29e` / `#059669` の AA 違反色を廃止し、`#57534e` / `#78716c` / `#047857` に統一。本文は 4.5:1 以上、大テキストも 3:1 以上を確保
  - SC 2.5.5 / 2.5.8 Target Size: `.filter-btn` / `.lang-tab` / `.modal-close` / `.search-clear` に `min-height: 44px` または固定 44x44 を明示
  - SC 3.1.2 Language of Parts: カード英名・学名・オノマトペ・モーダル・種ページの全箇所に `lang="en"` / `lang="la"` / `lang="${表示言語}"` を付与
  - SC 2.4.1 Bypass Blocks: `<a href="#main" class="skip-link">` + `<main id="main">` を両テンプレートに追加
  - SC 2.4.11 Focus Appearance (2.2 AA): 検索ボックスの `:focus-within` に border + 3px 半透明リングの二重視覚指標

### [V024] ビルド冪等性
- **Severity**: Informational → **検証完了**
- **Phase**: Code
- **Location**: scripts/build.py 全体
- **Technique**: ビルド冪等性検査 (同日 2 回実行で `dist/**` の SHA-256 ハッシュ一致)
- **Scenario**: 乱数・タイムスタンプの混入や集合のイテレーション順依存で出力が非決定的になると CD が不安定
- **Result**: 同日 2 回実行で全ファイルのハッシュが完全一致することを確認

### 監査ラウンド 1-3 の意図的保留項目

以下は監査中に「機能影響なし / 周辺品質の提案レベル」と判定し意図的に保留した項目。必要になった時点で追加 PR で対応する。

| ID | 概要 | 保留理由 |
|---|---|---|
| Q005 (R1 継続) | `A` プレフィックスの音声ソース判定が `aid.startswith("B")` に依存 | 現データセットでは `A*` は初期サンプルのみで鳥綱との混同なし |
| Q006 (R1 継続) | 種ページ URL が Service Worker precache に含まれない | オフライン種ページ閲覧の需要が低い。fetch 時の遅延キャッシュでカバー |
| ~~Q007~~ | ~~`sitemap.xml` の `lastmod` が全 URL 同日~~ | Resolved: サイトマップをトップページのみに削減 |
| L8 (UX R3) | `.share-btn` が 44x44 未達 (~31px) | WCAG 2.5.8 AA (24x24) は満たす。AAA 基準のみ未達 |
| L9 (UX R3) | `sw.js` の precache に PNG アイコン未登録 | Chrome が manifest 経由で自動取得するため機能影響なし |
| Info-1 (UX R3) | maskable アイコンの seafzone が 80% で猫耳先端がクリップされる可能性 | 実機マスクで視認性は維持される範囲 |
| O002 (QA R3) | 種別ページに `<link rel="manifest">` 未付与 | トップ経由なら問題なし |
| O003 (QA R3) | 種別ページに「鳴き声なし」明示バッジなし | カード一覧側では明示済み |

---

## 機能拡張ラウンド (2026-05-16)

SEO・UX 改善を目的とした機能追加と多言語 UI 全面対応。

### [V025] 関連種リンク・コンテンツ差別化・全 UI 多言語対応
- **Severity**: Informational → **実装済み**
- **Phase**: Code
- **Location**: `scripts/build.py`, `templates/index.html`, `templates/species.html`
- **Technique**: SEO 内部リンク分析、コンテンツ差別化レビュー、多言語 UI 網羅確認
- **変更内容**:
  1. **関連種リンク** (`_build_related_species`): family→order→class→phylum の 4 段フォールバックで最大 4 件を選出。全 305 種でリンクが生成されることを `test_all_species_pages_have_related_section` で保証
  2. **「詳細ページで見る →」リンク**: モーダル内に `/species/{ID}/` への遷移リンクを追加。カード→モーダル→種ページの導線を確立
  3. **コンテンツ差別化**: カードは名前+主オノマトペのみ、モーダルは1言語プレビュー+詳細リンク、種ページは4言語フル表示+外部リンク+共有+関連種
  4. **全 UI 多言語対応**: `VOICE_METHOD_EN` (27 エントリ)、`MODAL_LABELS`、`SEARCH_LABELS`、`NO_VOICE_LABEL`、`NO_ONO_LABEL`、`MODAL_HINT`、`CLOSE_LABEL`、`ALL_LABEL` を追加。`updateFilterLabels()` / `updateSearchLabels()` で `applyDisplayLang` 時に全 UI 要素を切替
- **テスト**: `tests/test_build.py` に 20 件追加 (計 114 件 Pass)。`TestBuildRelatedSpecies` (9)、`TestBuildRelatedHtml` (6)、`TestGenerateSpeciesPages` 拡充 (4)、`TestBuildIntegration` 拡充 (3)

---

## 総計サマリー (V001-V025, 2026-05-16 時点)

| 重要度 | 件数 | 修正済み | 保留 (機能影響なし) |
|---|---|---|---|
| S1 (CRITICAL) | 1 (V001) | 1 | 0 |
| S2 (HIGH) | 3 (V002, V013, V017) | 3 | 0 |
| S3 (MEDIUM) | 12 (V003, V004, V006, V008, V009, V010, V011, V014, V015, V018, V019, V023) | 10 | 2 (V003, V006, V009) |
| S4 (LOW) | 7 (V005, V007, V012, V016, V020, V021, V022) | 4 | 3 (V005, V007, V012) |
| Informational | 1 (V024) | 検証完了 | — |

S1/S2 は全件修正済み。S3/S4 の保留項目はすべて意図的な Documented 判断 (機能影響ゼロ)。
UX 監査ラウンド 3 で WCAG 2.1 AA / 2.2 AA SC は全項目 Pass 判定。
V025: 関連種リンク・コンテンツ差別化・全 UI 多言語対応 (機能追加、テスト 114 件 Pass)。

---

## 機能拡張ラウンド (2026-05-16, 詳細ページ多言語化 + SEO 強化)

### [V026] 詳細ページの 4 言語化と表示言語の引き継ぎ
- **Severity**: Informational → **実装済み**
- **Phase**: Code
- **Location**: `scripts/build.py`, `templates/species.html`, `templates/index.html`
- **Technique**: i18n DOM 書き換え設計、Bot vs JS クライアントの責務分離、契約レビュー
- **変更内容**:
  1. **詳細ページの 4 言語切替**: `templates/species.html` に `I18N` 辞書 (ラベル + IUCN 9 訳) を追加し、`applyLang(code)` で全テキスト・aria-label・関連種グリッドを書き換え。初期 HTML は日本語のまま (SEO / no-JS 訪問者向け)
  2. **データ埋め込み**: `scripts/build.py` に `_build_species_payload` / `_build_related_payload` / `_json_for_inline_script` を追加。種固有データ (`SPECIES_DATA`) と関連種データ (`RELATED_DATA`) を `<script>` 安全な JSON (`<` `>` `&` を `<` `>` `&` にエスケープ) として種ページに埋め込み
  3. **DOM マーカー**: `data-i18n` (テキスト) / `data-link-kind` (外部リンク aria-label) / `data-share-kind` (共有ボタン aria-label + コピーラベル) を build.py 側で付与し、`applyLang` から汎用的にアクセス
  4. **言語フォールバックを ja → en に変更**: `index.html` / `species.html` 共通で、URL `?lang=` → `navigator.language` → 英語フォールバック。フランス語・ドイツ語等の非 CJK 訪問者が読めない漢字を見ないため
  5. **言語タブの位置統一**: `index.html` のヘッダー (`.header-inner` の右側) と `species.html` の top-bar 内に配置。緑グラデーション帯上の半透明枠スタイル + `min-height: 44px` で統一 (WCAG 2.1 AA タップターゲット維持)
  6. **lang 引き継ぎリンク**: index→species (`<a class="species-detail-link" href="/species/{ID}/?lang=<xx>">`)、species→index (top-bar `← 動物の鳴き声図鑑`、back-link `← 図鑑で表示`)、species→species (関連種グリッド) で `?lang=` を引き継ぎ。ja は canonical 維持で付与しない
  7. **hreflang の整合化**: 種ページの hreflang を `/?lang=*&id={ID}` → `/species/{ID}/?lang=*` に変更し、ページ自身を指すよう統一
- **テスト**: `tests/test_build.py` に `TestSpeciesPageI18nPayload` (11) + `TestJsonForInlineScript` (3)、`tests/test_frontend.mjs` に `withLang` (4) + `detail link` (2) を追加。`detectLang` の期待値も `ja` → `en` フォールバックに更新

### [V027] SEO 正規化: canonical + WebSite JSON-LD + SearchAction
- **Severity**: S3 (MEDIUM) → **修正済み**
- **Phase**: Code
- **Location**: `templates/index.html` head
- **Technique**: 重複コンテンツ分析、Schema.org 適合確認
- **Scenario**: トップページに canonical が無く、`?lang=` / `?id=` / `?q=` バリエーションが重複コンテンツとして扱われる可能性。サイト内検索もクローラに認識されていなかった
- **Root Cause**: index.html テンプレートに `<link rel="canonical">` および `@type: WebSite` JSON-LD が未設定
- **Fix**:
  - `<link rel="canonical" href="https://koe-zukan.semnil.com/">` を追加
  - `@type: WebSite` JSON-LD を追加 (name / alternateName / url / description / `inLanguage` / `potentialAction: SearchAction`)
  - SearchAction の `urlTemplate` は `.../?q={search_term_string}`。index.html の JS が `?q=` を受けて検索ボックスに投入 + `onSearch()` を実行 (Google Sitelinks Search Box の契約遵守)
- **テスト**: `TestIndexSeoMetadata` 3 件 (canonical 存在 / WebSite JSON-LD parse / SearchAction 仕様適合)

### [V028] 種ページのオノマトペ発音再生 (Web Speech API)
- **Severity**: Informational → **実装済み**
- **Phase**: Code
- **Location**: `templates/species.html`, `scripts/build.py` (`generate_species_pages`, `LANG_LABELS_JA`)
- **Technique**: 機能設計レビュー、TTS 非対応環境の縮退設計、aria-label の言語追従契約
- **変更内容**:
  1. **発音ボタンの埋め込み**: build.py が各オノマトペセル (`.ono-cell`) に `<button class="ono-play" data-play-lang data-play-text aria-label>` を出力。`data-play-text` は HTML エスケープ済み (XSS 防御)
  2. **TTS 呼び出し**: `speakOnomatopoeia(btn)` が `data-play-lang` (ja/en/ko/zh) を `PLAY_LANG_MAP` で BCP-47 (`ja-JP`/`en-US`/`ko-KR`/`zh-CN`) に変換し `SpeechSynthesisUtterance` を生成・再生 (`rate = 0.9`)。連続再生・新規発話の前に `speechSynthesis.cancel()` で前の発話を停止
  3. **非対応環境の縮退**: `TTS_SUPPORTED` が false のとき `html.no-tts` クラスを付与し、CSS でボタンを `display: none` (Lighthouse 等のスコアに影響を与えない)
  4. **aria-label の言語追従**: 初期 HTML は日本語名 (`LANG_LABELS_JA`: 英語/韓国語/中国語) で出力し no-JS 時も自然な読み上げ。JS 動作後は `updatePlayLabels(code)` が `PLAY_LABELS` × `LANG_NAMES_LOCALIZED` (4×4 = 16 通り) で UI 言語に追従させる
  5. **再生状態の視覚化**: 再生中ボタンに `.playing` クラスを付与 (背景アクセント色)、`onend`/`onerror` で解除。多重再生防止のため発話開始前に他の `.playing` を全解除
  6. **ページ離脱時の停止**: `beforeunload` で `speechSynthesis.cancel()` を呼び、種ページ間遷移で前の発話が続行しないようにする
- **トレードオフ**: 発音精度は OS/ブラウザの音声エンジン依存で、辞書にないオノマトペ (「ニャー」「woof」等) は綴り通り読まれることがある。外部依存ゼロ志向のため許容
- **テスト**: `tests/test_build.py` に `TestOnomatopoeiaPlayButtons` を追加 (1セル1ボタン契約、`data-play-*` 値、初期 aria-label 4 言語、HTML エスケープ、ヘルパー定数、BCP-47 マッピング、空オノマトペでボタン非生成)

### サマリー追補

V025 以降の累積:

| 重要度 | 件数 | 修正済み |
|---|---|---|
| S3 (MEDIUM) | +1 (V027) | 1 |
| Informational | +3 (V025, V026, V028) | 実装完了 |

ビルド冪等性・全 JSON-LD parse・全外部リンク `rel=noopener` などの統合テストは引き続き全 Pass。
