# Feature decisions

> 日本語版は [features.ja.md](features.ja.md) を参照してください.

Closed decisions about what the site offers and how, with their reasons, the alternatives that were turned down and the conditions for reopening them. The current behavior is described in [CLAUDE.md](../../CLAUDE.md) ("Site architecture").

## Pronunciation playback uses the Web Speech API

- **Decision** (2026-05-16, commit `2fc3eb5`): each onomatopoeia cell of a species page has a play button that speaks the text with the browser's built-in speech synthesis (`speechSynthesis`). How a word is read is left to the speech engine of the OS and the browser.
- **Reason**: the aim is to let a visitor hear how an onomatopoeia is pronounced in a language other than their own. The Web Speech API does that with no external dependency and no added cost or files, and it covers the 4 languages (`ja-JP` / `en-US` / `ko-KR` / `zh-CN`) at once. That fits the site's policy of having no external dependencies.
- **Alternatives turned down**:
  - Generating mp3 files ahead of time with a cloud text-to-speech service and committing them. 305 species × 4 languages came to about 1,200 files, and the generation cost, the repository size and the API key to manage were too much for what it would give. The site would have stayed fully static.
  - Showing IPA notation beside the text. Sound answers "how is this pronounced" more directly than notation does.
- **Condition for reopening**: strong dissatisfaction with the pronunciation quality. The move is then to the pre-generated audio. For that, the build keeps a structure in which a generation step can be added right after it reads `data/animal-sounds-data.xlsx`.

## No fifth display language

- **Decision** (2026-10-17): no fifth display language is added. The display languages stay ja / en / ko / zh.
- **History**: `CLAUDE.md` had a "Future extension candidates" section that said a language could be added just by adding rows. The code names the 4 languages directly, so the statement did not match it, and the section was removed ([#45](https://github.com/semnil/koe-zukan/pull/45)).
