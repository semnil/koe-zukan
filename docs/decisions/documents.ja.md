# 文書の決定

> For the English version, see [documents.md](documents.md).

このリポジトリの文書について閉じた判断を持つ。今の規則は [CLAUDE.md](../../CLAUDE.md) の「Documents」にある。

## 検証と監査のレポートは、このリポジトリに置かない

- **決定** (2026-11-11): 検証のレポートと、UI/UX・品質の監査のレポートは、このリポジトリに置かない。`docs/` にあった 3 本 (`verification-report.md`・`ux-audit-report.md`・`quality-audit-report.md`) を消した。以後の検証や監査のラウンドのレポートも、ここには足さない。
- **前の形**: レポートは 2026-04-08 (コミット `376ab31`) から `docs/` で追跡していて、2026-10-20 ([#46](https://github.com/semnil/koe-zukan/pull/46)) からは英語だけだった。
- git の履歴は書き換えないので、消したレポートは前のコミットから読める状態のまま残る。

## 文書とコードの中の文の英語基本化

変更の中身と確かめたことは、pull request にある。

- 文書: [#46](https://github.com/semnil/koe-zukan/pull/46)
- スクリプトとテストのコメント・docstring・メッセージ: [#47](https://github.com/semnil/koe-zukan/pull/47)
- トップページの使われていない共有ボタンの削除: [#48](https://github.com/semnil/koe-zukan/pull/48)
