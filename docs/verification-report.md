# ソフトウェア検証レポート

- 対象: koe-zukan 全ソースコード
- 日付: 2026-04-08
- フェーズ: Code Review (Python + HTML/JS)
- 適用技法: BVA, エラーパス分析, 状態遷移分析, 決定表, セキュリティレビュー

## Findings

### [V001] XSS: openModal の onclick で ID がエスケープされていない
- **Severity**: S1 (CRITICAL)
- **Phase**: Code
- **Location**: templates/index.html:595
- **Technique**: セキュリティレビュー (入力境界分析)
- **Scenario**: Excel の ID 列に `');alert(1);//` のような値が含まれた場合、`onclick="openModal('');alert(1);//')"` として展開され、任意の JS が実行される。現在は ID が `B001` 等の安全なパターンだが、データソースが Excel であり将来の入力を保証できない。
- **Root Cause**: テンプレートリテラル内で `a.id` を `esc()` せずに直接展開している
- **Recommendation**: `onclick="openModal('${esc(a.id)}')"` に変更。ただし `esc()` は HTML エンティティエスケープのため、属性値内の `'` もエスケープが必要。`a.id` を `esc()` で囲み、`'` → `&#39;` のエスケープを追加する。

### [V002] フッターの統計値がハードコードで未置換
- **Severity**: S2 (HIGH)
- **Phase**: Code
- **Location**: templates/index.html:385, 412
- **Technique**: 決定表 (テンプレート注入パス分析)
- **Scenario**: ヘッダー (行385) に `258 species / 4 languages`、フッター (行412) に `258 species, 572 onomatopoeia entries across 4 languages` が残っている。build.py の `generate_html()` は文字列置換で対応しているが、テンプレートの文字列が変更されると置換が空振りする (サイレント失敗)。
- **Root Cause**: `str.replace()` はマッチしない場合にエラーにならない。プレースホルダー方式 (`{{...}}`) が OGP には適用されたが、ヘッダー/フッターには未適用。
- **Recommendation**: ヘッダー/フッターもプレースホルダー方式に統一する。

### [V003] `_parse_svg_points` が SVG の M コマンド座標を含む
- **Severity**: S3 (MEDIUM)
- **Phase**: Code
- **Location**: scripts/build.py:256
- **Technique**: BVA (入力フォーマット分析)
- **Scenario**: `re.findall(r"[\d.]+", path_data)` は SVG パスの全数値を抽出する。`M 32.0 15.0 L 33.7 15.0` のような形式では M/L コマンド文字は除外されるが、もし将来 SVG にグラデーション座標 (`x1="0" y1="0" x2="1" y2="1"`) 等が `d` 属性内に紛れ込む形に変更された場合、不正な座標が混入する。現在の favicon.svg では問題ないが、パーサーが脆弱。
- **Root Cause**: SVG パスの正式なパーサーではなく正規表現で座標を抽出している
- **Recommendation**: 現状の SVG 構造では問題ないため低優先度。変更時に注意。

### [V004] `row[14]` のインデックスアクセスが安全でない
- **Severity**: S3 (MEDIUM)
- **Phase**: Code
- **Location**: scripts/build.py:176
- **Technique**: BVA (境界値分析)
- **Scenario**: `row[14] if len(row) > 14 else ""` で taxonCode を取得しているが、Excel の行が14列未満の場合は空文字を返す。しかし `row[14]` が `None` の場合、`_build_audio_ref` の `taxon_code` 引数に `None` が渡り、`taxon_code not in _NO_AUDIO` が True になるため空の taxonCode で ML URL が生成される。
- **Root Cause**: `row[14]` の None チェックがない
- **Recommendation**: `row[14] if len(row) > 14 and row[14] else ""` に変更。

### [V005] Wikipedia リンクの `nameEN` に空白を含む名前が正しくエンコードされない可能性
- **Severity**: S4 (LOW)
- **Phase**: Code
- **Location**: templates/index.html:668
- **Technique**: BVA (文字列境界)
- **Scenario**: `encodeURIComponent(a.nameEN)` は空白を `%20` に変換するが、Wikipedia は `_` 区切りを正規とする。`Blue Whale` → `Blue%20Whale` でもリダイレクトされるため実害は少ないが、正規 URL ではない。
- **Root Cause**: Wikipedia URL の慣例と `encodeURIComponent` の差異
- **Recommendation**: 低優先度。現状でも動作する。

### [V006] `check_audio.py` の API レスポンスパースが脆弱
- **Severity**: S3 (MEDIUM)
- **Phase**: Code
- **Location**: scripts/check_audio.py:40
- **Technique**: エラーパス分析
- **Scenario**: `data.get("results", {}).get("content", [])` で API レスポンスをパースしているが、API がフォーマットを変更した場合（例: `results` が配列になった場合）、`AttributeError` が発生する。また HTTP ステータス 200 以外でもレスポンスボディがある場合にパースを試みる。
- **Root Cause**: 外部 API レスポンスの型検証がない
- **Recommendation**: ビルド時に毎回実行するスクリプトではなく手動実行のため、低優先度。エラー時は `-1` を返す既存のハンドリングで十分。

## 適用技法のカバレッジ

| 技法 | 対象 | 結果 |
|---|---|---|
| BVA | Excel 行列インデックス, SVG パーサー, URL エンコーディング | V003, V004, V005 検出 |
| エラーパス分析 | API レスポンス, ファイル I/O, テンプレート置換 | V002, V006 検出 |
| セキュリティレビュー | HTML テンプレートリテラル内のユーザー由来データ | V001 検出 |
| 状態遷移分析 | モーダル open/close, URL パラメータ, popstate | 問題なし |
| 決定表 | テンプレート注入パス, フィルタ/検索の組み合わせ | V002 検出 |

## Summary

- S1: 1件 (V001 — XSS)
- S2: 1件 (V002 — ハードコード統計値)
- S3: 3件 (V003, V004, V006)
- S4: 1件 (V005)
