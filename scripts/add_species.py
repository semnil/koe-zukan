#!/usr/bin/env python3
"""
add_species.py — 種を一括追加するスクリプト

SPECIES_DATA リストに定義された種を Excel の各シートに追加する。
既存 ID / 学名との重複はスキップ。

使い方:
    python scripts/add_species.py [--dry-run]
"""

import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    print("Error: openpyxl required. pip install openpyxl")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "animal-sounds-data.xlsx"

# ── 追加種データ ──────────────────────────────────────
# Each entry:
#   id, nameJA, phylum, class, order, family, hasVoice, onomatopoeiaJA,
#   voiceMethod, habitat, conservation,
#   scientificName, nameEN, altJA, altEN,
#   onomatopoeia: [(lang, langName, text, scene)],
#   regions: [regionID, ...]

SPECIES_DATA = [
    # ── 鳥類 (+27) ──
    {
        "id": "B096", "nameJA": "ツグミ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "ヒタキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "クィクィ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Turdus naumanni", "nameEN": "Naumann's thrush",
        "onomatopoeia": [("ja", "日本語", "クィクィ", "地鳴き"), ("en", "英語", "Kwee-kwee", "call")],
        "regions": ["REG01", "REG02", "REG03"],
    },
    {
        "id": "B097", "nameJA": "シロハラ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "ヒタキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ツィー", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Turdus pallidus", "nameEN": "Pale thrush",
        "onomatopoeia": [("ja", "日本語", "ツィー", "地鳴き"), ("en", "英語", "Tsee", "call")],
        "regions": ["REG01", "REG02", "REG03"],
    },
    {
        "id": "B098", "nameJA": "キクイタダキ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "キクイタダキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ツィツィツィ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Regulus regulus", "nameEN": "Goldcrest",
        "onomatopoeia": [("ja", "日本語", "ツィツィツィ", "さえずり"), ("en", "英語", "Tsee-tsee-tsee", "song")],
        "regions": ["REG01", "REG08"],
    },
    {
        "id": "B099", "nameJA": "キレンジャク", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "レンジャク科", "hasVoice": "あり",
        "onomatopoeiaJA": "チリリリリ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Bombycilla japonica", "nameEN": "Japanese waxwing",
        "onomatopoeia": [("ja", "日本語", "チリリリリ", "さえずり"), ("en", "英語", "Triiiii", "call")],
        "regions": ["REG01", "REG02", "REG07"],
    },
    {
        "id": "B100", "nameJA": "カワガラス", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "カワガラス科", "hasVoice": "あり",
        "onomatopoeiaJA": "ビッビッ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Cinclus pallasii", "nameEN": "Brown dipper",
        "altJA": None, "altEN": None,
        "onomatopoeia": [("ja", "日本語", "ビッビッ", "地鳴き"), ("en", "英語", "Zit-zit", "call")],
        "regions": ["REG01", "REG02", "REG03"],
    },
    {
        "id": "B101", "nameJA": "サンコウチョウ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "カササギヒタキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ツキヒホシ ホイホイホイ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Terpsiphone atrocaudata", "nameEN": "Black paradise flycatcher",
        "onomatopoeia": [("ja", "日本語", "ツキヒホシ ホイホイホイ", "さえずり"), ("en", "英語", "Tsuki-hi-hoshi hoi-hoi-hoi", "song")],
        "regions": ["REG01", "REG03", "REG05"],
    },
    {
        "id": "B102", "nameJA": "ヤマガラ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "シジュウカラ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ツーツーピー", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Sittiparus varius", "nameEN": "Varied tit",
        "onomatopoeia": [("ja", "日本語", "ツーツーピー", "さえずり"), ("en", "英語", "Tsuu-tsuu-pee", "song")],
        "regions": ["REG01", "REG03"],
    },
    {
        "id": "B103", "nameJA": "コゲラ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "キツツキ目", "family": "キツツキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ギィー", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Yungipicus kizuki", "nameEN": "Japanese pygmy woodpecker",
        "onomatopoeia": [("ja", "日本語", "ギィー", "地鳴き"), ("en", "英語", "Gee", "call")],
        "regions": ["REG01"],
    },
    {
        "id": "B104", "nameJA": "アオバト", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "ハト目", "family": "ハト科", "hasVoice": "あり",
        "onomatopoeiaJA": "アオーアオー", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Treron sieboldii", "nameEN": "White-bellied green pigeon",
        "onomatopoeia": [("ja", "日本語", "アオーアオー", "さえずり"), ("en", "英語", "Aoo-aoo", "song")],
        "regions": ["REG01", "REG03"],
    },
    {
        "id": "B105", "nameJA": "コマドリ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "ヒタキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ヒンカラカラカラ", "voiceMethod": "鳴管",
        "conservation": "NT",
        "scientificName": "Larvivora akahige", "nameEN": "Japanese robin",
        "onomatopoeia": [("ja", "日本語", "ヒンカラカラカラ", "さえずり"), ("en", "英語", "Hin-kara-kara-kara", "song")],
        "regions": ["REG01"],
    },
    {
        "id": "B106", "nameJA": "ミソサザイ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "ミソサザイ科", "hasVoice": "あり",
        "onomatopoeiaJA": "チリリリリ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Troglodytes troglodytes", "nameEN": "Eurasian wren",
        "onomatopoeia": [("ja", "日本語", "チリリリリ", "さえずり"), ("en", "英語", "Trill-trill", "song")],
        "regions": ["REG01", "REG08"],
    },
    {
        "id": "B107", "nameJA": "オオルリ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "ヒタキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ピールリ ピールリ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Cyanoptila cyanomelana", "nameEN": "Blue-and-white flycatcher",
        "onomatopoeia": [("ja", "日本語", "ピールリ ピールリ", "さえずり"), ("en", "英語", "Pee-ruri pee-ruri", "song")],
        "regions": ["REG01", "REG03"],
    },
    {
        "id": "B108", "nameJA": "イカル", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "アトリ科", "hasVoice": "あり",
        "onomatopoeiaJA": "キーコーキー", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Eophona personata", "nameEN": "Japanese grosbeak",
        "onomatopoeia": [("ja", "日本語", "キーコーキー", "さえずり"), ("en", "英語", "Kee-ko-kee", "song")],
        "regions": ["REG01", "REG02", "REG03"],
    },
    {
        "id": "B109", "nameJA": "オオヨシキリ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "ヨシキリ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ギョギョシ ギョギョシ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Acrocephalus orientalis", "nameEN": "Oriental reed warbler",
        "onomatopoeia": [("ja", "日本語", "ギョギョシ ギョギョシ", "さえずり"), ("en", "英語", "Gyo-gyo-shi", "song")],
        "regions": ["REG01", "REG02", "REG03"],
    },
    {
        "id": "B110", "nameJA": "ホオジロ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "ホオジロ科", "hasVoice": "あり",
        "onomatopoeiaJA": "チチチッ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Emberiza cioides", "nameEN": "Meadow bunting",
        "onomatopoeia": [("ja", "日本語", "チチチッ", "地鳴き"), ("en", "英語", "Chi-chi-chi", "call")],
        "regions": ["REG01", "REG02", "REG03"],
    },
    {
        "id": "B111", "nameJA": "セグロセキレイ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "セキレイ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ジジッ ジジッ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Motacilla grandis", "nameEN": "Japanese wagtail",
        "onomatopoeia": [("ja", "日本語", "ジジッ ジジッ", "地鳴き"), ("en", "英語", "Jit-jit", "call")],
        "regions": ["REG01"],
    },
    {
        "id": "B112", "nameJA": "キセキレイ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "セキレイ科", "hasVoice": "あり",
        "onomatopoeiaJA": "チチン チチン", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Motacilla cinerea", "nameEN": "Grey wagtail",
        "onomatopoeia": [("ja", "日本語", "チチン チチン", "地鳴き"), ("en", "英語", "Chisit", "call")],
        "regions": ["REG01", "REG08"],
    },
    {
        "id": "B113", "nameJA": "トラツグミ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "ヒタキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ヒー ヒョー", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Zoothera dauma", "nameEN": "Scaly thrush",
        "altJA": "鵺（ぬえ）",
        "onomatopoeia": [("ja", "日本語", "ヒー ヒョー", "夜間さえずり"), ("en", "英語", "Hee hyoo", "night song")],
        "regions": ["REG01", "REG03", "REG05"],
    },
    {
        "id": "B114", "nameJA": "サンショウクイ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "サンショウクイ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ピリリリ", "voiceMethod": "鳴管",
        "conservation": "VU",
        "scientificName": "Pericrocotus divaricatus", "nameEN": "Ashy minivet",
        "onomatopoeia": [("ja", "日本語", "ピリリリ", "さえずり"), ("en", "英語", "Piri-ri-ri", "song")],
        "regions": ["REG01", "REG03"],
    },
    {
        "id": "B115", "nameJA": "コサメビタキ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "ヒタキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "チチチチチ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Muscicapa dauurica", "nameEN": "Asian brown flycatcher",
        "onomatopoeia": [("ja", "日本語", "チチチチチ", "さえずり"), ("en", "英語", "Chi-chi-chi-chi", "song")],
        "regions": ["REG01", "REG02", "REG03"],
    },
    {
        "id": "B116", "nameJA": "カナリア", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "スズメ目", "family": "アトリ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ピロロロロ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Serinus canaria", "nameEN": "Atlantic canary",
        "onomatopoeia": [("ja", "日本語", "ピロロロロ", "さえずり"), ("en", "英語", "Tweet-tweet-tweet", "song")],
        "regions": ["REG20"],
    },
    {
        "id": "B117", "nameJA": "オニオオハシ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "キツツキ目", "family": "オオハシ科", "hasVoice": "あり",
        "onomatopoeiaJA": "グワッグワッ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Ramphastos toco", "nameEN": "Toco toucan",
        "onomatopoeia": [("ja", "日本語", "グワッグワッ", "さえずり"), ("en", "英語", "Grrawk-grrawk", "call")],
        "regions": ["REG14"],
    },
    {
        "id": "B118", "nameJA": "ノドアカハチドリ", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "アマツバメ目", "family": "ハチドリ科", "hasVoice": "あり",
        "onomatopoeiaJA": "チッチッチッ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Archilochus colubris", "nameEN": "Ruby-throated hummingbird",
        "onomatopoeia": [("ja", "日本語", "チッチッチッ", "地鳴き"), ("en", "英語", "Chit-chit-chit", "call")],
        "regions": ["REG12"],
    },
    {
        "id": "B119", "nameJA": "キバタン", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "オウム目", "family": "オウム科", "hasVoice": "あり",
        "onomatopoeiaJA": "ギャーギャー", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Cacatua galerita", "nameEN": "Sulphur-crested cockatoo",
        "onomatopoeia": [("ja", "日本語", "ギャーギャー", "地鳴き"), ("en", "英語", "Screeech", "call")],
        "regions": ["REG15", "REG16", "REG26"],
    },
    {
        "id": "B120", "nameJA": "ヨウム", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "オウム目", "family": "インコ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ピーヨ", "voiceMethod": "鳴管",
        "conservation": "EN",
        "scientificName": "Psittacus erithacus", "nameEN": "Grey parrot",
        "onomatopoeia": [("ja", "日本語", "ピーヨ", "地鳴き"), ("en", "英語", "Whistle", "call")],
        "regions": ["REG11"],
    },
    {
        "id": "B121", "nameJA": "ハクチョウ（コハクチョウ）", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "カモ目", "family": "カモ科", "hasVoice": "あり",
        "onomatopoeiaJA": "コォー コォー", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Cygnus columbianus", "nameEN": "Tundra swan",
        "altJA": "コハクチョウ",
        "onomatopoeia": [("ja", "日本語", "コォー コォー", "群鳴き"), ("en", "英語", "Koo-koo", "flocking call")],
        "regions": ["REG01", "REG02", "REG07", "REG08", "REG12"],
    },
    {
        "id": "B122", "nameJA": "アカショウビン", "phylum": "脊索動物門", "class": "鳥綱",
        "order": "ブッポウソウ目", "family": "カワセミ科", "hasVoice": "あり",
        "onomatopoeiaJA": "キョロロロロ", "voiceMethod": "鳴管",
        "conservation": "LC",
        "scientificName": "Halcyon coromanda", "nameEN": "Ruddy kingfisher",
        "onomatopoeia": [("ja", "日本語", "キョロロロロ", "さえずり"), ("en", "英語", "Kyorororo", "song")],
        "regions": ["REG01", "REG03", "REG05"],
    },

    # ── 哺乳類 (+13) ──
    {
        "id": "M069", "nameJA": "ジャガー", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "ネコ目", "family": "ネコ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ガウッ ガウッ", "voiceMethod": "喉",
        "conservation": "NT",
        "scientificName": "Panthera onca", "nameEN": "Jaguar",
        "onomatopoeia": [("ja", "日本語", "ガウッ ガウッ", "威嚇"), ("en", "英語", "Saw-like roar", "territorial call")],
        "regions": ["REG13", "REG14"],
    },
    {
        "id": "M070", "nameJA": "ヒョウ", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "ネコ目", "family": "ネコ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ゴロゴロ ガウ", "voiceMethod": "喉",
        "conservation": "VU",
        "scientificName": "Panthera pardus", "nameEN": "Leopard",
        "onomatopoeia": [("ja", "日本語", "ゴロゴロ ガウ", "威嚇"), ("en", "英語", "Rasping cough", "call")],
        "regions": ["REG04", "REG05", "REG10", "REG11"],
    },
    {
        "id": "M071", "nameJA": "シマリス", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "ネズミ目", "family": "リス科", "hasVoice": "あり",
        "onomatopoeiaJA": "チチチチ", "voiceMethod": "喉",
        "conservation": "LC",
        "scientificName": "Tamias sibiricus", "nameEN": "Siberian chipmunk",
        "onomatopoeia": [("ja", "日本語", "チチチチ", "警戒音"), ("en", "英語", "Chip-chip-chip", "alarm call")],
        "regions": ["REG01", "REG02", "REG07"],
    },
    {
        "id": "M072", "nameJA": "ムササビ", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "ネズミ目", "family": "リス科", "hasVoice": "あり",
        "onomatopoeiaJA": "グルルルル", "voiceMethod": "喉",
        "conservation": "LC",
        "scientificName": "Petaurista leucogenys", "nameEN": "Japanese giant flying squirrel",
        "onomatopoeia": [("ja", "日本語", "グルルルル", "夜間鳴き声"), ("en", "英語", "Grrrr", "night call")],
        "regions": ["REG01"],
    },
    {
        "id": "M073", "nameJA": "ミーアキャット", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "ネコ目", "family": "マングース科", "hasVoice": "あり",
        "onomatopoeiaJA": "ワッワッワッ", "voiceMethod": "喉",
        "conservation": "LC",
        "scientificName": "Suricata suricatta", "nameEN": "Meerkat",
        "onomatopoeia": [("ja", "日本語", "ワッワッワッ", "警戒音"), ("en", "英語", "Bark-bark", "sentinel alarm")],
        "regions": ["REG10"],
    },
    {
        "id": "M074", "nameJA": "ナマケモノ（フタユビナマケモノ）", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "有毛目", "family": "フタユビナマケモノ科", "hasVoice": "あり",
        "onomatopoeiaJA": "アーアー", "voiceMethod": "喉",
        "conservation": "LC",
        "scientificName": "Choloepus didactylus", "nameEN": "Linnaeus's two-toed sloth",
        "altJA": "フタユビナマケモノ",
        "onomatopoeia": [("ja", "日本語", "アーアー", "鳴き声"), ("en", "英語", "Aah-aah", "call")],
        "regions": ["REG14"],
    },
    {
        "id": "M075", "nameJA": "フェネック", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "ネコ目", "family": "イヌ科", "hasVoice": "あり",
        "onomatopoeiaJA": "キャンキャン", "voiceMethod": "喉",
        "conservation": "LC",
        "scientificName": "Vulpes zerda", "nameEN": "Fennec fox",
        "onomatopoeia": [("ja", "日本語", "キャンキャン", "鳴き声"), ("en", "英語", "Yip-yip", "bark")],
        "regions": ["REG09"],
    },
    {
        "id": "M076", "nameJA": "スカンク（シマスカンク）", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "ネコ目", "family": "スカンク科", "hasVoice": "あり",
        "onomatopoeiaJA": "シャーッ", "voiceMethod": "喉",
        "conservation": "LC",
        "scientificName": "Mephitis mephitis", "nameEN": "Striped skunk",
        "altJA": "シマスカンク",
        "onomatopoeia": [("ja", "日本語", "シャーッ", "威嚇"), ("en", "英語", "Hiss-stomp", "warning")],
        "regions": ["REG12"],
    },
    {
        "id": "M077", "nameJA": "マナティー", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "海牛目", "family": "マナティー科", "hasVoice": "あり",
        "onomatopoeiaJA": "キュー", "voiceMethod": "喉",
        "conservation": "VU",
        "scientificName": "Trichechus manatus", "nameEN": "West Indian manatee",
        "onomatopoeia": [("ja", "日本語", "キュー", "コミュニケーション"), ("en", "英語", "Squeak-squeal", "communication")],
        "regions": ["REG13"],
    },
    {
        "id": "M078", "nameJA": "オオカミ（タイリクオオカミ）", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "ネコ目", "family": "イヌ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ウォーーン", "voiceMethod": "喉",
        "conservation": "LC",
        "scientificName": "Canis lupus", "nameEN": "Gray wolf",
        "altJA": "タイリクオオカミ",
        "onomatopoeia": [("ja", "日本語", "ウォーーン", "遠吠え"), ("en", "英語", "Howl", "howling")],
        "regions": ["REG07", "REG08", "REG12"],
    },
    {
        "id": "M079", "nameJA": "コヨーテ", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "ネコ目", "family": "イヌ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ワォーン キャンキャン", "voiceMethod": "喉",
        "conservation": "LC",
        "scientificName": "Canis latrans", "nameEN": "Coyote",
        "onomatopoeia": [("ja", "日本語", "ワォーン キャンキャン", "遠吠え"), ("en", "英語", "Yip-howl", "group howl")],
        "regions": ["REG12"],
    },
    {
        "id": "M080", "nameJA": "カワウソ（ユーラシアカワウソ）", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "ネコ目", "family": "イタチ科", "hasVoice": "あり",
        "onomatopoeiaJA": "キュッキュッ", "voiceMethod": "喉",
        "conservation": "NT",
        "scientificName": "Lutra lutra", "nameEN": "Eurasian otter",
        "altJA": "ユーラシアカワウソ",
        "onomatopoeia": [("ja", "日本語", "キュッキュッ", "コミュニケーション"), ("en", "英語", "Chirp-chirp", "contact call")],
        "regions": ["REG08", "REG02"],
    },
    {
        "id": "M081", "nameJA": "オランウータン", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "サル目", "family": "ヒト科", "hasVoice": "あり",
        "onomatopoeiaJA": "ウォォォーン", "voiceMethod": "喉（喉袋共鳴）",
        "conservation": "CR",
        "scientificName": "Pongo pygmaeus", "nameEN": "Bornean orangutan",
        "onomatopoeia": [("ja", "日本語", "ウォォォーン", "ロングコール"), ("en", "英語", "Long call", "territorial long call")],
        "regions": ["REG06"],
    },

    # ── 昆虫 (+13) ──
    {
        "id": "I033", "nameJA": "ツクツクボウシ", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "カメムシ目", "family": "セミ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ツクツクオーシ", "voiceMethod": "発音膜振動",
        "conservation": "LC",
        "scientificName": "Meimuna opalifera", "nameEN": "Elongate cicada",
        "onomatopoeia": [("ja", "日本語", "ツクツクオーシ", "鳴き声"), ("en", "英語", "Tsuku-tsuku-oshi", "call")],
        "regions": ["REG01", "REG03"],
    },
    {
        "id": "I034", "nameJA": "ニイニイゼミ", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "カメムシ目", "family": "セミ科", "hasVoice": "あり",
        "onomatopoeiaJA": "チーーー", "voiceMethod": "発音膜振動",
        "conservation": "LC",
        "scientificName": "Platypleura kaempferi", "nameEN": "Kaempfer's cicada",
        "onomatopoeia": [("ja", "日本語", "チーーー", "鳴き声"), ("en", "英語", "Cheee", "call")],
        "regions": ["REG01", "REG03"],
    },
    {
        "id": "I035", "nameJA": "ハルゼミ", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "カメムシ目", "family": "セミ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ゲーキョ ゲーキョ", "voiceMethod": "発音膜振動",
        "conservation": "LC",
        "scientificName": "Terpnosia vacua", "nameEN": "Spring cicada",
        "onomatopoeia": [("ja", "日本語", "ゲーキョ ゲーキョ", "鳴き声"), ("en", "英語", "Ge-kyo ge-kyo", "call")],
        "regions": ["REG01"],
    },
    {
        "id": "I036", "nameJA": "クマゼミ", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "カメムシ目", "family": "セミ科", "hasVoice": "あり",
        "onomatopoeiaJA": "シャーシャーシャー", "voiceMethod": "発音膜振動",
        "conservation": "LC",
        "scientificName": "Cryptotympana facialis", "nameEN": "Black giant cicada",
        "onomatopoeia": [("ja", "日本語", "シャーシャーシャー", "鳴き声"), ("en", "英語", "Sha-sha-sha", "call")],
        "regions": ["REG01"],
    },
    {
        "id": "I037", "nameJA": "スズムシ", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "バッタ目", "family": "コオロギ科", "hasVoice": "あり",
        "onomatopoeiaJA": "リーンリーン", "voiceMethod": "翅摩擦",
        "conservation": "LC",
        "scientificName": "Meloimorpha japonica", "nameEN": "Asian bell cricket",
        "onomatopoeia": [("ja", "日本語", "リーンリーン", "鳴き声"), ("en", "英語", "Ring-ring", "stridulation")],
        "regions": ["REG01"],
    },
    {
        "id": "I038", "nameJA": "カンタン", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "バッタ目", "family": "コオロギ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ルルルルル", "voiceMethod": "翅摩擦",
        "conservation": "LC",
        "scientificName": "Oecanthus longicauda", "nameEN": "Long-tailed tree cricket",
        "onomatopoeia": [("ja", "日本語", "ルルルルル", "鳴き声"), ("en", "英語", "Ru-ru-ru-ru", "stridulation")],
        "regions": ["REG01"],
    },
    {
        "id": "I039", "nameJA": "クツワムシ", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "バッタ目", "family": "クツワムシ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ガチャガチャ", "voiceMethod": "翅摩擦",
        "conservation": "LC",
        "scientificName": "Mecopoda nipponensis", "nameEN": "Japanese katydid",
        "onomatopoeia": [("ja", "日本語", "ガチャガチャ", "鳴き声"), ("en", "英語", "Gacha-gacha", "stridulation")],
        "regions": ["REG01"],
    },
    {
        "id": "I040", "nameJA": "マツムシ", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "バッタ目", "family": "コオロギ科", "hasVoice": "あり",
        "onomatopoeiaJA": "チンチロリン", "voiceMethod": "翅摩擦",
        "conservation": "LC",
        "scientificName": "Xenogryllus marmoratus", "nameEN": "Japanese pine cricket",
        "onomatopoeia": [("ja", "日本語", "チンチロリン", "鳴き声"), ("en", "英語", "Chin-chiro-rin", "stridulation")],
        "regions": ["REG01"],
    },
    {
        "id": "I041", "nameJA": "ウマオイ", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "バッタ目", "family": "キリギリス科", "hasVoice": "あり",
        "onomatopoeiaJA": "スイッチョン", "voiceMethod": "翅摩擦",
        "conservation": "LC",
        "scientificName": "Hexacentrus japonicus", "nameEN": "Japanese horse-chaser",
        "onomatopoeia": [("ja", "日本語", "スイッチョン", "鳴き声"), ("en", "英語", "Sui-tchon", "stridulation")],
        "regions": ["REG01"],
    },
    {
        "id": "I042", "nameJA": "カネタタキ", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "バッタ目", "family": "カネタタキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "チッチッチッ", "voiceMethod": "翅摩擦",
        "conservation": "LC",
        "scientificName": "Ornebius kanetataki", "nameEN": "Ornebius kanetataki",
        "onomatopoeia": [("ja", "日本語", "チッチッチッ", "鳴き声"), ("en", "英語", "Chit-chit-chit", "stridulation")],
        "regions": ["REG01"],
    },
    {
        "id": "I043", "nameJA": "カマキリ（オオカマキリ）", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "カマキリ目", "family": "カマキリ科", "hasVoice": "あり",
        "onomatopoeiaJA": "シュー", "voiceMethod": "翅摩擦",
        "conservation": "LC",
        "scientificName": "Tenodera sinensis", "nameEN": "Chinese mantis",
        "altJA": "オオカマキリ",
        "onomatopoeia": [("ja", "日本語", "シュー", "威嚇音"), ("en", "英語", "Hiss", "threat display")],
        "regions": ["REG01", "REG03", "REG12"],
    },
    {
        "id": "I044", "nameJA": "ケラ（オケラ）", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "バッタ目", "family": "ケラ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ジーーー", "voiceMethod": "翅摩擦",
        "conservation": "LC",
        "scientificName": "Gryllotalpa orientalis", "nameEN": "Oriental mole cricket",
        "altJA": "オケラ",
        "onomatopoeia": [("ja", "日本語", "ジーーー", "鳴き声"), ("en", "英語", "Jeeee", "call")],
        "regions": ["REG01", "REG03"],
    },
    {
        "id": "I045", "nameJA": "ミンミンゼミ", "phylum": "節足動物門", "class": "昆虫綱",
        "order": "カメムシ目", "family": "セミ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ミーンミンミンミン", "voiceMethod": "発音膜振動",
        "conservation": "LC",
        "scientificName": "Hyalessa maculaticollis", "nameEN": "Robust cicada",
        "onomatopoeia": [("ja", "日本語", "ミーンミンミンミン", "鳴き声"), ("en", "英語", "Meen-min-min-min", "call")],
        "regions": ["REG01"],
    },

    # ── 両生類 (+6) ──
    {
        "id": "F030", "nameJA": "アフリカウシガエル", "phylum": "脊索動物門", "class": "両生綱",
        "order": "カエル目", "family": "アカガエル科", "hasVoice": "あり",
        "onomatopoeiaJA": "ウォーウォー", "voiceMethod": "鳴嚢共鳴",
        "conservation": "LC",
        "scientificName": "Pyxicephalus adspersus", "nameEN": "African bullfrog",
        "onomatopoeia": [("ja", "日本語", "ウォーウォー", "繁殖期"), ("en", "英語", "Whoop-whoop", "breeding call")],
        "regions": ["REG10"],
    },
    {
        "id": "F031", "nameJA": "ヤドクガエル（アイゾメヤドクガエル）", "phylum": "脊索動物門", "class": "両生綱",
        "order": "カエル目", "family": "ヤドクガエル科", "hasVoice": "あり",
        "onomatopoeiaJA": "ピッピッピッ", "voiceMethod": "鳴嚢共鳴",
        "conservation": "LC",
        "scientificName": "Dendrobates tinctorius", "nameEN": "Dyeing poison dart frog",
        "altJA": "アイゾメヤドクガエル",
        "onomatopoeia": [("ja", "日本語", "ピッピッピッ", "縄張り"), ("en", "英語", "Pip-pip-pip", "territorial call")],
        "regions": ["REG14"],
    },
    {
        "id": "F032", "nameJA": "モリアオガエル", "phylum": "脊索動物門", "class": "両生綱",
        "order": "カエル目", "family": "アオガエル科", "hasVoice": "あり",
        "onomatopoeiaJA": "カラララ", "voiceMethod": "鳴嚢共鳴",
        "conservation": "LC",
        "scientificName": "Zhangixalus arboreus", "nameEN": "Forest green tree frog",
        "onomatopoeia": [("ja", "日本語", "カラララ", "繁殖期"), ("en", "英語", "Kararara", "breeding call")],
        "regions": ["REG01"],
    },
    {
        "id": "F033", "nameJA": "ナガレタゴガエル", "phylum": "脊索動物門", "class": "両生綱",
        "order": "カエル目", "family": "アカガエル科", "hasVoice": "あり",
        "onomatopoeiaJA": "グッグッグッ", "voiceMethod": "鳴嚢共鳴",
        "conservation": "LC",
        "scientificName": "Rana sakuraii", "nameEN": "Sakurai's brown frog",
        "onomatopoeia": [("ja", "日本語", "グッグッグッ", "繁殖期"), ("en", "英語", "Guk-guk-guk", "breeding call")],
        "regions": ["REG01"],
    },
    {
        "id": "F034", "nameJA": "ウシガエル", "phylum": "脊索動物門", "class": "両生綱",
        "order": "カエル目", "family": "アカガエル科", "hasVoice": "あり",
        "onomatopoeiaJA": "ウォーウォー", "voiceMethod": "鳴嚢共鳴",
        "conservation": "LC",
        "scientificName": "Lithobates catesbeianus", "nameEN": "American bullfrog",
        "onomatopoeia": [("ja", "日本語", "ウォーウォー", "繁殖期"), ("en", "英語", "Jug-o-rum", "breeding call")],
        "regions": ["REG01", "REG12"],
    },
    {
        "id": "F035", "nameJA": "アカハライモリ", "phylum": "脊索動物門", "class": "両生綱",
        "order": "サンショウウオ目", "family": "イモリ科", "hasVoice": "あり",
        "onomatopoeiaJA": "キュッ", "voiceMethod": "喉",
        "conservation": "NT",
        "scientificName": "Cynops pyrrhogaster", "nameEN": "Japanese fire-bellied newt",
        "onomatopoeia": [("ja", "日本語", "キュッ", "鳴き声"), ("en", "英語", "Squeak", "call")],
        "regions": ["REG01"],
    },

    # ── 爬虫類 (+6) ──
    {
        "id": "R015", "nameJA": "グリーンイグアナ", "phylum": "脊索動物門", "class": "爬虫綱",
        "order": "有鱗目", "family": "イグアナ科", "hasVoice": "あり",
        "onomatopoeiaJA": "シュー フッ", "voiceMethod": "喉・鼻",
        "conservation": "LC",
        "scientificName": "Iguana iguana", "nameEN": "Green iguana",
        "onomatopoeia": [("ja", "日本語", "シュー フッ", "威嚇"), ("en", "英語", "Hiss-huff", "threat display")],
        "regions": ["REG13", "REG14"],
    },
    {
        "id": "R016", "nameJA": "ガラガラヘビ（ヒガシダイヤガラガラヘビ）", "phylum": "脊索動物門", "class": "爬虫綱",
        "order": "有鱗目", "family": "クサリヘビ科", "hasVoice": "あり",
        "onomatopoeiaJA": "シャカシャカ", "voiceMethod": "尾の発音器",
        "conservation": "LC",
        "scientificName": "Crotalus adamanteus", "nameEN": "Eastern diamondback rattlesnake",
        "altJA": "ヒガシダイヤガラガラヘビ",
        "onomatopoeia": [("ja", "日本語", "シャカシャカ", "威嚇"), ("en", "英語", "Rattle-rattle", "warning rattle")],
        "regions": ["REG12"],
    },
    {
        "id": "R017", "nameJA": "ミシシッピアカミミガメ", "phylum": "脊索動物門", "class": "爬虫綱",
        "order": "カメ目", "family": "ヌマガメ科", "hasVoice": "あり",
        "onomatopoeiaJA": "シュー", "voiceMethod": "喉・鼻",
        "conservation": "LC",
        "scientificName": "Trachemys scripta elegans", "nameEN": "Red-eared slider",
        "altJA": "ミドリガメ",
        "onomatopoeia": [("ja", "日本語", "シュー", "威嚇"), ("en", "英語", "Hiss", "threat display")],
        "regions": ["REG12", "REG01"],
    },
    {
        "id": "R018", "nameJA": "ヒョウモントカゲモドキ", "phylum": "脊索動物門", "class": "爬虫綱",
        "order": "有鱗目", "family": "トカゲモドキ科", "hasVoice": "あり",
        "onomatopoeiaJA": "キュッ", "voiceMethod": "喉",
        "conservation": "LC",
        "scientificName": "Eublepharis macularius", "nameEN": "Leopard gecko",
        "altJA": "レオパ",
        "onomatopoeia": [("ja", "日本語", "キュッ", "鳴き声"), ("en", "英語", "Chirp", "vocalization")],
        "regions": ["REG04", "REG05"],
    },
    {
        "id": "R019", "nameJA": "ガビアル（インドガビアル）", "phylum": "脊索動物門", "class": "爬虫綱",
        "order": "ワニ目", "family": "ガビアル科", "hasVoice": "あり",
        "onomatopoeiaJA": "ブーーン", "voiceMethod": "喉",
        "conservation": "CR",
        "scientificName": "Gavialis gangeticus", "nameEN": "Gharial",
        "altJA": "インドガビアル",
        "onomatopoeia": [("ja", "日本語", "ブーーン", "繁殖期"), ("en", "英語", "Buzz-hiss", "breeding call")],
        "regions": ["REG22"],
    },
    {
        "id": "R020", "nameJA": "エリマキトカゲ", "phylum": "脊索動物門", "class": "爬虫綱",
        "order": "有鱗目", "family": "アガマ科", "hasVoice": "あり",
        "onomatopoeiaJA": "シャーッ", "voiceMethod": "喉・鼻",
        "conservation": "LC",
        "scientificName": "Chlamydosaurus kingii", "nameEN": "Frilled-neck lizard",
        "onomatopoeia": [("ja", "日本語", "シャーッ", "威嚇"), ("en", "英語", "Hiss", "threat display")],
        "regions": ["REG15", "REG16"],
    },

    # ── 魚類 (+6) ──
    {
        "id": "S013", "nameJA": "ナマズ（マナマズ）", "phylum": "脊索動物門", "class": "条鰭綱",
        "order": "ナマズ目", "family": "ナマズ科", "hasVoice": "あり",
        "onomatopoeiaJA": "グーグー", "voiceMethod": "浮袋振動",
        "conservation": "LC",
        "scientificName": "Silurus asotus", "nameEN": "Amur catfish",
        "altJA": "マナマズ",
        "onomatopoeia": [("ja", "日本語", "グーグー", "鳴き声"), ("en", "英語", "Grunt-grunt", "drumming")],
        "regions": ["REG01", "REG03"],
    },
    {
        "id": "S014", "nameJA": "シログチ", "phylum": "脊索動物門", "class": "条鰭綱",
        "order": "スズキ目", "family": "ニベ科", "hasVoice": "あり",
        "onomatopoeiaJA": "グーグー", "voiceMethod": "浮袋振動",
        "conservation": "LC",
        "scientificName": "Pennahia argentata", "nameEN": "Silver croaker",
        "altJA": "イシモチ",
        "onomatopoeia": [("ja", "日本語", "グーグー", "鳴き声"), ("en", "英語", "Croak-croak", "drumming")],
        "regions": ["REG01", "REG03"],
    },
    {
        "id": "S015", "nameJA": "カサゴ", "phylum": "脊索動物門", "class": "条鰭綱",
        "order": "スズキ目", "family": "メバル科", "hasVoice": "あり",
        "onomatopoeiaJA": "ブーブー", "voiceMethod": "浮袋振動",
        "conservation": "LC",
        "scientificName": "Sebastiscus marmoratus", "nameEN": "False kelpfish",
        "onomatopoeia": [("ja", "日本語", "ブーブー", "鳴き声"), ("en", "英語", "Boo-boo", "drumming")],
        "regions": ["REG01", "REG03"],
    },
    {
        "id": "S016", "nameJA": "コイ", "phylum": "脊索動物門", "class": "条鰭綱",
        "order": "コイ目", "family": "コイ科", "hasVoice": "あり",
        "onomatopoeiaJA": "パクパク", "voiceMethod": "咽頭歯",
        "conservation": "VU",
        "scientificName": "Cyprinus carpio", "nameEN": "Common carp",
        "onomatopoeia": [("ja", "日本語", "パクパク", "摂餌音"), ("en", "英語", "Gulp-gulp", "feeding sound")],
        "regions": ["REG01", "REG08", "REG12"],
    },
    {
        "id": "S017", "nameJA": "ハコフグ", "phylum": "脊索動物門", "class": "条鰭綱",
        "order": "フグ目", "family": "ハコフグ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ブッブッ", "voiceMethod": "浮袋振動",
        "conservation": "LC",
        "scientificName": "Ostracion cubicus", "nameEN": "Yellow boxfish",
        "onomatopoeia": [("ja", "日本語", "ブッブッ", "鳴き声"), ("en", "英語", "Bub-bub", "drumming")],
        "regions": ["REG22", "REG23"],
    },
    {
        "id": "S018", "nameJA": "タチウオ", "phylum": "脊索動物門", "class": "条鰭綱",
        "order": "スズキ目", "family": "タチウオ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ギリギリ", "voiceMethod": "歯ぎしり",
        "conservation": "LC",
        "scientificName": "Trichiurus lepturus", "nameEN": "Largehead hairtail",
        "onomatopoeia": [("ja", "日本語", "ギリギリ", "摂餌音"), ("en", "英語", "Grinding", "feeding sound")],
        "regions": ["REG01", "REG23"],
    },

    # ── 無脊椎動物 (+6) ──
    {
        "id": "V007", "nameJA": "テッポウエビ", "phylum": "節足動物門", "class": "軟甲綱",
        "order": "エビ目", "family": "テッポウエビ科", "hasVoice": "あり",
        "onomatopoeiaJA": "パチン", "voiceMethod": "鋏脚キャビテーション",
        "conservation": "LC",
        "scientificName": "Alpheus bellulus", "nameEN": "Tiger snapping shrimp",
        "onomatopoeia": [("ja", "日本語", "パチン", "鳴き声"), ("en", "英語", "Snap", "claw snap")],
        "regions": ["REG22", "REG23"],
    },
    {
        "id": "V008", "nameJA": "ヤドカリ（オカヤドカリ）", "phylum": "節足動物門", "class": "軟甲綱",
        "order": "エビ目", "family": "オカヤドカリ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ギチギチ", "voiceMethod": "殻摩擦",
        "conservation": "LC",
        "scientificName": "Coenobita rugosus", "nameEN": "Rugose land hermit crab",
        "altJA": "オカヤドカリ",
        "onomatopoeia": [("ja", "日本語", "ギチギチ", "威嚇"), ("en", "英語", "Chirp-chirp", "stridulation")],
        "regions": ["REG22", "REG23"],
    },
    {
        "id": "V009", "nameJA": "カタツムリ（ミスジマイマイ）", "phylum": "軟体動物門", "class": "腹足綱",
        "order": "柄眼目", "family": "オナジマイマイ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ネチネチ", "voiceMethod": "摂食音",
        "conservation": "LC",
        "scientificName": "Euhadra peliomphala", "nameEN": "Misuji-maimai snail",
        "altJA": "ミスジマイマイ",
        "onomatopoeia": [("ja", "日本語", "ネチネチ", "摂食音"), ("en", "英語", "Munch-munch", "feeding sound")],
        "regions": ["REG01"],
    },
    {
        "id": "V010", "nameJA": "ザリガニ（アメリカザリガニ）", "phylum": "節足動物門", "class": "軟甲綱",
        "order": "エビ目", "family": "アメリカザリガニ科", "hasVoice": "あり",
        "onomatopoeiaJA": "キチキチ", "voiceMethod": "鋏摩擦",
        "conservation": "LC",
        "scientificName": "Procambarus clarkii", "nameEN": "Red swamp crayfish",
        "altJA": "アメリカザリガニ",
        "onomatopoeia": [("ja", "日本語", "キチキチ", "威嚇"), ("en", "英語", "Click-click", "claw snap")],
        "regions": ["REG01", "REG12"],
    },
    {
        "id": "V011", "nameJA": "ダンゴムシ", "phylum": "節足動物門", "class": "軟甲綱",
        "order": "ワラジムシ目", "family": "オカダンゴムシ科", "hasVoice": "なし",
        "onomatopoeiaJA": "", "voiceMethod": "",
        "conservation": "LC",
        "scientificName": "Armadillidium vulgare", "nameEN": "Common pill-bug",
        "onomatopoeia": [],
        "regions": ["REG01", "REG08", "REG12"],
    },
    {
        "id": "V012", "nameJA": "セミクジラ（イワシクジラ）", "phylum": "脊索動物門", "class": "哺乳綱",
        "order": "鯨偶蹄目", "family": "ナガスクジラ科", "hasVoice": "あり",
        "onomatopoeiaJA": "ウォーーン", "voiceMethod": "喉",
        "conservation": "EN",
        "scientificName": "Balaenoptera borealis", "nameEN": "Sei whale",
        "altJA": "イワシクジラ",
        "onomatopoeia": [("ja", "日本語", "ウォーーン", "コミュニケーション"), ("en", "英語", "Low moan", "contact call")],
        "regions": ["REG23"],
    },
]


def main():
    dry_run = "--dry-run" in sys.argv

    wb = openpyxl.load_workbook(DATA_FILE)
    ws_main = wb["メインデータ"]
    ws_name = wb["名称マッピング"]
    ws_ono = wb["オノマトペマッピング"]
    ws_reg = wb["地域マッピング"]

    # Collect existing IDs and scientific names
    existing_ids = set()
    existing_sci = set()
    for row in ws_name.iter_rows(min_row=2, values_only=True):
        if row[0]:
            existing_ids.add(str(row[0]))
            if row[2]:
                existing_sci.add(str(row[2]).strip().lower())

    added = 0
    skipped = 0

    for sp in SPECIES_DATA:
        aid = sp["id"]
        sci = sp["scientificName"]

        if aid in existing_ids:
            print(f"  SKIP {aid} {sp['nameJA']} (ID exists)")
            skipped += 1
            continue
        if sci.lower() in existing_sci:
            print(f"  SKIP {aid} {sp['nameJA']} (scientific name exists: {sci})")
            skipped += 1
            continue

        print(f"  ADD  {aid} {sp['nameJA']} ({sci})")

        if not dry_run:
            # メインデータ
            ws_main.append([
                aid, sp["nameJA"], sp["phylum"], sp["class"],
                sp["order"], sp["family"], sp["hasVoice"],
                sp.get("onomatopoeiaJA", ""), sp.get("voiceMethod", ""),
                "", sp.get("conservation", ""),
                f"https://commons.wikimedia.org/wiki/Category:{sci.replace(' ', '_')}",
                None, None, None,  # note, old audioRef, taxonCode (filled by fetch_taxon_codes.py)
            ])

            # 名称マッピング
            ws_name.append([
                aid, sp["nameJA"], sci, sp["nameEN"],
                sp.get("altJA"), sp.get("altEN"),
            ])

            # オノマトペマッピング
            for ono in sp.get("onomatopoeia", []):
                ws_ono.append([
                    aid, sp["nameJA"], ono[0], ono[1], ono[2], ono[3], None,
                ])

            # 地域マッピング
            for rid in sp.get("regions", []):
                ws_reg.append([aid, sp["nameJA"], rid])

        added += 1

    print(f"\nAdded: {added}, Skipped: {skipped}")

    if not dry_run and added > 0:
        wb.save(DATA_FILE)
        print(f"Saved to {DATA_FILE}")
    elif dry_run:
        print("(dry-run, no changes saved)")


if __name__ == "__main__":
    main()
