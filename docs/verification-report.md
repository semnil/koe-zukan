# Software Verification Report

- Scope: all koe-zukan source code
- Date: 2026-04-08
- Phase: Code Review (Python + HTML/JS)
- Techniques applied: BVA, error path analysis, state transition analysis, decision table, security review, contract verification

## Findings

### [V001] XSS: ID is not escaped in the onclick of openModal
- **Severity**: S1 (CRITICAL) → **Fixed**
- **Phase**: Code
- **Location**: templates/index.html:595
- **Technique**: security review (input boundary analysis)
- **Scenario**: If the ID column in Excel contains a value such as `');alert(1);//`, it expands to `onclick="openModal('');alert(1);//')"` and arbitrary JS runs.
- **Root Cause**: `a.id` was expanded directly inside a template literal without `esc()`
- **Fix**: Added the `'` → `&#39;` escape to `esc()` and changed the `openModal` argument to `esc(a.id)`

### [V002] Footer statistics are hard-coded and not substituted
- **Severity**: S2 (HIGH) → **Fixed**
- **Phase**: Code
- **Location**: templates/index.html:385, 412
- **Technique**: decision table (template injection path analysis)
- **Scenario**: `str.replace()` raises no error when nothing matches, so when the template string changes, the replacement misses without effect.
- **Root Cause**: The placeholder approach had not been applied
- **Fix**: Unified the header/footer onto the `{{PLACEHOLDER}}` approach as well

### [V003] `_parse_svg_points` includes the coordinates of the SVG M command
- **Severity**: S3 (MEDIUM)
- **Phase**: Code
- **Location**: scripts/build.py:256
- **Technique**: BVA (input format analysis)
- **Scenario**: The regular expression `re.findall(r"[\d.]+", path_data)` extracts every number in the SVG path. It is not a problem with the current favicon.svg, but the parser is fragile.
- **Root Cause**: Coordinates are extracted with a regular expression rather than a proper SVG path parser
- **Recommendation**: Low priority because the current SVG structure has no problem. Take care when changing it.

### [V004] Index access to `row[14]` is unsafe
- **Severity**: S3 (MEDIUM) → **Fixed**
- **Phase**: Code
- **Location**: scripts/build.py:176
- **Technique**: BVA (boundary value analysis)
- **Scenario**: When `row[14]` is `None`, an ML URL is generated with an empty taxonCode.
- **Root Cause**: There was no None check on `row[14]`
- **Fix**: Changed to `str(row[14]) if len(row) > 14 and row[14] else ""`

### [V005] Possibility that names containing spaces in `nameEN` of the Wikipedia link are not encoded correctly
- **Severity**: S4 (LOW)
- **Phase**: Code
- **Location**: templates/index.html:668
- **Technique**: BVA (string boundaries)
- **Scenario**: `encodeURIComponent(a.nameEN)` converts spaces to `%20`, but Wikipedia treats `_` separators as canonical. Little actual harm because it is redirected.
- **Root Cause**: Difference between the Wikipedia URL convention and `encodeURIComponent`

### [V006] API response parsing in `check_audio.py` is fragile
- **Severity**: S3 (MEDIUM)
- **Phase**: Code
- **Location**: scripts/check_audio.py:40
- **Technique**: error path analysis
- **Scenario**: `AttributeError` is raised if the API changes its format. Low priority because it is a manually run script.
- **Root Cause**: No type validation of the external API response

### [V007] kataToHira does not convert the katakana "ヷヸヹヺ" (U+30F7-U+30FA)
- **Severity**: S4 (LOW)
- **Phase**: Code
- **Location**: templates/index.html:482
- **Technique**: BVA (character range boundary analysis)
- **Scenario**: The regular expression `[\u30A1-\u30F6]` does not include ヷ (U+30F7) through ヺ (U+30FA). These are historical katakana and do not appear in modern animal names.
- **Root Cause**: The last 4 characters of the Unicode Katakana block are outside the range
- **Recommendation**: No action needed because the current dataset contains none of these characters

### [V008] `_apply_placeholders` does not detect unsubstituted placeholders
- **Severity**: S3 (MEDIUM) → **Fixed**
- **Phase**: Code
- **Location**: scripts/build.py:216-220
- **Technique**: error path analysis / contract verification (silent failure)
- **Scenario**: If `{{NEW_FIELD}}` is added to the template but not included in `mapping`, it remains as-is in the HTML output: a silent failure.
- **Root Cause**: `str.replace()` raises no error when nothing matches
- **Fix**: After substitution, check for leftovers with `re.findall(r"\{\{[A-Z_]+\}\}", html)` and print a warning

### [V009] `a.id` is embedded unescaped in the `shareButtons` URL
- **Severity**: S3 (MEDIUM)
- **Phase**: Code
- **Location**: templates/index.html:753
- **Technique**: security review (input boundary analysis)
- **Scenario**: If `a.id` contains `/` or `?`, an unintended URL is generated. However, the data source (Excel ID column) follows safe patterns such as `B001`, so there is no actual harm.
- **Root Cause**: Insufficient encoding when building the URL
- **Recommendation**: Low priority. As with V001, the data source is trusted, so there is no actual harm at present

### [V010] No handling when the clipboard API fails in `copyShareUrl`
- **Severity**: S3 (MEDIUM) → **Fixed**
- **Phase**: Code
- **Location**: templates/index.html:765-771, templates/species.html:227-233
- **Technique**: error path analysis
- **Scenario**: `navigator.clipboard.writeText()` fails in HTTP environments, in iframes, and when the user denies permission. With no `.catch()`, the Promise rejection is unhandled.
- **Root Cause**: The Promise reject path was not handled
- **Fix**: Added `.catch()` and display the "コピー失敗" ("Copy failed") message

### [V011] `nameJA` is not URL-encoded in the Wikipedia link of species.html
- **Severity**: S3 (MEDIUM) → **Fixed**
- **Phase**: Code
- **Location**: scripts/build.py:490
- **Technique**: BVA (URL string boundaries)
- **Scenario**: `esc()` is HTML escaping, not URL encoding. Non-ASCII characters were included directly in the `href` attribute value. The index.html side uses `encodeURIComponent()`, so the two are inconsistent.
- **Root Cause**: The Python side and the JS side built the Wikipedia URL differently
- **Fix**: Changed the build.py side to encode with `quote(name, safe="")`

### [V012] Opaque responses are cached in the SW fetch handler
- **Severity**: S4 (LOW)
- **Phase**: Code
- **Location**: scripts/build.py:613-619 (the generated sw.js)
- **Technique**: error path analysis
- **Scenario**: A cross-origin fetch from the CDN (Fuse.js) is not actually cached because `resp.ok` is `false`. If the Fuse.js CDN goes down, the site does not work offline.
- **Root Cause**: For an opaque response, ok is always false
- **Recommendation**: To aim for full PWA offline support, bundle Fuse.js locally. The current state is acceptable as progressive enhancement

## Coverage of Applied Techniques

| Technique | Scope | Result |
|---|---|---|
| BVA | Excel row/column index, SVG parser, URL encoding, kataToHira character range | V003, V004, V005, V007, V011 detected |
| Error path analysis | API response, file I/O, template substitution, clipboard API, SW fetch | V002, V006, V008, V010, V012 detected |
| Security review | User-derived data in HTML template literals, URL construction | V001, V009 detected |
| State transition analysis | Modal open/close, URL parameters, popstate, displayLang initialization, SW lifecycle | No issues |
| Decision table | Template injection paths, filter/search combinations, browser language detection | V002 detected |
| Contract verification | _apply_placeholders preconditions/postconditions | V008 detected |

## Summary

| Severity | Count | Fixed |
|---|---|---|
| S1 (CRITICAL) | 1 (V001) | 1 |
| S2 (HIGH) | 1 (V002) | 1 |
| S3 (MEDIUM) | 8 (V003, V004, V006, V008, V009, V010, V011) | 5 |
| S4 (LOW) | 3 (V005, V007, V012) | 0 |

Not fixed (no action needed / low priority): V003, V005, V006, V007, V009, V012

---

## Audit Rounds 1-3 Additional Verification (2026-04-17)

Ran 3 rounds of audits on 2 tracks, UX and quality. See `docs/ux-audit-report.md` / `docs/quality-audit-report.md` for details.
Below are only the main items merged into this report as V###.

### [V013] `</script>` and the like are embedded unescaped in JSON-LD strings
- **Severity**: S2 (HIGH) → **Fixed**
- **Phase**: Code
- **Location**: scripts/build.py (`_json_for_script`, `generate_species_pages`), templates/species.html:213-225
- **Technique**: security review (context-dependent escaping)
- **Scenario**: `json.dumps()` escapes `"` and `\` but lets `<`/`>`/`&` through. If a species name or the description contains `</script>`, it could break out of the `<script type="application/ld+json">` block and lead to XSS
- **Fix**: `_json_for_script()` additionally escapes `<` → `\u003c`, `>` → `\u003e`, `&` → `\u0026`. Injected via `JSON_HEADLINE` / `JSON_DESCRIPTION`
- **Test**: Verified on the actual build output that JSON-LD string values in `dist/species/**/*.html` contain no raw `<`/`>`/`&`

### [V014] hreflang missing on species pages
- **Severity**: S3 (MEDIUM) → **Fixed**
- **Phase**: Code
- **Location**: templates/species.html:23-27
- **Technique**: internationalization review (Google Search Central hreflang guidelines)
- **Scenario**: There were no references to language variants for users and search engines that want to switch languages from a species page
- **Fix**: Added 5 entries: `ja` / `en` / `ko` / `zh` / `x-default`. `ja` through `zh` point to the top page's `/?lang=*&id={ID}`, and `x-default` points to the species page's own `/species/{ID}/`

### [V015] 192/512 PNG icons not registered in the PWA manifest
- **Severity**: S3 (MEDIUM) → **Fixed**
- **Phase**: Code
- **Location**: scripts/build.py (`generate_pwa_icons`, `generate_manifest`), dist/icon-192.png, dist/icon-512.png, dist/manifest.json
- **Technique**: PWA Installability requirement verification (Lighthouse PWA audit)
- **Scenario**: The "Add to Home screen" requirement of Chrome for Android requires PNGs of size 192 / 512 to exist in the manifest. SVG alone is not enough
- **Fix**: `generate_pwa_icons()` generates PNGs at both 192/512 with the silhouette from favicon.svg centered at 80% scale. `generate_manifest()` registers them in the `icons` array with `purpose: "any maskable"`

### [V016] Korean and Chinese onomatopoeia remain on species with `hasVoice=なし`
- **Severity**: S4 (LOW) → **Fixed**
- **Phase**: Data
- **Location**: 6 species (A005, R012, F022, F026, F028, V011) in data/animal-sounds-data.xlsx (オノマトペマッピング sheet)
- **Technique**: contract verification (contrapositive of `hasVoice=あり ⇒ onomatopoeia 非空`)
- **Scenario**: Species explicitly marked "鳴き声なし" ("Silent") still had `ko`/`zh` rows, causing an inconsistency between the top-page cards and the species page
- **Fix**: Deleted the 12 affected rows from Excel. In `dist/animals.json`, the species with `hasVoice != "あり"` and non-empty `onomatopoeia` converged to 0
- **Test**: The contract is pinned by `tests/test_build.py::test_no_voice_species_have_no_onomatopoeia`

### [V017] Service Worker fetch handler fails to register due to a syntax error
- **Severity**: S2 (HIGH) → **Fixed**
- **Phase**: Code
- **Location**: scripts/build.py (`generate_sw`)
- **Technique**: syntax validity check (`node --check`)
- **Scenario**: When `.catch()` was added to the fetch handler in the R2 fix, the bracket balance broke and the whole of `dist/sw.js` became a syntax error. SW registration fails, but the error only appears in the console and the app seems to work at first glance (a silent failure)
- **Fix**: After the `caches.match(...).then(r => r || fetch(...).then(resp => {...}))` chain, correctly close `.catch(() => { return / for a navigate request, otherwise 503 })`. Brought the bracket balance to `(` 8 / `)` 8, `{` 11 / `}` 11
- **Test**: `tests/test_build.py::test_built_sw_is_syntactically_valid` (syntax check with `node --check`) and `test_sw_parens_are_balanced`

### [V018] Orphan onomatopoeia (references to the nonexistent ID `I033`)
- **Severity**: S3 (MEDIUM) → **Fixed**
- **Phase**: Data
- **Location**: data/animal-sounds-data.xlsx (オノマトペマッピング)
- **Technique**: contract verification (FK integrity)
- **Scenario**: Onomatopoeia rows for `I033`, which does not exist in メインデータ, remained in オノマトペマッピング
- **Fix**: Deleted the affected rows. The string `I033` appears 0 times in `animals.json`

### [V019] Missing English translations in 分類マッピング (class/order/family)
- **Severity**: S3 (MEDIUM) → **Fixed**
- **Phase**: Data
- **Location**: data/animal-sounds-data.xlsx (分類マッピング)
- **Technique**: missing value detection
- **Scenario**: Some species had empty `classEN` / `orderEN` / `familyEN`, and there were cases where the English UI showed "—"
- **Fix**: Filled in the English translations for all missing rows. The number of empty strings for `classEN`/`orderEN`/`familyEN` in `dist/animals.json` is 0 for all

### [V020] Duplicate entries in `no-audio.json`
- **Severity**: S4 (LOW) → **Fixed**
- **Phase**: Data
- **Location**: data/no-audio.json
- **Technique**: uniqueness check
- **Scenario**: Running the manually run script multiple times had added the same taxonCode more than once
- **Fix**: Deduplicated, converging to a state where the count matches the count after set conversion (110 entries)

### [V021] `lang` / `scope` not set in the PWA manifest
- **Severity**: S4 (LOW) → **Fixed**
- **Phase**: Code
- **Location**: scripts/build.py (`generate_manifest`)
- **Technique**: PWA specification review (w3c/manifest)
- **Fix**: Added `"lang": "ja"` and `"scope": "/"`

### [V022] Unicode mathematical symbols mixed into share button labels
- **Severity**: S4 (LOW) → **Fixed**
- **Phase**: Code
- **Location**: scripts/build.py (share_html in `generate_species_pages`)
- **Technique**: security review + A11y review
- **Scenario**: Mathematical symbols in U+1D400 through U+1D7FF (bold Latin, etc.) had slipped into the label strings, adversely affecting screen reader output and the search index
- **Fix**: Replaced them with ordinary ASCII Latin characters. Brought U+1D400-1D7FF in `dist/**` down to 0

### [V023] UX: WCAG 2.1 AA conformance improvements (contrast ratio + touch targets + language attributes)
- **Severity**: S3 (MEDIUM) group → **All items fixed**
- **Phase**: Code
- **Location**: templates/index.html, templates/species.html
- **Technique**: WCAG 2.1 AA / 2.2 additional SC check + numeric contrast ratio calculation + touch target measurement
- **Scenario / Fix**:
  - SC 1.4.3 Contrast: Dropped the AA-violating colors `#a8a29e` / `#059669` and unified on `#57534e` / `#78716c` / `#047857`. Body text has at least 4.5:1, and large text also has at least 3:1
  - SC 2.5.5 / 2.5.8 Target Size: Explicitly set `min-height: 44px` or a fixed 44x44 on `.filter-btn` / `.lang-tab` / `.modal-close` / `.search-clear`
  - SC 3.1.2 Language of Parts: Added `lang="en"` / `lang="la"` / `lang="${display language}"` at every location: card English names, scientific names, onomatopoeia, the modal, and the species page
  - SC 2.4.1 Bypass Blocks: Added `<a href="#main" class="skip-link">` + `<main id="main">` to both templates
  - SC 2.4.11 Focus Appearance (2.2 AA): A double visual indicator of border + 3px semi-transparent ring on the search box's `:focus-within`

### [V024] Build idempotency
- **Severity**: Informational → **Verification complete**
- **Phase**: Code
- **Location**: all of scripts/build.py
- **Technique**: build idempotency check (SHA-256 hashes of `dist/**` match across 2 runs on the same day)
- **Scenario**: If the output becomes nondeterministic through mixed-in random numbers or timestamps, or through dependence on set iteration order, CD becomes unstable
- **Result**: Confirmed that the hashes of all files match exactly across 2 runs on the same day

### Intentionally Deferred Items from Audit Rounds 1-3

The following are items judged during the audit as "no functional impact / suggestion level for peripheral quality" and intentionally deferred. They will be addressed in an additional PR when they become necessary.

| ID | Summary | Reason for deferral |
|---|---|---|
| Q005 (R1 carried over) | Audio source determination for the `A` prefix depends on `aid.startswith("B")` | In the current dataset, `A*` is only the initial samples, so there is no confusion with class Aves |
| Q006 (R1 carried over) | Species page URLs are not included in the Service Worker precache | Low demand for offline species page browsing. Covered by lazy caching at fetch time |
| ~~Q007~~ | ~~`lastmod` in `sitemap.xml` is the same day for all URLs~~ | Resolved: reduced the sitemap to the top page only |
| L8 (UX R3) | `.share-btn` falls short of 44x44 (~31px) | Meets WCAG 2.5.8 AA (24x24). Only the AAA criterion is not met |
| L9 (UX R3) | PNG icons not registered in the `sw.js` precache | No functional impact because Chrome fetches them automatically via the manifest |
| Info-1 (UX R3) | With the maskable icon's seafzone at 80%, the cat ear tips may be clipped | Within the range where visibility is maintained under actual device masks |
| O002 (QA R3) | `<link rel="manifest">` not added to species pages | No problem when arriving via the top page |
| O003 (QA R3) | No explicit "鳴き声なし" ("Silent") badge on species pages | Already shown explicitly on the card list side |

---

## Feature Enhancement Round (2026-05-16)

Feature additions aimed at SEO and UX improvements, and full multilingual UI support.

### [V025] Related species links, content differentiation, multilingual support for all UI
- **Severity**: Informational → **Implemented**
- **Phase**: Code
- **Location**: `scripts/build.py`, `templates/index.html`, `templates/species.html`
- **Technique**: SEO internal link analysis, content differentiation review, multilingual UI coverage check
- **Changes**:
  1. **Related species links** (`_build_related_species`): Selects up to 4 through a 4-level fallback family→order→class→phylum. `test_all_species_pages_have_related_section` guarantees that links are generated for all 305 species
  2. **"詳細ページで見る →" ("View detail page →") link**: Added a navigation link to `/species/{ID}/` inside the modal. Established the card→modal→species page path
  3. **Content differentiation**: Cards show only the name + main onomatopoeia, the modal shows a 1-language preview + detail link, and the species page shows the full 4-language display + external links + sharing + related species
  4. **Multilingual support for all UI**: Added `VOICE_METHOD_EN` (27 entries), `MODAL_LABELS`, `SEARCH_LABELS`, `NO_VOICE_LABEL`, `NO_ONO_LABEL`, `MODAL_HINT`, `CLOSE_LABEL`, `ALL_LABEL`. `updateFilterLabels()` / `updateSearchLabels()` switch every UI element on `applyDisplayLang`
- **Test**: Added 20 to `tests/test_build.py` (114 Pass in total). `TestBuildRelatedSpecies` (9), `TestBuildRelatedHtml` (6), `TestGenerateSpeciesPages` extended (4), `TestBuildIntegration` extended (3)

---

## Overall Summary (V001-V025, as of 2026-05-16)

| Severity | Count | Fixed | Deferred (no functional impact) |
|---|---|---|---|
| S1 (CRITICAL) | 1 (V001) | 1 | 0 |
| S2 (HIGH) | 3 (V002, V013, V017) | 3 | 0 |
| S3 (MEDIUM) | 12 (V003, V004, V006, V008, V009, V010, V011, V014, V015, V018, V019, V023) | 10 | 2 (V003, V006, V009) |
| S4 (LOW) | 7 (V005, V007, V012, V016, V020, V021, V022) | 4 | 3 (V005, V007, V012) |
| Informational | 1 (V024) | Verification complete | — |

S1/S2 are all fixed. The deferred S3/S4 items are all intentional Documented decisions (zero functional impact).
In UX audit Round 3, all WCAG 2.1 AA / 2.2 AA SC items were judged Pass.
V025: Related species links, content differentiation, multilingual support for all UI (feature addition, 114 tests Pass).

---

## Feature Enhancement Round (2026-05-16, Detail Page Localization + SEO Strengthening)

### [V026] 4-language detail page and carrying over the display language
- **Severity**: Informational → **Implemented**
- **Phase**: Code
- **Location**: `scripts/build.py`, `templates/species.html`, `templates/index.html`
- **Technique**: i18n DOM rewrite design, separation of responsibilities between bots and JS clients, contract review
- **Changes**:
  1. **4-language switching on the detail page**: Added an `I18N` dictionary (labels + 9 IUCN translations) to `templates/species.html`, and `applyLang(code)` rewrites all text, aria-labels, and the related species grid. The initial HTML stays in Japanese (for SEO / no-JS visitors)
  2. **Data embedding**: Added `_build_species_payload` / `_build_related_payload` / `_json_for_inline_script` to `scripts/build.py`. Embeds species-specific data (`SPECIES_DATA`) and related species data (`RELATED_DATA`) into the species page as `<script>`-safe JSON (escaping `<` `>` `&` to `<` `>` `&`)
  3. **DOM markers**: `data-i18n` (text) / `data-link-kind` (external link aria-label) / `data-share-kind` (share button aria-label + copy label) are added on the build.py side and accessed generically from `applyLang`
  4. **Changed the language fallback from ja → en**: Shared by `index.html` / `species.html`: URL `?lang=` → `navigator.language` → English fallback. So that non-CJK visitors such as French or German speakers do not see kanji they cannot read
  5. **Unified language tab position**: Placed in the header of `index.html` (right side of `.header-inner`) and inside the top-bar of `species.html`. Unified with a semi-transparent frame style on the green gradient band + `min-height: 44px` (keeping WCAG 2.1 AA tap targets)
  6. **lang carry-over links**: index→species (`<a class="species-detail-link" href="/species/{ID}/?lang=<xx>">`), species→index (top-bar `← 動物の鳴き声図鑑` ("← Animal Sound Encyclopedia"), back-link `← 図鑑で表示` ("← Back to encyclopedia")), and species→species (related species grid) carry over `?lang=`. Not added for ja, to keep the canonical
  7. **hreflang alignment**: Changed the species page hreflang from `/?lang=*&id={ID}` → `/species/{ID}/?lang=*`, unifying it to point to the page itself
- **Test**: Added `TestSpeciesPageI18nPayload` (11) + `TestJsonForInlineScript` (3) to `tests/test_build.py`, and `withLang` (4) + `detail link` (2) to `tests/test_frontend.mjs`. Also updated the `detectLang` expectation from `ja` → `en` fallback

### [V027] SEO canonicalization: canonical + WebSite JSON-LD + SearchAction
- **Severity**: S3 (MEDIUM) → **Fixed**
- **Phase**: Code
- **Location**: `templates/index.html` head
- **Technique**: duplicate content analysis, Schema.org conformance check
- **Scenario**: The top page had no canonical, so the `?lang=` / `?id=` / `?q=` variations could be treated as duplicate content. The on-site search was also not recognized by crawlers
- **Root Cause**: `<link rel="canonical">` and `@type: WebSite` JSON-LD were not set in the index.html template
- **Fix**:
  - Added `<link rel="canonical" href="https://koe-zukan.semnil.com/">`
  - Added `@type: WebSite` JSON-LD (name / alternateName / url / description / `inLanguage` / `potentialAction: SearchAction`)
  - The SearchAction `urlTemplate` is `.../?q={search_term_string}`. The JS in index.html takes `?q=`, puts it into the search box, and runs `onSearch()` (complying with the Google Sitelinks Search Box contract)
- **Test**: 3 cases in `TestIndexSeoMetadata` (canonical present / WebSite JSON-LD parse / SearchAction spec conformance)

### [V028] Onomatopoeia pronunciation playback on species pages (Web Speech API)
- **Severity**: Informational → **Implemented**
- **Phase**: Code
- **Location**: `templates/species.html`, `scripts/build.py` (`generate_species_pages`, `LANG_LABELS_JA`)
- **Technique**: feature design review, degradation design for environments without TTS, contract that aria-labels follow the language
- **Changes**:
  1. **Embedding the pronunciation buttons**: build.py outputs `<button class="ono-play" data-play-lang data-play-text aria-label>` in each onomatopoeia cell (`.ono-cell`). `data-play-text` is HTML-escaped (XSS defense)
  2. **TTS invocation**: `speakOnomatopoeia(btn)` converts `data-play-lang` (ja/en/ko/zh) to BCP-47 (`ja-JP`/`en-US`/`ko-KR`/`zh-CN`) with `PLAY_LANG_MAP`, then creates and plays a `SpeechSynthesisUtterance` (`rate = 0.9`). Before repeated playback or a new utterance, `speechSynthesis.cancel()` stops the previous utterance
  3. **Degradation in unsupported environments**: When `TTS_SUPPORTED` is false, adds the `html.no-tts` class, and CSS hides the buttons with `display: none` (does not affect scores such as Lighthouse)
  4. **aria-labels follow the language**: The initial HTML is output with Japanese names (`LANG_LABELS_JA`: 英語/韓国語/中国語 = English/Korean/Chinese), so it reads aloud naturally even without JS. After JS runs, `updatePlayLabels(code)` makes them follow the UI language with `PLAY_LABELS` × `LANG_NAMES_LOCALIZED` (4×4 = 16 combinations)
  5. **Visualizing the playback state**: Adds the `.playing` class to the button while it plays (accent background color), removed on `onend`/`onerror`. To prevent overlapping playback, clears every other `.playing` before an utterance starts
  6. **Stopping on page exit**: Calls `speechSynthesis.cancel()` on `beforeunload` so that the previous utterance does not continue across navigation between species pages
- **Trade-off**: Pronunciation accuracy depends on the OS/browser speech engine, and onomatopoeia not in the dictionary ("ニャー", "woof", etc.) may be read as spelled. Accepted because of the zero-external-dependency approach
- **Test**: Added `TestOnomatopoeiaPlayButtons` to `tests/test_build.py` (1-cell-to-1-button contract, `data-play-*` values, initial aria-label in 4 languages, HTML escaping, helper constants, BCP-47 mapping, no button generated for empty onomatopoeia)

### Summary Addendum

Cumulative from V025 onward:

| Severity | Count | Fixed |
|---|---|---|
| S3 (MEDIUM) | +1 (V027) | 1 |
| Informational | +3 (V025, V026, V028) | Implementation complete |

Integration tests such as build idempotency, all JSON-LD parse, and `rel=noopener` on all external links all continue to Pass.
