#!/usr/bin/env python3
"""Plan a time-boxed pitch or demo video, and check your scripts against the clock.

Usage:
  time_plan.py --minutes 3 --format live-demo      # pitch with a live demo inside it
  time_plan.py --minutes 3 --format video-demo     # pitch that plays a recorded demo
  time_plan.py --minutes 2 --format video-only     # the demo video IS the submission (async judging)
  time_plan.py --minutes 3 --format live-demo --check <project-root>  # check PITCH.md / DEMO_SCRIPT.md

Speaking rate: 140 words per minute (comfortable, clear for non-native listeners), with a 10% buffer
reserved for transitions, clicks and laughter. Prints a segment table (seconds, words, slides) you can
paste into PITCH.md, and with --check counts the words in each timed script and flags overruns.
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

WPM = 140
BUFFER = 0.10

# (segment, share of usable time, slides, what to show) — demo gets the biggest share in every format
PLANS = {
    "live-demo": [
        ("Hook: one person, one problem", 0.08, 1, "Title slide with the product name, or straight to a problem photo"),
        ("Problem + evidence", 0.10, 1, "One statistic or quote, big"),
        ("Solution in one sentence", 0.06, 1, "Product name, tagline, hero screenshot"),
        ("LIVE DEMO: core loop + hero moment", 0.50, 0, "The real app. No slides. Have a backup video cued"),
        ("How it works + the hard part", 0.12, 1, "One architecture diagram, sponsor tech highlighted"),
        ("Impact + what's next", 0.09, 1, "One impact number, 2–3 next steps"),
        ("Close: name + memorable line", 0.05, 1, "Name, URL or QR, team"),
    ],
    "video-demo": [
        ("Hook: one person, one problem", 0.08, 1, "Problem slide"),
        ("Problem + evidence", 0.09, 1, "One statistic or quote"),
        ("Solution in one sentence", 0.06, 1, "Product name + tagline"),
        ("DEMO VIDEO (play it, narrate live or let it speak)", 0.52, 0, "The recorded demo, captioned"),
        ("How it works + the hard part", 0.12, 1, "Architecture diagram"),
        ("Impact + what's next", 0.08, 1, "Impact number"),
        ("Close", 0.05, 1, "Name, URL or QR"),
    ],
    "video-only": [
        ("Cold open: the problem in one shot", 0.08, 0, "The 'before' state or a problem stat, captioned"),
        ("Product name + one-line promise", 0.05, 0, "Title card"),
        ("Hero moment first: show the magic", 0.17, 0, "The differentiator result. Lead with the wow, explain after"),
        ("Core loop walkthrough", 0.40, 0, "Screen recording, captioned, real data"),
        ("How it works (fast)", 0.12, 0, "Architecture card + sponsor tech (if allowed)"),
        ("Impact + end card", 0.18, 0, "Impact number, then name, URL, team on a ≥3s end card"),
    ],
}
QA_TIPS = [
    "What happens when the AI / model is wrong?",
    "What did you build during the event vs before?",
    "How is this different from <closest competitor>?",
    "Who is the first user, and how do you reach them?",
    "How does it scale or what does it cost to run?",
]


def words(text: str) -> int:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"^\s*\|?\s*-{3,}.*$", "", text, flags=re.M)
    return len(re.findall(r"[A-Za-z0-9'’]+", text))


def section(md: str, name: str) -> str:
    m = re.search(rf"^#+\s*{name}[^\n]*\n(.*?)(?=^#+\s|\Z)", md, re.S | re.M | re.I)
    return m.group(1) if m else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--minutes", type=float, required=True)
    ap.add_argument("--format", choices=sorted(PLANS), required=True)
    ap.add_argument("--qa-minutes", type=float, default=0, help="separate Q&A time after the pitch, if any")
    ap.add_argument("--check", metavar="ROOT", help="project root: check PITCH.md 'Script' and DEMO_SCRIPT.md 'Video script'")
    args = ap.parse_args()

    total = args.minutes * 60
    usable = total * (1 - BUFFER)
    plan = PLANS[args.format]
    print(f"# Time plan: {args.minutes:g} min, {args.format}\n")
    print(f"Speaking rate {WPM} wpm · {int(total * BUFFER)}s buffer kept for transitions · usable {int(usable)}s\n")
    print("| # | Segment | Seconds | Words (max) | Slides | Show |")
    print("|---|---|---|---|---|---|")
    t, slides, spoken_words = 0, 0, 0
    for i, (name, share, n, show) in enumerate(plan, 1):
        secs = usable * share
        w = int(secs / 60 * WPM)
        is_demo = name.startswith(("LIVE DEMO", "DEMO VIDEO"))
        # live demos are ~60% talking while clicking; recorded demos are narrated over
        w_shown = int(w * (0.6 if is_demo and args.format == "live-demo" else 1))
        print(f"| {i} | {name} | {int(t)}–{int(t + secs)}s ({int(secs)}s) | {w_shown} | {n} | {show} |")
        t += secs
        slides += n
        spoken_words += w_shown
    print(f"\n**Total:** ~{spoken_words} spoken words · {slides} slides (+ appendix) · finish by {int(usable)}s, hard stop {int(total)}s.")
    if args.format != "video-only":
        print(f"\n**Slide budget:** {slides} main slides. Put answers to likely judge questions in 2–4 appendix slides after the close:")
        for q in QA_TIPS:
            print(f"- {q}")
    else:
        print("\n**Video rules:** captions on everything (many judges watch muted), the hero moment within the first 30–45s, an end card of at least 3s, and no slow logo intro.")
    if args.minutes <= 3 and args.format != "video-only":
        print("\n**Short slot rules (≤3 min):** no agenda slide, no team-intro slide at the start (team goes on the last slide), "
              "one idea per slide, start the demo before the 40-second mark, and rehearse with a timer at least 3 times.")
    if args.qa_minutes:
        print(f"\n**Q&A:** {args.qa_minutes:g} min after the pitch. Prepare 30-second answers for the questions above (see PITCH.md › Judge Q&A).")

    if args.check:
        root = Path(args.check)
        rc = 0
        pitch = (root / "submission" / "PITCH.md")
        if pitch.exists():
            md = pitch.read_text(encoding="utf-8")
            body = section(md, "Script") or md
            n = words(body)
            est = n / WPM * 60
            flag = "OVER" if est > usable else ("TIGHT" if est > usable * 0.9 else "OK")
            print(f"\n**Check PITCH.md script:** {n} words ≈ {int(est)}s spoken vs {int(usable)}s usable → {flag}")
            rc |= flag == "OVER"
        demo = root / "submission" / "DEMO_SCRIPT.md"
        if demo.exists() and args.format in ("video-only", "video-demo"):
            body = section(demo.read_text(encoding="utf-8"), "Video script")
            if body.strip():
                n = words(body)
                limit = total if args.format == "video-only" else usable * 0.52
                est = n / WPM * 60
                flag = "OVER" if est > limit else ("TIGHT" if est > limit * 0.9 else "OK")
                print(f"**Check DEMO_SCRIPT.md video script:** {n} words ≈ {int(est)}s narration vs {int(limit)}s → {flag}")
                rc |= flag == "OVER"
        return 1 if rc else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
