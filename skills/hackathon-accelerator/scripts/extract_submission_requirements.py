#!/usr/bin/env python3
"""Heuristically extract submission requirements from hackathon rules/overview text.

Usage:
  extract_submission_requirements.py <file-or-dir> [...] [--out requirements.json] [--markdown brief_draft.md]

Input: .txt/.md/.html files (e.g. research/raw from fetch_hackathon_docs.py).
Output JSON keys: sources, deadlines, team_size, judging_criteria, prize_tracks, required_deliverables,
technology_requirements, pre_existing_code_policy, disqualification_conditions, warnings.
Every item carries `evidence` (the matching line) and `source` so a human or the rules-auditor
can verify it. THIS IS A FIRST PASS, NOT THE TRUTH: always verify against the official rules.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hackutil import html_to_text  # noqa: E402

MONTHS = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_RE = re.compile(rf"\b{MONTHS}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?|\b\d{{4}}-\d{{2}}-\d{{2}}\b|\b\d{{1,2}}/\d{{1,2}}/\d{{2,4}}\b", re.I)
TIME_RE = re.compile(r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b|\b\d{1,2}:\d{2}\b", re.I)
TZ_RE = re.compile(r"\b(?:UTC|GMT|[ECMP][SD]T|BST|CEST|CET|IST|JST|AEST|AEDT)(?:[+-]\d{1,2})?\b|\b(?:eastern|pacific|central|mountain) time\b", re.I)
URL_RE = re.compile(r"https?://\S+")
HEADER_WORDS = {"criterion", "criteria", "weight", "category", "categories", "points", "score", "description"}
WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "ten": 10}

SECTION_KEYS = {
    "judging": ["judging", "criteria", "how projects will be judged", "evaluation", "scoring", "rubric"],
    "prizes": ["prize", "track", "award", "challenge"],
    "requirements": ["requirement", "what to submit", "submission", "deliverable", "how to enter"],
    "rules": ["rule", "eligib", "terms", "disqualif"],
}


def load(paths: list[str]) -> list[tuple[str, str]]:
    docs = []
    for p in paths:
        P = Path(p)
        files = sorted(x for x in P.rglob("*") if x.suffix.lower() in (".txt", ".md", ".html", ".htm")) if P.is_dir() else [P]
        # prefer .txt over the .html twin produced by fetch_hackathon_docs.py
        stems_with_txt = {f.with_suffix("") for f in files if f.suffix == ".txt"}
        for f in files:
            if f.suffix.lower() in (".html", ".htm") and f.with_suffix("") in stems_with_txt:
                continue
            raw = f.read_text(encoding="utf-8", errors="replace")
            text = html_to_text(raw)[1] if f.suffix.lower() in (".html", ".htm") else raw
            docs.append((str(f), text))
    return docs


def is_heading(line: str) -> bool:
    s = line.strip()
    if s.startswith("#"):
        return True
    return 0 < len(s) <= 60 and not s.endswith((".", ",", ";")) and not s.startswith(("-", "*", "|")) \
        and not re.search(r"\d+\s*%", s) and s[:1].isupper() and len(s.split()) <= 7


def sectionize(text: str):
    """Yield (current_section_kind, heading, line) for each non-empty line."""
    kind, heading = None, ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if is_heading(line):
            h = line.lstrip("# ").lower()
            new = next((k for k, keys in SECTION_KEYS.items() if any(key in h for key in keys)), None)
            if new or line.startswith("#"):
                kind, heading = new, line.lstrip("# ")
                continue
        yield kind, heading, line


def clean_item(line: str) -> str:
    return re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip(" |")


def extract(docs: list[tuple[str, str]]) -> dict:
    res = {k: [] for k in ["deadlines", "judging_criteria", "prize_tracks", "required_deliverables",
                           "technology_requirements", "pre_existing_code_policy", "disqualification_conditions"]}
    res["team_size"] = None
    res["sources"] = [s for s, _ in docs]
    res["warnings"] = []
    seen = set()

    def add(key, item):
        sig = (key, item.get("name") or item.get("type", "") + item.get("detail", ""), item["evidence"][:80])
        if sig not in seen:
            seen.add(sig)
            res[key].append(item)

    for src, text in docs:
        for kind, heading, line in sectionize(text):
            low = line.lower()
            ev = {"evidence": clean_item(line)[:300], "source": src}

            # --- deadlines
            if re.search(r"deadline|due\b|submissions? (?:close|end|are due)|submit (?:by|before)|closes? on|ends? on", low) and DATE_RE.search(line):
                add("deadlines", {**ev, "date": DATE_RE.search(line).group(0),
                                  "time": (TIME_RE.search(line) or [None])[0] if TIME_RE.search(line) else None,
                                  "timezone": TZ_RE.search(line).group(0) if TZ_RE.search(line) else None})

            # --- team size
            m = re.search(r"teams?\s+(?:of|can (?:have|include)|may (?:have|include)|must (?:have|be)|(?:are )?(?:limited|capped) to|size(?: is)?(?: limited to)?:?|up to|between)\s+(?:up to |a maximum of |at most |between )?(\d+|one|two|three|four|five|six|seven|eight|ten)(?:\s*(?:-|–|to|and)\s*(\d+|two|three|four|five|six|eight|ten))?\s*(?:members|people|participants|persons|hackers)?", low)
            if not m:
                m2 = re.search(r"(?:maximum|max|up to|no more than)\s+(?:of\s+)?(\d+|one|two|three|four|five|six)\s+(?:members|people|participants)\s+(?:per|in a|on a)\s+team", low)
                if m2:
                    m = m2
            if m and res["team_size"] is None:
                a = WORDNUM.get(m.group(1), m.group(1))
                b = WORDNUM.get(m.group(2), m.group(2)) if m.lastindex and m.lastindex >= 2 and m.group(2) else None
                a, b = int(a), (int(b) if b else None)
                res["team_size"] = {"min": a if b else 1, "max": b or a, **ev}

            # --- judging criteria
            w = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", line)
            pts = re.search(r"\(?\b(\d{1,3})\s*(?:points|pts)\b", low)
            if kind == "judging" and not re.search(r"judg(?:ing|es) (?:will|period|begins|takes)|winners? (?:will|announced)", low):
                name = clean_item(line)
                name = re.split(r"\s*[:–—(|]\s*|\s+-\s+", name)[0].strip(" *|")
                if w or pts or (line.lstrip().startswith(("-", "*", "•", "|")) or re.match(r"^\d+[.)]", line.strip())):
                    if 2 <= len(name) <= 80 and len(name.split()) <= 10 and name.lower() not in HEADER_WORDS:
                        add("judging_criteria", {"name": name,
                                                 "weight": float(w.group(1)) if w else (float(pts.group(1)) if pts else None),
                                                 "weight_unit": "%" if w else ("points" if pts else None), **ev})
            elif w and re.search(r"criteri|judg|scor|weight", low):
                name = re.split(r"\s*[:–—(|]\s*|\s+-\s+", clean_item(line))[0]
                add("judging_criteria", {"name": name, "weight": float(w.group(1)), "weight_unit": "%", **ev})

            # --- prizes / tracks
            if (kind == "prizes" and (re.search(r"[$€£]\s?\d|\bprize\b|\btrack\b|\baward\b|\bbest\b", low))) or \
               re.search(r"\b(?:best|most) [\w\s-]{2,40}(?:hack|use|project|app)\b.*[$€£]\s?\d", low):
                add("prize_tracks", {"name": clean_item(line)[:120],
                                     "value": (re.search(r"[$€£]\s?[\d,]+(?:k)?", line) or [None])[0] if re.search(r"[$€£]\s?[\d,]+", line) else None, **ev})

            # --- deliverables
            deliv = []
            if re.search(r"\bvideo\b", low) and re.search(r"demo|submit|include|must|require|upload|record", low):
                mm = re.search(r"(\d+(?:\.\d+)?|one|two|three|four|five)\s*(?:-|\s)?\s*(minutes?|mins?|seconds?|secs?)\b", low)
                d = {"type": "video", "detail": line[:200]}
                if mm:
                    n = float(WORDNUM.get(mm.group(1), mm.group(1)))
                    d["video_max_minutes"] = n if mm.group(2).startswith("min") else round(n / 60, 2)
                deliv.append(d)
            if re.search(r"github|gitlab|repositor|source code|public repo|code repository", low) and re.search(r"submit|include|must|require|provide|link|share", low):
                deliv.append({"type": "repo", "detail": line[:200]})
            if re.search(r"devpost", low) and re.search(r"submit|submission|project page", low):
                deliv.append({"type": "devpost", "detail": line[:200]})
            if re.search(r"(?:live|deployed|working|hosted) (?:demo|url|link|app|site)|demo link|url to (?:your|the) (?:app|project)", low) and re.search(r"submit|include|must|require|provide", low):
                deliv.append({"type": "demo_url", "detail": line[:200]})
            if re.search(r"slides?|pitch deck|presentation deck|\bdeck\b", low) and re.search(r"submit|include|must|require|upload|provide", low):
                deliv.append({"type": "slides", "detail": line[:200]})
            if re.search(r"\breadme\b", low):
                deliv.append({"type": "readme", "detail": line[:200]})
            if re.search(r"open[- ]source licen[cs]e|\blicen[cs]e\b.*(?:mit|apache|osi|open)", low):
                deliv.append({"type": "license", "detail": line[:200]})
            if re.search(r"(?:live|in-person) (?:pitch|presentation|demo)|present (?:your|the) project|pitch to (?:the )?judges", low):
                deliv.append({"type": "pitch", "detail": line[:200]})
            for d in deliv:
                d["detail"] = clean_item(d["detail"])
                existing = next((x for x in res["required_deliverables"] if x["type"] == d["type"]), None)
                if existing:  # one entry per type; keep extra evidence for the auditor
                    if clean_item(line)[:300] != existing["evidence"]:
                        existing.setdefault("more_evidence", []).append(clean_item(line)[:300])
                    if d.get("video_max_minutes") and not existing.get("video_max_minutes"):
                        existing["video_max_minutes"] = d["video_max_minutes"]
                else:
                    add("required_deliverables", {**d, **ev})

            # --- technology
            if re.search(r"must (?:use|be built|integrate|incorporate)|required to use|requires? (?:the )?use of|built (?:with|using|on) .* (?:api|sdk|platform)|only .* (?:are|is) (?:allowed|permitted)|(?:not|never) (?:allowed|permitted) to use|must not use", low):
                add("technology_requirements", {**ev})

            # --- pre-existing code
            if re.search(r"pre-?existing|existing (?:code|projects?|work)|started before|prior to the (?:event|hackathon)|previously (?:built|created)|new (?:projects?|work) only|must be (?:created|built|started) during", low):
                add("pre_existing_code_policy", {**ev})

            # --- disqualification
            if re.search(r"disqualif|ineligible|will not be (?:eligible|judged|considered)|grounds for (?:removal|disqualification)|prohibited|is not permitted|are not permitted", low):
                add("disqualification_conditions", {**ev})

    if not res["judging_criteria"]:
        res["warnings"].append("No judging criteria detected - find them manually (they may be on a separate page or rendered by JavaScript).")
    elif not any(c["weight"] for c in res["judging_criteria"]):
        res["warnings"].append("Judging criteria found but no weights detected - weights may be unpublished (assume equal, say so).")
    if not res["deadlines"]:
        res["warnings"].append("No submission deadline detected - confirm it (with timezone) manually.")
    elif not any(d["timezone"] for d in res["deadlines"]):
        res["warnings"].append("Deadline found without a timezone - confirm the timezone.")
    if res["team_size"] is None:
        res["warnings"].append("Team size not detected.")
    res["notes"] = "Heuristic extraction. Verify every item against the official rules before relying on it."
    return res


def to_markdown(r: dict) -> str:
    esc = lambda s: str(s).replace("|", "\\|")  # noqa: E731
    L = ["# Extracted requirements (heuristic draft - VERIFY)", ""]
    L += ["## Deadlines"] + [f"- {d['evidence']}  _(source: {d['source']})_" for d in r["deadlines"]] + [""]
    ts = r["team_size"]
    L += ["## Team size", f"- {ts['min']}-{ts['max']}  _({ts['evidence']})_" if ts else "- not detected", ""]
    L += ["## Judging criteria", "| Criterion | Weight | Evidence |", "|---|---|---|"]
    L += [f"| {esc(c['name'])} | {(str(c['weight']) + (c['weight_unit'] or '')) if c['weight'] else 'not published?'} | {esc(c['evidence'][:90])} |" for c in r["judging_criteria"]] + [""]
    L += ["## Prize tracks"] + [f"- {p['name']}" for p in r["prize_tracks"]] + [""]
    L += ["## Required deliverables"] + [f"- [ ] **{d['type']}**: {d['detail']}" + (f" (max {d['video_max_minutes']} min)" if d.get("video_max_minutes") else "") for d in r["required_deliverables"]] + [""]
    for key, title in [("technology_requirements", "Technology requirements"), ("pre_existing_code_policy", "Pre-existing code policy"),
                       ("disqualification_conditions", "Disqualification conditions")]:
        L += [f"## {title}"] + [f"- {x['evidence']}" for x in r[key]] + [""]
    if r["warnings"]:
        L += ["## Warnings"] + [f"- {w}" for w in r["warnings"]]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", help="Write JSON here (default: stdout)")
    ap.add_argument("--markdown", help="Also write a markdown draft for HACKATHON_BRIEF.md")
    args = ap.parse_args()
    docs = load(args.inputs)
    if not docs:
        print("No readable input files found.", file=sys.stderr)
        return 1
    r = extract(docs)
    js = json.dumps(r, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(js, encoding="utf-8")
        print(f"Wrote {args.out}: {len(r['judging_criteria'])} criteria, {len(r['required_deliverables'])} deliverables, "
              f"{len(r['deadlines'])} deadline lines, {len(r['disqualification_conditions'])} DQ conditions.")
        for w in r["warnings"]:
            print(f"warning: {w}")
    else:
        print(js)
    if args.markdown:
        Path(args.markdown).write_text(to_markdown(r), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
