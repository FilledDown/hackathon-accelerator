# Demo Video

Many hackathons require a 2–3 minute demo video, and in async judging it's the only thing judges see. Even with a live pitch, a recorded video is your backup when Wi-Fi dies. This pipeline records your **real running app** with a visible cursor and captions, adds title and impact cards, and stitches everything into a 1080p MP4 that fits the limit.

## 1. Plan it against the clock
```bash
python3 <skill-dir>/scripts/time_plan.py --minutes 2 --format video-only
```
The structure that works for judges, who are often skimming and often muted:
1. **Cold open (0–8s):** the problem in one shot, either the "before" state or one striking number. No logo intro.
2. **Name + promise (~5s):** title card.
3. **Hero moment first (by ~30s):** show the magic result early. Explain after.
4. **Core loop (~40%):** the real app, real data, one continuous journey, captioned.
5. **How it works (~12%):** architecture card, the hard part, the sponsor tech.
6. **Impact + end card (~18%):** a real number, then the name, URL and team (≥3s).

Write the shot list in `submission/DEMO_SCRIPT.md` → "Video script": time | what's on screen | caption | narration.

## 2. Record the app (automated, repeatable)
Copy the templates into the project:
```bash
mkdir video
cp <skill-dir>/assets/video/record-demo.mjs <skill-dir>/assets/video/render-cards.mjs <skill-dir>/assets/video/cards.html video/
npm i -D playwright && npx playwright install chromium
```
Edit `STEPS` in `video/record-demo.mjs` to follow the demo script. Each step has a **caption** (what the viewer should notice, ≤70 characters), a `run(page, h)` using the helpers, and a `hold` time. Helpers:

| Helper | Does |
|---|---|
| `h.goto(url)` | Open a page and wait for it to settle |
| `h.click(sel)` / `h.hover(sel)` / `h.move(sel)` | Glide the visible cursor to an element (eased), with a click ripple |
| `h.type(sel, text)` | Type like a person (45ms per key) |
| `h.drag(sel, dx, dy)` | Drag (sliders, before/after, canvases) |
| `h.scroll(dy)` | Smooth scroll |
| `h.spotlight(sel)` / `h.unspotlight()` | Dim everything except the hero element |
| `h.caption(text)` | Change the caption (set automatically from each step) |

Run it with the app running (`npm run dev`):
```bash
DEMO_URL=http://localhost:3000 node video/record-demo.mjs        # PowerShell: $env:DEMO_URL="http://localhost:3000"; node video/record-demo.mjs
```
Output: `video/raw/demo.webm` (1920×1080, captions and cursor recorded in) plus `demo.srt`. Because the recording is a script, you can re-record in a minute after fixing a bug. That's much better than redoing a manual screen capture.

**Tips:**
- Use demo mode and seeded data (see `demo-engineering.md`), so it looks the same every run.
- Prefer stable selectors: `text=Plan my week`, `[data-testid=record]`, roles.
- Keep each step's hold long enough to read the caption (about 1s per 12 characters).
- For slow AI calls, use cached demo responses during recording, and say so if asked. Never fake the result itself.
- If something can't be automated (native app, hardware, phone), record it manually (OBS, the Win+G Xbox Game Bar, macOS Cmd+Shift+5, or a phone screen recording) and drop the clip into the stitch step.

## 3. Make the cards
Edit `video/cards.html` (title, problem, how, impact, end), using the same tokens as the product. Then:
```bash
node video/render-cards.mjs          # → video/cards/title.png, problem.png, how.png, impact.png, end.png
```

## 4. Stitch the final video
```bash
python3 <skill-dir>/scripts/make_video.py \
  video/cards/problem.png:3 video/cards/title.png:2.5 video/raw/demo.webm@1-75 video/cards/how.png:4 video/cards/impact.png:3 video/cards/end.png:4 \
  --music video/music.mp3 --out submission/demo.mp4 --limit 120
```
- Parts are joined with 0.4s crossfades, normalized to 1920×1080 at 30 fps, H.264 + AAC with fast start (uploads cleanly to YouTube and Devpost).
- `file.webm@start-end` trims a recording. `image.png:seconds` sets card time.
- `--voiceover vo.mp3` adds narration. `--music` loops the track at `--music-volume` (default 0.12) and fades it out at the end. Use royalty-free music only (YouTube Audio Library, Pixabay Music), and credit it in the description if required.
- `--captions demo.srt` burns captions in (the recorder already draws them, so you only need this for manual clips).
- `--limit` fails if the video runs over. Trim recordings rather than speeding them up.
- It needs **ffmpeg**: Windows `winget install Gyan.FFmpeg`, macOS `brew install ffmpeg`.

## 5. Narration
Best: one teammate records the narration from the script in a quiet room (phone voice memo is fine), then passes it as `--voiceover`. Read at about 140 wpm. If nobody can record, captions alone are fine: many judges watch muted anyway. Never use a cloned voice of a real person.

## 6. Polish (optional, more time)
- **Zoom on the hero moment:** record that step a second time at a smaller viewport (or use `spotlight`), and insert it as its own clip.
- **Motion-graphic intro or outro:** Remotion (React to video) makes polished animated cards. It's free for individuals and teams of up to 3 people, otherwise it needs a company license. Only worth it with time to spare.
- **Thumbnail:** export `cards/title.png` as the YouTube thumbnail.

## 7. Final checks
- [ ] Within the time limit (`--limit` passed)
- [ ] The hero moment appears by about 30–45s
- [ ] Readable at 720p (text ≥ 24px in the recording)
- [ ] Captions on every step, with no typos
- [ ] Every feature shown is VERIFIED in `PROGRESS.md`. Anything simulated is labeled or left out
- [ ] Uploaded (unlisted is fine), the link added to `DEVPOST.md` and `README.md`, and `validate_submission.py` passes
