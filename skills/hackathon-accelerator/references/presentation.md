# Presentations

How to build a pitch deck that fits the time slot, answers judges' questions before they ask, and looks like the product.

## 1. Find out the format first
Check `HACKATHON_BRIEF.md` (or ask the user) for:
- **Slot length** (2, 3 or 5 minutes are common), and whether Q&A is included or separate.
- **Format:** live pitch with a live demo, live pitch with a recorded video, or video-only (async judging).
- Whether slides are submitted as a file (PDF, link) as well as presented.

Then generate the time plan, and paste its table into `submission/PITCH.md`:
```bash
python3 <skill-dir>/scripts/time_plan.py --minutes 3 --format live-demo --qa-minutes 2
```
Formats: `live-demo`, `video-demo`, `video-only`. The plan budgets seconds, spoken words (at 140 wpm) and slides per segment, and keeps a 10% buffer. After writing the script, check it with `--check <project-root>`.

## 2. Rules for short slots (3 minutes or less)
- **The demo is at least half the time.** Start it before the 40-second mark.
- **6 main slides at most:** hook/title, problem, solution, [demo], how it works, impact + close. No agenda slide, and no team slide at the start (the team goes on the close slide).
- **One idea per slide,** 3 short lines at most, and big type (body text 28px+ on a 1600×900 slide).
- **Numbers on slides must be real,** with the sample size said out loud ("9 testers, 5 days").
- **Rehearse with the deck's built-in timer** (press `T`) at least 3 times, and cut words until it fits with ~15 seconds to spare.

## 3. Answer the questions before they're asked
Judges ask the same handful of questions. Handle them in two places:
1. **Inside the pitch** (costs no extra time): the "how it works" slide answers "is it real?", the impact slide answers "does it matter?", and saying "everything you saw was built this weekend" answers "what did you build?".
2. **Appendix slides after the close** (2–4 slides, one question each, with a short, specific answer). Jump to them during Q&A. Pick the questions most likely for *this* project:
   - What happens when the AI / model is wrong?
   - What did you build during the event vs before?
   - How is it different from <closest competitor>?
   - Who's the first user, and how do you reach them?
   - What does it cost to run, and how does it scale?
   - How do you handle privacy or user data?
   - A sponsor-specific question for each targeted prize ("why did you use <sponsor> instead of X?")

Write 30-second spoken answers for all of them in the Judge Q&A table in `PITCH.md`.

## 4. Building the deck

### Option A: Canva (when connected)
If `PROGRESS.md` → Environment shows a Canva MCP server, use it.
1. List the Canva tools available in this session, and read their descriptions. Tool names vary by version, so never guess them.
2. Create a presentation design from the `SLIDES.md` outline (title, ≤3 lines and speaker notes per slide), using the style from `design/DIRECTION.md` (colors, fonts) and the product's real screenshots.
3. Export it as PDF (for submission) and keep the Canva link (for editing). Record both in `PITCH.md`.
4. Check the exported PDF page by page. Fix text overflow and any slide with more than 3 lines.

**To connect Canva** (tell the user, it takes a minute and needs a Canva account):
```bash
claude mcp add --transport http Canva https://mcp.canva.com/mcp
```
Then restart Claude Code, run `/mcp`, choose Canva and sign in. Don't block on this: if Canva isn't connected, use Option B and mention Canva as an upgrade.

### Option B: the HTML deck (always works, offline)
Copy `<skill-dir>/assets/templates/deck/deck.html` to `submission/deck.html` and replace the sample content (a piano-practice app called "Cadence") with the project's.
- Each `<section class="slide" data-seconds="…">` takes its budget from the time plan. The built-in timer (`T`) turns red when a slide or the whole talk runs long.
- Restyle it by changing the `:root` tokens to match `design/DIRECTION.md`. The deck should look like the product.
- Use real product screenshots (`<img>` inside a `.shot` frame) instead of the sample's CSS mock.
- Speaker notes go in `<aside class="n">` (press `N` to show them).
- Appendix slides use `data-appendix` (they're excluded from the timer and progress bar).
- **PDF:** open the deck in Chrome, press `P` and choose "Save as PDF" (one slide per page, 16:9, with background graphics on).
- Present with `F` (fullscreen) and the arrow keys. A clicker that sends arrow keys works.

### Option C: PowerPoint or Google Slides
If the event requires .pptx or Google Slides, build the outline in `SLIDES.md`, then produce the file with the available tools (a pptx skill, or a Slides connector). Keep the same slide structure and timing.

## 5. Slide checklist
- [ ] Fits the time plan with a buffer (timer-tested)
- [ ] The demo starts before 40 seconds in a 3-minute slot
- [ ] Every claim matches `PROGRESS.md` (VERIFIED only), and `validate_submission.py` passes
- [ ] The style matches the product (same fonts, accent, radius)
- [ ] Real screenshots, not mockups
- [ ] Team names and roles on the close slide, with a URL or QR
- [ ] 2–4 appendix slides for likely questions
- [ ] Exported PDF checked page by page
- [ ] A backup demo video is ready in case the live demo fails
