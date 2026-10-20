# koe-zukan quality audit report

- Scope: the whole koe-zukan project (scripts/build.py, templates/*, tests/*, data/*, dist/ build outputs)
- Latest audit: 2026-04-17 (Round 3)
- Previous audits: 2026-04-17 (Round 1 / Round 2)
- Techniques applied: actual build inspection, contract/invariant verification, boundary value analysis, error path analysis, security review (HTML / JSON-LD escaping), state transition analysis (SW lifecycle), syntax validity check (V8 parser), pixel inspection (PNG build outputs), build idempotency check
- Predecessor: docs/verification-report.md V001-V012

## Round 3 (2026-04-17) summary

### Q010 / Q011 resolution status

| ID | R2 severity | R3 resolution status | Actual build inspection evidence |
|---|---|---|---|
| **Q010** Service Worker bracket mismatch | **S2 (HIGH)** | **Fixed** | `dist/sw.js` is syntactically valid under `node --check`. Bracket balance converged to `(` 8 / `)` 8, `{` 11 / `}` 11. The 3 `xfail(strict=True)` tests added in R2 (`test_sw_parses_as_valid_javascript`, `test_sw_parens_are_balanced`, `test_built_sw_is_syntactically_valid`) were all promoted to normal passes |
| **Q011** ko/zh onomatopoeia remaining on hasVoice=なし | S4 (LOW) | **Fixed** | In `dist/animals.json`, there are **0** species with `hasVoice != "あり"` and a non-empty `onomatopoeia`. The 6 affected species (A005/R012/F022/F026/F028/V011) all have `onomatopoeia=[]`. Total onomatopoeia 1208 → **1196** (12 rows fewer, as expected). The `xfail(strict=True)` on `test_no_voice_species_have_no_onomatopoeia` added in R2 was promoted to pass |

**All 4 of the R1/R2 xfail(strict=True) tests have been promoted to normal passes.**

### Regression check of existing R1 / R2 Fixed items

| ID | Regression check method | Result |
|---|---|---|
| Q001 JSON-LD `</script>` escaping | Check that JSON-LD string values in `dist/species/**/*.html` contain no raw `<`/`>` | **No regression (0 found)** |
| Q002 `no-audio.json` duplicates | The JSON entry count equals the count after converting to a set | **No regression (110 / 110)** |
| Q003 orphan onomatopoeia `I033` | The `I033` string in `animals.json` | **No regression (0 found)** |
| Q004 missing entries in the 分類マッピング sheet | Number of empty strings in `classEN` / `orderEN` / `familyEN` | **No regression (0 / 0 / 0)** |
| Q008 manifest `lang` / `scope` | Load `dist/manifest.json` | **No regression (`"ja"` / `"/"`)** |
| Q009 Unicode mathematical symbols in the X Post button | U+1D400-1D7FF code points in `dist/**` | **No regression (0 found)** |

### Defects newly found in R3

#### No new findings (zero S2 / S3, zero S4 as well)

In R3 the R2 fixes were rebuilt and measured, and the areas left unverified in R2 (the PNG icon generation added in M8, the SVG regex anchor, build idempotency) were attacked with new techniques, but **no new defect with functional impact was found**. The items below are recorded as "observation level (below S4)".

### Observations (below S4 / Informational)

| ID | Category | Description |
|---|---|---|
| **O001** | Informational | The precache URLS array in `sw.js` still has the 5 entries `[/, /animals.json, /regions.json, /favicon.svg, /manifest.json]`. The `/icon-192.png` / `/icon-512.png` added in M8 are not precached. **However, because the fetch handler lazily caches GET requests that satisfy `resp.ok && method=GET`, they are cached automatically on the first visit and there is no functional problem**. It also meets the "installable" requirement of the Lighthouse PWA audit (it is enough for the 192 / 512 PNGs to exist in the manifest). The R3 test `test_manifest_png_icons_lazy_cached_only` pins the current contract. If a future design change precaches them, this test has to be inverted |
| **O002** | Informational | The species page (`/species/{ID}/`) has no `<link rel="manifest">`. When it is reached through a deep link, Chrome's "Add to Home screen" prompt does not appear until the user goes back to the top page. It is not a PWA requirement, but there is room for UX improvement. Judged below S4 on the premise that "few users arrive through a deep link first" |
| **O003** | Informational | The **species page** of a `hasVoice=なし` species has no explicit "鳴き声なし" ("Silent") label (the vocalization method shows "—" and it is only mentioned in the Note section). The top page's card list does show "鳴き声なし". An equivalent explicit indication is wanted on the species page as well (equivalent to a UX audit item; an improvement item on the source code side) |

## Actual build inspection summary (R3)

| Item | Result |
|---|---|
| `python3 scripts/build.py` build succeeds | OK |
| Outputs: species 305 / onomatopoeia **1196** (R2: 1208 → -12) / languages 4 | OK |
| `animals.json` / `regions.json` / `index.html` generated | OK |
| `sitemap.xml` URL count = 1 (top page only; species pages excluded for indexing efficiency) | OK |
| 305 `species/{ID}/index.html` files generated | OK |
| 305 `species/{ID}/ogp.png` files generated (no 0-byte files) | OK |
| `dist/icon-192.png` / `dist/icon-512.png` generated, valid PNG, resolution matches | **OK (newly verified for M8)** |
| PWA icon center shows the silhouette (center brightness 255 / corner brightness 69-70) | **OK (newly verified for M8)** |
| Leftover unreplaced placeholders `{{...}}` | None |
| All 305 JSON-LD blocks valid as JSON / no raw `<` `>` `&` | **OK (Q001 no regression)** |
| Number of empty strings in `classEN` / `orderEN` / `familyEN` | **0 / 0 / 0 (Q004 no regression)** |
| The `I033` string in `animals.json` | **None (Q003 no regression)** |
| Duplicate count in `no-audio.json` | **0 (Q002 no regression)** |
| `lang` / `scope` in `manifest.json` | **`"ja"` / `"/"` (Q008 no regression)** |
| Remaining mathematical symbols U+1D400-1D7FF | **0 found (Q009 no regression)** |
| `dist/sw.js` is syntactically valid under `node --check` | **OK (Q010 Fixed)** |
| `dist/sw.js` bracket balance | **OK (`(` 8/`)` 8, `{` 11/`}` 11)** |
| `dist/sitemap.xml` parses with ElementTree | OK |
| `animals.json` / `regions.json` / `manifest.json` valid JSON | OK |
| Inline scripts in `index.html` / `species/*/index.html` pass `node --check` | OK |
| `rel="noopener"` present on every external link | OK |
| `no-audio.json` taxonCodes do not leak into audioRef | OK |
| FK from 地域マッピング → 地域マスター | OK |
| Species with `hasVoice=あり` and empty onomatopoeia | 0 (OK) |
| `hasVoice=なし` with onomatopoeia remaining | **0 found (Q011 Fixed)** |
| Build idempotency (SHA-256 of `dist/**` matches across 2 runs on the same day) | **OK (newly verified)** |
| SVG regex does not falsely match the `d=` in `id="..."` / `data-d="..."` | **OK (contract for the R2 fix confirmed)** |

## Coverage of techniques applied (R3)

| Technique | R1 / R2 scope | R3 additions | Result |
|---|---|---|---|
| Actual build inspection | Outputs for 305 species | Build idempotency (byte-diff of 2 runs on the same day) | **All files identical** |
| Contract/invariant verification | FKs between Excel sheets, set uniqueness, `hasVoice ⇒ onomatopoeia` | Dependency between SW precache × manifest PNGs | **No problem thanks to the lazy-cache design (O001)** |
| Syntax validity check | Parsing dist/sw.js / inline scripts with `node --check` | — | **All pass (Q010 Fixed)** |
| Boundary value analysis (BVA) | `_build_audio_ref`, `kataToHira` | — | Existing coverage continues; no new boundary values |
| Error path analysis | SW fetch fallback, build idempotency | — | No change |
| Security review | JSON-LD escaping / HTML escaping / external link rel | Re-check of the aria-label on the species page share buttons (plain Latin letters instead of Unicode mathematical symbols) | No regression |
| State transition analysis | SW install→activate→fetch | Re-review of the fixed fetch handler (bracket implications of moving it into a catch block) | **Logic valid** |
| Decision table | ID prefix × audio source | — | No change |
| **Pixel inspection (new in R3)** | — | Verify silhouette visibility from the center/corner pixels of the PNG icons | **Visible in both 192/512 with center/corner contrast 186+** |
| **Regex anchoring check (new in R3)** | — | Whether SVG regex `(?:^|[\s])d="..."` falsely matches other attributes | **OK (no false match on id/data-d; only the d value is extracted)** |
| UI/operability | index.html share buttons / species page display and operation | Confirm the onomatopoeia section is hidden on species pages (hasVoice=なし) | **OK (no ono-grid in body for any of the 6 species)** |

## Tests added (R3)

All appended to `tests/test_build.py`. 7 in total, all normal passes (not xfail).

| Test | Status | What it verifies |
|---|---|---|
| `TestPwaIcons::test_generate_pwa_icons_produces_192_and_512` | pass | Pins that the M8 icon generation function produces 2 PNGs, 192 / 512 |
| `TestPwaIcons::test_generate_pwa_icons_are_valid_png_with_correct_dimensions` | pass | Opens the PNG with Pillow and verifies `img.format == "PNG"` and `img.size == (N, N)` |
| `TestPwaIcons::test_generate_pwa_icons_render_silhouette` | pass | Verifies that the silhouette is drawn, by a brightness difference > 50 between the center pixel and the corner pixel |
| `TestBuildIdempotency::test_two_builds_produce_identical_dist` | pass | Runs build 2 times on the same day and verifies that the SHA-256 hashes of `dist/**` match exactly. Guards against nondeterminism in the SW cache name and random values slipping in |
| `TestServiceWorkerManifestCoherence::test_manifest_png_icons_lazy_cached_only` | pass | Pins the current design (PNGs are lazily cached, not precached) as a contract. A comment states that the test has to be inverted if a future change precaches them |
| `TestSvgPointExtractionAnchoring::test_does_not_match_id_attribute` | pass | The SVG regex fixed in R2 correctly extracts the `d="..."` right after `id="foo"` |
| `TestSvgPointExtractionAnchoring::test_does_not_match_embedded_d_in_other_attributes` | pass | Does not falsely match the `d=` in other attributes such as `data-d="..."`, and extracts only `<path d="...">` |

`tests/test_frontend.mjs` had no additions in R3 (all new verification is on the build.py side).

## Health of existing tests (as of R3)

- `python3 -m pytest tests/test_build.py`: **93 collected / 93 passed / 0 failed / 0 xfailed**
  - The 7 xfails of R1 → promoted to pass because they were Fixed in R2 (existing)
  - The 4 xfails of R2 (Q010 x 3 + Q011 x 1) → **all promoted to pass** because they were Fixed in R3
  - 7 new passing tests added in R3
- `node --test tests/test_frontend.mjs`: **52 tests / 52 pass / 0 fail** (no change from R2)

## Remaining issues and recommended actions

| ID | Severity | Recommended action |
|---|---|---|
| Q005 audio reference for the `A` prefix | S4 | When the timing suits, change `aid.startswith("B")` to `class == "鳥綱"`. Documented as of R1 |
| Q006 SW does not precache species URLs | S4 | If offline species browsing matters, add the 305 URLs to precache. Documented as of R1 |
| Q007 `sitemap.xml` lastmod identical for all URLs | ~~S4~~ Resolved | Resolved because the sitemap was reduced to the top page only |
| **O001** SW × manifest PNGs not precached | Informational | Functionally OK through lazy caching. To precache them, add `/icon-192.png` / `/icon-512.png` to URLS in `generate_sw` (outside qa's responsibility) |
| **O002** species page lacks a manifest link | Informational | Consider adding `<link rel="manifest" href="/manifest.json">` to `templates/species.html` |
| **O003** species page has no explicit "鳴き声なし" | Informational | Consider adding a badge for `hasVoice=なし` species in `templates/species.html` / `build.py` |

## Overall assessment (R3)

| Severity | R1 count | R2 count | R3 count | Delta |
|---|---|---|---|---|
| S1 (CRITICAL) | 0 | 0 | 0 | — |
| S2 (HIGH) | 1 (Q001) | 1 (Q010 new) | **0** | **Q010 Fixed** |
| S3 (MEDIUM) | 2 (Q003, Q004) | 0 | 0 | — |
| S4 (LOW) | 6 | 5 | **3** (Q005, Q006, Q007, all intentionally deferred) | -1 from Q011 Fixed; the other S4 items of R2 were already confirmed as deferred |
| Informational (below S4) | 0 | 0 | **3** (O001, O002, O003) | Recorded as new observations in R3 |

**Both the HIGH (Q010) and the LOW (Q011) findings of R2 are Fixed**, the existing R1/R2 Fixed items show **no regression** either, and in R3 **no new defect with functional impact was found**. The remaining 3 S4 items were all judged "intentionally deferred" as of R1. The new observations O001-O003 have zero functional impact (all at the level of room for UX improvement).

### Audit closure decision

**Audit closed**.

Grounds:
- S1 / S2 / S3 remaining issues: **zero**
- S4 remaining issues: all 3 judged intentionally deferred as of R1 (Q005 / Q006 / Q007)
- All 4 `xfail(strict=True)` monitoring tests added in R2 were promoted to pass
- All 7 assertion tests added in R3 pass as well
- pytest: 93/93 pass、node --test: 52/52 pass
- No regression in existing Fixed items (Q001-Q004, Q008, Q009)
- Build idempotency (byte-identical across 2 runs on the same day) newly confirmed
- The 3 Informational items (O001-O003) have zero functional impact and are outside qa's responsibility (the implement agent decides on improvements)
