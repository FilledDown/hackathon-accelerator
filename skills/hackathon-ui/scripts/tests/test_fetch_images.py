#!/usr/bin/env python3
"""Offline tests for fetch_images.py: provider responses come from fixtures, image URLs are file:// paths."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "fetch_images.py"
FIX = HERE / "fixtures" / "images"


def prepared(tmp: Path, provider: str) -> Path:
    url = (FIX / "sample.png").resolve().as_uri()
    p = tmp / f"{provider}.json"
    p.write_text((FIX / f"{provider}.json").read_text(encoding="utf-8").replace("SAMPLE_URL", url), encoding="utf-8")
    return p


def run(*args, env=None):
    import os
    e = {k: v for k, v in os.environ.items() if k not in ("PEXELS_API_KEY", "UNSPLASH_ACCESS_KEY")}
    e.update(env or {})
    p = subprocess.run([sys.executable, "-I", str(SCRIPT), *map(str, args)], capture_output=True, text=True, encoding="utf-8", env=e)
    return p.returncode, p.stdout, p.stderr


class FetchImages(unittest.TestCase):
    def test_openverse_filters_small_images_and_writes_credits(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            code, out, err = run("rainy street", "--provider", "openverse", "--from-json", prepared(d, "openverse"), "--count", "5", "--out", d / "img")
            self.assertEqual(code, 0, err)
            files = sorted(p.name for p in (d / "img").glob("*.png"))
            self.assertEqual(files, ["rainy-street-1.png", "rainy-street-2.png"])   # the 640px image is filtered out
            credits = (d / "img" / "CREDITS.md").read_text(encoding="utf-8")
            self.assertIn("by Mika is licensed under CC BY 2.0", credits)
            self.assertIn("https://creativecommons.org/licenses/by-sa/4.0/", credits)
            manifest = json.loads((d / "img" / "images.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest[0]["provider"], "openverse")
            self.assertEqual(manifest[0]["page"], "https://www.flickr.com/photos/x/1")

    def test_pexels_and_unsplash_credit_format_and_append(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            run("piano hands", "--provider", "pexels", "--from-json", prepared(d, "pexels"), "--out", d / "img")
            code, out, err = run("ceramic vase", "--provider", "unsplash", "--from-json", prepared(d, "unsplash"), "--out", d / "img")
            self.assertEqual(code, 0, err)
            credits = (d / "img" / "CREDITS.md").read_text(encoding="utf-8")
            self.assertIn("Photo by Jo Park on Pexels", credits)
            self.assertIn("Photo by Sam Rivera on Unsplash", credits)
            self.assertEqual(len(json.loads((d / "img" / "images.json").read_text(encoding="utf-8"))), 2)

    def test_dry_run_downloads_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            code, out, _ = run("rainy street", "--provider", "openverse", "--from-json", prepared(d, "openverse"), "--dry-run", "--out", d / "img")
            self.assertEqual(code, 0)
            self.assertIn("CC BY 2.0", out)
            self.assertFalse((d / "img").exists())

    def test_missing_api_key_is_explained(self):
        code, _, err = run("x", "--provider", "pexels")
        self.assertNotEqual(code, 0)
        self.assertIn("PEXELS_API_KEY", err)


if __name__ == "__main__":
    unittest.main()
