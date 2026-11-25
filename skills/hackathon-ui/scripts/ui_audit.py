#!/usr/bin/env python3
"""Static anti-slop audit for frontend source code.

Usage:
  ui_audit.py <src-dir-or-file> [...] [--json] [--strict]

Scans .css/.scss/.html/.jsx/.tsx/.js/.ts/.vue/.svelte/.astro/.mdx files (skips node_modules, dist,
build, .next, .git, coverage). Reports:

ERROR  placeholder copy (lorem ipsum, John Doe, "Item 1"...), the default AI gradient
       (purple/indigo -> blue/pink), <img> without alt
WARN   hardcoded colors outside token/theme files, too many distinct font sizes, generic marketing
       copy ("revolutionize", "seamless"...), emoji in headings or buttons, focus outline removed
       with no :focus-visible style, animations with no prefers-reduced-motion handling,
       `transition: all`, heavy glassmorphism, rounded-2xl/shadow-xl everywhere
Exit code 1 if any ERROR (or any WARN with --strict). Heuristic: read each finding, don't fix blindly.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

EXTS = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro", ".mdx"}
SKIP = {"node_modules", "dist", "build", ".next", ".git", "coverage", ".turbo", ".vercel", "out", ".svelte-kit", "vendor"}
TOKEN_FILE = re.compile(r"token|theme|variables|vars|globals?|tailwind\.config|design-system|palette", re.I)

PLACEHOLDER = re.compile(r"lorem ipsum|dolor sit amet|\bjohn doe\b|\bjane doe\b|\bfoo bar\b|['\">]\s*item \d\s*['\"<]|\byour company\b|\bplaceholder text\b|\bsample text\b|\$1,?234\b", re.I)
SLOP_COPY = re.compile(r"\brevolutioni[sz]e|unlock the power|\bseamless(ly)?\b|\belevate your\b|\bsupercharge|game[- ]changer|cutting[- ]edge|next[- ]generation|\bleverage\b|\bempower(s|ing)?\b|in today's fast[- ]paced|\bwelcome to\b|\bunleash\b|\btake .{1,20} to the next level", re.I)
TW_SLOP_GRADIENT = re.compile(r"from-(purple|indigo|violet|fuchsia)-\d{3}[^\"'`]*?to-(blue|pink|purple|indigo|cyan)-\d{3}")
CSS_SLOP_GRADIENT = re.compile(r"linear-gradient\([^)]*(#8b5cf6|#7c3aed|#6366f1|#a855f7|#9333ea|#667eea|#764ba2)[^)]*(#3b82f6|#ec4899|#06b6d4|#2563eb|#764ba2|#667eea)", re.I)
HEX = re.compile(r"(?<![\w&])#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
RGB = re.compile(r"\b(?:rgb|rgba|hsl|hsla)\(\s*\d")
TW_ARBITRARY_COLOR = re.compile(r"\b(?:bg|text|border|from|to|via|fill|stroke|ring|shadow)-\[(?:#|rgb|hsl)")
FONT_SIZE_CSS = re.compile(r"font-size\s*:\s*([\d.]+(?:px|rem|em))|\bfont\s*:\s*(?:[\w-]+\s+)*?([\d.]+(?:px|rem))\s*(?:/|\s)")
FONT_SIZE_TW = re.compile(r"\btext-(xs|sm|base|lg|xl|[2-9]xl|\[[\d.]+(?:px|rem)\])\b")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
HEADING_OR_BUTTON = re.compile(r"<(h[1-6]|button)\b[^>]*>(.*?)</\1>", re.S | re.I)
IMG_TAG = re.compile(r"<(img|Image)\b[^>]*?>", re.S)
OUTLINE_NONE = re.compile(r"outline\s*:\s*(none|0)\b|\boutline-none\b")
FOCUS_VISIBLE = re.compile(r"focus-visible|:focus\b|focus:ring|focus:outline|focus-within")
ANIMATION = re.compile(r"@keyframes|\banimation\s*:|\banimate-\w+|framer-motion|from\s+['\"]motion|gsap")
REDUCED = re.compile(r"prefers-reduced-motion|useReducedMotion|motion-reduce|motion-safe")
TRANSITION_ALL = re.compile(r"transition\s*:\s*all\b|\btransition-all\b")
BLUR = re.compile(r"backdrop-filter\s*:\s*blur|\bbackdrop-blur(-\w+)?\b")
ROUNDED_BIG = re.compile(r"\brounded-(2xl|3xl)\b")
SHADOW_BIG = re.compile(r"\bshadow-(xl|2xl)\b")


def files_in(paths):
    for p in map(Path, paths):
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.suffix.lower() in EXTS and f.is_file() and not any(part in SKIP for part in f.parts):
                    yield f


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def audit(paths):
    items, sizes, colors = [], Counter(), Counter()
    any_anim = any_reduced = False
    blur = rounded = shadow = 0
    nfiles = 0

    def add(level, check, f, ln, msg):
        items.append({"level": level, "check": check, "file": str(f), "line": ln, "message": msg})

    for f in files_in(paths):
        nfiles += 1
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        is_token_file = bool(TOKEN_FILE.search(f.name))
        is_style = f.suffix.lower() in {".css", ".scss", ".sass", ".less"}

        for m in PLACEHOLDER.finditer(text):
            add("ERROR", "placeholder", f, line_of(text, m.start()), f"placeholder copy '{m.group(0).strip(chr(39)+chr(34)+'<>').strip()}' — use realistic domain data")
        for rx in (TW_SLOP_GRADIENT, CSS_SLOP_GRADIENT):
            for m in rx.finditer(text):
                add("ERROR", "slop-gradient", f, line_of(text, m.start()), "default purple→blue/pink gradient — use your style's accent or a subtle brand glow")
        for m in IMG_TAG.finditer(text):
            if not re.search(r"\balt\s*=", m.group(0)):
                add("ERROR", "a11y-alt", f, line_of(text, m.start()), "image without alt text (use alt=\"\" for decorative images)")

        if not is_style:
            for m in SLOP_COPY.finditer(text):
                add("WARN", "generic-copy", f, line_of(text, m.start()), f"generic marketing phrase '{m.group(0)}' — say what it does, for whom, with a concrete detail")
            for m in HEADING_OR_BUTTON.finditer(text):
                inner = re.sub(r"<[^>]+>", "", m.group(2))
                if EMOJI.search(inner):
                    add("WARN", "emoji-ui", f, line_of(text, m.start()), f"emoji in <{m.group(1)}> — use an icon set (Lucide/Phosphor) unless it's a deliberate brand choice")

        if not is_token_file:
            for i, line in enumerate(text.splitlines(), 1):
                if re.match(r"\s*--[\w-]+\s*:", line):   # defining a CSS custom property = a token
                    continue
                if re.search(r"<svg|<path|<stop|<circle|<rect|fill=|stroke=|stop-color", line):  # inline SVG art
                    continue
                n = len(HEX.findall(line)) + len(RGB.findall(line)) + len(TW_ARBITRARY_COLOR.findall(line))
                if n:
                    colors[str(f)] += n
        for m in FONT_SIZE_CSS.finditer(text):
            sizes[(m.group(1) or m.group(2))] += 1
        for m in FONT_SIZE_TW.finditer(text):
            sizes["text-" + m.group(1)] += 1

        if OUTLINE_NONE.search(text) and not FOCUS_VISIBLE.search(text):
            m = OUTLINE_NONE.search(text)
            add("WARN", "a11y-focus", f, line_of(text, m.start()), "focus outline removed with no :focus-visible / focus: style in this file")
        for m in TRANSITION_ALL.finditer(text):
            add("WARN", "perf-transition", f, line_of(text, m.start()), "`transition: all` — list the properties (transform, opacity, color...)")
        any_anim |= bool(ANIMATION.search(text))
        any_reduced |= bool(REDUCED.search(text))
        blur += len(BLUR.findall(text))
        rounded += len(ROUNDED_BIG.findall(text))
        shadow += len(SHADOW_BIG.findall(text))

    total_colors = sum(colors.values())
    if total_colors:
        worst = ", ".join(f"{Path(k).name} ({v})" for k, v in colors.most_common(5))
        add("WARN", "hardcoded-color", "-", 0, f"{total_colors} hardcoded color values outside token files — move them to tokens. Most in: {worst}")
    if len(sizes) > 8:
        add("WARN", "type-scale", "-", 0, f"{len(sizes)} distinct font sizes ({', '.join(sorted(sizes)[:14])}{'…' if len(sizes) > 14 else ''}) — aim for ≤ 6–8 from a scale")
    if any_anim and not any_reduced:
        add("WARN", "a11y-motion", "-", 0, "animations found but no prefers-reduced-motion handling")
    if blur > 6:
        add("WARN", "glassmorphism", "-", 0, f"{blur} backdrop blurs — keep blur for overlays (nav, palette, modals)")
    if rounded + shadow > 20:
        add("WARN", "same-everything", "-", 0, f"rounded-2xl/3xl ×{rounded}, shadow-xl/2xl ×{shadow} — pick one radius personality and use borders more than shadows")
    return {"files": nfiles, "distinct_font_sizes": len(sizes), "hardcoded_colors": total_colors, "items": items}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    args = ap.parse_args()
    r = audit(args.paths)
    if r["files"] == 0:
        print("No frontend files found in: " + ", ".join(args.paths), file=sys.stderr)
        return 2
    errors = [i for i in r["items"] if i["level"] == "ERROR"]
    warns = [i for i in r["items"] if i["level"] == "WARN"]
    if args.json:
        print(json.dumps(r, indent=2))
    else:
        for i in sorted(r["items"], key=lambda i: (i["level"] != "ERROR", i["check"], i["file"], i["line"])):
            loc = f"{i['file']}:{i['line']}" if i["line"] else "(project)"
            print(f"[{i['level']:5}] {i['check']:16} {loc}  {i['message']}")
        print(f"\nScanned {r['files']} files · {len(errors)} error(s), {len(warns)} warning(s) · "
              f"{r['distinct_font_sizes']} font sizes · {r['hardcoded_colors']} hardcoded colors. "
              + ("FAIL" if errors or (args.strict and warns) else "PASS"))
    return 1 if errors or (args.strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
