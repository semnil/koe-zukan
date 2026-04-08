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
