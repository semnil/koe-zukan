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
