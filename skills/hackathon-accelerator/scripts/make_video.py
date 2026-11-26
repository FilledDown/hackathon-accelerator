#!/usr/bin/env python3
"""Stitch cards and screen recordings into a judge-ready demo video (1080p H.264 MP4) with ffmpeg.

Usage:
  make_video.py PART [PART ...] --out submission/demo.mp4 [--limit 180] [--fade 0.4]
                [--voiceover vo.mp3] [--music music.mp3 --music-volume 0.12] [--captions demo.srt]

PART is a file with an optional length or trim:
  video/cards/title.png:3          an image shown for 3 seconds (images default to 3s)
  video/raw/demo.webm              a whole recording
  video/raw/demo.webm@2.5-41       a recording trimmed to 2.5s → 41s
Parts are joined with crossfades, scaled/padded to 1920×1080 at 30 fps. Audio: optional voiceover (full volume)
and/or music (looped, ducked to --music-volume, faded out at the end); otherwise a silent track so every
player and upload site accepts it. --captions burns an .srt file in (skip it if captions were recorded in).
--limit checks the final length against the event's maximum (exit code 1 if over).
Requires ffmpeg + ffprobe on PATH (Windows: winget install Gyan.FFmpeg · macOS: brew install ffmpeg).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

IMG = {".png", ".jpg", ".jpeg", ".webp"}
W, H, FPS = 1920, 1080, 30


def run(cmd, cwd=None):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{' '.join(map(str, cmd))[:400]}\n{p.stderr[-1500:]}")
    return p.stdout


def duration(path: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)])
    return float(json.loads(out)["format"]["duration"])


def parse_part(spec: str):
    m = re.match(r"^(.*?)(?:@([\d.]+)-([\d.]+))?(?::([\d.]+))?$", spec)
    path, a, b, secs = m.group(1), m.group(2), m.group(3), m.group(4)
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Part not found: {path}")
    return p, (float(a) if a else None), (float(b) if b else None), (float(secs) if secs else None)


def normalize(part, idx: int, tmp: Path) -> Path:
    p, a, b, secs = part
    out = tmp / f"part{idx:02d}.mp4"
    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS},format=yuv420p,setsar=1"
    if p.suffix.lower() in IMG:
        cmd = ["ffmpeg", "-y", "-loop", "1", "-t", str(secs or 3), "-i", str(p)]
    else:
        cmd = ["ffmpeg", "-y"] + (["-ss", str(a)] if a is not None else []) + (["-to", str(b)] if b is not None else []) + ["-i", str(p)]
    cmd += ["-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(out)]
    run(cmd)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("parts", nargs="+")
    ap.add_argument("--out", default="submission/demo.mp4")
    ap.add_argument("--fade", type=float, default=0.4)
    ap.add_argument("--limit", type=float, help="max allowed length in seconds (e.g. 180 for 3 minutes)")
    ap.add_argument("--voiceover")
    ap.add_argument("--music")
    ap.add_argument("--music-volume", type=float, default=0.12)
    ap.add_argument("--captions", help=".srt file to burn in")
    ap.add_argument("--crf", type=int, default=20)
    args = ap.parse_args()

    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print("ffmpeg/ffprobe not found. Install: Windows `winget install Gyan.FFmpeg`, macOS `brew install ffmpeg`, Linux `sudo apt install ffmpeg`.", file=sys.stderr)
        return 2
    parts = [parse_part(s) for s in args.parts]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        segs = [normalize(p, i, tmp) for i, p in enumerate(parts)]
        durs = [duration(s) for s in segs]
        fade = min(args.fade, *(d / 3 for d in durs)) if len(segs) > 1 else 0
        total = sum(durs) - fade * (len(segs) - 1)

        # video: chain of xfades
        inputs = []
        for s in segs:
            inputs += ["-i", str(s)]
        filt, last, t = [], "[0:v]", durs[0]
        for i in range(1, len(segs)):
            lab = f"[v{i}]"
            filt.append(f"{last}[{i}:v]xfade=transition=fade:duration={fade:.3f}:offset={t - fade:.3f}{lab}")
            last, t = lab, t + durs[i] - fade
        if args.captions:
            shutil.copy(args.captions, tmp / "captions.srt")   # relative name avoids Windows path escaping
            filt.append(f"{last}subtitles=captions.srt:force_style='FontName=Inter,FontSize=22,PrimaryColour=&H00FFFFFF,BackColour=&H99000000,BorderStyle=4,Outline=0,MarginV=60'[vc]")
            last = "[vc]"
        filt.append(f"{last}format=yuv420p[vout]")

        # audio
        n = len(segs)
        amap = []
        if args.voiceover or args.music:
            mix = []
            if args.voiceover:
                inputs += ["-i", str(Path(args.voiceover).resolve())]
                filt.append(f"[{n}:a]apad[vo]")
                mix.append("[vo]")
                n += 1
            if args.music:
                inputs += ["-stream_loop", "-1", "-i", str(Path(args.music).resolve())]
                filt.append(f"[{n}:a]volume={args.music_volume},afade=t=out:st={max(0, total - 2):.2f}:d=2[mu]")
                mix.append("[mu]")
                n += 1
            filt.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=longest:normalize=0,atrim=0:{total:.3f}[aout]" if len(mix) > 1
                        else f"{mix[0]}atrim=0:{total:.3f}[aout]")
        else:
            inputs += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
            filt.append(f"[{n}:a]anull[aout]")
        amap = ["-map", "[aout]"]

        cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[vout]", *amap,
               "-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf), "-r", str(FPS), "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", f"{total:.3f}", str(out.resolve())]
        run(cmd, cwd=tmp)

    final = duration(out)
    mb = out.stat().st_size / 1e6
    mm, ss = divmod(final, 60)
    print(f"Saved {out}: {int(mm)}:{ss:04.1f} · {mb:.1f} MB · {len(parts)} parts · {W}×{H} @ {FPS} fps")
    if args.limit:
        if final > args.limit:
            print(f"OVER the {args.limit:g}s limit by {final - args.limit:.1f}s. Trim a recording (file.webm@start-end) or shorten card times.")
            return 1
        print(f"Within the {args.limit:g}s limit ({args.limit - final:.1f}s to spare).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
