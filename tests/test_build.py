"""
tests/test_build.py — build.py unit tests

Usage:
    python -m pytest tests/ -v
"""

import html as html_mod
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

import pytest

# Ensure scripts/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import build


# ── _build_audio_ref ────────────────────────────────────

class TestBuildAudioRef:
    """Audio reference URL generation."""

    def test_bird_xeno_canto(self):
        url = build._build_audio_ref("B001", "Passer montanus", "pasmon1")
        assert url == "https://xeno-canto.org/species/Passer-montanus"

    def test_bird_no_scientific_name(self):
        assert build._build_audio_ref("B001", "", "pasmon1") == ""

    def test_bird_single_word_scientific_name(self):
        assert build._build_audio_ref("B001", "Passer", "pasmon1") == ""

    def test_mammal_macaulay(self):
        url = build._build_audio_ref("M001", "Canis lupus", "canlup1")
        assert "macaulaylibrary.org" in url
        assert "taxonCode=canlup1" in url

    def test_mammal_no_audio(self):
        """taxonCode in _NO_AUDIO list should return empty."""
        with patch.object(build, "_NO_AUDIO", {"canlup1"}):
            assert build._build_audio_ref("M001", "Canis lupus", "canlup1") == ""

    def test_mammal_empty_taxon_code(self):
        assert build._build_audio_ref("M001", "Canis lupus", "") == ""

    def test_mammal_none_taxon_code(self):
        """V004 fix: None taxon_code should not generate URL."""
        assert build._build_audio_ref("M001", "Canis lupus", None) == ""

    def test_insect_id_prefix(self):
        url = build._build_audio_ref("I001", "Gryllus bimaculatus", "grybim1")
        assert "macaulaylibrary.org" in url

    def test_amphibian_id_prefix(self):
        url = build._build_audio_ref("F001", "Rana japonica", "ranjap1")
        assert "macaulaylibrary.org" in url

    def test_initial_sample_prefix(self):
        """A-prefix uses Macaulay Library (only B-prefix uses xeno-canto)."""
        url = build._build_audio_ref("A001", "Felis catus", "felcat1")
        assert "macaulaylibrary.org" in url


# ── build_stats ─────────────────────────────────────────

class TestBuildStats:
    def _make_animals(self, ono_langs):
        return [{
            "onomatopoeia": [{"lang": l} for l in ono_langs],
        }]

    def test_basic_stats(self):
        animals = self._make_animals(["ja", "en", "ko"])
        stats = build.build_stats(animals)
        assert stats["total_species"] == 1
        assert stats["total_onomatopoeia"] == 3
        assert stats["language_count"] == 3
        assert sorted(stats["languages"]) == ["en", "ja", "ko"]

    def test_empty_animals(self):
        stats = build.build_stats([])
        assert stats["total_species"] == 0
        assert stats["total_onomatopoeia"] == 0
        assert stats["language_count"] == 0

    def test_duplicate_languages(self):
        animals = self._make_animals(["ja", "ja", "en"])
        stats = build.build_stats(animals)
        assert stats["language_count"] == 2

    def test_empty_lang_ignored(self):
        animals = self._make_animals(["ja", "", "en"])
        stats = build.build_stats(animals)
        assert stats["language_count"] == 2
        assert "" not in stats["languages"]


# ── generate_html (template placeholder replacement) ────

class TestGenerateHtml:
    def test_placeholder_replacement(self, tmp_path):
        template = tmp_path / "template.html"
        template.write_text(
            "<p>{{SITE_URL}}</p>"
            "<p>{{SPECIES_COUNT}} species</p>"
            "<p>{{LANGUAGE_COUNT}} langs</p>"
            "<p>{{ONOMATOPOEIA_COUNT}} onomatopoeia</p>",
            encoding="utf-8",
        )
        output = tmp_path / "index.html"
        animals = [
            {"onomatopoeia": [{"lang": "ja"}, {"lang": "en"}]},
            {"onomatopoeia": [{"lang": "ja"}]},
        ]
        build.generate_html(animals, template, output)
        html = output.read_text(encoding="utf-8")
        assert build.SITE_URL in html
        assert "2 species" in html
        assert "2 langs" in html
        assert "3 onomatopoeia" in html

    def test_missing_template_no_fallback(self, tmp_path):
        """No template and no fallback should print warning, not crash."""
        output = tmp_path / "index.html"
        build.generate_html([], tmp_path / "nonexistent.html", output)
        assert not output.exists()


# ── generate_sitemap ────────────────────────────────────

class TestGenerateSitemap:
    def test_sitemap_structure(self, tmp_path):
        animals = [{"id": "B001"}, {"id": "M001"}]
        out = tmp_path / "sitemap.xml"
        build.generate_sitemap(animals, out)
        xml = out.read_text(encoding="utf-8")
        assert '<?xml version="1.0"' in xml
        assert f"{build.SITE_URL}/" in xml
        assert f"{build.SITE_URL}/species/B001/" in xml
        assert f"{build.SITE_URL}/species/M001/" in xml

    def test_sitemap_url_count(self, tmp_path):
        animals = [{"id": f"X{i:03d}"} for i in range(5)]
        out = tmp_path / "sitemap.xml"
        build.generate_sitemap(animals, out)
        xml = out.read_text(encoding="utf-8")
        assert xml.count("<url>") == 6  # top page + 5 species

    def test_sitemap_empty(self, tmp_path):
        out = tmp_path / "sitemap.xml"
        build.generate_sitemap([], out)
        xml = out.read_text(encoding="utf-8")
        assert xml.count("<url>") == 1  # top page only


# ── generate_manifest ──────────────────────────────────

class TestGenerateManifest:
    def test_manifest_valid_json(self, tmp_path):
        out = tmp_path / "manifest.json"
        build.generate_manifest(out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["name"] == "動物の鳴き声図鑑"
        assert data["display"] == "standalone"
        assert data["theme_color"] == "#059669"
        assert any(icon["src"] == "/favicon.svg" for icon in data["icons"])


# ── generate_sw ─────────────────────────────────────────

class TestGenerateServiceWorker:
    def test_sw_contains_cache_name(self, tmp_path):
        out = tmp_path / "sw.js"
        build.generate_sw([{"id": "B001"}], out)
        js = out.read_text(encoding="utf-8")
        assert "CACHE_NAME" in js
        assert "koe-zukan-v" in js

    def test_sw_contains_required_urls(self, tmp_path):
        out = tmp_path / "sw.js"
        build.generate_sw([], out)
        js = out.read_text(encoding="utf-8")
        for url in ["/", "/animals.json", "/regions.json", "/favicon.svg", "/manifest.json"]:
            assert url in js

    def test_sw_event_handlers(self, tmp_path):
        out = tmp_path / "sw.js"
        build.generate_sw([], out)
        js = out.read_text(encoding="utf-8")
        assert '"install"' in js
        assert '"activate"' in js
        assert '"fetch"' in js


# ── generate_species_pages ──────────────────────────────

class TestGenerateSpeciesPages:
    def _make_animal(self, aid="B001"):
        return {
            "id": aid,
            "nameJA": "スズメ",
            "nameEN": "Eurasian Tree Sparrow",
            "scientificName": "Passer montanus",
            "altJA": "すずめ",
            "altEN": "",
            "class": "鳥綱",
            "order": "スズメ目",
            "family": "スズメ科",
            "voiceMethod": "鳴管",
            "conservation": "LC",
            "habitat": "ユーラシア",
            "note": "",
            "imageRef": "https://commons.wikimedia.org/wiki/Category:Passer_montanus",
            "audioRef": "https://xeno-canto.org/species/Passer-montanus",
            "onomatopoeiaJA": "チュンチュン",
            "onomatopoeia": [
                {"lang": "ja", "onomatopoeia": "チュンチュン", "scene": "さえずり", "note": ""},
                {"lang": "en", "onomatopoeia": "Chirp chirp", "scene": "", "note": ""},
            ],
            "regions": [{"id": "R01", "nameJA": "日本", "nameEN": "Japan"}],
        }

    def test_species_page_generated(self, tmp_path):
        animal = self._make_animal()
        count = build.generate_species_pages([animal], tmp_path)
        assert count == 1
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert "スズメ" in page
        assert "Eurasian Tree Sparrow" in page
        assert "Passer montanus" in page

    def test_species_page_ogp_meta(self, tmp_path):
        animal = self._make_animal()
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert f'{build.SITE_URL}/species/B001/ogp.png' in page
        assert f'{build.SITE_URL}/species/B001/' in page

    def test_species_page_canonical_url(self, tmp_path):
        animal = self._make_animal()
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert f'rel="canonical" href="{build.SITE_URL}/species/B001/"' in page

    def test_species_page_json_ld(self, tmp_path):
        animal = self._make_animal()
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert '"@type": "Article"' in page
        assert '"@context": "https://schema.org"' in page

    def test_species_page_onomatopoeia_section(self, tmp_path):
        animal = self._make_animal()
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert "チュンチュン" in page
        assert "Chirp chirp" in page

    def test_species_page_share_buttons(self, tmp_path):
        animal = self._make_animal()
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert "twitter.com/intent/tweet" in page
        assert "facebook.com/sharer" in page
        assert "line.me/lineit/share" in page
        assert "copyShareUrl" in page

    def test_species_page_conservation_label(self, tmp_path):
        animal = self._make_animal()
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert "LC (低懸念)" in page

    def test_species_page_external_links(self, tmp_path):
        animal = self._make_animal()
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert "Wikimedia Commons" in page
        assert "xeno-canto" in page
        assert "Wikipedia (JA)" in page
        assert "Wikipedia (EN)" in page

    def test_species_page_html_escaping(self, tmp_path):
        """V001: Special chars in data fields must be HTML-escaped."""
        animal = self._make_animal()
        animal["note"] = 'Test <b>"note"</b> & more'
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert "Test &lt;b&gt;&quot;note&quot;&lt;/b&gt; &amp; more" in page
        assert '<b>"note"</b>' not in page

    def test_species_page_no_note(self, tmp_path):
        animal = self._make_animal()
        animal["note"] = ""
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert "備考" not in page

    def test_species_page_with_note(self, tmp_path):
        animal = self._make_animal()
        animal["note"] = "テスト備考"
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert "備考" in page
        assert "テスト備考" in page

    def test_species_page_no_voice_method(self, tmp_path):
        animal = self._make_animal()
        animal["voiceMethod"] = ""
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert "—" in page

    def test_species_page_back_link(self, tmp_path):
        animal = self._make_animal()
        build.generate_species_pages([animal], tmp_path)
        page = (tmp_path / "species" / "B001" / "index.html").read_text(encoding="utf-8")
        assert '/?id=B001' in page


# ── _parse_svg_points ───────────────────────────────────

class TestParseSvgPoints:
    def test_basic_path(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text('<svg><path d="M 10 20 L 30 40 50 60"/></svg>')
        points = build._parse_svg_points(svg)
        assert (10.0, 20.0) in points
        assert (30.0, 40.0) in points
        assert (50.0, 60.0) in points

    def test_no_path(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text('<svg><circle cx="10" cy="10" r="5"/></svg>')
        points = build._parse_svg_points(svg)
        assert points == []


# ── _find_cjk_fonts ─────────────────────────────────────

class TestFindCjkFonts:
    def test_returns_all_keys(self):
        fonts = build._find_cjk_fonts()
        assert "ja" in fonts
        assert "ko" in fonts
        assert "zh" in fonts

    def test_ko_zh_fallback_to_ja(self):
        """If ko/zh font not found, should fall back to ja font."""
        fonts = build._find_cjk_fonts()
        # On any platform, ko and zh should never be None if ja is found
        if fonts["ja"]:
            assert fonts["ko"] is not None
            assert fonts["zh"] is not None


# ── CNAME generation ────────────────────────────────────

class TestCnameGeneration:
    def test_cname_from_site_url(self):
        domain = urlparse(build.SITE_URL).netloc
        assert domain == "koe-zukan.semnil.com"


# ── CONSERVATION_JA ─────────────────────────────────────

class TestConservationLabels:
    def test_all_iucn_categories_present(self):
        expected = {"LC", "NT", "VU", "EN", "CR", "DD", "NE", "EW", "EX"}
        assert set(build.CONSERVATION_JA.keys()) == expected

    def test_labels_are_non_empty(self):
        for key, val in build.CONSERVATION_JA.items():
            assert val, f"Empty label for {key}"


# ── LANG_LABELS ─────────────────────────────────────────

class TestLangLabels:
    def test_four_languages(self):
        assert set(build.LANG_LABELS.keys()) == {"ja", "en", "ko", "zh"}

    def test_labels_non_empty(self):
        for key, val in build.LANG_LABELS.items():
            assert val, f"Empty label for {key}"
