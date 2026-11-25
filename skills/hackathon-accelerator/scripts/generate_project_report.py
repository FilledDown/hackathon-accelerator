#!/usr/bin/env python3
"""Summarize hackathon project health from the shared project docs.

Usage:
  generate_project_report.py <project-root> [--json] [--out report.md]

Reads PROGRESS.md (Started/Deadline/Phase lines, Features table, Known bugs, Next up),
RISK_REGISTER.md, DECISION_LOG.md and the IDEA_SCORECARD.md live scorecard.
Reports time remaining and checkpoint status, feature status counts, demo-critical readiness,
open bugs/risks, recent decisions, weighted scorecard (current = verified-only vs projected),
and rule-based warnings. Read-only.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hackutil import (STATUSES, fmt_delta, load_decisions, load_progress, load_risks,  # noqa: E402
                      load_scorecard, weighted)

CHECKPOINTS = [(25, "core journey skeleton runs end-to-end"), (50, "core journey works for real"),
               (70, "FEATURE FREEZE"), (85, "submission materials drafted"), (95, "submit")]


def build(root: Path, now: datetime) -> dict:
    p = load_progress(root)
    risks = load_risks(root)
    sc = load_scorecard(root)
    counts = Counter(f["status"] for f in p["features"])
    demo = [f for f in p["features"] if f["demo_critical"]]
    demo_ok = [f for f in demo if f["status"] == "VERIFIED"]
    r = {
        "root": str(root), "generated_at": now.isoformat(timespec="minutes"),
        "phase": p["phase"], "deadline": p["deadline_raw"],
        "time_remaining": None, "pct_elapsed": None, "next_checkpoint": None,
        "feature_counts": {s: counts.get(s, 0) for s in STATUSES if counts.get(s)},
        "features_total": len(p["features"]),
        "demo_critical": {"total": len(demo), "verified": len(demo_ok),
                          "not_verified": [f"{f['name']} ({f['status']})" for f in demo if f["status"] != "VERIFIED"]},
        "open_bugs": p["open_bugs"],
        "open_risks": [x for x in risks if x.get("status", "open").lower() not in ("closed", "mitigated")],
        "recent_decisions": load_decisions(root)[-3:],
        "scorecard": {"current": weighted(sc, "current"), "projected": weighted(sc, "projected")},
        "next_up": p["next_up"][:5], "warnings": [],
    }
    W = r["warnings"]
    if not p["exists"]:
        W.append("PROGRESS.md not found - run init_project.py first.")
        return r
    if p["deadline"]:
        left = p["deadline"] - now
        r["time_remaining"] = fmt_delta(left)
        if left.total_seconds() < 0:
            W.append("Deadline has passed.")
        if p["started"] and p["deadline"] > p["started"]:
            pct = 100 * (now - p["started"]) / (p["deadline"] - p["started"])
            r["pct_elapsed"] = round(max(0, min(100, pct)), 1)
            nxt = next(((c, d) for c, d in CHECKPOINTS if c > pct), None)
            r["next_checkpoint"] = f"{nxt[0]}% - {nxt[1]}" if nxt else "past 95% - submit now"
            planned_demo = [f for f in demo if f["status"] in ("PLANNED", "IN_PROGRESS", "BLOCKED")]
            if pct >= 50 and planned_demo:
                W.append(f"{pct:.0f}% of time used and {len(planned_demo)} demo-critical feature(s) not built - cut scope now.")
            if pct >= 70 and counts.get("PLANNED"):
                W.append("Past feature freeze (70%) with PLANNED features remaining - move them to 'What's next' or CUT.")
            if pct >= 85 and not (root / "submission" / "DEVPOST.md").exists():
                W.append("85% of time used and no submission/DEVPOST.md yet.")
        elif not p["started"]:
            W.append("No 'Started:' line - checkpoint tracking disabled.")
    else:
        W.append("No parseable deadline in PROGRESS.md ('Deadline: YYYY-MM-DD HH:MM Area/City').")
    if counts.get("IMPLEMENTED", 0) >= 3:
        W.append(f"{counts['IMPLEMENTED']} features IMPLEMENTED but unverified - run them.")
    if any(x.get("impact", "").upper().startswith("H") for x in r["open_risks"]):
        W.append("Open high-impact risks in RISK_REGISTER.md.")
    if p["features"] and not demo:
        W.append("No features marked demo-critical - mark the demo path in PROGRESS.md.")
    return r


def to_md(r: dict) -> str:
    L = [f"# Project report — {r['generated_at']}", ""]
    L.append(f"**Phase:** {r['phase'] or '?'}  ·  **Deadline:** {r['deadline'] or '?'}  ·  **Time left:** {r['time_remaining'] or '?'}"
             + (f"  ·  **Elapsed:** {r['pct_elapsed']}%" if r["pct_elapsed"] is not None else ""))
    if r["next_checkpoint"]:
        L.append(f"**Next checkpoint:** {r['next_checkpoint']}")
    L += ["", "## Features", ", ".join(f"{k}: {v}" for k, v in r["feature_counts"].items()) or "none listed"]
    dc = r["demo_critical"]
    L.append(f"Demo-critical verified: {dc['verified']}/{dc['total']}" + (f" — pending: {'; '.join(dc['not_verified'])}" if dc["not_verified"] else ""))
    sc = r["scorecard"]
    if sc["current"] is not None or sc["projected"] is not None:
        L += ["", "## Scorecard (1–9, weighted)", f"Current (verified only): {sc['current']}  ·  Projected: {sc['projected']}"]
    if r["open_bugs"]:
        L += ["", "## Open bugs"] + [f"{b}" for b in r["open_bugs"]]
    if r["open_risks"]:
        L += ["", "## Open risks"] + [f"- {x.get('id', '')} {x.get('risk', '')} (L:{x.get('likelihood', '?')} I:{x.get('impact', '?')}) → {x.get('mitigation', '')}" for x in r["open_risks"]]
    if r["recent_decisions"]:
        L += ["", "## Recent decisions"] + [f"- {d}" for d in r["recent_decisions"]]
    if r["next_up"]:
        L += ["", "## Next up"] + r["next_up"]
    if r["warnings"]:
        L += ["", "## ⚠ Warnings"] + [f"- {w}" for w in r["warnings"]]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--now", help=argparse.SUPPRESS)
    args = ap.parse_args()
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
    r = build(Path(args.root).resolve(), now)
    out = json.dumps(r, indent=2, default=str) if args.json else to_md(r)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
