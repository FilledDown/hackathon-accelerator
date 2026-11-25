#!/usr/bin/env python3
"""Fetch hackathon pages (URLs) or ingest saved files into research/raw as HTML + clean text.

Usage:
  fetch_hackathon_docs.py <url-or-file> [...] --out <project>/research/raw
  fetch_hackathon_docs.py https://x.devpost.com https://x.devpost.com/rules --out research/raw

Prefer Firecrawl / WebFetch when available. This is the dependency-free fallback.
Network access may be restricted in some sandboxes; if a URL fails, save the page
from a browser (or paste text into a .txt file) and pass the file path instead.
Writes manifest.json describing every source and its outcome. Exit code 0 if at least one source succeeded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hackutil import html_to_text  # noqa: E402

UA = "Mozilla/5.0 (compatible; hackathon-accelerator/1.0; +research)"


def slug(source: str) -> str:
    base = re.sub(r"^https?://", "", source)
    base = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-")[:60] or "source"
    return f"{base}-{hashlib.sha1(source.encode()).hexdigest()[:6]}"


def fetch_url(url: str, timeout: float) -> tuple[str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,text/plain,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        ctype = resp.headers.get("Content-Type", "")
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace"), ctype


def process(source: str, out: Path, timeout: float) -> dict:
    rec = {"source": source, "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    name = slug(source)
    try:
        if re.match(r"^https?://", source):
            body, ctype = fetch_url(source, timeout)
            is_html = "html" in ctype or body.lstrip().lower().startswith(("<!doctype", "<html"))
        else:
            p = Path(source)
            body = p.read_text(encoding="utf-8", errors="replace")
            is_html = p.suffix.lower() in (".html", ".htm") or body.lstrip().lower().startswith(("<!doctype", "<html"))
        if is_html:
            (out / f"{name}.html").write_text(body, encoding="utf-8")
            title, text = html_to_text(body)
            rec["html_path"] = str(out / f"{name}.html")
        else:
            title, text = "", body
        header = f"<!-- source: {source} | retrieved: {rec['retrieved_at']} -->\n"
        if title:
            header += f"# {title}\n\n"
        (out / f"{name}.txt").write_text(header + text, encoding="utf-8")
        rec.update(status="ok", text_path=str(out / f"{name}.txt"), title=title, chars=len(text))
        if len(text) < 500 and is_html:
            rec["warning"] = ("Very little text extracted - the page may render with JavaScript. "
                              "Use a browser tool/Firecrawl, or save the rendered page and pass the file.")
    except (urllib.error.URLError, OSError, ValueError) as e:
        rec.update(status="error", error=f"{type(e).__name__}: {e}")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+", help="URLs or local file paths (.html/.htm/.txt/.md)")
    ap.add_argument("--out", required=True, help="Output directory, e.g. <project>/research/raw")
    ap.add_argument("--timeout", type=float, default=20.0)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    seen = {m["source"]: i for i, m in enumerate(manifest)}

    results = [process(s, out, args.timeout) for s in args.sources]
    for r in results:
        if r["source"] in seen:
            manifest[seen[r["source"]]] = r
        else:
            manifest.append(r)
        flag = "OK " if r["status"] == "ok" else "ERR"
        detail = r.get("text_path") or r.get("error")
        print(f"[{flag}] {r['source']} -> {detail}")
        if r.get("warning"):
            print(f"      warning: {r['warning']}")
    manifest_path.write_text(json.dumps(manifest, indent=2))
    ok = sum(r["status"] == "ok" for r in results)
    print(f"{ok}/{len(results)} sources saved. Manifest: {manifest_path}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
