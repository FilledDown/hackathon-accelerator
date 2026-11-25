#!/usr/bin/env python3
"""Create the hackathon shared project memory in a project root. Never overwrites existing files.

Usage:
  init_project.py <project-root> [--deadline "2026-12-01 17:00 America/Denver"] [--tz America/Denver]

Creates: HACKATHON_BRIEF.md, COMPETITIVE_ANALYSIS.md, IDEA_SCORECARD.md, PRODUCT_SPEC.md, ARCHITECTURE.md,
BUILD_PLAN.md, PROGRESS.md, DECISION_LOG.md, RISK_REGISTER.md, submission/*, and dirs app/ tests/ assets/
research/ reviews/ design/. Appends the hackathon block to CLAUDE.md (once, idempotent) so every session
loads the project context. Fills PROGRESS.md 'Started:' with now and 'Deadline:' if given.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):  # Windows consoles/pipes default to cp1252; our output has unicode
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "templates"
MARK = "<!-- hackathon-accelerator:start -->"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--deadline", help="e.g. '2026-12-01 17:00 America/Denver' or ISO 8601 with offset")
    ap.add_argument("--tz", help="IANA timezone for the Started: line, e.g. America/Denver")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    created, skipped = [], []
    for src in sorted(TEMPLATES.rglob("*.md")):
        rel = src.relative_to(TEMPLATES)
        if rel.name == "CLAUDE_BLOCK.md":
            continue
        dst = root / rel
        if dst.exists():
            skipped.append(str(rel))
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        created.append(str(rel))
    for d in ["app", "tests", "assets", "research/raw", "reviews", "design"]:
        (root / d).mkdir(parents=True, exist_ok=True)

    prog = root / "PROGRESS.md"
    if "PROGRESS.md" in created:
        text = prog.read_text(encoding="utf-8")
        tz = args.tz
        try:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo(tz)) if tz else datetime.now().astimezone()
        except Exception:
            if tz:
                print(f"warning: timezone '{tz}' not found (on Windows run `pip install tzdata`); using your computer's UTC offset.")
            now, tz = datetime.now().astimezone(), None
        started = now.strftime("%Y-%m-%d %H:%M ") + (tz or now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:])
        text = text.replace("Started: YYYY-MM-DD HH:MM Area/City", f"Started: {started}", 1)
        if args.deadline:
            text = text.replace("Deadline: YYYY-MM-DD HH:MM Area/City", f"Deadline: {args.deadline}", 1)
        prog.write_text(text, encoding="utf-8")

    cm = root / "CLAUDE.md"
    skill_dir = TEMPLATES.parents[1]
    agents_dir = skill_dir.parents[1] / "agents"  # plugin root/agents, or .claude/agents
    block = (TEMPLATES / "CLAUDE_BLOCK.md").read_text(encoding="utf-8")
    block = block.replace("{{SKILL_DIR}}", str(skill_dir)).replace("{{CODING_ASSISTANT}}", str(agents_dir / "hackathon-coding-assistant.md"))
    existing = cm.read_text(encoding="utf-8") if cm.exists() else ""
    if MARK in existing and str(skill_dir) not in existing:
        # skill moved (e.g. plugin updated): refresh the managed block in place
        import re as _re
        existing = _re.sub(r"<!-- hackathon-accelerator:start -->.*?<!-- hackathon-accelerator:end -->\n?", block, existing, flags=_re.S)
        cm.write_text(existing, encoding="utf-8")
        created.append("CLAUDE.md (hackathon block refreshed)")
    elif MARK not in existing:
        cm.write_text((existing.rstrip() + "\n\n" if existing else "") + block, encoding="utf-8")
        created.append("CLAUDE.md (hackathon block)")
    else:
        skipped.append("CLAUDE.md (block already present)")

    print(f"Project root: {root}")
    print("Created: " + (", ".join(created) or "nothing"))
    if skipped:
        print("Kept existing: " + ", ".join(skipped))
    if not args.deadline and "PROGRESS.md" in created:
        print("Next: set the 'Deadline:' line in PROGRESS.md (with timezone).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
