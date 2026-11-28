# Demo Video

Two deliverables, both made by the `demo-video-producer` agent:
1. **A finished ~30-second demo** of the real app: recorded, edited, with captions, cards and music. One command.
2. **The full demo script** for the event's actual limit (often 2–3 min), in `submission/DEMO_SCRIPT.md`. Use it to record a longer cut or to narrate live.

## 1. The one command
```bash
python3 <skill-dir>/scripts/demo_video.py . --check     # what's installed, exact fix commands for your OS
python3 <skill-dir>/scripts/demo_video.py . --plan      # validate video/shots.json and estimate timing
python3 <skill-dir>/scripts/demo_video.py .             # record → edit → submission/demo.mp4 + thumbnail.png
```
Windows: use `python` (or `py -3`) instead of `python3`. Start the app first (`npm run dev`) unless `url` points at a local `.html` file.

**Requirements:** Node 18+, ffmpeg (`winget install Gyan.FFmpeg` / `brew install ffmpeg`) and Chrome or Edge (Edge is built into Windows). The recorder (`playwright-core`) installs itself into `.hackathon/video-tools/` the first time, so your `package.json` stays clean. Frames are captured through Chrome DevTools and encoded with your own ffmpeg, so there's no Playwright browser or ffmpeg download (those are often blocked on school and work networks).

**What the edit does:** hook card (a real number) → title card → each shot as its own clip, trimmed to fit the target while keeping the end of the shot (where results appear) → a slow push-in on the hero shot → captions composited on top (so zooms never crop them) → gentle zoom on cards → 0.4 s crossfades → a generated royalty-free music pad with fades → end card → H.264/AAC, fast start, 1080p30. Re-edit without recording again: `--skip-record`. Other options: `--target 45`, `--music none|file.mp3`, `--voiceover vo.mp3`, `--keep` (keeps clips in `video/build/`).

## 2. shots.json
```json
{
  "url": "http://localhost:3000",
  "target_seconds": 30,
  "limit_seconds": 35,
  "zoom": 1.25,
  "brand": { "name": "Cadence", "tagline": "Practice with intention, not guilt.", "accent": "#f97316", "bg": "#0b0b0d", "font": "Inter" },
  "hook":  { "kicker": "The problem", "big": "73%", "text": "of music students practice by just playing pieces through." },
  "end":   { "url": "cadence.app", "team": "Team Fermata", "event": "PolarHacks 2026" },
  "shots": [
    { "caption": "Add what you're learning in *seconds*",
      "actions": [ { "type": ["#piece", "Chopin · Nocturne Op. 9 No. 2"] }, { "click": "text=Add piece" } ], "hold": 1.0 },
    { "caption": "Play a run-through. Cadence *listens*",
      "actions": [ { "click": "#record" }, { "waitFor": "#result.on" } ], "hold": 0.6 },
    { "caption": "The rushed bars *light up*, with a plan to fix them",
      "actions": [ { "spotlight": "#result" } ], "hold": 3.4, "hero": true }
  ]
}
```
| Action | Value | Does |
|---|---|---|
| `goto` | `"/path"` or URL | Open a page (relative to `url`) |
| `click` · `hover` · `move` | selector | Glide the visible cursor there (eased), click with a ripple |
| `type` | `[selector, text]` | Click the field and type like a person |
| `fill` | `[selector, text]` | Set a value instantly (long text) |
| `press` | `"Enter"` | Press a key |
| `drag` | `[selector, dx, dy]` | Drag (sliders, canvases) |
| `scroll` | pixels | Smooth scroll |
| `wait` | ms | Pause |
| `waitFor` | selector | Wait until something appears (slow AI calls, up to 30 s) |
| `spotlight` · `unspotlight` | selector | Dim everything except the hero element |

**Rules for a good 30 s cut:**
- 4–6 shots, one idea each. Caption ≤ 60 characters, present tense, one `*accent*` word.
- Exactly one `"hero": true` shot: the wow moment. It gets the push-in and at least 3 s.
- `zoom` 1.25–1.5 makes small UIs readable (it records like a laptop screen and scales up crisply).
- Selectors: prefer `text=Visible label`, `#id`, `[data-testid=…]`. Check them in the source before recording.
- Hook number: from `research/` with a source, or leave `hook` out. Never invent one.
- Seed demo data and use demo mode (`demo-engineering.md`) so every take looks the same. Cache slow AI responses for recording if needed, but never fake the result itself.

## 3. The full script (for the real limit)
`time_plan.py --minutes 2 --format video-only` gives the budget. Structure judges respond to (often skimming, often muted):
1. **Cold open (0–8 s):** the problem in one shot or one striking number. No logo intro.
2. **Name + promise (~5 s).**
3. **Hero moment by ~30 s:** show the magic first, explain after.
4. **Core loop (~40%):** the real app, one continuous journey, captioned.
5. **How it works (~12%):** architecture, the hard part, sponsor tech.
6. **Impact + close (~18%):** a real number, then name, URL, team (≥ 3 s).

Write it in `submission/DEMO_SCRIPT.md` → "Video script" as a table: time | on screen | caption | narration (~140 wpm). For the long cut, make extra `shots.json` files (`--shots video/long.json --target 120`), or record clips manually (OBS, Win+G, Cmd+Shift+5, phone) and stitch with `make_video.py`:
```bash
python3 <skill-dir>/scripts/make_video.py video/cards/title.png:3 clip1.mp4@2-40 video/cards/end.png:4 --music music.mp3 --out submission/demo-long.mp4 --limit 180
```

## 4. Narration (optional)
One teammate reads the script in a quiet room (a phone voice memo is fine) → `--voiceover vo.mp3`. The music ducks automatically. Captions alone are fine too: many judges watch muted. Never use a cloned voice of a real person.

## 5. Check before you say it's done
- [ ] Watched it (or extracted 6 frames and looked): text readable, captions not cut off, hero visible
- [ ] Within `limit_seconds`
- [ ] Every feature shown is VERIFIED in `PROGRESS.md`
- [ ] Uploaded (unlisted is fine), linked in `DEVPOST.md` and `README.md`, `thumbnail.png` used as the cover

## Troubleshooting
| Symptom | Fix |
|---|---|
| `✗ browser` | Install Chrome, or set `CHROME_PATH` to chrome.exe/msedge.exe |
| `FAILED: shot 2, click "text=Plan"` | The selector didn't match. Check the exact visible text, or add `data-testid` |
| App not reachable | Start it first and use the URL it prints |
| Video too long | Lower `hold`s, remove a shot, or `--target 25` (shots are trimmed from the start, keeping results) |
| Blank or white frames at the start | Add `{ "waitFor": "main" }` as the first action |
