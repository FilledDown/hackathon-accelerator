#!/usr/bin/env python3
"""Project brain: a compact, always-current map of the codebase and the hackathon project, so Claude (and every
agent) reads one small file instead of re-exploring the repo and re-deriving decisions each session.

  brain.py ROOT                    update (incremental: only changed files are re-read) and write .hackathon/brain/BRAIN.md
  brain.py ROOT --query TERM       find files, symbols, routes and notes matching TERM (file:line)
  brain.py ROOT --file PATH        everything the brain knows about one file (symbols, imports, used by)
  brain.py ROOT --note "TEXT"      remember a durable fact ("auth uses Supabase magic links", "never touch /legacy")
  brain.py ROOT --json             machine-readable dump

BRAIN.md holds: what the project is (from the brief/spec), feature status, stack, entry points, folder map, the most
connected files with their key symbols, routes/endpoints, recent decisions, and saved notes. It is capped at about
2,000 tokens. Standard library only. Language-aware for Python, JS/TS, Lua/Luau (Roblox), GDScript (Godot),
C# (Unity), C++ (Unreal), Go, Rust, Java, plus HTML/CSS.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", ".nuxt", "out", "venv", ".venv", "env", "__pycache__",
             ".cache", "coverage", "target", "Library", "Temp", "Obj", "obj", "Binaries", "Intermediate", "DerivedDataCache",
             "Saved", ".godot", ".import", "Packages", ".hackathon", ".idea", ".vscode", "vendor", "Pods", ".turbo", ".svelte-kit"}
LANG = {".py": "py", ".js": "js", ".jsx": "js", ".mjs": "js", ".cjs": "js", ".ts": "js", ".tsx": "js", ".vue": "js", ".svelte": "js",
        ".lua": "lua", ".luau": "lua", ".gd": "gd", ".cs": "cs", ".cpp": "cpp", ".h": "cpp", ".hpp": "cpp", ".go": "go",
        ".rs": "rs", ".java": "java", ".kt": "java", ".swift": "swift", ".html": "html", ".css": "css", ".scss": "css", ".sql": "sql"}
MAX_BYTES = 400_000

SYM = {
    "py": [r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)", r"^\s*class\s+([A-Za-z_]\w*)"],
    "js": [r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)",
           r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>",
           r"^\s*(?:export\s+)?(?:default\s+)?class\s+([A-Za-z_$][\w$]*)", r"^\s*(?:export\s+)?(?:interface|type)\s+([A-Z][\w$]*)"],
    "lua": [r"^\s*(?:local\s+)?function\s+([\w.:]+)", r"^\s*(?:local\s+)?([A-Za-z_]\w*)\s*=\s*function"],
    "gd": [r"^\s*func\s+([A-Za-z_]\w*)", r"^\s*class_name\s+([A-Za-z_]\w*)", r"^\s*signal\s+([A-Za-z_]\w*)"],
    "cs": [r"^\s*(?:public|private|protected|internal)?\s*(?:static\s+|abstract\s+|sealed\s+|partial\s+)*class\s+([A-Za-z_]\w*)",
           r"^\s*(?:public|private|protected|internal)\s+(?:static\s+|override\s+|virtual\s+|async\s+)*[\w<>\[\],]+\s+([A-Z]\w*)\s*\("],
    "cpp": [r"^\s*(?:class|struct)\s+(?:\w+_API\s+)?([A-Z]\w*)", r"^\s*[\w:<>*&\s]+\s+([A-Z]\w*::\w+)\s*\("],
    "go": [r"^func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)", r"^type\s+([A-Za-z_]\w*)\s+struct"],
    "rs": [r"^\s*(?:pub\s+)?fn\s+([a-z_]\w*)", r"^\s*(?:pub\s+)?struct\s+([A-Z]\w*)"],
    "java": [r"^\s*(?:public|private|protected)?\s*(?:static\s+)?class\s+([A-Z]\w*)", r"^\s*(?:public|private|protected)\s+[\w<>\[\]]+\s+([a-z]\w*)\s*\("],
    "swift": [r"^\s*(?:func)\s+([a-zA-Z_]\w*)", r"^\s*(?:class|struct)\s+([A-Z]\w*)"],
}
IMP = {
    "py": [r"^\s*from\s+([.\w]+)\s+import", r"^\s*import\s+([\w.]+)"],
    "js": [r"""^\s*import\s+(?:[^'"]*from\s+)?['"]([^'"]+)['"]""", r"""require\(\s*['"]([^'"]+)['"]\s*\)""", r"""import\(\s*['"]([^'"]+)['"]\s*\)"""],
    "lua": [r"""require\(\s*([\w.:]+(?:\.\w+)*)\s*\)""", r"""require\(\s*['"]([^'"]+)['"]\s*\)"""],
    "gd": [r"""(?:preload|load)\(\s*['"]res://([^'"]+)['"]\s*\)""", r"^\s*extends\s+(\w+)"],
    "cs": [r"^\s*using\s+([\w.]+)\s*;"],
    "cpp": [r'^\s*#include\s+"([^"]+)"'],
    "go": [r'^\s*"([\w./-]+)"$'],
    "rs": [r"^\s*use\s+([\w:]+)"],
    "java": [r"^\s*import\s+([\w.]+);"],
}
ROUTE = [r"""\b(?:app|router|server|api)\.(get|post|put|patch|delete)\(\s*['"`]([^'"`]+)""",
         r"""@(?:app|bp|router|api)\.(get|post|put|patch|delete|route)\(\s*['"]([^'"]+)""",
         r"""export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)\b"""]
ENTRY = {"main.py", "app.py", "server.py", "manage.py", "index.js", "index.ts", "main.ts", "main.tsx", "server.js", "server.ts",
         "App.tsx", "App.jsx", "App.vue", "page.tsx", "layout.tsx", "main.go", "main.rs", "project.godot", "default.project.json",
         "init.server.lua", "init.client.lua", "Main.cs", "GameManager.cs", "index.html"}


def norm(p: Path, root: Path) -> str:
    return p.relative_to(root).as_posix()


def scan_file(path: Path, lang: str) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    lines = text.splitlines()
    syms, imps, routes = [], [], []
    for i, ln in enumerate(lines, 1):
        for rx in SYM.get(lang, []):
            m = re.search(rx, ln)
            if m and not m.group(1).startswith("_") and m.group(1) not in ("if", "for", "while", "return", "switch"):
                syms.append([m.group(1), i])
                break
        for rx in IMP.get(lang, []):
            for m in re.finditer(rx, ln):
                imps.append(m.group(1))
        if lang in ("js", "py"):
            for rx in ROUTE:
                m = re.search(rx, ln)
                if m:
                    routes.append([" ".join(g for g in m.groups() if g).upper() if len(m.groups()) == 1 else
                                   f"{m.group(1).upper()} {m.group(2)}", i])
    summary = ""
    for ln in lines[:25]:
        if ln.startswith("#!") or "-*- coding" in ln:
            continue
        s = ln.strip().lstrip("#/*-!;<>").strip().strip('"\'').strip()
        if len(s) > 12 and not re.match(r"^(import|from|use|using|require|package|include|extends|@|\{|<!doctype|<html)", s, re.I):
            summary = s[:110]
            break
    if lang == "html":
        m = re.search(r"<title>([^<]+)</title>", text, re.I)
        summary = (m.group(1).strip() if m else summary)[:110]
    return {"lang": lang, "lines": len(lines), "syms": syms[:40], "imports": sorted(set(imps))[:40], "routes": routes[:20], "summary": summary}


def resolve(imp: str, src: str, files: set[str]) -> str | None:
    base = Path(src).parent
    cands = []
    if imp.startswith("."):
        if "/" in imp or imp.startswith("./") or imp.startswith("../"):
            cands.append((base / imp).as_posix())
        else:   # python relative: ..pkg.mod
            dots = len(imp) - len(imp.lstrip("."))
            b = base
            for _ in range(dots - 1):
                b = b.parent
            cands.append((b / imp.lstrip(".").replace(".", "/")).as_posix())
    elif imp.startswith("@/") or imp.startswith("~/"):
        cands += [("src/" + imp[2:]), imp[2:]]
    else:
        cands += [(base / imp.replace(".", "/")).as_posix(), imp.replace(".", "/"), imp]
    exts = ["", ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".lua", ".luau", ".gd", "/index.ts", "/index.tsx", "/index.js", "/__init__.py", "/init.lua"]
    for c in cands:
        c = os.path.normpath(c).replace("\\", "/")
        for e in exts:
            if c + e in files:
                return c + e
    leaf = imp.replace(".", "/").split("/")[-1]
    hits = [f for f in files if Path(f).stem == leaf and Path(f).suffix in (".lua", ".luau", ".cs", ".gd")]
    return hits[0] if len(hits) == 1 else None


def walk(root: Path):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in fns:
            p = Path(dp) / fn
            if p.suffix.lower() in LANG or fn in ("package.json", "requirements.txt", "pyproject.toml", "project.godot", "Cargo.toml", "go.mod"):
                yield p


def section(text: str, name: str) -> str:
    m = re.search(rf"^#+\s*{name}[^\n]*\n(.*?)(?=^#+\s|\Z)", text, re.S | re.M | re.I)
    return m.group(1).strip() if m else ""


def read(root: Path, name: str) -> str:
    p = root / name
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def stack(root: Path) -> list[str]:
    out = []
    pj = root / "package.json"
    if pj.exists():
        try:
            d = json.loads(pj.read_text(encoding="utf-8"))
            deps = {**d.get("dependencies", {}), **d.get("devDependencies", {})}
            keys = [k for k in deps if k in ("next", "react", "vue", "svelte", "vite", "express", "fastify", "tailwindcss", "typescript",
                                             "three", "phaser", "prisma", "drizzle-orm", "@supabase/supabase-js", "firebase", "openai",
                                             "@anthropic-ai/sdk", "motion", "framer-motion", "animejs", "echarts", "socket.io", "electron")]
            out.append("node: " + ", ".join(f"{k}@{deps[k].lstrip('^~')}" for k in keys) if keys else "node project")
            if d.get("scripts"):
                out.append("scripts: " + ", ".join(f"`npm run {k}`" for k in list(d["scripts"])[:6]))
        except (ValueError, OSError):
            pass
    req = root / "requirements.txt"
    if req.exists():
        pk = [l.split("==")[0].split(">=")[0].strip() for l in req.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip() and not l.startswith("#")]
        out.append("python: " + ", ".join(pk[:10]))
    if (root / "project.godot").exists():
        out.append("engine: Godot")
    if list(root.glob("*.rbxlx")) or (root / "default.project.json").exists():
        out.append("engine: Roblox (Rojo/Luau)" if (root / "default.project.json").exists() else "engine: Roblox")
    if (root / "Assets").is_dir() and (root / "ProjectSettings").is_dir():
        out.append("engine: Unity")
    if list(root.glob("*.uproject")):
        out.append("engine: Unreal Engine")
    return out


def build(root: Path, quiet=False) -> dict:
    bdir = root / ".hackathon" / "brain"
    bdir.mkdir(parents=True, exist_ok=True)
    cache_p = bdir / "brain.json"
    old = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
    files_old = old.get("files", {})
    files, changed = {}, 0
    for p in walk(root):
        rel = norm(p, root)
        lang = LANG.get(p.suffix.lower())
        if not lang:
            continue
        try:
            st = p.stat()
        except OSError:
            continue
        if st.st_size > MAX_BYTES:
            continue
        prev = files_old.get(rel)
        if prev and prev.get("mtime") == int(st.st_mtime) and prev.get("size") == st.st_size:
            files[rel] = prev
            continue
        info = scan_file(p, lang)
        info.update(mtime=int(st.st_mtime), size=st.st_size)
        files[rel] = info
        changed += 1
    names = set(files)
    used_by = defaultdict(set)
    for rel, info in files.items():
        info["deps"] = sorted({r for r in (resolve(i, rel, names) for i in info.get("imports", [])) if r and r != rel})
        for d in info["deps"]:
            used_by[d].add(rel)
    for rel in files:
        files[rel]["used_by"] = sorted(used_by.get(rel, []))
    data = {"updated": time.strftime("%Y-%m-%d %H:%M"), "files": files, "notes": old.get("notes", []), "stack": stack(root)}
    cache_p.write_text(json.dumps(data, indent=0), encoding="utf-8")
    (bdir / "BRAIN.md").write_text(render(root, data), encoding="utf-8")
    if not quiet:
        removed = len(set(files_old) - names)
        print(f"Brain updated: {len(files)} files ({changed} re-read, {removed} removed) → .hackathon/brain/BRAIN.md")
    return data


def render(root: Path, d: dict) -> str:
    files = d["files"]
    brief, spec, prog, dec = read(root, "HACKATHON_BRIEF.md"), read(root, "PRODUCT_SPEC.md"), read(root, "PROGRESS.md"), read(root, "DECISION_LOG.md")
    out = [f"# Project brain (auto-generated {d['updated']} · do not edit; add facts with `brain.py . --note`)", ""]
    name = re.search(r"^#\s+(.+)$", spec, re.M)
    problem = section(spec, "Problem") or section(spec, "Overview") or section(brief, "Overview")
    out.append("## What this is")
    if name:
        out.append(f"- **{name.group(1).strip()}**")
    if problem:
        out.append("- " + " ".join(problem.split())[:300])
    dl = re.search(r"Deadline:\s*(.+)", prog)
    if dl and "YYYY" not in dl.group(1):
        out.append(f"- Deadline: {dl.group(1).strip()}")
    statuses = Counter(re.findall(r"\|\s*(VERIFIED|IMPLEMENTED|IN_PROGRESS|PLANNED|SIMULATED|BLOCKED|CUT)\s*\|", prog))
    if statuses:
        out.append("- Features: " + ", ".join(f"{k} {v}" for k, v in statuses.most_common()))
    if not (name or problem or statuses):
        out.append("- (no PRODUCT_SPEC.md / PROGRESS.md yet)")
    if d.get("stack"):
        out += ["", "## Stack"] + [f"- {s}" for s in d["stack"]]
    entries = sorted(f for f in files if Path(f).name in ENTRY)[:10]
    if entries:
        out += ["", "## Entry points"] + [f"- `{f}`" + (f": {files[f]['summary']}" if files[f].get("summary") else "") for f in entries]
    dirs = Counter(str(Path(f).parent.as_posix()) for f in files)
    out += ["", "## Folder map (code files per folder)"]
    for dname, n in sorted(dirs.items(), key=lambda x: (-x[1], x[0]))[:14]:
        langs = Counter(files[f]["lang"] for f in files if str(Path(f).parent.as_posix()) == dname)
        out.append(f"- `{dname}/` {n} · {', '.join(l for l, _ in langs.most_common(2))}")
    rank = sorted(files, key=lambda f: (-(len(files[f]["used_by"]) * 3 + len(files[f]["deps"]) + min(files[f]["lines"], 600) / 150), f))
    out += ["", "## Key files (most connected first)"]
    for f in rank[:18]:
        i = files[f]
        syms = ", ".join(s[0] for s in i["syms"][:7])
        extra = f" · used by {len(i['used_by'])}" if i["used_by"] else ""
        out.append(f"- `{f}` ({i['lines']} lines{extra})" + (f": {i['summary']}" if i.get("summary") else "") + (f"\n  - {syms}" if syms else ""))
    routes = [(r[0], f, r[1]) for f, i in files.items() for r in i.get("routes", [])]
    if routes:
        out += ["", "## Routes / endpoints"] + [f"- {r} → `{f}:{ln}`" for r, f, ln in routes[:20]]
    heads = re.findall(r"^#{2,3}\s+(.+)$", dec, re.M)
    heads = [h for h in heads if not re.match(r"(template|how to|format)", h, re.I)]
    if heads:
        out += ["", "## Recent decisions (DECISION_LOG.md)"] + [f"- {h.strip()}" for h in heads[-6:]]
    if d.get("notes"):
        out += ["", "## Notes (durable facts)"] + [f"- {n['text']} _({n['date']})_" for n in d["notes"][-25:]]
    out += ["", "## Use", "- Find code: `brain.py . --query <word>` · one file: `brain.py . --file <path>` · refresh after edits: `brain.py .`",
            "- Read only the files you need from here. Don't re-explore the whole repo."]
    text = "\n".join(out) + "\n"
    if len(text) > 9000:      # keep it ~2k tokens
        text = text[:8800].rsplit("\n", 1)[0] + "\n- … (truncated; use --query)\n"
    return text


def query(d: dict, term: str) -> list[str]:
    t = term.lower()
    hits = []
    for f, i in d["files"].items():
        if t in f.lower():
            hits.append(f"{f}  (file, {i['lines']} lines)")
        for s, ln in i["syms"]:
            if t in s.lower():
                hits.append(f"{f}:{ln}  {s}")
        for r, ln in i.get("routes", []):
            if t in r.lower():
                hits.append(f"{f}:{ln}  route {r}")
        if t in (i.get("summary") or "").lower():
            hits.append(f"{f}  ({i['summary']})")
    for n in d.get("notes", []):
        if t in n["text"].lower():
            hits.append(f"note: {n['text']}")
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--query")
    ap.add_argument("--file")
    ap.add_argument("--note")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    if a.note:
        cache_p = root / ".hackathon" / "brain" / "brain.json"
        d = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else build(root, quiet=True)
        if not any(n["text"] == a.note for n in d.get("notes", [])):
            d.setdefault("notes", []).append({"text": a.note.strip(), "date": time.strftime("%Y-%m-%d")})
        cache_p.write_text(json.dumps(d, indent=0), encoding="utf-8")
        (cache_p.parent / "BRAIN.md").write_text(render(root, d), encoding="utf-8")
        print(f"Noted. {len(d['notes'])} notes in the brain.")
        return 0
    d = build(root, quiet=a.quiet or bool(a.query or a.file or a.json))
    if a.json:
        print(json.dumps(d, indent=1))
    elif a.query:
        hits = query(d, a.query)
        print("\n".join(hits[:60]) if hits else f"No match for '{a.query}'.")
    elif a.file:
        f = Path(a.file).as_posix().lstrip("./")
        i = d["files"].get(f)
        if not i:
            print(f"Not in the brain: {f}")
            return 1
        print(f"{f} · {i['lang']} · {i['lines']} lines" + (f"\n{i['summary']}" if i.get("summary") else ""))
        print("symbols: " + (", ".join(f"{s}:{ln}" for s, ln in i["syms"]) or "-"))
        print("imports: " + (", ".join(i["deps"]) or "-"))
        print("used by: " + (", ".join(i["used_by"]) or "-"))
        if i.get("routes"):
            print("routes:  " + ", ".join(f"{r}:{ln}" for r, ln in i["routes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
