# Document decisions

> 日本語版は [documents.ja.md](documents.ja.md) を参照してください.

Closed decisions about the documents of this repository, with the alternatives that were turned down. The current rules are in [CLAUDE.md](../../CLAUDE.md) ("Documents").

## The verification and audit reports are English only

- **Decision** (2026-10-20, [#46](https://github.com/semnil/koe-zukan/pull/46)): `docs/verification-report.md`, `docs/ux-audit-report.md` and `docs/quality-audit-report.md` were translated to English in place and have no Japanese counterpart. An audit round writes the English file only.
- **Alternatives turned down**:
  - A translation `docs/<name>.ja.md` beside each report. Every later audit round would have to update both languages.
  - Leaving the reports in Japanese and saying so in the language override line of `CLAUDE.md`.

## Past audit records are left as written

- **Decision** (2026-10-17 and 2026-10-20): an entry of a past round in the reports under `docs/` stays as it was written when a later change overtakes it. It is not rewritten to the current state.
- **Cases**:
  - "They will be addressed in an additional PR when they become necessary" under "Intentionally Deferred Items from Audit Rounds 1-3" in `docs/verification-report.md` keeps its future tense. Rewriting it was turned down.
  - The trade-off line of V028 in `docs/verification-report.md` (onomatopoeia that is not in the dictionary may be read as spelled) stays. The same statement was removed from `CLAUDE.md` on 2026-10-17, because nothing records a check of it ([#45](https://github.com/semnil/koe-zukan/pull/45)).
  - The mentions of the top page's share buttons stay after those buttons were removed ([#48](https://github.com/semnil/koe-zukan/pull/48)).

## English base of the documents and the code text

The changes and their checks are in the pull requests:

- Documents: [#46](https://github.com/semnil/koe-zukan/pull/46)
- Comments, docstrings and messages in the scripts and tests: [#47](https://github.com/semnil/koe-zukan/pull/47)
- Removal of the unused share buttons of the top page: [#48](https://github.com/semnil/koe-zukan/pull/48)
