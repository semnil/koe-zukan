# koe-zukan 品質監査レポート

- 対象: koe-zukan プロジェクト全体（scripts/build.py, templates/*, tests/*, data/*, dist/ 生成物）
- 最新監査: 2026-04-17 (ラウンド 3)
- 過去監査: 2026-04-17 (ラウンド 1 / ラウンド 2)
- 適用技法: 実機ビルド検査、契約/不変条件検証、境界値分析、エラーパス分析、セキュリティレビュー（HTML / JSON-LD エスケープ）、状態遷移分析（SW lifecycle）、構文妥当性検査（V8 parser）、ピクセル検査（PNG 生成物）、ビルド冪等性検査
- 前身: docs/verification-report.md V001-V012

## ラウンド 3 (2026-04-17) サマリー

### Q010 / Q011 解決状況

| ID | R2 重要度 | R3 解決状況 | 実機検査エビデンス |
|---|---|---|---|
| **Q010** Service Worker 括弧不整合 | **S2 (HIGH)** | **Fixed** | `dist/sw.js` が `node --check` で構文妥当。括弧バランス `(` 8 / `)` 8、`{` 11 / `}` 11 に収束。R2 で追加した 3 件の `xfail(strict=True)`（`test_sw_parses_as_valid_javascript`、`test_sw_parens_are_balanced`、`test_built_sw_is_syntactically_valid`）がすべて通常の pass に昇格 |
| **Q011** hasVoice=なし に ko/zh オノマトペ残存 | S4 (LOW) | **Fixed** | `dist/animals.json` 中、`hasVoice != "あり"` かつ `onomatopoeia` が非空の種は **0 件**。対象 6 種（A005/R012/F022/F026/F028/V011）はすべて `onomatopoeia=[]`。オノマトペ総数 1208 → **1196**（12 行減、期待通り）。R2 で追加した `test_no_voice_species_have_no_onomatopoeia` の `xfail(strict=True)` が pass に昇格 |

**R1/R2 の xfail(strict=True) 4 件はすべて通常の pass に昇格済み。**

### R1 / R2 既存 Fixed 項目の退行確認

| ID | 退行確認方法 | 結果 |
|---|---|---|
| Q001 JSON-LD `</script>` エスケープ | `dist/species/**/*.html` の JSON-LD 文字列値に生の `<`/`>` が含まれないか検査 | **退行なし（0 件）** |
| Q002 `no-audio.json` 重複 | JSON 件数と set 変換後の件数が一致 | **退行なし（110 / 110）** |
| Q003 孤児オノマトペ `I033` | `animals.json` 中に `I033` 文字列 | **退行なし（0 件）** |
| Q004 分類マッピング欠落 | `classEN` / `orderEN` / `familyEN` 空文字数 | **退行なし（0 / 0 / 0）** |
| Q008 manifest `lang` / `scope` | `dist/manifest.json` を読み込み | **退行なし（`"ja"` / `"/"`）** |
| Q009 X Post ボタンの Unicode 数学記号 | `dist/**` 中の U+1D400-1D7FF コードポイント | **退行なし（0 件）** |

### R3 で新たに発見した欠陥

#### 新規発見なし（S2 / S3 ゼロ、S4 もゼロ）

R3 では R2 の修正内容を再ビルド・実測し、さらに R2 で未検証だった領域（M8 で追加された PNG アイコン生成、SVG regex のアンカー、ビルド冪等性）を新技法で攻めたが、**機能影響のある新規欠陥は発見されなかった**。以下は「気づきレベル（S4 未満）」として記録する。

### 観察事項（S4 未満 / Informational）

| ID | 区分 | 内容 |
|---|---|---|
| **O001** | Informational | `sw.js` の precache URLS 配列は `[/, /animals.json, /regions.json, /favicon.svg, /manifest.json]` の 5 件のまま。M8 で追加された `/icon-192.png` / `/icon-512.png` は precache されていない。**ただし fetch ハンドラが `resp.ok && method=GET` の GET を遅延キャッシュするため、初回訪問時に自動キャッシュされ機能的な問題はない**。Lighthouse PWA 監査の「installable」要件も満たす（192 / 512 の PNG が manifest に存在するだけで十分）。R3 テスト `test_manifest_png_icons_lazy_cached_only` で現状の契約を固定。将来 precache する設計変更があった場合はこのテストを反転させる必要がある |
| **O002** | Informational | 種別ページ（`/species/{ID}/`）に `<link rel="manifest">` が存在しない。ディープリンクからアクセスした場合、Chrome の「ホーム画面に追加」プロンプトはトップページまで戻らないと出ない。PWA 必須要件ではないが UX 向上の余地あり。影響は「初回ディープリンクのユーザーが少ない」前提で S4 未満と判定 |
| **O003** | Informational | `hasVoice=なし` の種の**種別ページ**には「鳴き声なし」の明示ラベルがない（発声方法が「—」・備考に記載があるのみ）。トップページのカード一覧では「鳴き声なし」が表示される。種別ページにも同等の明示が欲しい（UX audit 相当。ソースコード側の改善項目） |

## 実機検査サマリー (R3)

| 項目 | 結果 |
|---|---|
| `python3 scripts/build.py` ビルド成功 | OK |
| 生成物: 種数 305 / オノマトペ **1196** (R2: 1208 → -12) / 言語 4 | OK |
| `animals.json` / `regions.json` / `index.html` 生成 | OK |
| `sitemap.xml` URL 数 = 1 (トップページのみ、種ページはインデックス効率のため除外) | OK |
| `species/{ID}/index.html` 305 ファイル生成 | OK |
| `species/{ID}/ogp.png` 305 ファイル生成（0 バイト なし） | OK |
| `dist/icon-192.png` / `dist/icon-512.png` 生成、PNG 有効、解像度一致 | **OK (M8 新規検証)** |
| PWA アイコン中央がシルエット表示（center 明度 255 / corner 明度 69-70） | **OK (M8 新規検証)** |
| 未置換プレースホルダー `{{...}}` の残存 | なし |
| JSON-LD 305 件すべて JSON として妥当 / 生の `<` `>` `&` なし | **OK (Q001 退行なし)** |
| `classEN` / `orderEN` / `familyEN` 空文字数 | **0 / 0 / 0 (Q004 退行なし)** |
| `animals.json` 内に `I033` 文字列 | **なし (Q003 退行なし)** |
| `no-audio.json` 重複数 | **0 (Q002 退行なし)** |
| `manifest.json` の `lang` / `scope` | **`"ja"` / `"/"` (Q008 退行なし)** |
| 数学記号 U+1D400-1D7FF の残存 | **0 件 (Q009 退行なし)** |
| `dist/sw.js` が `node --check` で構文妥当 | **OK (Q010 Fixed)** |
| `dist/sw.js` 括弧バランス | **OK (`(` 8/`)` 8、`{` 11/`}` 11)** |
| `dist/sitemap.xml` が ElementTree でパース可能 | OK |
| `animals.json` / `regions.json` / `manifest.json` valid JSON | OK |
| `index.html` / `species/*/index.html` インラインスクリプト `node --check` 通過 | OK |
| `rel="noopener"` が全外部リンクに付与 | OK |
| `no-audio.json` taxonCode が audioRef に漏れ出ていない | OK |
| 地域マッピング → 地域マスター の FK | OK |
| `hasVoice=あり` かつ空 onomatopoeia の種 | 0（OK） |
| `hasVoice=なし` かつ onomatopoeia が残存 | **0 件 (Q011 Fixed)** |
| ビルド冪等性（同日 2 回実行で `dist/**` の SHA-256 が一致） | **OK（新規検証）** |
| SVG regex が `id="..."` / `data-d="..."` の `d=` を誤マッチしない | **OK（R2 修正分の契約確定）** |

## 適用技法カバレッジ (R3)

| 技法 | R1 / R2 対象 | R3 追加 | 結果 |
|---|---|---|---|
| 実機ビルド検査 | 305 種の生成物 | ビルド冪等性（同日 2 回実行の byte-diff） | **全ファイル一致** |
| 契約/不変条件検証 | Excel シート間 FK、集合一意性、`hasVoice ⇒ onomatopoeia` | SW precache × manifest PNG 依存関係 | **遅延キャッシュ設計で問題なし（O001）** |
| 構文妥当性検査 | `node --check` による dist/sw.js / インラインスクリプト解析 | — | **全 pass (Q010 Fixed)** |
| 境界値分析 (BVA) | `_build_audio_ref`, `kataToHira` | — | 既存網羅継続、新規の境界値なし |
| エラーパス分析 | SW fetch fallback, ビルド冪等性 | — | 変化なし |
| セキュリティレビュー | JSON-LD エスケープ / HTML エスケープ / 外部リンク rel | 種別ページ共有ボタンの aria-label 再確認（Unicode 数学記号の代わりに普通のラテン文字） | 退行なし |
| 状態遷移分析 | SW install→activate→fetch | 修正後の fetch ハンドラを再レビュー（catch ブロック化の括弧含意） | **ロジック妥当** |
| 決定表 | ID プレフィックス × 音声ソース | — | 変化なし |
| **ピクセル検査 (R3 新規)** | — | PNG アイコンの中心/隅ピクセルで silhouette 視認可能性を検証 | **192/512 ともに center/corner コントラスト 186+ で視認可能** |
| **正規表現アンカリング検査 (R3 新規)** | — | SVG regex `(?:^|[\s])d="..."` が他属性を誤マッチしないか | **OK（id/data-d で誤マッチせず d 値のみ抽出）** |
| UI/操作性 | index.html 共有ボタン / 種別ページの表示・操作 | 種別ページ（hasVoice=なし）のオノマトペ section 非表示確認 | **OK（6 種とも body に ono-grid なし）** |

## 追加したテスト (R3)

すべて `tests/test_build.py` に追記。合計 7 件、いずれも通常の pass（xfail ではない）。

| テスト | 状態 | 何を検証しているか |
|---|---|---|
| `TestPwaIcons::test_generate_pwa_icons_produces_192_and_512` | pass | M8 アイコン生成関数が 192 / 512 の 2 つの PNG を作ることを固定 |
| `TestPwaIcons::test_generate_pwa_icons_are_valid_png_with_correct_dimensions` | pass | Pillow で PNG を開き、`img.format == "PNG"` と `img.size == (N, N)` を検証 |
| `TestPwaIcons::test_generate_pwa_icons_render_silhouette` | pass | center ピクセルと corner ピクセルの明度差 > 50 でシルエットが描画されていることを検証 |
| `TestBuildIdempotency::test_two_builds_produce_identical_dist` | pass | 同日 2 回 build を実行し、`dist/**` の SHA-256 ハッシュが完全一致することを検証。SW cache name の非決定性や乱数の混入を防ぐ |
| `TestServiceWorkerManifestCoherence::test_manifest_png_icons_lazy_cached_only` | pass | 現状の設計（PNG は遅延キャッシュ、precache されない）を契約として固定。将来 precache する変更があれば反転させる必要があることをコメントで明示 |
| `TestSvgPointExtractionAnchoring::test_does_not_match_id_attribute` | pass | R2 で修正した SVG regex が `id="foo"` の直後の `d="..."` を正しく抽出できる |
| `TestSvgPointExtractionAnchoring::test_does_not_match_embedded_d_in_other_attributes` | pass | `data-d="..."` 等の他属性の `d=` を誤マッチせず、`<path d="...">` のみを抽出する |

`tests/test_frontend.mjs` は R3 で追加なし（全ての新規検証は build.py 側）。

## 既存テストの健全性 (R3 時点)

- `python3 -m pytest tests/test_build.py`: **93 collected / 93 passed / 0 failed / 0 xfailed**
  - R1 の 7 件の xfail → R2 で Fixed により pass 昇格（既存）
  - R2 の 4 件の xfail(Q010 x 3 + Q011 x 1) → R3 で Fixed により **全て pass 昇格**
  - R3 で新規 pass テスト 7 件追加
- `node --test tests/test_frontend.mjs`: **52 tests / 52 pass / 0 fail**（R2 から変化なし）

## 残課題と推奨対応

| ID | 重要度 | 推奨アクション |
|---|---|---|
| Q005 `A` プレフィックス音声参照 | S4 | 時期見て `aid.startswith("B")` を `class == "鳥綱"` に変更。R1 時点で Documented |
| Q006 SW species URL 非 precache | S4 | オフライン species 閲覧を重視するなら precache 305 URL 追加。R1 時点で Documented |
| Q007 `sitemap.xml` lastmod 全 URL 同一 | ~~S4~~ Resolved | サイトマップをトップページのみに削減したため解消 |
| **O001** SW × manifest PNG 非 precache | Informational | 遅延キャッシュで機能的には OK。precache したい場合は `generate_sw` の URLS に `/icon-192.png` / `/icon-512.png` を追加（qa 責務外） |
| **O002** 種別ページに manifest link 未付与 | Informational | `templates/species.html` に `<link rel="manifest" href="/manifest.json">` 追加検討 |
| **O003** 種別ページに「鳴き声なし」明示なし | Informational | `templates/species.html` / `build.py` で `hasVoice=なし` 種にバッジ表示を追加検討 |

## 総括 (R3)

| 重要度 | R1 件数 | R2 件数 | R3 件数 | 差分 |
|---|---|---|---|---|
| S1 (CRITICAL) | 0 | 0 | 0 | — |
| S2 (HIGH) | 1 (Q001) | 1 (Q010 新規) | **0** | **Q010 Fixed** |
| S3 (MEDIUM) | 2 (Q003, Q004) | 0 | 0 | — |
| S4 (LOW) | 6 | 5 | **3** (Q005, Q006, Q007 いずれも意図的保留) | Q011 Fixed で -1、R2 の他 S4 は既に保留確定 |
| Informational (S4 未満) | 0 | 0 | **3** (O001, O002, O003) | R3 で新観察事項として記録 |

**R2 指摘の HIGH (Q010) と LOW (Q011) は両方 Fixed**、R1/R2 既存 Fixed 項目にも**退行なし**、R3 で新たに**機能影響のある欠陥は発見されず**。残る S4 3 件はすべて R1 時点で「意図的保留」と判定済み。新規観察事項 O001-O003 は機能影響ゼロ（いずれも UX 向上の余地レベル）。

### 監査終了判定

**監査終了**。

根拠:
- S1 / S2 / S3 残課題: **ゼロ**
- S4 残課題: 3 件すべて R1 時点で意図的保留と判定済み（Q005 / Q006 / Q007）
- R2 で追加された 4 件の `xfail(strict=True)` 監視テストは全て pass に昇格
- R3 で追加した 7 件のアサーションテストも全て pass
- pytest: 93/93 pass、node --test: 52/52 pass
- 既存 Fixed 項目 (Q001-Q004, Q008, Q009) に退行なし
- ビルド冪等性 (同日 2 回実行で byte-identical) を新規確認
- Informational 3 件 (O001-O003) は機能影響ゼロで qa の責務範囲外（implement エージェントが改善判断）
