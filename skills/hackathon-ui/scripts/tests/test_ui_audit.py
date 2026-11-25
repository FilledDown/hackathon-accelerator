#!/usr/bin/env python3
"""Tests for ui_audit.py. Run: python -m unittest discover -s <this dir>"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent / "ui_audit.py"
FIX = HERE / "fixtures"
SHOWCASE = HERE.parents[1] / "assets" / "showcase"


def run(*args):
    p = subprocess.run([sys.executable, "-I", str(AUDIT), *map(str, args)], capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout, p.stderr


class Audit(unittest.TestCase):
    def test_slop_fixture_fails_with_expected_findings(self):
        code, out, _ = run(FIX / "slop", "--json")
        self.assertEqual(code, 1)
        checks = {i["check"] for i in json.loads(out)["items"]}
        for c in ["placeholder", "slop-gradient", "a11y-alt", "generic-copy", "emoji-ui", "a11y-focus",
                  "perf-transition", "hardcoded-color", "type-scale", "a11y-motion"]:
            self.assertIn(c, checks, c)

    def test_clean_fixture_passes_strict(self):
        code, out, _ = run(FIX / "clean", "--strict")
        self.assertEqual(code, 0, out)

    def test_token_definitions_are_not_hardcoded_colors(self):
        code, out, _ = run(FIX / "clean", "--json")
        self.assertEqual(json.loads(out)["hardcoded_colors"], 0)

    def test_showcase_pages_have_no_errors(self):
        code, out, _ = run(SHOWCASE, "--json")
        self.assertEqual(code, 0, out)
        self.assertEqual([i for i in json.loads(out)["items"] if i["level"] == "ERROR"], [])

    def test_skips_node_modules_and_reports_empty(self):
        with tempfile.TemporaryDirectory() as d:
            nm = Path(d) / "node_modules" / "pkg"
            nm.mkdir(parents=True)
            (nm / "x.tsx").write_text("<p>Lorem ipsum</p>", encoding="utf-8")
            code, _, err = run(d)
            self.assertEqual(code, 2)
            self.assertIn("No frontend files", err)

    def test_decorative_img_with_empty_alt_is_fine(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.html").write_text('<img src="x.png" alt="">', encoding="utf-8")
            code, out, _ = run(d)
            self.assertEqual(code, 0, out)


class Showcase(unittest.TestCase):
    STYLES = ["precision-dark", "fintech-gradient", "calm-workspace", "dev-platform", "editorial-luxe",
              "spec-sheet", "bold-media", "data-dashboard", "playful-builder"]

    def test_every_style_has_doc_page_and_screenshot(self):
        refs = HERE.parents[1] / "references" / "styles"
        index = (refs / "index.md").read_text(encoding="utf-8")
        for s in self.STYLES + ["immersive"]:
            self.assertTrue((refs / f"{s}.md").exists(), s)
            self.assertIn(f"({s}.md)", index, s)
        for s in self.STYLES:
            html = (SHOWCASE / f"{s}.html").read_text(encoding="utf-8")
            self.assertTrue("prefers-reduced-motion" in html, f"{s}.html has no prefers-reduced-motion rule")
            self.assertIn('lang="en"', html, s)
            self.assertTrue((SHOWCASE / "screenshots" / f"{s}.png").exists(), s)


if __name__ == "__main__":
    unittest.main()
