# SEO and content decisions

> 日本語版は [seo.ja.md](seo.ja.md) を参照してください.

Closed decisions about how the site presents itself to search engines and how content is divided between the card, the modal and the species page, with their reasons and the conditions for reopening them. The current behavior is described in [CLAUDE.md](../../CLAUDE.md) ("SEO settings" and "Content differentiation (card / modal / species page)").

## The sitemap lists the top page only

- **Decision** (2026-04-27, commit `8f76bf3`): `sitemap.xml` lists the top page and no species page (`generate_sitemap()` in `scripts/build.py`).
- **Reason**: Google Search Console reported the species pages as "Crawled - currently not indexed", so listing them in the sitemap did not get them indexed.
- **Earlier form**: the sitemap listed every species page (305 URLs when it was reduced).
- **Condition for reopening**: search traffic to the species pages is wanted. In that case the species pages themselves come first — more internal links that lead to them, and more content that only they carry — and the sitemap is extended after that.

## Cards, the modal and species pages carry different content

- **Decision** (2026-05-16, commit `1f0bcf3`): each layer has its own purpose and its own content.

  | Layer | Purpose | Content of its own |
  |---|---|---|
  | Card | Scanning the list | The name in the display language and the main onomatopoeia |
  | Modal | A light preview | Onomatopoeia in one language without the situation, and the link to the species page |
  | Species page | The detail view, and the page meant for search engines | Onomatopoeia in 4 languages with the situations, pronunciation playback, external links, share buttons, related species |

  External links and share buttons appear on the species page only.
- **Reason**: the same content on every layer would make the layers duplicate one another for search engines. Keeping the detail on the species page also leads visitors from the card through the modal to that page.

## Query-parameter URLs are canonicalized and hreflang points at the page itself

- **Decision** (2026-05-16, commit `9d494fe`): the top page and each species page declare a canonical URL without query parameters, so the `?lang=`, `?id=` and `?q=` variations of a page count as that one page. Both kinds of page carry 5 hreflang links (ja / en / ko / zh / x-default), and those of a species page point at its own `/species/{ID}/?lang=*`.
- **Reason**: language switching, the deep link to a card and the search entry point give one page several URLs, and without a canonical URL those can be treated as duplicate content. The hreflang links follow Google's specification, in which the language versions of a page, the page itself included, link to one another.
- **Earlier form**: the hreflang links of a species page pointed at the top page (`/?lang=*&id={ID}`).

## The SearchAction and `?q=` stay after the rich result was retired

- **Decision**: the `WebSite` JSON-LD of the top page keeps its `SearchAction`, and `index.html` keeps handling `?q=`. As long as the `urlTemplate` is declared, the URL it describes has to work.
- **History**: the `SearchAction` was added on 2026-05-16 (commit `9d494fe`) to meet the conditions of Google's Sitelinks Search Box. Google announced the end of that rich result in its Search Central blog post "Farewell, Sitelinks Search Box" (2024-10-21). On 2026-10-17 the mention of the Sitelinks Search Box as the reason was removed from `CLAUDE.md` ([#45](https://github.com/semnil/koe-zukan/pull/45)).
