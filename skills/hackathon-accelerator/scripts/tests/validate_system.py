#!/usr/bin/env python3
"""Validate the installed hackathon-accelerator system: frontmatter, agent roster, references, paths.

Usage: validate_system.py [<plugin root>]   (default: auto-detect from this file's location)
Exit 0 if no errors.
"""
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):  # Windows consoles/pipes default to cp1252; our output has unicode
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

try:
    import yaml
except ImportError:  # minimal fallback parser for simple `key: value` frontmatter
    yaml = None

HERE = Path(__file__).resolve()
SKILL = HERE.parents[2]                  # .../skills/hackathon-accelerator
CLAUDE = SKILL.parents[1]                # plugin root (or .claude) holding skills/ and agents/
if len(sys.argv) > 1:
    CLAUDE = Path(sys.argv[1]).resolve()
    SKILL = CLAUDE / "skills" / "hackathon-accelerator"
VALID_TOOLS = {"Read", "Write", "Edit", "MultiEdit", "Bash", "Grep", "Glob", "WebSearch", "WebFetch", "NotebookEdit",
               "TodoWrite", "Agent", "Task", "Skill"}
VALID_MODELS = {"inherit", "sonnet", "opus", "haiku", "fable"}
VALID_COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan", "magenta"}
errors, warns = [], []


def fm(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{path}: missing frontmatter")
        return None, text
    raw = m.group(1)
    if yaml:
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as e:
            errors.append(f"{path}: invalid YAML: {e}")
            return None, text
    else:
        data = dict(re.findall(r"^(\w+):\s*(.*)$", raw, re.M))
    return data, text[m.end():]


# ---- skill
data, body = fm(SKILL / "SKILL.md")
if data:
    if data.get("name") != "hackathon-accelerator":
        errors.append("SKILL.md name mismatch")
    if not data.get("description") or len(data["description"]) > 1024:
        errors.append("SKILL.md description missing or >1024 chars")
    if len(body.splitlines()) > 500:
        warns.append(f"SKILL.md body is {len(body.splitlines())} lines (>500)")
skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

# referenced files exist
for ref in sorted(set(re.findall(r"`((?:references|scripts|assets)/[\w./-]+)", skill_text))):
    if not (SKILL / ref).exists():
        errors.append(f"SKILL.md references missing file: {ref}")
for f in (SKILL / "references").glob("*.md"):
    if f"references/{f.name}" not in skill_text:
        warns.append(f"reference not linked from SKILL.md: {f.name}")
for f in (SKILL / "scripts").glob("*.py"):
    if f.name != "hackutil.py" and f"scripts/{f.name}" not in skill_text and f.name not in skill_text:
        warns.append(f"script not mentioned in SKILL.md: {f.name}")

# ---- hackathon-ui skill (ships next to the accelerator)
UI = SKILL.parent / "hackathon-ui"
if UI.exists():
    d, b = fm(UI / "SKILL.md")
    if d and (d.get("name") != "hackathon-ui" or not d.get("description") or len(d["description"]) > 1024):
        errors.append("hackathon-ui SKILL.md name/description invalid")
    ui_text = (UI / "SKILL.md").read_text(encoding="utf-8")
    for ref in sorted(set(re.findall(r"`((?:references|scripts|assets)/[\w./-]+)", ui_text))):
        if "<" not in ref and not (UI / ref).exists():
            errors.append(f"hackathon-ui SKILL.md references missing file: {ref}")
    styles = UI / "references" / "styles"
    index = (styles / "index.md").read_text(encoding="utf-8")
    for sf in styles.glob("*.md"):
        if sf.name != "index.md" and f"({sf.name})" not in index:
            errors.append(f"style not listed in styles/index.md: {sf.name}")
        if sf.name not in ("index.md", "immersive.md") and not (UI / "assets" / "showcase" / sf.name.replace(".md", ".html")).exists():
            errors.append(f"style has no showcase page: {sf.name}")
else:
    warns.append("hackathon-ui skill not found next to hackathon-accelerator")

# ---- agents
names = {}
for path in sorted((CLAUDE / "agents").rglob("*.md")):
    d, b = fm(path)
    if not d:
        continue
    n = d.get("name")
    if not n or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", n):
        errors.append(f"{path}: bad name {n!r}")
    if n in names:
        errors.append(f"duplicate agent name {n}: {path} and {names[n]}")
    names[n] = path
    if path.stem != n:
        errors.append(f"{path}: filename doesn't match name {n}")
    desc = d.get("description") or ""
    if len(desc) < 60:
        errors.append(f"{n}: description too short")
    if "tools" in d:
        tools = {t.strip() for t in str(d["tools"]).split(",")}
        bad = {t for t in tools if t not in VALID_TOOLS and not t.startswith("mcp__")}
        if bad:
            errors.append(f"{n}: unknown tools {bad}")
    if d.get("model") and d["model"] not in VALID_MODELS:
        errors.append(f"{n}: unknown model {d['model']}")
    if d.get("color") and d["color"] not in VALID_COLORS:
        warns.append(f"{n}: unusual color {d['color']}")
    for ref in re.findall(r"`<skill-dir>/([\w./-]+)`", b):
        if not (SKILL / ref).exists():
            errors.append(f"{n}: references missing path <skill-dir>/{ref}")
    for ref in re.findall(r"`<ui-dir>/([\w./-]+)", b):
        if not (SKILL.parent / "hackathon-ui" / ref).exists():
            errors.append(f"{n}: references missing path <ui-dir>/{ref}")
    if len(b.strip()) < 400:
        errors.append(f"{n}: body too thin to be operational")

# roster in SKILL.md matches agent files
roster = set(re.findall(r"`([a-z]+(?:-[a-z]+)+)`", skill_text.split("## Agent roster")[1].split("##")[0]))
missing = roster - set(names)
extra = set(names) - roster
if missing:
    errors.append(f"SKILL.md roster names without agent files: {sorted(missing)}")
if extra:
    errors.append(f"agent files not in SKILL.md roster: {sorted(extra)}")
pj = CLAUDE / ".claude-plugin" / "plugin.json"
if pj.exists():
    import json
    meta = json.loads(pj.read_text(encoding="utf-8"))
    if meta.get("name") != "hackathon-accelerator":
        errors.append("plugin.json name mismatch")

# agent names mentioned anywhere in skill/references/agents resolve
mentioned = set()
for f in [SKILL / "SKILL.md", *(SKILL / "references").glob("*.md"), *(CLAUDE / "agents").rglob("*.md")]:
    mentioned |= set(re.findall(r"`([a-z]+(?:-[a-z]+){1,4})`", f.read_text(encoding="utf-8")))
agentish = {m for m in mentioned if any(m.endswith(s) for s in ("-engineer", "-analyst", "-specialist", "-director", "-critic",
                                                                "-designer", "-writer", "-producer", "-reviewer", "-judge",
                                                                "-researcher", "-auditor", "-strategist", "-generator",
                                                                "-manager", "-architect", "-storyteller", "-orchestrator", "-assistant"))}
for m in sorted(agentish - set(names)):
    errors.append(f"mentioned agent has no definition: {m}")

# templates required by spec
for t in ["HACKATHON_BRIEF.md", "COMPETITIVE_ANALYSIS.md", "IDEA_SCORECARD.md", "PRODUCT_SPEC.md", "ARCHITECTURE.md",
          "BUILD_PLAN.md", "PROGRESS.md", "DECISION_LOG.md", "RISK_REGISTER.md", "submission/README.md",
          "submission/DEVPOST.md", "submission/PITCH.md", "submission/DEMO_SCRIPT.md", "submission/SLIDES.md",
          "submission/FINAL_CHECKLIST.md", "CLAUDE_BLOCK.md"]:
    if not (SKILL / "assets" / "templates" / t).exists():
        errors.append(f"missing template {t}")

print(f"Agents: {len(names)}  ·  references: {len(list((SKILL / 'references').glob('*.md')))}  ·  "
      f"scripts: {len(list((SKILL / 'scripts').glob('*.py')))}")
for w in warns:
    print(f"[WARN ] {w}")
for e in errors:
    print(f"[ERROR] {e}")
print("PASS" if not errors else f"FAIL ({len(errors)} errors)")
sys.exit(1 if errors else 0)
