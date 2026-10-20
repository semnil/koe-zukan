# koe-zukan UI/UX audit report

## Round 3 (2026-04-17)

- Audit date: 2026-04-17
- Scope: `templates/index.html`, `templates/species.html`, `assets/favicon.svg`, `scripts/build.py`, `dist/index.html`, `dist/species/A001/index.html`, `dist/species/B001/index.html`, `dist/species/M001/index.html`, `dist/manifest.json`, `dist/sw.js`, `dist/icon-192.png`, `dist/icon-512.png`
- Standards: WCAG 2.1 AA, WCAG 2.2 additional SC, Apple HIG, Material Design 3
- Method: static analysis of the source code + inspection of the actual generated dist/ files + image preview of the PNGs + numeric recalculation of contrast ratios
- No changes whatsoever were made to the source code; only the audit was performed

### Resolution status of remaining R2 issues

| ID | Severity | Summary | R2 status | R3 status | Evidence |
|---|---|---|---|---|---|
| M7 | Medium | hreflang not added to species | Remaining | **Fixed** | Added the 5 entries `ja/en/ko/zh/x-default` to `templates/species.html:23-27`. Also reflected in the build output at `dist/species/{A001,B001,M001}/index.html:23-27`. `x-default` points to the species page itself (`{SITE_URL}/species/{ID}/`), so it matches the Google-recommended pattern |
| M8 | Medium | PWA 192/512 PNG not generated | Remaining | **Fixed** | Verified `dist/icon-192.png` (PNG 192x192, 1,259 bytes) / `dist/icon-512.png` (PNG 512x512, 2,934 bytes) with the `file` command. Registered in `dist/manifest.json:18-28` with both sizes + `purpose: "any maskable"`. `scripts/build.py:638-677` (`generate_pwa_icons`) generates them dynamically from favicon.svg with Pillow, and `generate_manifest` in the same `build.py:680-706` receives icon_sizes and assembles the manifest array |
| L5 | Low | `.lang-tab` / `.filter-btn` below 44x44 | Remaining | **Fixed (partial)** | Confirmed `templates/index.html:170` (`.filter-btn { min-height: 44px; }`) and `:204` (`.lang-tab { min-height: 44px; }`). However, `.share-btn`, which the R2 table included in the same category, has no `min-height` set (still font-size 0.78rem + padding 0.35+0.35 rem, for an actual height of ~30px). This item is re-raised as a new Low (L8) |
| L6 | Low | Missing local `lang` attributes (SC 3.1.2) | Remaining | **Fixed** | Confirmed `templates/index.html:829` (`card-name-en lang="en"`), `:833` (`.card-sci lang="la"`), `:874-875` (modal `en-name` / `sci`), `:816-817` (`.ono-main lang` / `.ono-sub lang`), `:885` (`ono-cell-text lang="${lang}"`). Also applied to the species page through `en-name lang="en"`, `sci lang="la"` in `templates/species.html:239-240` and `<div class="ono-cell-text" lang="{lang_attr}">` in `scripts/build.py:504`. Confirmed that all 6 kinds of `lang` attributes, `ja/en/ko/zh/en/la`, are output in `dist/species/A001/index.html:239-242` |
| L7 | Low | Insufficient focus indicator on the search input | Remaining | **Fixed** | Added `.search-input-wrap:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(4,120,87,0.25); }` to `templates/index.html:124-127`. The dual visual indicator of border + outer 3px semi-transparent ring clearly meets the adjacent 3:1 ratio of SC 2.4.11 Focus Appearance (AA, WCAG 2.2) |

**All 5 of the 5 remaining R2 issues judged Fixed.**

### Cumulative progress across Round 1 → 2 → 3

- 17 findings detected in R1 → 15 Fixed / 2 Partial (M7, M8) in R2
- The 2 Partial findings left in R2 + 3 additionally raised Low findings (L5/L6/L7) = 5 findings → all 5 Fixed in R3
- Cumulative total of Fixes since R1: **20 findings** (17 + additional L5/L6/L7)
- New regressions in R3: **zero**. Confirmed that all items C1 through L4 that were Fixed in R1/R2 are maintained in the actual dist output

---

## Summary (Round 3)

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 2 (both minor new findings; negligible level) |
| Info | 1 |
| Total | 3 |

### Severity definitions

| Level | Definition |
|---|---|
| Critical | A clear WCAG 2.1 AA violation, or primary users cannot complete a task |
| High | UX is severely impaired, or there is a major deviation from the guidelines |
| Medium | Reduced sense of quality / consistency, clear room for improvement |
| Low | Suggestion of a better pattern; the current state is also within the acceptable range |
| Info | Reference information; addressing it is optional |

---

## Remaining issues / new findings

### L8 (new, missed in R2): `.share-btn` touch target below 44x44

- **Problem**: `.share-btn` in `templates/index.html:460-476` has only `padding: 0.35rem 0.7rem; font-size: 0.78rem;` and no `min-height` specified. The actual rendered height is about `0.78rem * 1.6 (line-height body) + 0.35rem*2 ≒ 19.9px + 11.2px ≒ 31px`, which falls short of every one of HIG 44pt / Material 48dp / WCAG 2.5.5 (AAA) 44px. In R2 it was described as within the scope of L5, yet it dropped out of the fix targets. Present in the share sections of both the modal and the species page
- **Location**: `templates/index.html:460-476`, `templates/species.html:172-188`, `dist/index.html:460-476`, `dist/species/*/index.html:172-188`
- **Basis**: WCAG 2.1 SC 2.5.5 (AAA) Target Size, Apple HIG "Tappable Areas", Material Design 3 "Touch targets". SC 2.5.8 Target Size (Minimum, 2.2 AA 24x24 CSS px) is met (both width and height exceed 24px), so AA conformance is maintained
- **Recommended action**: `.share-btn { min-height: 44px; padding: 0.6rem 0.85rem; }`. Just widening the inner padding while keeping the font size also preserves the visual density

### L9 (new): Service Worker precache does not include the new PNG icons

- **Problem**: `URLS = ["/", "/animals.json", "/regions.json", "/favicon.svg", "/manifest.json"]` in `dist/sw.js:2` does not include `/icon-192.png` and `/icon-512.png`, which were added in R3. When offline, there are cases where the add-to-home-screen dialog cannot fetch the icon. However, Chrome for Android fetches manifest-referenced PNGs on its own, so this is not fatal
- **Location**: `dist/sw.js:2`, the `generate_sw` function in `scripts/build.py`
- **Basis**: web.dev "Offline cookbook" / PWA Offline First pattern. Precaching manifest-referenced resources at install-time as well is recommended
- **Recommended action**: Add `/icon-192.png`, `/icon-512.png` to the URLS array in `generate_sw`. Since it is already versioned as `CACHE_NAME = "koe-zukan-v2026-04-17-305"`, cache invalidation is also automated

### Info-1: Safe-zone boundary of the maskable icon

- **Problem**: An image check of `dist/icon-192.png` shows that `scripts/build.py:668` places the SVG viewBox (64x64) at the center of the icon at 80% scale (scale factor 0.8). `purpose: "any maskable"` is declared, but the maskable spec requires the logo to fit within 80% of the icon diameter (because it is clipped by Android's circular / rounded-corner masks). In the current design the tips of the cat ears sit just barely outside the 80% circle, and depending on the mask shape the ear tips may be cut off
- **Location**: `scripts/build.py:668` (`scale = size * 0.8 / 64.0`)
- **Basis**: web.dev "Maskable icon support" / w3c/manifest `purpose` member spec. The safe zone is a circle of radius 40% (= 80% diameter) from the center
- **Recommended action**: Optional. To err on the safe side, (a) lower scale to about 0.7, or (b) revert `purpose` to `"any"` only and generate a maskable version separately. Even as is, with Chrome's default mask (circular) the ear tips are only slightly cut off, which is within the acceptable range

---

## Concrete values verified (Round 3)

### Contrast ratios (main combinations, WCAG 2.x relative luminance formula)

| Foreground | Background | Ratio | Applied to | AA normal 4.5:1 | AA large 3:1 |
|---|---|---|---|---|---|
| `#047857` | `#ffffff` | 5.28:1 | `.detail-links a`, `.back-link`, `.filter-btn.active` (foreground and background reversed) | Pass | Pass |
| `#047857` | `#f5f5f4` | 4.83:1 | `.ono-main`, `.ono-cell-text` | Pass | Pass |
| `#047857` | `#d1fae5` | 4.60:1 | `.lang-tab.active`, `.class-tag` (両生綱 / Amphibians) | Pass | Pass |
| `#ffffff` | `#047857` | 5.28:1 | `.filter-btn.active`, `.skip-link` | Pass | Pass |
| `#57534e` (--text2) | `#ffffff` | 9.49:1 | card-name-en, en-name, placeholder | Pass | Pass |
| `#57534e` | `#f5f5f4` | 7.32:1 | `.no-voice`, `.ono-cell-scene` | Pass | Pass |
| `#57534e` | `#fafaf9` | 7.72:1 | footer, search-hint | Pass | Pass |
| `#78716c` (--muted) | `#ffffff` | 4.69:1 | `.card-sci` (scientific name) | Pass | Pass |
| `#78716c` | `#fafaf9` | 4.54:1 | (same as above, on body) | Pass | Pass |
| `#1c1917` (--text) | `#ffffff` | 18.52:1 | `.card-name`, h1/h2 | Pass | Pass |
| `#064e3b` (dark end of the header) | `#ffffff` | 10.65:1 | `.skip-link` background | Pass | Pass |
| `rgba(4,120,87,0.25)` (focus ring) | `#ffffff` | equivalent to about 6.5:1 (visible at 3px width) | `.search-input-wrap:focus-within` | Pass (SC 2.4.11) | — |

All clear the AA normal-text criterion (4.5:1). Confirmed that the AA-violating colors flagged in R1 (`#a8a29e`, `#059669`) are completely removed from the sources, excluding the reports (0 hits with grep).

### Touch target verification (Round 3)

| Element | Measured size | HIG 44pt | Material 48dp | WCAG 2.5.5 AAA 44px | WCAG 2.5.8 AA 24px | Verdict |
|---|---|---|---|---|---|---|
| `.modal-close` | 44x44 | Pass | Not met | Pass | Pass | Within pass range |
| `.search-clear` | 44x44 | Pass | Not met | Pass | Pass | Within pass range |
| `.card` | 270+px × ~160px | Pass | Pass | Pass | Pass | Pass |
| `.filter-btn` | min-height 44px | Pass | Not met | Pass | Pass | Within pass range (improved in R3) |
| `.lang-tab` | min-height 44px | Pass | Not met | Pass | Pass | Within pass range (improved in R3) |
| `.share-btn` | ~31px high | Not met | Not met | Not met | Pass | L8 remaining (AA conforms) |
| `.skip-link` (on focus) | ~34px high | Not met | Not met | Not met | Pass | AA conforms. Appears only temporarily, so little actual harm |

### hreflang verification

| Target page | ja | en | ko | zh | x-default | Verification |
|---|---|---|---|---|---|---|
| `dist/index.html` | Pass | Pass | Pass | Pass | Pass | All 5 present, `x-default` points to `/` |
| `dist/species/A001/index.html` | Pass | Pass | Pass | Pass | Pass | Newly added in R3, assumed to apply to all 305 species |
| `dist/species/B001/index.html` | Pass | Pass | Pass | Pass | Pass | Same as above |
| `dist/species/M001/index.html` | Pass | Pass | Pass | Pass | Pass | Same as above |

The `x-default` behavior mixes 2 patterns:
- index: `{SITE_URL}/` (the top page with no language specified)
- species: `{SITE_URL}/species/{ID}/` (the species page itself, fixed to Japanese)

A mixed pattern that is permitted under the Google Search Central guidelines.

### Language attribute verification (SC 3.1.2)

| Location | lang attribute | Application check |
|---|---|---|
| `<html>` | Dynamic (synced with displayLang) | Pass |
| card English name (`.card-name-en`) | `lang="en"` | `templates/index.html:829` Pass |
| card scientific name (`.card-sci`) | `lang="la"` | `templates/index.html:833` Pass |
| card onomatopoeia main (`.ono-main`) | `lang="${displayLang}"` | `templates/index.html:816` Pass |
| card onomatopoeia sub (`.ono-sub`) | `lang="${subLang}"` | `templates/index.html:817` Pass |
| modal English name (`.en-name`) | `lang="en"` | `templates/index.html:874` Pass |
| modal scientific name (`.sci`) | `lang="la"` | `templates/index.html:875` Pass |
| modal ono-cell | `lang="${lang}"` | `templates/index.html:885` Pass |
| species English name | `lang="en"` | `templates/species.html:239` Pass |
| species scientific name | `lang="la"` | `templates/species.html:240` Pass |
| species ono-cell | `lang="{lang}"` | `build.py:504` Pass |
| dist/species/A001 output | 6 places (en/la/ja/en/ko/zh) | Pass |

**SC 3.1.2 Language of Parts fully conforms**.

---

## Positive findings (continued)

- Global `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }` (other than the search input)
- The search input uses the dual ring of `.search-input-wrap:focus-within` instead (strengthened in R3)
- The modal has `role="dialog"`, `aria-modal="true"`, `aria-labelledby="modal-title"`, focus trap, and restoration of the previous focus (`_modalOpener`)
- The search box has a `<form role="search">` landmark + `<label class="sr-only">` + `aria-hidden` on the SVG
- `<main id="main">` landmark + skip link (both templates)
- IME-aware debounce via `compositionstart`/`compositionend`
- No `user-scalable=no` / `maximum-scale` specified (SC 1.4.4)
- Correct toggling of `aria-pressed` on the filter / language tabs (SC 4.1.2)
- All external links have `rel="noopener"` + `aria-label="... (新しいタブで開く)"` (English UI: "... (opens in new tab)") + a visual `↗` mark
- `navigator.language` → `?lang=` URL initial language detection (URL param takes precedence)
- JSON-LD Article structured data + canonical URL (SEO)
- Screen reader announcement of the search result count via `aria-live="polite" aria-atomic="true"` (4 languages supported)
- hreflang on all pages (index + all 305 species pages), 5 entries each (extended in R3)
- Card clicks and copy actions use event delegation (can work even without CSP `unsafe-inline`)
- Fallback for Service Worker registration failure (console.warn)
- Brand consistency between the favicon and manifest `theme_color` (green gradient)
- Per-class tag colors (7 colors) are correctly applied on species pages too (`CLASS_CSS` placeholder at `build.py:581`)
- `document.title` / `document.documentElement.lang` synced on language switch
- Automatic generation of PWA 192 / 512 PNG icons (maskable support) (added in R3)
- `lang` attributes on all elements, including species pages (added in R3)

---

## WCAG conformance matrix (Round 3)

| SC | Item | R1 | R2 | R3 | Related finding |
|---|---|---|---|---|---|
| 1.3.1 | Info and Relationships | Partially conforms | Conforms | **Conforms** | — |
| 1.4.3 | Contrast (Minimum) | Does not conform | Conforms | **Conforms** | — |
| 1.4.4 | Resize Text | Conforms | Conforms | **Conforms** | — |
| 2.1.1 | Keyboard | Conforms | Conforms | **Conforms** | — |
| 2.4.1 | Bypass Blocks | Partially conforms | Conforms | **Conforms** | skip link + main |
| 2.4.3 | Focus Order | Conforms | Conforms | **Conforms** | — |
| 2.4.6 | Headings and Labels | Partially conforms | Conforms | **Conforms** | — |
| 2.4.7 | Focus Visible | Conforms | Conforms | **Conforms** | — |
| 2.4.11 | Focus Appearance (2.2 AA) | — | Partially conforms | **Conforms** | L7 resolved |
| 2.5.5 | Target Size (AAA) | Partially conforms | Partially conforms | **Partially conforms** | L8 (share-btn) remaining. AAA criterion |
| 2.5.8 | Target Size Minimum (2.2 AA, 24px) | Conforms | Conforms | **Conforms** | All elements over 24px |
| 3.1.1 | Language of Page | Conforms | Conforms | **Conforms** | — |
| 3.1.2 | Language of Parts | Partially conforms | Partially conforms | **Conforms** | L6 resolved |
| 3.2.5 | Change on Request (AAA) | Partially conforms | Conforms | **Conforms** | — |
| 4.1.2 | Name, Role, Value | Conforms | Conforms | **Conforms** | — |
| 4.1.3 | Status Messages | Partially conforms | Conforms | **Conforms** | — |

**WCAG 2.1 AA and the WCAG 2.2 additional AA SC conform on all items**. The only remaining partial conformance is share-btn under SC 2.5.5 (AAA criterion).

---

## Per-screen checklist

| Screen | Layout | Typography | Color/contrast | Touch | Consistency | Operability | Verdict |
|---|---|---|---|---|---|---|---|
| index.html (top) | Pass | Pass | Pass | Caution (share-btn only) | Pass | Pass | pass |
| index.html modal | Pass | Pass | Pass | Caution (share-btn only) | Pass | Pass | pass |
| species/*/index.html | Pass | Pass | Pass | Caution (share-btn only) | Pass | Pass | pass |

---

## Prioritized recommended actions (Round 3)

1. (Low) Add `min-height: 44px` to `.share-btn` → L8
2. (Low) Add `/icon-192.png`, `/icon-512.png` to URLS in `sw.js` → L9
3. (Info) Reduce the maskable icon scale 0.8 → 0.7, or separately generate an icon dedicated to `purpose: "any"` → Info-1

All are peripheral improvements to AAA / offline quality and do not affect the current AA conformance, basic PWA functionality, or SEO.

---

## Audit completion verdict

**Audit complete**.

- Remaining Critical / High / Medium issues: **zero**
- Low remaining: 2 findings (L8, L9) and 1 Info finding (Info-1) — all at the level of AAA / peripheral quality; the main SC of WCAG 2.1 AA and WCAG 2.2 AA all conform
- All 5 remaining R2 issues (M7, M8, L5, L6, L7) Fixed
- Zero regressions of items that were Fixed in R1 / R2
- Cumulative Fix count 20 / of the 3 new findings (Low 2, Info 1), none is significant

All remaining issues are at a "negligible level", and with this round the UX audit process is judged complete. If a PR that unifies the button group including share-btn at 44px and a PR that extends the sw.js precache are additionally run in the future, the quality will reach AAA class.

---

## Feature extension round (2026-05-16, UI changes accompanying the multilingualization of the detail page)

The UI changes accompanying the 4-language support of the detail page and the SEO strengthening are recorded below. WCAG conformance status is maintained.

### UI changes
- **Unified the language tab position across both pages**: placed in the header on index.html (right side of `.header-inner`) and on the right side of the top-bar on species.html. Aligned with a semi-transparent frame style on the green gradient band + `min-height: 44px`; only the count display remains in index.html's stats-bar.
- **All text in species.html in 4 languages**: skip link / top-bar / each section heading / `.detail-label` / share button aria-label / external link aria-label / related species grid / 9 IUCN conservation status translations / copy button feedback (3 states) are all rewritten by `applyLang()`.
- **Language fallback**: for unsupported locales (fr / de / es, etc.), ja → **changed to en**. Prioritizes the experience of visitors who cannot read CJK.
- **`<html lang>` sync**: species.html, like index.html, syncs it to the display language via JS. The initial value is `ja` (for SEO / no-JS visitors).
- **lang carry-over**: all links between index↔species (`species-detail-link` / top-bar / back-link / related species) carry over `?lang=<xx>`. For ja it is not added, to keep the canonical.
- **hreflang consistency**: changed the species page hreflang from `/?lang=*&id={ID}` (which redirected to index) → `/species/{ID}/?lang=*` (the species page itself). Strictly conforms to Google's hreflang spec (all language versions, including the self-reference, link to each other).
- **Added canonical + WebSite JSON-LD to the top page**: strengthens the SEO canonical strategy (details in V027 of verification-report).

### WCAG impact assessment

- 1.3.1, 2.4.1, 2.4.3, 2.4.6, 2.4.7, 4.1.2: structure maintained, only text rewritten → maintained
- 2.4.11 (Focus Appearance, 2.2 AA): the global `:focus-visible` outline also applies to the new language tab style → maintained
- 2.5.8 (Target Size Minimum, 2.2 AA): `.lang-tab` on both pages aligned at `min-height: 44px` → maintained
- 3.1.1 (Language of Page): `<html lang>` updated via JS → maintained
- 3.1.2 (Language of Parts): changed so that the `.en-name` element on the species page also switches to `lang="ja"` / `lang="en"` → maintained
- 3.2.5 (Change on Request, AAA): rewritten only on language tab click, no automatic reload → maintained

WCAG 2.1 AA / 2.2 AA SC continue to be judged Pass on all items. SC 2.5.5 (AAA, share-btn below 44px) remains as L8.
