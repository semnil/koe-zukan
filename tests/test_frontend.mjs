/**
 * tests/test_frontend.mjs — Frontend logic unit tests
 *
 * Tests for functions extracted from templates/index.html.
 * Uses Node.js built-in test runner (node --test).
 *
 * Usage:
 *     node --test tests/test_frontend.mjs
 */

import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

// ── kataToHira ─────────────────────────────────────────
// Extracted from templates/index.html
function kataToHira(str) {
  return str.replace(/[\u30A1-\u30F6]/g, ch =>
    String.fromCharCode(ch.charCodeAt(0) - 0x60)
  );
}

describe("kataToHira", () => {
  it("converts basic katakana to hiragana", () => {
    assert.equal(kataToHira("ネコ"), "ねこ");
    assert.equal(kataToHira("スズメ"), "すずめ");
    assert.equal(kataToHira("イヌ"), "いぬ");
  });

  it("converts all katakana characters (ア-ヶ range)", () => {
    assert.equal(kataToHira("アイウエオ"), "あいうえお");
    assert.equal(kataToHira("カキクケコ"), "かきくけこ");
    assert.equal(kataToHira("サシスセソ"), "さしすせそ");
    assert.equal(kataToHira("タチツテト"), "たちつてと");
    assert.equal(kataToHira("ナニヌネノ"), "なにぬねの");
    assert.equal(kataToHira("ハヒフヘホ"), "はひふへほ");
    assert.equal(kataToHira("マミムメモ"), "まみむめも");
    assert.equal(kataToHira("ヤユヨ"), "やゆよ");
    assert.equal(kataToHira("ラリルレロ"), "らりるれろ");
    assert.equal(kataToHira("ワヲン"), "わをん");
  });

  it("converts voiced and semi-voiced katakana", () => {
    assert.equal(kataToHira("ガギグゲゴ"), "がぎぐげご");
    assert.equal(kataToHira("パピプペポ"), "ぱぴぷぺぽ");
    assert.equal(kataToHira("ザジズゼゾ"), "ざじずぜぞ");
    assert.equal(kataToHira("ダヂヅデド"), "だぢづでど");
    assert.equal(kataToHira("バビブベボ"), "ばびぶべぼ");
  });

  it("converts small katakana", () => {
    assert.equal(kataToHira("ァィゥェォ"), "ぁぃぅぇぉ");
    assert.equal(kataToHira("ッ"), "っ");
    assert.equal(kataToHira("ャュョ"), "ゃゅょ");
  });

  it("preserves hiragana (no double conversion)", () => {
    assert.equal(kataToHira("ねこ"), "ねこ");
    assert.equal(kataToHira("すずめ"), "すずめ");
  });

  it("preserves non-kana characters", () => {
    assert.equal(kataToHira("Hello"), "Hello");
    assert.equal(kataToHira("猫123"), "猫123");
    assert.equal(kataToHira(""), "");
  });

  it("handles mixed katakana and other characters", () => {
    assert.equal(kataToHira("ネコ（猫）"), "ねこ（猫）");
    assert.equal(kataToHira("オオカミ wolf"), "おおかみ wolf");
  });

  it("handles long katakana words", () => {
    assert.equal(kataToHira("ニホンアマガエル"), "にほんあまがえる");
    assert.equal(kataToHira("チュウゴクオオサンショウウオ"), "ちゅうごくおおさんしょううお");
  });

  it("handles katakana-hiragana boundary characters", () => {
    // ァ (U+30A1) is the first, ヶ (U+30F6) is the last in the regex range
    assert.equal(kataToHira("ァ"), "ぁ");
    assert.equal(kataToHira("ヶ"), "ゖ");
  });

  it("does not convert katakana prolonged sound mark", () => {
    // ー (U+30FC) is outside [\u30A1-\u30F6] range — should be preserved
    assert.equal(kataToHira("ニャー"), "にゃー");
    assert.equal(kataToHira("ワンワーン"), "わんわーん");
  });

  it("handles combined iteration marks and punctuation", () => {
    // 々 (U+3005), 〜 (U+301C), 、 (U+3001) sit outside the katakana range
    // and must pass through unchanged.
    assert.equal(kataToHira("ニャ々"), "にゃ々");
    assert.equal(kataToHira("ケロ〜"), "けろ〜");
    assert.equal(kataToHira("ワン、ワン"), "わん、わん");
  });

  it("leaves halfwidth katakana untouched (documented limitation)", () => {
    // Halfwidth katakana (U+FF66-U+FF9D) is NOT converted. Search for
    // ｶﾀｶﾅ against ひらがな-indexed fields will miss. Safe as long as
    // Excel data uses only fullwidth katakana (audit confirms).
    assert.equal(kataToHira("ｶﾀｶﾅ"), "ｶﾀｶﾅ");
    assert.equal(kataToHira("ﾆｬｰ"), "ﾆｬｰ");
  });

  it("leaves pre-5.0 JIS katakana ヷヸヹヺ untouched (V007)", () => {
    // U+30F7-U+30FA are historical, outside the conversion regex. Real data
    // does not contain these so no user-visible impact.
    assert.equal(kataToHira("ヷ"), "ヷ");
    assert.equal(kataToHira("ヸ"), "ヸ");
    assert.equal(kataToHira("ヹ"), "ヹ");
    assert.equal(kataToHira("ヺ"), "ヺ");
  });

  it("handles surrogate-pair emoji interleaved with katakana", () => {
    // Emoji (e.g., 🐱) is represented by surrogate pairs; conversion must
    // not corrupt the surrogate pair while mapping adjacent katakana.
    assert.equal(kataToHira("🐱ネコ"), "🐱ねこ");
    assert.equal(kataToHira("ネコ🐈ネコ"), "ねこ🐈ねこ");
  });
});

// ── esc (XSS prevention) ──────────────────────────────
// Extracted from templates/index.html
function esc(s) {
  if (!s) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

describe("esc", () => {
  it("escapes HTML special characters", () => {
    assert.equal(esc("<script>"), "&lt;script&gt;");
    assert.equal(esc('a"b'), "a&quot;b");
    assert.equal(esc("a&b"), "a&amp;b");
  });

  it("escapes single quotes (V001 fix)", () => {
    assert.equal(esc("');alert(1);//"), "&#39;);alert(1);//");
  });

  it("returns empty string for falsy values", () => {
    assert.equal(esc(""), "");
    assert.equal(esc(null), "");
    assert.equal(esc(undefined), "");
    assert.equal(esc(0), "");
  });

  it("preserves safe strings", () => {
    assert.equal(esc("Hello World"), "Hello World");
    assert.equal(esc("ネコ"), "ネコ");
    assert.equal(esc("B001"), "B001");
  });

  it("handles combined special characters", () => {
    assert.equal(
      esc(`<div class="x" data-v='y'>&`),
      "&lt;div class=&quot;x&quot; data-v=&#39;y&#39;&gt;&amp;"
    );
  });

  it("coerces numbers to strings", () => {
    assert.equal(esc(42), "42");
    assert.equal(esc(3.14), "3.14");
  });
});

// ── Browser language detection ─────────────────────────
// Extracted from templates/index.html
function detectLang(navigatorLang) {
  const lang = (navigatorLang || "ja").toLowerCase();
  if (lang.startsWith("ko")) return "ko";
  if (lang.startsWith("zh")) return "zh";
  if (lang.startsWith("en")) return "en";
  return "ja";
}

describe("detectLang", () => {
  it("detects Japanese", () => {
    assert.equal(detectLang("ja"), "ja");
    assert.equal(detectLang("ja-JP"), "ja");
  });

  it("detects Korean", () => {
    assert.equal(detectLang("ko"), "ko");
    assert.equal(detectLang("ko-KR"), "ko");
  });

  it("detects Chinese variants", () => {
    assert.equal(detectLang("zh"), "zh");
    assert.equal(detectLang("zh-CN"), "zh");
    assert.equal(detectLang("zh-TW"), "zh");
    assert.equal(detectLang("zh-Hans"), "zh");
    assert.equal(detectLang("zh-Hant"), "zh");
  });

  it("detects English", () => {
    assert.equal(detectLang("en"), "en");
    assert.equal(detectLang("en-US"), "en");
    assert.equal(detectLang("en-GB"), "en");
  });

  it("defaults to Japanese for unsupported languages", () => {
    assert.equal(detectLang("fr"), "ja");
    assert.equal(detectLang("de-DE"), "ja");
    assert.equal(detectLang("es"), "ja");
    assert.equal(detectLang("pt-BR"), "ja");
  });

  it("defaults to Japanese for null/undefined", () => {
    assert.equal(detectLang(null), "ja");
    assert.equal(detectLang(undefined), "ja");
    assert.equal(detectLang(""), "ja");
  });

  it("is case insensitive", () => {
    assert.equal(detectLang("KO-KR"), "ko");
    assert.equal(detectLang("ZH-CN"), "zh");
    assert.equal(detectLang("EN-US"), "en");
  });
});

// ── Fuse.js search key configuration ──────────────────

describe("search key configuration", () => {
  // Verify that hiragana fields (_hira, _altHira) are properly generated
  // Simulates what init() does in index.html

  function addHiraFields(animal) {
    animal._hira = kataToHira(animal.nameJA || "");
    if (animal.altJA) animal._altHira = kataToHira(animal.altJA);
    animal._onoHira = kataToHira(animal.onomatopoeiaJA || "");
    const onos = animal.onomatopoeia || [];
    animal._onoAllHira = onos.map(o => kataToHira(o.onomatopoeia || "")).filter(Boolean);
    return animal;
  }

  it("generates _hira from nameJA", () => {
    const a = addHiraFields({ nameJA: "ネコ" });
    assert.equal(a._hira, "ねこ");
  });

  it("generates _altHira from altJA", () => {
    const a = addHiraFields({ nameJA: "ネコ", altJA: "ミケネコ" });
    assert.equal(a._altHira, "みけねこ");
  });

  it("does not add _altHira when altJA is empty", () => {
    const a = addHiraFields({ nameJA: "ネコ", altJA: "" });
    assert.equal(a._altHira, undefined);
  });

  it("handles hiragana nameJA (no change)", () => {
    const a = addHiraFields({ nameJA: "ねこ" });
    assert.equal(a._hira, "ねこ");
  });

  it("handles kanji altJA with katakana", () => {
    const a = addHiraFields({ nameJA: "スズメ", altJA: "雀（スズメ）" });
    assert.equal(a._hira, "すずめ");
    assert.equal(a._altHira, "雀（すずめ）");
  });

  it("handles empty nameJA", () => {
    const a = addHiraFields({ nameJA: "" });
    assert.equal(a._hira, "");
  });

  it("handles null nameJA", () => {
    const a = addHiraFields({ nameJA: null });
    assert.equal(a._hira, "");
  });

  it("generates _onoHira from onomatopoeiaJA", () => {
    const a = addHiraFields({
      nameJA: "ネコ",
      onomatopoeiaJA: "ニャー",
      onomatopoeia: [{ onomatopoeia: "ニャー" }],
    });
    assert.equal(a._onoHira, "にゃー");
  });

  it("generates _onoAllHira from all onomatopoeia", () => {
    const a = addHiraFields({
      nameJA: "ネコ",
      onomatopoeiaJA: "ニャー",
      onomatopoeia: [
        { onomatopoeia: "ニャー" },
        { onomatopoeia: "Meow" },
        { onomatopoeia: "ミャオ" },
      ],
    });
    assert.deepEqual(a._onoAllHira, ["にゃー", "Meow", "みゃお"]);
  });

  it("filters empty onomatopoeia in _onoAllHira", () => {
    const a = addHiraFields({
      nameJA: "テスト",
      onomatopoeiaJA: "",
      onomatopoeia: [{ onomatopoeia: "" }, { onomatopoeia: "ワン" }],
    });
    assert.deepEqual(a._onoAllHira, ["わん"]);
  });
});

// ── getOno (display-language fallback) ─────────────────
// Extracted from templates/index.html renderResults path.

function getOno(animal, lang) {
  const entries = (animal.onomatopoeia || []).filter(o => o.lang === lang);
  if (entries.length === 0) return null;
  return entries.map(e => e.onomatopoeia).filter(Boolean).join(" / ");
}

describe("getOno", () => {
  const animal = {
    onomatopoeia: [
      { lang: "ja", onomatopoeia: "ニャー" },
      { lang: "en", onomatopoeia: "Meow" },
      { lang: "ko", onomatopoeia: "야옹" },
      { lang: "zh", onomatopoeia: "喵" },
    ],
  };

  it("returns Japanese onomatopoeia for ja", () => {
    assert.equal(getOno(animal, "ja"), "ニャー");
  });

  it("returns English onomatopoeia for en", () => {
    assert.equal(getOno(animal, "en"), "Meow");
  });

  it("returns null for language with no entries", () => {
    assert.equal(getOno({ onomatopoeia: [] }, "ja"), null);
  });

  it("joins multiple entries with slash", () => {
    const a = {
      onomatopoeia: [
        { lang: "ja", onomatopoeia: "ニャー" },
        { lang: "ja", onomatopoeia: "ミャオ" },
      ],
    };
    assert.equal(getOno(a, "ja"), "ニャー / ミャオ");
  });

  it("filters falsy onomatopoeia within a language", () => {
    const a = {
      onomatopoeia: [
        { lang: "ja", onomatopoeia: "" },
        { lang: "ja", onomatopoeia: "ワン" },
      ],
    };
    assert.equal(getOno(a, "ja"), "ワン");
  });
});

// ── URL parameter handling (?id=) ──────────────────────
// Regression guard for the deep-link path that opens modals on load.

describe("URL id parameter extraction", () => {
  function extractId(urlString) {
    return new URL(urlString).searchParams.get("id");
  }

  it("extracts standard ID", () => {
    assert.equal(extractId("https://koe-zukan.semnil.com/?id=B001"), "B001");
  });

  it("returns null when id is absent", () => {
    assert.equal(extractId("https://koe-zukan.semnil.com/"), null);
  });

  it("decodes URL-encoded IDs", () => {
    // IDs never contain % in real data, but validate decoding works regardless.
    assert.equal(extractId("https://x/?id=B%30%30%31"), "B001");
  });

  it("takes first id when duplicated", () => {
    assert.equal(extractId("https://x/?id=B001&id=B002"), "B001");
  });
});

// ── Share URL encoding ─────────────────────────────────
// Protects against regressions in the share button URL construction.

describe("share URL encoding", () => {
  function buildShareUrl(baseUrl, id) {
    return `${baseUrl}/species/${id}/`;
  }

  it("builds canonical share URL", () => {
    const url = buildShareUrl("https://koe-zukan.semnil.com", "B001");
    assert.equal(url, "https://koe-zukan.semnil.com/species/B001/");
  });

  it("encodes share URL for Twitter intent", () => {
    const url = "https://koe-zukan.semnil.com/species/B001/";
    const encoded = encodeURIComponent(url);
    // & and / must be percent-encoded for query values
    assert.match(encoded, /%3A%2F%2F/);
    assert.equal(encoded, "https%3A%2F%2Fkoe-zukan.semnil.com%2Fspecies%2FB001%2F");
  });
});

// ── hasVoice decision path ─────────────────────────────
// Mirrors renderResults onomatopoeia display branching.

describe("hasVoice display decision", () => {
  function decide(animal, displayLang, getOnoFn) {
    const ono = getOnoFn(animal, displayLang)
      || (displayLang !== "ja" ? animal.onomatopoeiaJA : "");
    const hasVoice = animal.hasVoice === "あり";
    if (hasVoice && ono) return { type: "ono", text: ono };
    if (hasVoice) return { type: "no-data", lang: displayLang };
    return { type: "silent" };
  }

  it("renders onomatopoeia when hasVoice and lang entry present", () => {
    const a = {
      hasVoice: "あり",
      onomatopoeiaJA: "ニャー",
      onomatopoeia: [{ lang: "ja", onomatopoeia: "ニャー" }],
    };
    assert.deepEqual(decide(a, "ja", getOno), { type: "ono", text: "ニャー" });
  });

  it("falls back to onomatopoeiaJA when displayLang lacks data", () => {
    const a = {
      hasVoice: "あり",
      onomatopoeiaJA: "ニャー",
      onomatopoeia: [{ lang: "ja", onomatopoeia: "ニャー" }],
    };
    assert.deepEqual(decide(a, "ko", getOno), { type: "ono", text: "ニャー" });
  });

  it("shows no-data when hasVoice but all empty for displayLang", () => {
    const a = {
      hasVoice: "あり",
      onomatopoeiaJA: "",
      onomatopoeia: [],
    };
    assert.deepEqual(decide(a, "ja", getOno), { type: "no-data", lang: "ja" });
  });

  it("shows silent when hasVoice is not あり", () => {
    const a = { hasVoice: "なし", onomatopoeiaJA: "", onomatopoeia: [] };
    assert.deepEqual(decide(a, "ja", getOno), { type: "silent" });
  });
});
