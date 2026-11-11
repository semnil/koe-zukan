# Document decisions

> 日本語版は [documents.ja.md](documents.ja.md) を参照してください.

Closed decisions about the documents of this repository. The current rules are in [CLAUDE.md](../../CLAUDE.md) ("Documents").

## Verification and audit reports are not kept in this repository

- **Decision** (2026-11-11): the verification report and the UI/UX and quality audit reports are not kept in this repository. The three reports that were under `docs/` (`verification-report.md`, `ux-audit-report.md`, `quality-audit-report.md`) were removed, and the report of a later verification or audit round is not added here.
- **Earlier form**: the reports were tracked under `docs/` from 2026-04-08 (commit `376ab31`), and were English only from 2026-10-20 ([#46](https://github.com/semnil/koe-zukan/pull/46)).
- The git history is not rewritten, so the removed reports stay readable in earlier commits.

## English base of the documents and the code text

The changes and their checks are in the pull requests:

- Documents: [#46](https://github.com/semnil/koe-zukan/pull/46)
- Comments, docstrings and messages in the scripts and tests: [#47](https://github.com/semnil/koe-zukan/pull/47)
- Removal of the unused share buttons of the top page: [#48](https://github.com/semnil/koe-zukan/pull/48)
