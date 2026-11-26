#!/usr/bin/env python3
"""Download licensed photos for a project and record credits automatically.

Usage:
  fetch_images.py "<search query>" [--count 4] [--out assets/images] [--provider auto|openverse|pexels|unsplash]
                  [--orientation landscape|portrait|square] [--min-width 1000] [--allow-noncommercial] [--dry-run]

Providers:
  openverse  No API key. Creative Commons and public domain images (Flickr, Wikimedia...). Commercial-use
             licenses only by default. Attribution is usually required and is written to CREDITS.md.
  pexels     Free API key (https://www.pexels.com/api/) in env PEXELS_API_KEY. Free to use, credit appreciated.
  unsplash   Free access key (https://unsplash.com/developers) in env UNSPLASH_ACCESS_KEY. Free to use, credit required
             by API guidelines.
  auto       pexels if PEXELS_API_KEY is set, else unsplash if UNSPLASH_ACCESS_KEY is set, else openverse.

Writes: <out>/<slug>-<n>.<ext>, <out>/images.json (manifest) and <out>/CREDITS.md (attribution list).
Never use this to find photos of a specific real person, a logo, or a trademarked product.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

UA = "hackathon-accelerator-image-fetch/1.3 (+https://github.com/FilledDown/hackathon-accelerator)"
EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "image/gif": "gif", "image/avif": "avif"}


def http_json(url: str, headers: dict | None = None, timeout: float = 20) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def search(provider: str, q: str, count: int, orientation: str | None, allow_nc: bool, raw: dict | None) -> list[dict]:
    """Return normalized results: url, page, title, creator, creator_url, license, license_url, credit, width, height."""
    n = max(count * 3, 10)
    if provider == "openverse":
        params = {"q": q, "page_size": min(n, 20), "mature": "false"}
        if not allow_nc:
            params["license_type"] = "commercial"
        if orientation:
            params["aspect_ratio"] = {"landscape": "wide", "portrait": "tall", "square": "square"}[orientation]
        data = raw or http_json("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params))
        out = []
        for r in data.get("results", []):
            lic = (r.get("license") or "").lower()
            lic_name = "Public Domain (CC0)" if lic in ("cc0", "pdm") else f"CC {lic.upper()} {r.get('license_version') or ''}".strip()
            out.append({"url": r.get("url"), "page": r.get("foreign_landing_url"), "title": r.get("title") or "Untitled",
                        "creator": r.get("creator") or "Unknown", "creator_url": r.get("creator_url"),
                        "license": lic_name, "license_url": r.get("license_url"),
                        "credit": r.get("attribution") or f"\"{r.get('title')}\" by {r.get('creator')} ({lic_name})",
                        "width": r.get("width") or 0, "height": r.get("height") or 0, "source": r.get("source") or "openverse"})
        return out
    if provider == "pexels":
        key = os.environ.get("PEXELS_API_KEY")
        if not key and raw is None:
            raise SystemExit("PEXELS_API_KEY is not set. Get a free key at https://www.pexels.com/api/ or use --provider openverse.")
        params = {"query": q, "per_page": min(n, 80)}
        if orientation:
            params["orientation"] = orientation
        data = raw or http_json("https://api.pexels.com/v1/search?" + urllib.parse.urlencode(params), {"Authorization": key})
        return [{"url": (p.get("src") or {}).get("large2x") or (p.get("src") or {}).get("original"), "page": p.get("url"),
                 "title": p.get("alt") or "Pexels photo", "creator": p.get("photographer") or "Unknown",
                 "creator_url": p.get("photographer_url"), "license": "Pexels License", "license_url": "https://www.pexels.com/license/",
                 "credit": f"Photo by {p.get('photographer')} on Pexels", "width": p.get("width") or 0, "height": p.get("height") or 0,
                 "source": "pexels"} for p in data.get("photos", [])]
    if provider == "unsplash":
        key = os.environ.get("UNSPLASH_ACCESS_KEY")
        if not key and raw is None:
            raise SystemExit("UNSPLASH_ACCESS_KEY is not set. Get a free key at https://unsplash.com/developers or use --provider openverse.")
        params = {"query": q, "per_page": min(n, 30), "content_filter": "high"}
        if orientation:
            params["orientation"] = {"landscape": "landscape", "portrait": "portrait", "square": "squarish"}[orientation]
        data = raw or http_json("https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(params), {"Authorization": f"Client-ID {key}"})
        return [{"url": (p.get("urls") or {}).get("regular"), "page": (p.get("links") or {}).get("html"),
                 "title": p.get("alt_description") or p.get("description") or "Unsplash photo",
                 "creator": (p.get("user") or {}).get("name") or "Unknown", "creator_url": ((p.get("user") or {}).get("links") or {}).get("html"),
                 "license": "Unsplash License", "license_url": "https://unsplash.com/license",
                 "credit": f"Photo by {(p.get('user') or {}).get('name')} on Unsplash", "width": p.get("width") or 0, "height": p.get("height") or 0,
                 "source": "unsplash", "download_location": (p.get("links") or {}).get("download_location")} for p in data.get("results", [])]
    raise SystemExit(f"Unknown provider: {provider}")


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "image"


def download(url: str, dest_base: Path) -> Path:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
        ext = EXT.get(ctype) or (Path(urllib.parse.urlparse(url).path).suffix.lstrip(".").lower() or "jpg")
        ext = "jpg" if ext == "jpeg" else ext
        data = r.read()
    if len(data) < 1000:
        raise ValueError("file too small, probably not an image")
    path = dest_base.with_suffix("." + ext)
    path.write_bytes(data)
    return path


def write_credits(out: Path, manifest: list[dict]) -> None:
    lines = ["# Image credits", "", "Images in this folder and their licenses. Keep this file in the repo and link it from the README or the app's footer.", ""]
    for m in manifest:
        page = f" — [source]({m['page']})" if m.get("page") else ""
        lic = f"[{m['license']}]({m['license_url']})" if m.get("license_url") else m["license"]
        lines.append(f"- `{m['file']}`: {m['credit']} · {lic}{page}")
    (out / "CREDITS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query")
    ap.add_argument("--count", type=int, default=4)
    ap.add_argument("--out", default="assets/images")
    ap.add_argument("--provider", default="auto", choices=["auto", "openverse", "pexels", "unsplash"])
    ap.add_argument("--orientation", choices=["landscape", "portrait", "square"])
    ap.add_argument("--min-width", type=int, default=1000)
    ap.add_argument("--allow-noncommercial", action="store_true", help="openverse only: include non-commercial licenses")
    ap.add_argument("--dry-run", action="store_true", help="list matches without downloading")
    ap.add_argument("--from-json", help=argparse.SUPPRESS)  # test hook: use a saved provider response
    args = ap.parse_args()

    provider = args.provider
    if provider == "auto":
        provider = "pexels" if os.environ.get("PEXELS_API_KEY") else "unsplash" if os.environ.get("UNSPLASH_ACCESS_KEY") else "openverse"
    raw = json.loads(Path(args.from_json).read_text(encoding="utf-8")) if args.from_json else None
    try:
        results = search(provider, args.query, args.count, args.orientation, args.allow_noncommercial, raw)
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"Search failed ({provider}): {e}\nIf the network is restricted, download images manually and record credits in CREDITS.md.", file=sys.stderr)
        return 1
    results = [r for r in results if r["url"] and (not r["width"] or r["width"] >= args.min_width)]
    if not results:
        print(f"No {provider} results for '{args.query}' at ≥{args.min_width}px. Try broader words, or --min-width 800.", file=sys.stderr)
        return 1
    print(f"{provider}: {len(results)} usable results for '{args.query}'")
    if args.dry_run:
        for r in results[: args.count]:
            print(f"- {r['width']}×{r['height']}  {r['title'][:60]}  ·  {r['credit'][:80]}  ·  {r['license']}")
        return 0

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    mpath = out / "images.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else []
    slug, saved = slugify(args.query), 0
    existing = {m["file"] for m in manifest}
    n = 1
    for r in results:
        if saved >= args.count:
            break
        while any(f.startswith(f"{slug}-{n}.") for f in existing):
            n += 1
        try:
            path = download(r["url"], out / f"{slug}-{n}")
        except (urllib.error.URLError, OSError, ValueError) as e:
            print(f"  skip ({e}): {r['url'][:80]}")
            continue
        if r.get("download_location") and os.environ.get("UNSPLASH_ACCESS_KEY"):
            try:  # required by Unsplash API guidelines when a photo is used
                http_json(r["download_location"], {"Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"})
            except (urllib.error.URLError, OSError, ValueError):
                pass
        entry = {k: r.get(k) for k in ("title", "creator", "creator_url", "license", "license_url", "credit", "page", "width", "height", "source")}
        entry.update(file=path.name, query=args.query, provider=provider, fetched=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        manifest.append(entry)
        existing.add(path.name)
        saved += 1
        print(f"  saved {path}  ({r['credit'][:70]})")
    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    write_credits(out, manifest)
    print(f"{saved} image(s) saved to {out}. Credits: {out / 'CREDITS.md'}")
    return 0 if saved else 1


if __name__ == "__main__":
    sys.exit(main())
