#!/usr/bin/env python3
"""Audit an HTML pitch deck (assets/templates/deck/deck.html format) before anyone presents it.

  deck_audit.py submission/deck.html [--minutes 3]

Checks each main slide (slides marked data-appendix are backup Q&A) for:
  - a headline (h1/h2) and at least one PROOF element: number, screenshot frame, diagram/flow, comparison table, quote
  - thin slides (too few words and no proof → empty-looking) and dense slides (> 95 words, not counting text inside screenshots → nobody reads it)
  - images: every <img> inside a .frame (fixed aspect + object-fit, so nothing is stretched), alt text, file exists
  - leftover placeholders ("add a 2× screenshot", "Lorem", "TODO")
  - timing: every main slide has data-seconds, and the total fits --minutes (with 10% buffer)
  - an appendix with Q&A answers
Exit code 1 if there are errors. Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

PROOF = [r'class="[^"]*\bframe\b', r'class="[^"]*\b(num|big)\b', r"<table", r'class="[^"]*\b(flow|compare|quote|kpis|chart)\b', r"<svg", r"<canvas"]


def strip_frames(html: str) -> str:
    """Remove the inside of .frame blocks (screenshots/mockups) so their UI text doesn't count as slide words."""
    out, i = [], 0
    for m in re.finditer(r'<div[^>]*class="[^"]*\bframe\b[^"]*"[^>]*>', html):
        if m.start() < i:
            continue
        out.append(html[i:m.end()])
        depth, j = 1, m.end()
        for t in re.finditer(r"<(/?)div\b[^>]*>", html[m.end():]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                j = m.end() + t.end()
                break
        out.append("</div>")
        i = j
    out.append(html[i:])
    return "".join(out)


def words(html: str) -> int:
    html = strip_frames(html)
    html = re.sub(r"<aside[^>]*>.*?</aside>", " ", html, flags=re.S)
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&[a-z#0-9]+;", " ", text)
    return len([w for w in text.split() if re.search(r"\w", w)])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--minutes", type=float)
    a = ap.parse_args()
    path = Path(a.deck)
    if not path.exists():
        print(f"Not found: {path}")
        return 2
    src = path.read_text(encoding="utf-8", errors="replace")
    slides = re.findall(r'(<section[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>)(.*?)</section>', src, flags=re.S)
    if not slides:
        print("No <section class=\"slide\"> found. Is this the HTML deck template?")
        return 2
    errors, warns = [], []
    main_slides, appendix = [], []
    for i, (tag, body) in enumerate(slides, 1):
        (appendix if "data-appendix" in tag else main_slides).append((i, tag, body))
    css = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", src, flags=re.S))
    if "<img" in src and "object-fit" not in css:
        errors.append("CSS has no object-fit rule: images will stretch. Put every image in .frame (see the template).")
    total = 0.0
    last = main_slides[-1][0] if main_slides else -1
    for i, tag, body in main_slides:
        n = words(body)
        has_head = bool(re.search(r"<h[12]\b", body))
        proofs = sum(1 for p in PROOF if re.search(p, body))
        secs = re.search(r'data-seconds="([\d.]+)"', tag)
        if secs:
            total += float(secs.group(1))
        else:
            warns.append(f"slide {i}: no data-seconds (time budget from time_plan.py)")
        if not has_head:
            warns.append(f"slide {i}: no headline (h1/h2). Lead every slide with a claim")
        if proofs == 0 and i != last:
            (errors if n < 25 else warns).append(f"slide {i}: no proof element (number, screenshot, diagram, comparison, quote)")
        if n < 12 and proofs < 2 and "demo" not in tag:
            errors.append(f"slide {i}: looks empty ({n} words, {proofs} proof elements). Add a screenshot, a number with its source, or a diagram")
        if n > 95:
            warns.append(f"slide {i}: {n} words is too dense to read while you talk. Cut to the claim + proof")
    for i, tag, body in main_slides + appendix:
        for m in re.finditer(r"<img\b[^>]*>", body):
            img = m.group(0)
            before = body[:m.start()]
            opened = len(re.findall(r'class="[^"]*\bframe\b', before))
            if opened == 0:
                errors.append(f"slide {i}: <img> outside a .frame, so it can stretch or overflow. Wrap it: <div class=\"frame\" style=\"--ar:16/10\">…</div>")
            if not re.search(r'\balt="[^"]+"', img):
                warns.append(f"slide {i}: image without alt text")
            sm = re.search(r'\bsrc="([^"]+)"', img)
            if sm and not re.match(r"(https?:|data:)", sm.group(1)) and not (path.parent / sm.group(1)).exists():
                errors.append(f"slide {i}: image file missing: {sm.group(1)} (capture a 2× screenshot of the real product)")
            if re.search(r'style="[^"]*\bheight:\s*\d', img) and re.search(r'style="[^"]*\bwidth:\s*\d', img):
                warns.append(f"slide {i}: image has fixed width AND height inline, which distorts it. Use .frame + --ar instead")
        for ph in ("Lorem", "TODO", "TBD", "add a 2× screenshot", "John Doe"):
            if ph.lower() in body.lower() and "onerror" not in body.lower().split(ph.lower())[0][-200:]:
                errors.append(f"slide {i}: placeholder text \"{ph}\"")
    if not appendix:
        warns.append("no appendix: add Q&A backup slides from submission/QA.md (data-appendix)")
    elif not any("Q&amp;A" in b or "Q&A" in b or "?" in b for _, _, b in appendix):
        warns.append("appendix has no questions answered")
    if a.minutes:
        usable = a.minutes * 60 * 0.9
        if total > usable:
            errors.append(f"timing: slides add up to {total:.0f}s but a {a.minutes:g}-minute slot gives ~{usable:.0f}s after buffer")
    print(f"Deck: {len(main_slides)} main slides, {len(appendix)} appendix · {total:.0f}s budgeted")
    for e in errors:
        print(f"  ✗ {e}")
    for w in warns:
        print(f"  ! {w}")
    print("OK" if not errors else f"{len(errors)} error(s) to fix")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
