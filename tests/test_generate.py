"""Verify portable assets, safe animation, and the removed-content boundary."""

import importlib.util
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generate", ROOT / "scripts/generate.py")
generate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate)
NS = {"svg": "http://www.w3.org/2000/svg"}


class AssetTests(unittest.TestCase):
    def test_every_hero_has_script_free_motion_and_reduced_motion_fallback(self):
        for theme in generate.THEMES:
            for mobile in (False, True):
                source = generate.hero(theme, mobile)
                root = ET.fromstring(source)
                self.assertEqual(len(root.findall(".//svg:animateMotion", NS)), 3)
                self.assertIn("prefers-reduced-motion:reduce", source)
                self.assertFalse(root.findall(".//svg:script", NS))
                self.assertNotIn("href=", source)
                fade = root.find("svg:rect[@id='background-fade']/svg:animate", NS)
                self.assertIsNotNone(fade)
                self.assertEqual(fade.get("attributeName"), "fill")
                self.assertEqual(fade.get("dur"), "16s")
                colors = fade.get("values").split(";")
                self.assertEqual(colors[0], colors[-1])
                self.assertEqual(len(set(colors)), 4)
                still = ET.fromstring(generate.hero(theme, mobile, animated=False))
                self.assertFalse(still.findall(".//svg:animateMotion", NS))
                self.assertFalse(still.findall(".//svg:animate", NS))

    def test_svg_text_escapes_external_content(self):
        text = generate.text(0, 10, 'A&B <example> "quoted"')
        svg = generate.svg(150, 46, "A&B", "<example>", text, "dark")
        ET.fromstring(svg)
        self.assertNotIn("<example>", svg)
        self.assertIn("A&amp;B", svg)

    def test_expected_assets_are_small_and_well_formed(self):
        assets = generate.outputs()
        self.assertEqual(len(assets), 16)
        for path, source in assets.items():
            self.assertTrue(path.is_relative_to(ROOT / "assets"))
            self.assertLess(len(source.encode("utf-8")), 10_000)
            root = ET.fromstring(source)
            self.assertIsNotNone(root.find("svg:title", NS))
            self.assertNotIn("{accent}", source)

    def test_removed_sections_and_slogans_do_not_return(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        hero_text = "".join(generate.hero(t, m) for t in generate.THEMES for m in (False, True)).lower()
        for phrase in ("selected work", "public repository activity", "public work",
                       "source code. human patterns.", "studying authorship."):
            self.assertNotIn(phrase, readme + hero_text)


if __name__ == "__main__":
    unittest.main()
