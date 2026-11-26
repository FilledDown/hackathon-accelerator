#!/usr/bin/env python3
"""Show the hackathon team and what each agent did.

Usage:
  team_log.py <project-root> [--last 15] [--roster] [--json]
  team_log.py <project-root> --add <agent> "<task>" "<result>"     # log work done in the main session

Reads <root>/.hackathon/agent-log.jsonl, written automatically by the plugin's hook every time an agent
starts (PreToolUse on the Agent tool) and finishes (SubagentStop). Pairs starts with stops, and prints a
table of who did what, plus usage counts. --roster also lists all 40 agents by department (parsed from
the accelerator SKILL.md roster, the single source of truth).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SKILL_MD = Path(__file__).resolve().parent.parent / "SKILL.md"


def roster() -> dict[str, list[str]]:
    text = SKILL_MD.read_text(encoding="utf-8")
    sec = text.split("## Agent roster", 1)[-1].split("\n## ", 1)[0]
    out = {}
    for m in re.finditer(r"^- \*\*([^*]+?):?\*\*:?\s*(.+)$", sec, re.M):
        out[m.group(1).strip().rstrip(":")] = re.findall(r"`([a-z]+(?:-[a-z]+)+)`", m.group(2))
    return out


def dept_of(r: dict[str, list[str]]) -> dict[str, str]:
    return {a: d for d, agents in r.items() for a in agents}


def first_line(summary: str) -> str:
    s = re.sub(r"#+\s*(Result|Summary)\s*", "", summary or "", flags=re.I).strip()
    s = re.split(r"(?<=[.!?])\s|\s#+\s", s)[0] if s else ""
    return s[:140]


def load(root: Path) -> list[dict]:
    p = root / ".hackathon" / "agent-log.jsonl"
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def pair(rows: list[dict]) -> list[dict]:
    """Match each stop to the oldest open start of the same agent (FIFO)."""
    open_starts: dict[str, deque] = defaultdict(deque)
    runs = []
    for r in rows:
        if r.get("event") == "start":
            run = {"agent": r.get("agent"), "task": r.get("task", ""), "start": r.get("ts"), "end": None, "result": "", "status": "running"}
            open_starts[r.get("agent")].append(run)
            runs.append(run)
        elif r.get("event") == "stop":
            q = open_starts.get(r.get("agent"))
            run = q.popleft() if q else None
            if run is None:
                run = {"agent": r.get("agent"), "task": "", "start": None, "end": None, "result": "", "status": "done"}
                runs.append(run)
            run.update(end=r.get("ts"), result=first_line(r.get("summary", "")), status="done")
        elif r.get("event") == "manual":
            runs.append({"agent": r.get("agent"), "task": r.get("task", ""), "start": r.get("ts"), "end": r.get("ts"),
                         "result": r.get("summary", ""), "status": "done (main session)"})
    return runs


def dur(a, b) -> str:
    try:
        s = (datetime.fromisoformat(b.replace("Z", "+00:00")) - datetime.fromisoformat(a.replace("Z", "+00:00"))).total_seconds()
        return f"{int(s // 60)}m {int(s % 60)}s" if s >= 60 else f"{int(s)}s"
    except (AttributeError, ValueError, TypeError):
        return "—"


def hhmm(ts) -> str:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%H:%M")
    except (AttributeError, ValueError):
        return "—"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--last", type=int, default=15)
    ap.add_argument("--roster", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--add", nargs=3, metavar=("AGENT", "TASK", "RESULT"))
    args = ap.parse_args()
    root = Path(args.root).resolve()

    if args.add:
        d = root / ".hackathon"
        d.mkdir(parents=True, exist_ok=True)
        entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": "manual",
                 "agent": args.add[0], "task": args.add[1][:160], "summary": args.add[2][:300]}
        with (d / "agent-log.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"Logged: {args.add[0]} — {args.add[1]}")
        return 0

    r = roster()
    depts = dept_of(r)
    runs = pair(load(root))
    counts = Counter(x["agent"] for x in runs)
    if args.json:
        print(json.dumps({"roster": r, "runs": runs, "counts": counts}, indent=2, default=str))
        return 0

    print("# Your hackathon team\n")
    if not runs:
        print("No agent activity logged yet in this project. The plugin logs automatically every time an agent runs\n"
              "(only in folders with PROGRESS.md or HACKATHON_BRIEF.md). Start with /hackathon-accelerator:hackathon-accelerator.\n")
    else:
        recent = runs[-args.last:]
        print(f"## Activity (last {len(recent)} of {len(runs)})\n")
        print("| Time | Agent | Team | Task | Result | Took |")
        print("|---|---|---|---|---|---|")
        for x in recent:
            res = x["result"] or ("…still working" if x["status"] == "running" else "—")
            print(f"| {hhmm(x['start'] or x['end'])} | **{x['agent']}** | {depts.get(x['agent'], '—')} | {x['task'] or '—'} | {res} | "
                  f"{dur(x['start'], x['end']) if x['end'] and x['start'] and x['status'] == 'done' else ('—' if x['status'] != 'running' else '…')} |")
        print("\n## Who's done the most\n")
        print(", ".join(f"{a} ×{n}" for a, n in counts.most_common(8)))
        running = [x["agent"] for x in runs if x["status"] == "running"]
        if running:
            print(f"\nStill running (or stopped without reporting): {', '.join(running)}")
    if args.roster or not runs:
        print("\n## The roster\n")
        for d, agents in r.items():
            marks = [f"{a}{' ✓' if counts.get(a) else ''}" for a in agents]
            print(f"- **{d}** ({len(agents)}): {', '.join(marks)}")
        print("\n✓ = has worked on this project")
    return 0


if __name__ == "__main__":
    sys.exit(main())
