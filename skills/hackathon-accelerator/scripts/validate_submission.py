#!/usr/bin/env python3
"""Validate a hackathon project's submission against requirements and its own PROGRESS.md.

Usage:
  validate_submission.py <project-root> [--requirements research/requirements.json] [--strict] [--json]

Checks (ERROR fails the run; WARN is advisory; --strict promotes selected WARNs to ERRORs):
  docs        core project docs present
  submission  submission/* present, filled in, and free of placeholders (TODO, <link>, lorem ipsum...)
  claims      submission text doesn't present non-VERIFIED features as working
              (PLANNED/IN_PROGRESS/BLOCKED/CUT mentioned outside a "What's next"/roadmap section = ERROR;
               IMPLEMENTED = WARN; SIMULATED without "mock/simulated/demo data" nearby = WARN)
  demo        demo-critical features not VERIFIED
  deliverables required deliverables from requirements.json (video link, repo, live URL, slides, license, README)
  video       estimated video script length vs limit (~140 spoken words/minute)
  deadline    deadline passed / close
  secrets     likely API keys or private keys in tracked files; .env not gitignored
Exit code: 0 = no errors, 1 = errors found, 2 = bad invocation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hackutil import (SUBMISSION_DOCS, fmt_delta, load_progress, read, strip_comments)  # noqa: E402

PLACEHOLDER_RE = re.compile(
    r"\bTODO\b|\bTBD\b|\bFIXME\b|lorem ipsum|<link>|<project name>|<two-line description\.?>|YYYY-MM-DD|"
    r"\[insert[^\]]*\]|<names?\b[^>]*>|<m:ss>|<h>\b|\bxxx+\b|placeholder", re.I)
FUTURE_HEAD_RE = re.compile(r"what'?s next|roadmap|future|next steps|coming soon|planned", re.I)
SIM_WORDS_RE = re.compile(r"mock|simulat|demo data|seeded|fake|stub|placeholder data", re.I)
VIDEO_LINK_RE = re.compile(r"https?://(?:www\.)?(?:youtube\.com|youtu\.be|vimeo\.com|loom\.com|drive\.google\.com|streamable\.com)\S*", re.I)
REPO_LINK_RE = re.compile(r"https?://(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org)/\S+", re.I)
URL_RE = re.compile(r"https?://[^\s)>\]]+")
SECRET_PATTERNS = {
    "OpenAI/Anthropic-style key": r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
    "Google API key": r"\bAIza[0-9A-Za-z_-]{35}\b",
    "Slack token": r"\bxox[abpors]-[A-Za-z0-9-]{10,}",
    "Stripe live key": r"\b[sr]k_live_[A-Za-z0-9]{20,}",
    "Private key block": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
}
SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", ".venv", "venv", "__pycache__", ".claude", "research", ".turbo", ".vercel"}
TEXT_EXT = {".js", ".jsx", ".ts", ".tsx", ".py", ".json", ".env", ".yml", ".yaml", ".toml", ".md", ".txt", ".html",
            ".css", ".go", ".rs", ".java", ".kt", ".swift", ".rb", ".php", ".sh", ".ini", ".cfg", ".vue", ".svelte"}


class Report:
    def __init__(self, strict: bool):
        self.items, self.strict = [], strict

    def add(self, level, check, msg, promotable=False):
        if promotable and self.strict and level == "WARN":
            level = "ERROR"
        self.items.append({"level": level, "check": check, "message": msg})

    @property
    def errors(self):
        return [i for i in self.items if i["level"] == "ERROR"]


def meaningful(text: str) -> str:
    """Strip comments, headings, table scaffolding and checkbox stubs; return remaining content."""
    t = strip_comments(text)
    keep = []
    for line in t.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or re.fullmatch(r"\|?[\s:|-]*\|?", s):
            continue
        if re.fullmatch(r"[-*]\s*(\[ \])?\s*\S{0,3}:?\s*", s) or re.fullmatch(r"\d+\.\s*", s):
            continue
        if re.fullmatch(r"-\s*[A-Za-z ]+:\s*", s):  # "- Repo:" with nothing after
            continue
        keep.append(s)
    return "\n".join(keep)


def split_sections(text: str):
    """Yield (heading_path_text, line) pairs."""
    stack = []
    for line in strip_comments(text).splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            lvl = len(m.group(1))
            stack = [h for h in stack if h[0] < lvl] + [(lvl, m.group(2))]
            continue
        yield " / ".join(h[1] for h in stack), line


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s.lower())).strip()


def check_docs(root: Path, rep: Report):
    if not (root / "PROGRESS.md").exists():
        rep.add("ERROR", "docs", "PROGRESS.md missing - claims cannot be checked. Run init_project.py.")
    for d in ["HACKATHON_BRIEF.md", "PRODUCT_SPEC.md", "ARCHITECTURE.md"]:
        if not (root / d).exists():
            rep.add("WARN", "docs", f"{d} missing.")


def check_submission(root: Path, rep: Report, required_types: set):
    sub = root / "submission"
    for name in SUBMISSION_DOCS:
        p = sub / name
        essential = name in ("DEVPOST.md", "README.md", "DEMO_SCRIPT.md") or \
            (name == "SLIDES.md" and "slides" in required_types) or (name == "PITCH.md" and "pitch" in required_types)
        if not p.exists():
            rep.add("ERROR" if essential else "WARN", "submission", f"submission/{name} missing.")
            continue
        text = read(p)
        content = meaningful(text)
        if len(content) < 80:
            rep.add("ERROR" if essential else "WARN", "submission", f"submission/{name} looks unfilled (template only).")
            continue
        for i, line in enumerate(strip_comments(text).splitlines(), 1):
            m = PLACEHOLDER_RE.search(line)
            if m and name != "FINAL_CHECKLIST.md":
                rep.add("ERROR", "submission", f"submission/{name}:{i} placeholder '{m.group(0)}': {line.strip()[:100]}")
    fc = read(sub / "FINAL_CHECKLIST.md")
    if fc and re.search(r"\|\s*not run\s*\|", fc, re.I):
        n = len(re.findall(r"\|\s*not run\s*\|", fc, re.I))
        rep.add("WARN", "submission", f"FINAL_CHECKLIST.md has {n} check(s) marked 'not run'.", promotable=True)


def check_claims(root: Path, rep: Report, progress: dict):
    sub = root / "submission"
    texts = {n: read(sub / n) for n in ("DEVPOST.md", "PITCH.md", "README.md", "SLIDES.md", "DEMO_SCRIPT.md")}
    texts["README.md (repo root)"] = read(root / "README.md")
    for feat in progress["features"]:
        st = feat["status"]
        if st == "VERIFIED":
            continue
        phrase = norm(feat["name"])
        if len(phrase) < 4:
            continue
        for doc, text in texts.items():
            if not text:
                continue
            for head, line in split_sections(text):
                if phrase not in norm(line):
                    continue
                if FUTURE_HEAD_RE.search(head) or FUTURE_HEAD_RE.search(line):
                    continue
                where = f"{doc} [{head or 'top'}]"
                snippet = line.strip()[:110]
                if st in ("PLANNED", "IN_PROGRESS", "BLOCKED", "CUT", "UNKNOWN"):
                    rep.add("ERROR", "claims", f"'{feat['name']}' is {st} but appears as a feature in {where}: {snippet}")
                elif st == "IMPLEMENTED":
                    rep.add("WARN", "claims", f"'{feat['name']}' is IMPLEMENTED (not verified) but claimed in {where}. Verify it, then mark VERIFIED.", promotable=True)
                elif st == "SIMULATED" and not SIM_WORDS_RE.search(line):
                    rep.add("WARN", "claims", f"'{feat['name']}' is SIMULATED but {where} doesn't say it's mocked: {snippet}", promotable=True)
                break  # one finding per feature per doc


def check_demo(rep: Report, progress: dict):
    if not progress["features"]:
        rep.add("WARN", "demo", "No features listed in PROGRESS.md - cannot check demo readiness.")
    for f in progress["features"]:
        if f["demo_critical"] and f["status"] != "VERIFIED":
            rep.add("WARN", "demo", f"Demo-critical feature '{f['name']}' is {f['status']}, not VERIFIED.", promotable=True)
    for b in progress["open_bugs"]:
        rep.add("WARN", "demo", f"Open bug: {b[:120]}")


def check_deliverables(root: Path, rep: Report, reqs: dict | None):
    sub = root / "submission"
    alltext = "\n".join(read(sub / n) for n in ("DEVPOST.md", "README.md")) + read(root / "README.md")
    types = {d["type"] for d in (reqs or {}).get("required_deliverables", [])}
    if reqs is None:
        types = {"video", "repo"}  # sensible defaults for most hackathons
        rep.add("WARN", "deliverables", "No requirements.json given - checking default deliverables (video, repo) only.")
    if "video" in types and not VIDEO_LINK_RE.search(alltext):
        rep.add("ERROR", "deliverables", "Demo video required but no video link (YouTube/Vimeo/Loom/Drive) found in DEVPOST.md or README.")
    if "repo" in types and not (REPO_LINK_RE.search(alltext) or (root / ".git").exists()):
        rep.add("ERROR", "deliverables", "Repository required but no repo link found and project is not a git repo.")
    if "demo_url" in types:
        others = [u for u in URL_RE.findall(alltext) if not VIDEO_LINK_RE.match(u) and not REPO_LINK_RE.match(u)]
        if not others:
            rep.add("ERROR", "deliverables", "Live/deployed demo URL required but none found.")
    if "license" in types and not any((root / n).exists() for n in ("LICENSE", "LICENSE.md", "LICENSE.txt")):
        rep.add("ERROR", "deliverables", "License required but no LICENSE file in project root.")
    readme = read(root / "README.md") or read(sub / "README.md")
    if readme and "```" not in readme:
        rep.add("WARN", "deliverables", "README has no code block - add copy-pasteable run instructions.")
    if not (root / "README.md").exists():
        rep.add("WARN", "deliverables", "No README.md at the repo root (judges look there first). Copy submission/README.md.")
    return types


def check_video(root: Path, rep: Report, reqs: dict | None):
    limits = [d.get("video_max_minutes") for d in (reqs or {}).get("required_deliverables", []) if d.get("video_max_minutes")]
    if not limits:
        return
    limit = min(limits)
    vs = read(root / "submission" / "DEMO_SCRIPT.md")
    m = re.search(r"#+\s*Video script\s*\n(.*)", strip_comments(vs), re.S | re.I)
    if not m:
        rep.add("WARN", "video", f"Video limit is {limit} min but DEMO_SCRIPT.md has no 'Video script' section to check.")
        return
    words = len(re.findall(r"[A-Za-z']+", meaningful(m.group(1))))
    est = words / 140
    if est > limit:
        rep.add("ERROR", "video", f"Video script ~{words} words ≈ {est:.1f} min spoken > limit {limit} min.")
    elif est > limit * 0.9:
        rep.add("WARN", "video", f"Video script ≈ {est:.1f} min, close to the {limit} min limit - leave room for demo pauses.")


def check_deadline(rep: Report, progress: dict, now: datetime):
    dl = progress["deadline"]
    if not dl:
        rep.add("WARN", "deadline", "No parseable 'Deadline:' line in PROGRESS.md (use 'YYYY-MM-DD HH:MM Area/City').")
        return
    left = dl - now
    if left.total_seconds() < 0:
        rep.add("ERROR", "deadline", f"Deadline passed {fmt_delta(-left)} ago ({progress['deadline_raw']}).")
    elif left < timedelta(hours=2):
        rep.add("WARN", "deadline", f"Only {fmt_delta(left)} until the deadline - submit early; portals slow down.")


def check_secrets(root: Path, rep: Report):
    gitignore = read(root / ".gitignore")
    if (root / ".env").exists() and not re.search(r"^\s*\.env\b", gitignore, re.M):
        rep.add("ERROR", "secrets", ".env exists but is not listed in .gitignore.")
    count = 0
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts[:-1]) or not p.is_file():
            continue
        if p.suffix.lower() not in TEXT_EXT and p.name not in (".env", ".env.local"):
            continue
        if p.name in (".env", ".env.local") and re.search(r"^\s*\.env", gitignore, re.M):
            continue  # ignored locally; fine
        if p.stat().st_size > 2_000_000:
            continue
        text = read(p)
        for label, pat in SECRET_PATTERNS.items():
            m = re.search(pat, text)
            if m:
                count += 1
                rep.add("ERROR", "secrets", f"Possible {label} in {p.relative_to(root)} ('{m.group(0)[:8]}...'). Remove it and rotate the key.")
                break
        if count > 20:
            break


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--requirements", help="requirements.json from extract_submission_requirements.py (path relative to root or absolute)")
    ap.add_argument("--strict", action="store_true", help="Treat demo/claim/checklist warnings as errors (use for the final audit)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--now", help=argparse.SUPPRESS)  # ISO datetime override, for tests
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2
    reqs = None
    if args.requirements:
        rp = Path(args.requirements)
        rp = rp if rp.is_absolute() else (root / rp if (root / rp).exists() else rp)
        try:
            reqs = json.loads(rp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"Cannot read requirements file {rp}: {e}", file=sys.stderr)
            return 2
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)

    rep = Report(args.strict)
    progress = load_progress(root)
    check_docs(root, rep)
    types = check_deliverables(root, rep, reqs)
    check_submission(root, rep, types)
    check_claims(root, rep, progress)
    check_demo(rep, progress)
    check_video(root, rep, reqs)
    check_deadline(rep, progress, now)
    check_secrets(root, rep)

    if args.json:
        print(json.dumps({"errors": len(rep.errors), "items": rep.items}, indent=2))
    else:
        order = {"ERROR": 0, "WARN": 1}
        for it in sorted(rep.items, key=lambda i: (order[i["level"]], i["check"])):
            print(f"[{it['level']:5}] {it['check']:12} {it['message']}")
        w = len(rep.items) - len(rep.errors)
        print(f"\n{len(rep.errors)} error(s), {w} warning(s). " + ("FAIL" if rep.errors else "PASS"))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
