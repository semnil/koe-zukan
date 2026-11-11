# 文書の決定

> For the English version, see [documents.md](documents.md).

このリポジトリの文書について閉じた判断と、却下した案を持つ。今の規則は [CLAUDE.md](../../CLAUDE.md) の「Documents」にある。

## 検証と監査のレポートは英語だけにする

- **決定** (2026-10-20、[#46](https://github.com/semnil/koe-zukan/pull/46)): `docs/verification-report.md`・`docs/ux-audit-report.md`・`docs/quality-audit-report.md` は、その場で英語に訳し、日本語版を持たない。監査のラウンドが書くのは英語のファイルだけ。
- **却下した案**:
  - レポートごとに訳の `docs/<name>.ja.md` を並べる。以後の監査のラウンドのたびに、2 つの言語の更新が要る。
  - レポートを日本語のまま残し、`CLAUDE.md` の言語の上書き行にそう書く。

## 過去の監査の記録は、書かれたままにする

- **決定** (2026-10-17 と 2026-10-20): `docs/` のレポートにある過去のラウンドの記述は、後の変更で古くなっても、書かれたときのまま残す。今の姿に合わせて書き直さない。
- **例**:
  - `docs/verification-report.md` の「Intentionally Deferred Items from Audit Rounds 1-3」にある「They will be addressed in an additional PR when they become necessary」は、未来形のまま残す。書き換える案は却下した。
  - `docs/verification-report.md` の V028 のトレードオフの行 (辞書に無いオノマトペは綴りのとおりに読まれることがある) は残す。同じ記述は、確かめた記録が無いので、2026-10-17 に `CLAUDE.md` から消した ([#45](https://github.com/semnil/koe-zukan/pull/45))。
  - トップページの共有ボタンに触れた記述は、ボタンを消した後も残す ([#48](https://github.com/semnil/koe-zukan/pull/48))。

## 文書とコードの中の文の英語基本化

変更の中身と確かめたことは、pull request にある。

- 文書: [#46](https://github.com/semnil/koe-zukan/pull/46)
- スクリプトとテストのコメント・docstring・メッセージ: [#47](https://github.com/semnil/koe-zukan/pull/47)
- トップページの使われていない共有ボタンの削除: [#48](https://github.com/semnil/koe-zukan/pull/48)
