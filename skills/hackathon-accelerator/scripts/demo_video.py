#!/usr/bin/env python3
"""One command from a shot list to a finished, edited demo video (default ~30 s, 1080p MP4).

  demo_video.py ROOT --check                 what's installed, what's missing, and the exact fix commands
  demo_video.py ROOT --plan                  validate video/shots.json and estimate the timing (no recording)
  demo_video.py ROOT                         record the running app, render cards, edit, write submission/demo.mp4

Options: --shots video/shots.json  --out submission/demo.mp4  --target 30  --limit SECONDS
         --music auto|none|FILE (auto = a generated royalty-free pad)  --voiceover FILE  --keep

The shot list (agents write it, see references/demo-video.md):
  {"url": "http://localhost:3000", "target_seconds": 30,
   "brand": {"name": "Cadence", "tagline": "Practice with intention", "accent": "#f97316", "bg": "#0b0b0d"},
   "hook": {"kicker": "The problem", "big": "73%", "text": "of students practice by playing pieces through"},
   "end": {"url": "cadence.app", "team": "Team Fermata", "event": "PolarHacks 2026"},
   "shots": [{"caption": "Add a piece in seconds", "actions": [{"click": "text=Add piece"}, {"type": ["input", "Chopin"]}], "hold": 1.2},
             {"caption": "The rushed bars light up", "actions": [{"click": "text=Record"}, {"spotlight": ".result"}], "hold": 2.5, "hero": true}]}
Actions: goto, click, hover, move, type [sel, text], fill [sel, text], press, drag [sel, dx, dy], scroll, wait (ms), waitFor, spotlight, unspotlight.
"url" may also be a local .html file. Captions accept *word* for accent-colored emphasis.

What the edit does: hook card → title card → each shot as its own clip (trimmed to fit the target, keeping the
end of each shot where the result is), a slow push-in on the "hero" shot, gentle zoom on cards, 0.4 s crossfades,
music with fade in/out, end card, H.264/AAC with fast start, plus submission/thumbnail.png.
Needs Node 18+, ffmpeg, and Chrome/Edge (or Playwright's Chromium). Installs playwright-core privately into
ROOT/.hackathon/video-tools/ the first time, so the project's package.json is untouched.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent / "assets" / "video" / "video-engine.mjs"
W, H, FPS = 1920, 1080, 30
FADE = 0.4
ACTION_SECS = {"goto": 1.5, "click": 1.3, "hover": 1.6, "move": 0.7, "press": 0.4, "scroll": 1.3, "drag": 2.0,
               "spotlight": 0.9, "unspotlight": 0.1, "waitFor": 1.0, "fill": 0.2}
OS = platform.system()


def fix(tool: str) -> str:
    table = {
        "node": {"Windows": "winget install OpenJS.NodeJS.LTS", "Darwin": "brew install node", "Linux": "sudo apt install nodejs npm"},
        "ffmpeg": {"Windows": "winget install Gyan.FFmpeg", "Darwin": "brew install ffmpeg", "Linux": "sudo apt install ffmpeg"},
        "browser": {"Windows": "Edge is built in. If it isn't found: winget install Google.Chrome",
                    "Darwin": "brew install --cask google-chrome", "Linux": "npx playwright-core install --with-deps chromium"},
    }
    return table[tool].get(OS, table[tool]["Linux"]) + ("  (then close and reopen the terminal)" if OS == "Windows" else "")


def run(cmd, cwd=None, check=True, live=False):
    if live:
        p = subprocess.run(cmd, cwd=cwd)
        if check and p.returncode != 0:
            raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str, cmd))[:300]}")
        return ""
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(map(str, cmd))[:300]}\n{(p.stderr or p.stdout)[-1500:]}")
    return p.stdout


def which(name):
    return shutil.which(name) or shutil.which(name + ".cmd") or shutil.which(name + ".exe")


def find_browser():
    if os.environ.get("CHROME_PATH") and Path(os.environ["CHROME_PATH"]).exists():
        return os.environ["CHROME_PATH"]
    cands = {
        "Windows": [r"%ProgramFiles%\Google\Chrome\Application\chrome.exe", r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
                    r"%LocalAppData%\Google\Chrome\Application\chrome.exe", r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
                    r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"],
        "Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
    }.get(OS, ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/microsoft-edge"])
    for c in cands:
        p = Path(os.path.expandvars(c))
        if p.exists():
            return str(p)
    return None


def ffprobe_dur(p: Path) -> float:
    return float(json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(p)]))["format"]["duration"])


# ---------------------------------------------------------------- check / plan
def check(root: Path, spec: dict | None, base: Path | None = None) -> bool:
    ok = True
    def line(good, name, detail):
        nonlocal ok
        ok = ok and good
        print(f"  {'✓' if good else '✗'} {name:<10} {detail}")
    print("Demo video: environment check")
    node = which("node")
    ver = run([node, "--version"], check=False).strip() if node else ""
    major = int(ver.lstrip("v").split(".")[0]) if ver.startswith("v") else 0
    line(major >= 18, "node", ver if major >= 18 else f"Node 18+ needed. Fix: {fix('node')}")
    line(bool(which("npm")), "npm", "found" if which("npm") else f"comes with Node. Fix: {fix('node')}")
    line(bool(which("ffmpeg") and which("ffprobe")), "ffmpeg", "found" if which("ffmpeg") else f"Fix: {fix('ffmpeg')}")
    b = find_browser()
    tools = root / ".hackathon" / "video-tools" / "node_modules" / "playwright-core"
    line(bool(b) or tools.exists(), "browser", b or f"none found. Fix: {fix('browser')}")
    line(True, "recorder", "installed" if tools.exists() else "installs automatically on first run (npm, ~10 MB)")
    if spec:
        url = spec.get("url", "")
        if url.startswith("http"):
            try:
                urllib.request.urlopen(url, timeout=4)
                line(True, "app", f"{url} is running")
            except Exception as e:
                line(False, "app", f"{url} isn't reachable ({e.__class__.__name__}). Start the app first (e.g. npm run dev).")
        elif url:
            p = ((base or root) / url) if not Path(url).is_absolute() else Path(url)
            line(p.exists(), "app", str(p) if p.exists() else f"file not found: {p}")
    print("Ready." if ok else "Fix the ✗ items above, then run again.")
    return ok


def estimate(shot: dict) -> float:
    t = 0.0
    for a in shot.get("actions", []):
        name, arg = next(iter(a.items()))
        if name == "wait":
            t += float(arg) / 1000
        elif name == "type":
            t += 0.9 + len(str(arg[1])) * 0.045
        else:
            t += ACTION_SECS.get(name, 1.0)
    return t + float(shot.get("hold", 1.6))


def validate(spec: dict) -> list[str]:
    errs = []
    shots = spec.get("shots")
    if not isinstance(shots, list) or not shots:
        return ["shots.json needs a non-empty \"shots\" list"]
    known = set(ACTION_SECS) | {"wait", "type"}
    for i, s in enumerate(shots, 1):
        if len(s.get("caption", "")) > 80:
            errs.append(f"shot {i}: caption over 80 characters (viewers can't read it in time)")
        for a in s.get("actions", []):
            if not isinstance(a, dict) or len(a) != 1:
                errs.append(f"shot {i}: each action is one key, like {{\"click\": \"text=Start\"}}")
                continue
            name, arg = next(iter(a.items()))
            if name not in known:
                errs.append(f"shot {i}: unknown action \"{name}\"")
            if name in ("type", "fill") and not (isinstance(arg, list) and len(arg) >= 2):
                errs.append(f"shot {i}: {name} needs [selector, text]")
    if not any(s.get("hero") for s in shots):
        errs.append("no shot has \"hero\": true. Mark the wow moment so the edit can push in on it")
    return errs


def card_times(spec: dict) -> list[tuple[str, float]]:
    cards = []
    if spec.get("hook"):
        cards.append(("hook", 2.4))
    cards.append(("title", 2.2))
    return cards


def plan(spec: dict, target: float) -> tuple[list[float], float]:
    est = [estimate(s) for s in spec["shots"]]
    cards = card_times(spec) + [("end", 3.0)]
    n_parts = len(cards) + len(est)
    avail = target - sum(c[1] for c in cards) + FADE * (n_parts - 1)
    return est, avail


# ---------------------------------------------------------------- cards
def cards_html(spec: dict) -> str:
    b = spec.get("brand", {})
    acc, bg = b.get("accent", "#f97316"), b.get("bg", "#0b0b0d")
    font = b.get("font", "Inter")
    e = lambda s: html.escape(str(s or ""))
    hook, end = spec.get("hook") or {}, spec.get("end") or {}
    sections = []
    if hook:
        sections.append(f'<section class="card" id="hook"><span class="k">{e(hook.get("kicker", "The problem"))}</span>'
                        + (f'<div class="big">{e(hook["big"])}</div>' if hook.get("big") else "")
                        + f'<h2>{e(hook.get("text"))}</h2></section>')
    sections.append(f'<section class="card" id="title"><span class="k">{e(end.get("event", ""))}</span>'
                    f'<h1>{e(b.get("name", "Our project"))}</h1><p>{e(b.get("tagline", ""))}</p></section>')
    sections.append(f'<section class="card" id="end"><h1 class="sm">{e(b.get("name", ""))}</h1><p>{e(b.get("tagline", ""))}</p>'
                    f'<div class="row"><span class="url">{e(end.get("url", ""))}</span><span>{e(end.get("team", ""))}</span></div></section>')
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{{--bg:{bg};--accent:{acc};--text:#f6f6f4;--text-2:#a9a9b2}}
*{{box-sizing:border-box;margin:0}}body{{background:#000}}
.card{{width:1920px;height:1080px;background:var(--bg);color:var(--text);font-family:"{font}","Segoe UI",system-ui,sans-serif;display:flex;flex-direction:column;justify-content:center;padding:0 190px;position:relative;overflow:hidden}}
.card::before{{content:"";position:absolute;width:1500px;height:1000px;left:50%;top:-480px;transform:translateX(-50%);background:radial-gradient(closest-side,color-mix(in oklab,var(--accent) 50%,transparent),transparent);filter:blur(50px);opacity:.75}}
.card::after{{content:"";position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.04) 1px,transparent 1px);background-size:4px 4px}}
.card>*{{position:relative;z-index:1}}
.k{{font:500 28px "JetBrains Mono",monospace;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}}
h1{{font-weight:700;font-size:210px;line-height:.95;letter-spacing:-.05em;margin-top:22px}}h1.sm{{font-size:150px}}
h2{{font-weight:600;font-size:88px;line-height:1.06;letter-spacing:-.035em;max-width:1500px;margin-top:20px}}
p{{font-size:48px;color:var(--text-2);margin-top:28px;max-width:1400px;line-height:1.3}}
.big{{font-weight:700;font-size:290px;line-height:1;letter-spacing:-.05em;color:var(--accent);margin-top:10px}}
.row{{display:flex;justify-content:space-between;align-items:center;margin-top:90px;font-size:38px;color:var(--text-2);border-top:1px solid rgba(255,255,255,.14);padding-top:40px}}
.url{{font:500 46px "JetBrains Mono",monospace;color:var(--text)}}
</style></head><body>{''.join(sections)}</body></html>"""


def captions_html(spec: dict) -> str:
    """Transparent 1920×1080 caption overlays, one per shot, composited in the edit (so zooms never crop them)."""
    b = spec.get("brand", {})
    acc, font = b.get("accent", "#f97316"), b.get("font", "Inter")
    secs = []
    for i, s in enumerate(spec["shots"]):
        cap = html.escape(s.get("caption", ""))
        while "*" in cap and cap.count("*") >= 2:
            cap = cap.replace("*", "<b>", 1).replace("*", "</b>", 1)
        secs.append(f'<section class="card overlay" id="cap{i}"><div class="pill">{cap}</div></section>' if cap else
                    f'<section class="card overlay" id="cap{i}"></section>')
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@500;600;700&display=swap" rel="stylesheet">
<style>*{{margin:0;box-sizing:border-box}}html,body{{background:transparent}}
.card{{width:1920px;height:1080px;position:relative;font-family:"{font}","Segoe UI",system-ui,sans-serif}}
.pill{{position:absolute;left:50%;bottom:70px;transform:translateX(-50%);max-width:1500px;padding:20px 36px;border-radius:20px;
background:rgba(10,10,12,.9);border:1px solid rgba(255,255,255,.14);color:#fff;font-weight:600;font-size:40px;line-height:1.25;
letter-spacing:-.01em;box-shadow:0 24px 60px rgba(0,0,0,.45);white-space:nowrap}}
.pill b{{color:{acc}}}</style></head><body>{''.join(secs)}</body></html>"""


# ---------------------------------------------------------------- audio
def make_music(path: Path, secs: float):
    """A soft, royalty-free 4-chord pad (Am–F–C–G) generated with ffmpeg, so every video has music."""
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (130.81, 196.0, 261.63), (196.0, 246.94, 293.66)]
    seg = max(2.0, secs / 4)
    inputs, labels = [], []
    for i, (a, b, c) in enumerate(chords):
        expr = (f"(sin(2*PI*{a}*t)+0.8*sin(2*PI*{b}*t)+0.7*sin(2*PI*{c}*t)+0.35*sin(2*PI*{a/2}*t))"
                f"*(0.55+0.45*sin(2*PI*0.25*t))*min(1\\,t/0.6)*min(1\\,({seg:.2f}-t)/0.6)*0.11")
        inputs += ["-f", "lavfi", "-i", f"aevalsrc={expr}:s=48000:d={seg:.2f}"]
        labels.append(f"[{i}:a]")
    filt = (f"{''.join(labels)}concat=n=4:v=0:a=1,aloop=loop=-1:size={int(seg * 4 * 48000)},atrim=0:{secs:.2f},"
            f"lowpass=f=2200,aecho=0.8:0.7:120|240:0.25|0.15,pan=stereo|c0=c0|c1=c0,"
            f"afade=t=in:d=1.2,afade=t=out:st={max(0, secs - 2):.2f}:d=2,volume=2.2[a]")
    run(["ffmpeg", "-y", *inputs, "-filter_complex", filt, "-map", "[a]", "-c:a", "pcm_s16le", str(path)])


# ---------------------------------------------------------------- edit
VF = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"


def card_clip(png: Path, secs: float, out: Path):
    frames = int(secs * FPS)
    zp = f"zoompan=z='1+0.035*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}"
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-t", f"{secs:.2f}", "-i", str(png),
         "-vf", f"scale={W * 2}:{H * 2},{zp},format=yuv420p", "-frames:v", str(frames), "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(out)])


def shot_clip(src: Path, a: float, b: float, out: Path, hero: dict | None, caption_png: Path | None = None):
    vf = VF + f",fps={FPS}"
    if hero:
        frames = max(1, int((b - a) * FPS))
        cx = hero["x"] + hero["w"] / 2
        cy = hero["y"] + hero["h"] / 2
        zmax = 1.22
        vf += (f",zoompan=z='1+{zmax - 1:.2f}*min(1\\,on/{frames}*1.4)':"
               f"x='max(0\\,min(iw-iw/zoom\\,{cx:.0f}-iw/zoom/2))':y='max(0\\,min(ih-ih/zoom\\,{cy:.0f}-ih/zoom/2))':d=1:s={W}x{H}:fps={FPS}")
    if caption_png and caption_png.exists():
        cmd = ["ffmpeg", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(src), "-loop", "1", "-i", str(caption_png),
               "-filter_complex", f"[0:v]{vf}[v];[1:v]format=rgba,fade=t=in:st=0.25:d=0.35:alpha=1[c];[v][c]overlay=0:0:shortest=1,format=yuv420p[o]",
               "-map", "[o]"]
    else:
        cmd = ["ffmpeg", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(src), "-vf", vf + ",format=yuv420p"]
    run(cmd + ["-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(out)])


def join(clips: list[Path], out: Path, music: Path | None, voiceover: Path | None, tmp: Path) -> float:
    durs = [ffprobe_dur(c) for c in clips]
    fade = min(FADE, *(d / 3 for d in durs))
    total = sum(durs) - fade * (len(clips) - 1)
    inputs, filt = [], []
    for c in clips:
        inputs += ["-i", str(c)]
    last, t = "[0:v]", durs[0]
    for i in range(1, len(clips)):
        filt.append(f"{last}[{i}:v]xfade=transition=fade:duration={fade:.3f}:offset={t - fade:.3f}[v{i}]")
        last, t = f"[v{i}]", t + durs[i] - fade
    filt.append(f"{last}format=yuv420p[vout]")
    n = len(clips)
    mix = []
    if voiceover:
        inputs += ["-i", str(voiceover)]
        filt.append(f"[{n}:a]apad[vo]")
        mix.append("[vo]")
        n += 1
    if music:
        inputs += ["-i", str(music)]
        vol = 0.45 if voiceover else 1.0
        filt.append(f"[{n}:a]volume={vol},apad[mu]")
        mix.append("[mu]")
        n += 1
    if not mix:
        inputs += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
        filt.append(f"[{n}:a]anull[aout]")
    elif len(mix) == 1:
        filt.append(f"{mix[0]}atrim=0:{total:.3f}[aout]")
    else:
        filt.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=longest:normalize=0,atrim=0:{total:.3f}[aout]")
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[vout]", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", str(FPS), "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", f"{total:.3f}", str(out)], cwd=tmp)
    return total


def fit(timeline: list[dict], avail: float) -> list[tuple[float, float]]:
    """Trim each shot to fit the time available, keeping the END of every shot (that's where results appear)."""
    lens = [s["end"] - s["start"] for s in timeline]
    total = sum(lens)
    if total <= avail:
        return [(s["start"], s["end"]) for s in timeline]
    floor = 1.8
    scale = max(0.0, (avail - floor * len(lens)) / max(0.01, total - floor * len(lens)))
    out = []
    for s, ln in zip(timeline, lens):
        keep = min(ln, floor + (ln - floor) * scale) if ln > floor else ln
        if s.get("hero"):
            keep = min(ln, max(keep, 3.0))
        out.append((s["end"] - keep, s["end"]))
    return out


def ensure_tools(root: Path) -> Path:
    tools = root / ".hackathon" / "video-tools"
    tools.mkdir(parents=True, exist_ok=True)
    shutil.copy(ENGINE, tools / "video-engine.mjs")
    if not (tools / "node_modules" / "playwright-core").exists():
        print("Installing the recorder (playwright-core) into .hackathon/video-tools/ …")
        (tools / "package.json").write_text('{"name":"hackathon-video-tools","private":true,"type":"module"}\n', encoding="utf-8")
        run([which("npm"), "install", "playwright-core@1", "--no-audit", "--no-fund", "--loglevel=error"], cwd=tools)
    gi = root / ".gitignore"
    text = gi.read_text(encoding="utf-8") if gi.exists() else ""
    if ".hackathon/video-tools" not in text:
        gi.write_text(text + ("" if text.endswith("\n") or not text else "\n") + ".hackathon/video-tools/\nvideo/raw/\n", encoding="utf-8")
    return tools


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--shots", default="video/shots.json")
    ap.add_argument("--out", default="submission/demo.mp4")
    ap.add_argument("--target", type=float)
    ap.add_argument("--limit", type=float)
    ap.add_argument("--music", default="auto")
    ap.add_argument("--voiceover")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--keep", action="store_true", help="keep intermediate clips in video/build/")
    ap.add_argument("--skip-record", action="store_true", help="re-edit the last recording without recording again")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    shots_path = (root / args.shots) if not Path(args.shots).is_absolute() else Path(args.shots)
    spec = None
    if shots_path.exists():
        spec = json.loads(shots_path.read_text(encoding="utf-8"))
    if args.check:
        return 0 if check(root, spec, shots_path.parent) else 1
    if spec is None:
        print(f"No shot list at {shots_path}. Ask the demo-video-producer agent to write it, or copy "
              f"{HERE.parent / 'assets' / 'video' / 'shots.example.json'}")
        return 2
    target = args.target or float(spec.get("target_seconds", 30))
    errs = validate(spec)
    hard = [e for e in errs if "hero" not in e]
    for e in errs:
        print(("✗ " if e in hard else "! ") + e)
    if hard:
        return 2
    est, avail = plan(spec, target)
    print(f"Plan: {len(est)} shots, ~{sum(est):.1f}s of recording for {avail:.1f}s of screen time (target {target:g}s)")
    for i, (s, t) in enumerate(zip(spec["shots"], est), 1):
        print(f"  {i}. ~{t:4.1f}s  {'★ ' if s.get('hero') else ''}{s.get('caption', '')}")
    if sum(est) > avail * 1.6:
        print("! Much more recording than screen time: shots will be trimmed hard. Cut a shot or shorten holds.")
    if args.plan:
        return 0
    if not check(root, spec, shots_path.parent):
        return 1

    video = root / "video"
    raw = video / "raw"
    tools = ensure_tools(root)
    node = which("node")
    if not args.skip_record or not (raw / "timeline.json").exists():
        print("Recording …")
        env_ff = dict(os.environ, FFMPEG=which("ffmpeg") or "ffmpeg")
        p = subprocess.run([node, str(tools / "video-engine.mjs"), "record", str(shots_path), str(raw)], cwd=tools, env=env_ff)
        if p.returncode not in (0, 1):
            print("The recorder couldn't start a browser. Run with --check for the fix.")
    tl = json.loads((raw / "timeline.json").read_text(encoding="utf-8")) if (raw / "timeline.json").exists() else None
    if not tl or tl.get("failed"):
        print(f"Recording failed: {(tl or {}).get('failed', 'no timeline written')}")
        print("Fix the selector in shots.json and run again. Tip: open the app, right-click the element → Inspect, "
              "and prefer text=Visible label or [data-testid=…].")
        return 1
    cards_dir = video / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    (video / "cards.html").write_text(cards_html(spec), encoding="utf-8")
    run([node, str(tools / "video-engine.mjs"), "cards", str(video / "cards.html"), str(cards_dir)], cwd=tools)
    if not spec.get("page_captions"):
        (video / "captions.html").write_text(captions_html(spec), encoding="utf-8")
        run([node, str(tools / "video-engine.mjs"), "cards", str(video / "captions.html"), str(cards_dir)], cwd=tools)

    out = (root / args.out) if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) if not args.keep else (video / "build")
        tmp.mkdir(parents=True, exist_ok=True)
        clips = []
        for name, secs in card_times(spec):
            clips.append(tmp / f"c_{name}.mp4")
            card_clip(cards_dir / f"{name}.png", secs, clips[-1])
        cuts = fit(tl["shots"], avail)
        for i, ((a, b), s) in enumerate(zip(cuts, tl["shots"])):
            clips.append(tmp / f"s_{i:02d}.mp4")
            shot_clip(raw / "demo.mp4", a, b, clips[-1], s.get("hero"),
                      None if spec.get("page_captions") else cards_dir / f"cap{s['i']}.png")
        clips.append(tmp / "c_end.mp4")
        card_clip(cards_dir / "end.png", 3.0, clips[-1])
        est_total = sum(ffprobe_dur(c) for c in clips) - FADE * (len(clips) - 1)
        music = None
        if args.music == "auto":
            music = tmp / "music.wav"
            make_music(music, est_total)
        elif args.music not in ("none", ""):
            music = Path(args.music).resolve()
        vo = Path(args.voiceover).resolve() if args.voiceover else None
        join(clips, out.resolve(), music, vo, tmp)
    shutil.copy(cards_dir / "title.png", out.parent / "thumbnail.png")
    final = ffprobe_dur(out)
    print(f"Saved {out.relative_to(root) if out.is_relative_to(root) else out}: {final:.1f}s · {out.stat().st_size / 1e6:.1f} MB · "
          f"{len(clips)} clips · 1920×1080 · music: {'generated pad' if args.music == 'auto' else args.music}")
    print(f"Thumbnail: {out.parent / 'thumbnail.png'}")
    limit = args.limit or spec.get("limit_seconds")
    if limit and final > float(limit):
        print(f"OVER the {float(limit):g}s limit by {final - float(limit):.1f}s. Lower --target or cut a shot.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
