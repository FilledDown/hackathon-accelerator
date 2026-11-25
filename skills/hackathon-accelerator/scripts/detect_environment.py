#!/usr/bin/env python3
"""Detect which MCP servers, skills, plugins, agents and CLIs are actually available.

Usage:
  detect_environment.py <project-root> [--write] [--json] [--no-mcp-cli]

--write   replace the "## Environment" section of <root>/PROGRESS.md with the findings
--no-mcp-cli  skip `claude mcp list` (it health-checks servers and can be slow)

Sources inspected: `claude --version`, `claude mcp list`, <root>/.mcp.json, ~/.claude.json,
<root>/.claude/settings*.json, ~/.claude/settings.json, skills in <root>/.claude/skills and
~/.claude/skills (incl. synced/plugin subfolders), ~/.claude/plugins, agents in .claude/agents, and common CLIs.
Known optional integrations from the accelerator spec are matched by name. A match means
"something with that name exists", not that it is configured correctly; agents should still
read a skill's SKILL.md / test an MCP tool before relying on it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

KNOWN = {  # integration -> name patterns (lowercase substrings)
    "Context7 (docs)": ["context7"],
    "Firecrawl (web extraction)": ["firecrawl"],
    "Playwright (browser testing)": ["playwright"],
    "GitHub MCP": ["github"],
    "Serena (code intelligence)": ["serena"],
    "Graphify (code graph)": ["graphify"],
    "Superpowers (workflows)": ["superpowers"],
    "Planning with Files": ["planning-with-files", "planning_with_files", "planning with files"],
    "Beads (tasks)": ["beads", "bd-"],
    "Vibe Kanban": ["vibe-kanban", "vibe_kanban", "vibekanban"],
    "UI/UX Pro Max": ["ui-ux-pro-max", "uiux-pro-max", "ui_ux_pro_max"],
    "Taste Skill": ["taste"],
    "Claude Code Router": ["claude-code-router", "ccr"],
    "ECC": ["ecc", "everything-claude-code"],
    "Frontend design skill": ["frontend-design"],
    "Browser automation (other)": ["chrome", "browser", "puppeteer"],
}
CLIS = ["git", "gh", "node", "npm", "pnpm", "yarn", "bun", "python3", "uv", "pip", "docker", "vercel",
        "netlify", "supabase", "firebase", "railway", "flyctl", "npx", "playwright", "ccr", "bd", "gitleaks", "trufflehog"]


def run(cmd: list[str], timeout: int = 30) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (out.stdout or "") + (out.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        return None


def load_json(p: Path):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def mcp_servers(root: Path, use_cli: bool) -> dict[str, str]:
    found: dict[str, str] = {}
    home = Path.home()
    for p, label in [(root / ".mcp.json", "project .mcp.json"), (home / ".claude.json", "~/.claude.json"),
                     (root / ".claude" / "settings.json", "project settings"),
                     (root / ".claude" / "settings.local.json", "project local settings"),
                     (home / ".claude" / "settings.json", "user settings")]:
        data = load_json(p)
        if not isinstance(data, dict):
            continue
        for name in (data.get("mcpServers") or {}):
            found.setdefault(name, label)
        proj = (data.get("projects") or {}).get(str(root)) or {}
        for name in (proj.get("mcpServers") or {}):
            found.setdefault(name, f"{label} (project entry)")
    if use_cli and shutil.which("claude"):
        out = run(["claude", "mcp", "list"], timeout=60)
        if out:
            for line in out.splitlines():
                m = re.match(r"^\s*([A-Za-z0-9_.@/-]+):\s+(.*)$", line)
                if m and not line.lower().startswith(("checking", "no mcp")):
                    status = "connected" if re.search(r"✓|connected", m.group(2), re.I) else ("failed" if re.search(r"✗|fail", m.group(2), re.I) else "listed")
                    found[m.group(1)] = f"claude mcp list ({status})"
    return found


def skills(root: Path) -> dict[str, str]:
    found = {}
    for base, label in [(root / ".claude" / "skills", "project"), (Path.home() / ".claude" / "skills", "user"),
                        (Path.home() / ".claude" / "plugins", "plugin")]:
        if not base.exists():
            continue
        for sk in base.rglob("SKILL.md"):
            if len(sk.relative_to(base).parts) > 7:
                continue
            name = sk.parent.name
            try:
                m = re.search(r"^name:\s*['\"]?([^'\"\n]+)", sk.read_text(errors="replace")[:2000], re.M)
                if m:
                    name = m.group(1).strip()
            except OSError:
                pass
            found.setdefault(name, f"{label}: {sk.parent}")
    return found


def plugins() -> list[str]:
    base = Path.home() / ".claude" / "plugins"
    names = set()
    data = load_json(base / "installed_plugins.json")
    if isinstance(data, dict):
        names.update((data.get("plugins") or data).keys())
    for mf in base.rglob("plugin.json") if base.exists() else []:
        d = load_json(mf)
        if isinstance(d, dict) and d.get("name"):
            names.add(d["name"])
    return sorted(names)


def agents(root: Path) -> list[str]:
    out = []
    for base in [root / ".claude" / "agents", Path.home() / ".claude" / "agents"]:
        if base.exists():
            for f in base.rglob("*.md"):
                m = re.search(r"^name:\s*(\S+)", f.read_text(errors="replace")[:500], re.M)
                if m:
                    out.append(m.group(1))
    return sorted(set(out))


def detect(root: Path, use_cli: bool) -> dict:
    ver = run(["claude", "--version"]) if shutil.which("claude") else None
    mcps, sks, plugs = mcp_servers(root, use_cli), skills(root), plugins()
    clis = {c: shutil.which(c) for c in CLIS if shutil.which(c)}
    haystack = [(n.lower(), f"MCP '{n}'") for n in mcps] + [(n.lower(), f"skill '{n}'") for n in sks] + \
               [(n.lower(), f"plugin '{n}'") for n in plugs] + [(n.lower(), f"CLI '{n}'") for n in clis]
    integrations = {}
    for label, pats in KNOWN.items():
        hits = []
        for name, where in haystack:
            for pat in pats:
                if (len(pat) <= 4 and re.search(rf"(^|[^a-z]){re.escape(pat)}([^a-z]|$)", name)) or (len(pat) > 4 and pat in name):
                    hits.append(where)
                    break
        integrations[label] = sorted(set(hits))
    return {"detected_at": datetime.now().isoformat(timespec="minutes"), "claude_version": (ver or "").strip() or None,
            "mcp_servers": mcps, "skills": sks, "plugins": plugs, "agents": agents(root), "clis": clis,
            "integrations": integrations,
            "agent_teams_env": os.environ.get("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS") or None}


def to_md(d: dict) -> str:
    L = [f"_Detected {d['detected_at']} by detect_environment.py — re-run after installing tools._", ""]
    L.append(f"- Claude Code: {d['claude_version'] or 'not found on PATH'}")
    L.append(f"- Agent Teams env flag: {d['agent_teams_env'] or 'not set'}")
    avail = [k for k, v in d["integrations"].items() if v]
    missing = [k for k, v in d["integrations"].items() if not v]
    L.append("- **Available integrations:** " + ("; ".join(f"{k} ({', '.join(d['integrations'][k])})" for k in avail) or "none of the optional integrations detected"))
    L.append(f"- Not detected (do not rely on): {', '.join(missing) or '—'}")
    L.append(f"- MCP servers: {', '.join(f'{k} [{v}]' for k, v in d['mcp_servers'].items()) or 'none found'}")
    L.append(f"- Skills ({len(d['skills'])}): {', '.join(sorted(d['skills'])) or 'none'}")
    L.append(f"- Plugins: {', '.join(d['plugins']) or 'none'}")
    L.append(f"- Agents ({len(d['agents'])}): {len(d['agents'])} definitions found")
    L.append(f"- CLIs: {', '.join(sorted(d['clis'])) or 'none'}")
    return "\n".join(L)


def write_progress(root: Path, md: str) -> bool:
    p = root / "PROGRESS.md"
    if not p.exists():
        return False
    text = p.read_text()
    new_sec = "## Environment\n" + md + "\n"
    if re.search(r"^## Environment\s*$", text, re.M):
        text = re.sub(r"^## Environment\s*\n.*?(?=^## |\Z)", new_sec + "\n", text, count=1, flags=re.M | re.S)
    else:
        text = text.rstrip() + "\n\n" + new_sec
    p.write_text(text)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-mcp-cli", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    d = detect(root, not args.no_mcp_cli)
    print(json.dumps(d, indent=2) if args.json else to_md(d))
    if args.write:
        print("\nPROGRESS.md Environment section updated." if write_progress(root, to_md(d)) else "\nPROGRESS.md not found; nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
