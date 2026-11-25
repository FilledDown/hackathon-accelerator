"""Shared helpers for hackathon-accelerator scripts. Standard library only."""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

for _s in (sys.stdout, sys.stderr):  # Windows consoles/pipes default to cp1252; our output has unicode
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

STATUSES = ["VERIFIED", "IMPLEMENTED", "IN_PROGRESS", "PLANNED", "SIMULATED", "BLOCKED", "CUT"]

PROJECT_DOCS = ["HACKATHON_BRIEF.md", "COMPETITIVE_ANALYSIS.md", "IDEA_SCORECARD.md", "PRODUCT_SPEC.md",
                "ARCHITECTURE.md", "BUILD_PLAN.md", "PROGRESS.md", "DECISION_LOG.md", "RISK_REGISTER.md"]
SUBMISSION_DOCS = ["README.md", "DEVPOST.md", "PITCH.md", "DEMO_SCRIPT.md", "SLIDES.md", "FINAL_CHECKLIST.md"]


def read(path: Path) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def find_root(start: Path) -> Path:
    """Walk up from start to the first dir containing PROGRESS.md or HACKATHON_BRIEF.md."""
    p = Path(start).resolve()
    for cand in [p, *p.parents]:
        if (cand / "PROGRESS.md").exists() or (cand / "HACKATHON_BRIEF.md").exists():
            return cand
    return p


# ---------- time ----------
# Fallback when the IANA database is missing (common on Windows without `pip install tzdata`).
# Standard-time offsets only, so they can be an hour off during daylight saving time.
_TZ_FALLBACK = {"America/New_York": -5, "America/Toronto": -5, "America/Chicago": -6, "America/Denver": -7,
                "America/Phoenix": -7, "America/Los_Angeles": -8, "America/Vancouver": -8, "Europe/London": 0,
                "Europe/Dublin": 0, "Europe/Paris": 1, "Europe/Berlin": 1, "Europe/Madrid": 1, "Europe/Amsterdam": 1,
                "Asia/Kolkata": 5.5, "Asia/Singapore": 8, "Asia/Shanghai": 8, "Asia/Tokyo": 9, "Asia/Seoul": 9,
                "Australia/Sydney": 10, "UTC": 0, "Etc/UTC": 0}
_TZ_ABBR = {"UTC": 0, "GMT": 0, "EST": -5, "EDT": -4, "CST": -6, "CDT": -5, "MST": -7, "MDT": -6,
            "PST": -8, "PDT": -7, "BST": 1, "CET": 1, "CEST": 2, "IST": 5.5, "JST": 9, "AEST": 10, "AEDT": 11}


def parse_datetime(value: str) -> datetime | None:
    """Parse 'YYYY-MM-DD HH:MM Area/City', 'YYYY-MM-DD HH:MM PST', or ISO 8601 with offset.
    Returns an aware datetime, or None if unparseable / placeholder."""
    if not value:
        return None
    value = value.strip()
    if "YYYY" in value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo:
            return dt
    except ValueError:
        pass
    m = re.match(r"(\d{4}-\d{2}-\d{2})[ T](\d{1,2}:\d{2})(?::\d{2})?\s*(\S+)?", value)
    if not m:
        return None
    base = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M")
    tz = m.group(3)
    if not tz:
        return base.replace(tzinfo=timezone.utc)  # assume UTC; caller should warn
    if tz.upper() in _TZ_ABBR:
        return base.replace(tzinfo=timezone(timedelta(hours=_TZ_ABBR[tz.upper()])))
    om = re.fullmatch(r"(?:UTC|GMT)?([+-])(\d{1,2}):?(\d{2})?", tz)
    if om:
        sign = 1 if om.group(1) == "+" else -1
        return base.replace(tzinfo=timezone(sign * timedelta(hours=int(om.group(2)), minutes=int(om.group(3) or 0))))
    if ZoneInfo:
        try:
            return base.replace(tzinfo=ZoneInfo(tz))
        except Exception:
            pass
    if tz in _TZ_FALLBACK:
        return base.replace(tzinfo=timezone(timedelta(hours=_TZ_FALLBACK[tz])))
    return None


def fmt_delta(td: timedelta) -> str:
    secs = int(td.total_seconds())
    sign = "-" if secs < 0 else ""
    secs = abs(secs)
    d, r = divmod(secs, 86400)
    h, r = divmod(r, 3600)
    m = r // 60
    return f"{sign}{d}d {h}h {m}m" if d else f"{sign}{h}h {m}m"


# ---------- markdown ----------
def section(text: str, heading: str) -> str:
    """Return the body of the first markdown section whose heading contains `heading` (case-insensitive)."""
    lines = text.splitlines()
    out, level, capturing = [], None, False
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            if capturing and len(m.group(1)) <= level:
                break
            if not capturing and heading.lower() in m.group(2).lower():
                capturing, level = True, len(m.group(1))
                continue
        if capturing:
            out.append(line)
    return "\n".join(out)


def parse_table(text: str) -> list[dict]:
    """Parse the first markdown table in text into a list of dicts keyed by lowercase header."""
    rows, header = [], None
    for line in text.splitlines():
        s = line.strip()
        if not (s.startswith("|") and s.endswith("|")):
            if header and rows:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells)))
    return rows


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def kv_line(text: str, key: str) -> str | None:
    m = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", strip_comments(text), re.M | re.I)
    return m.group(1) if m else None


# ---------- project state ----------
def load_progress(root: Path) -> dict:
    text = read(Path(root) / "PROGRESS.md")
    feats = []
    for r in parse_table(section(text, "Features")):
        name = r.get("feature", "").strip()
        if not name:
            continue
        status = re.sub(r"[^A-Z_]", "", r.get("status", "").upper())
        feats.append({
            "id": r.get("id", ""), "name": name,
            "status": status if status in STATUSES else (status or "UNKNOWN"),
            "demo_critical": r.get("demo-critical", "").lower().startswith("y"),
            "owner": r.get("owner", ""), "notes": r.get("notes", ""),
        })
    bugs_sec = strip_comments(section(text, "Known bugs"))
    open_bugs = [l.strip() for l in bugs_sec.splitlines() if re.match(r"^\s*-\s*\[ \]", l)]
    return {
        "exists": bool(text),
        "started": parse_datetime(kv_line(text, "Started") or ""),
        "deadline_raw": kv_line(text, "Deadline"),
        "deadline": parse_datetime(kv_line(text, "Deadline") or ""),
        "phase": kv_line(text, "Phase"),
        "features": feats,
        "open_bugs": open_bugs,
        "next_up": [l.strip() for l in strip_comments(section(text, "Next up")).splitlines()
                    if re.match(r"^\s*(\d+\.|-)\s*\S", l) and not re.match(r"^\s*\d+\.\s*$", l)],
    }


def load_risks(root: Path) -> list[dict]:
    return [r for r in parse_table(read(Path(root) / "RISK_REGISTER.md")) if r.get("risk")]


def load_decisions(root: Path) -> list[str]:
    text = strip_comments(read(Path(root) / "DECISION_LOG.md"))
    return re.findall(r"^##\s+(D-\d+.*)$", text, re.M)


def load_scorecard(root: Path) -> list[dict]:
    rows = parse_table(section(read(Path(root) / "IDEA_SCORECARD.md"), "Live scorecard"))
    out = []
    for r in rows:
        def num(k):
            m = re.search(r"\d+(\.\d+)?", r.get(k, ""))
            return float(m.group()) if m else None
        out.append({"dimension": r.get("dimension", ""), "weight": num("weight"),
                    "current": num("current"), "projected": num("projected")})
    return out


def weighted(scorecard: list[dict], key: str) -> float | None:
    pairs = [(r["weight"], r[key]) for r in scorecard if r["weight"] and r[key] is not None]
    if not pairs:
        return None
    tw = sum(w for w, _ in pairs)
    return round(sum(w * s for w, s in pairs) / tw, 2)


# ---------- html ----------
class _TextExtractor(HTMLParser):
    BLOCK = {"p", "div", "section", "article", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6",
             "ul", "ol", "table", "header", "footer", "main", "dd", "dt", "blockquote"}
    SKIP = {"script", "style", "noscript", "svg", "head", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip, self.title = [], 0, ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
            if tag == "head":
                pass
        if tag == "title":
            self._in_title = True
        if self.skip:
            return
        if tag in self.BLOCK:
            self.parts.append("\n")
        if re.fullmatch(r"h[1-6]", tag):
            self.parts.append("#" * int(tag[1]) + " ")
        elif tag == "li":
            self.parts.append("- ")
        elif tag in ("td", "th"):
            self.parts.append(" | ")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in self.SKIP and self.skip:
            self.skip -= 1
            return
        if not self.skip and tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if not self.skip:
            self.parts.append(data)


def html_to_text(html: str) -> tuple[str, str]:
    """Return (title, markdown-ish text) from HTML."""
    p = _TextExtractor()
    p.feed(html)
    text = "".join(p.parts)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return p.title.strip(), text.strip()
