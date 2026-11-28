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

## 2. Content: every slide earns its space
Judges skim slides while you talk. A slide that is only a title wastes the screen; a wall of text loses them. Every main slide is a **claim headline + proof**, laid out to fill the 16:9 canvas.

| Slide | Headline (a claim, not a label) | Proof that fills the space |
|---|---|---|
| Title | Name + one-line promise | The product's hero screen (real screenshot) + 3 headline numbers |
| Problem | "73% of students practice the least effective way" | One huge number with its source + 2 fact cards with sources + one real user quote |
| Solution | What it does in one sentence | Large screenshot of the result + 3 numbered features (title + one line each) |
| Demo | What they're about to see, and how fast | 3 cue cards, each with a thumbnail of the step and what to watch for |
| How it works | The technical insight | Pipeline diagram (4 boxes) + "the hard part" + stack/sponsor chips + 3 performance numbers |
| Impact / why us | Why it's different | 3 KPI cards with sample sizes + a comparison table vs the 2 real alternatives |
| Close | Name + line | Next 3 milestones + team with roles + URL/QR |
| Appendix | One per question | Top-6 Q&A grid from `submission/QA.md`, each answer ≤ 35 words with evidence |

- **Juicy, specific, sourced.** Every number has a source line (`research/`, a test you ran, or a citation). Prefer "86% of 40 recordings matched a teacher" over "highly accurate". No number? Show a screenshot or a diagram instead; never invent one.
- **Density:** 25–90 words per slide (not counting text inside screenshots), 3–6 visual elements, body text ≥ 18px on the 1600×900 canvas, headlines 44–60px. One idea per slide.
- **Short slots (≤ 3 min):** the demo is at least half the time and starts before 0:40. 6–7 main slides, no agenda or team-first slide. Rehearse with the timer (`T`) 3 times.
- **Numbers said out loud with their sample size** ("9 testers, 5 days").

### Images: never stretched, never blurry
- Capture **real 2× screenshots** of the product (browser zoom 100%, `deviceScaleFactor: 2` in Playwright, or Cmd/Win+Shift+S on a retina/high-DPI screen). Crop to the part that matters.
- In the HTML deck, every image sits in a `.frame` with a fixed aspect ratio: `<div class="frame chrome" style="--ar:16/10"><img src="img/result.png" alt="…"></div>`. `object-fit: cover` fills the frame without distortion; use `data-fit="contain"` for logos and diagrams that must not be cropped. Never set both width and height on an `<img>`.
- Match the frame ratio to the screenshot (16/10 laptop, 9/19.5 phone, 1/1 square) so cropping is minimal.
- Photos (people, places) come from `hackathon-ui/scripts/fetch_images.py` with credits; never hotlink random images.
- In Canva, insert images into frames or grids (they crop to fill) and use "Fit" for logos, never drag-stretch corners off ratio.

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

The `judge-qa-coach` agent writes the full bank with evidence-backed answers in `submission/QA.md`; its top 6 become the appendix Q&A grid.

## 4. Building the deck

### Option A: Canva (when connected): use Canva's own layouts and elements
If `PROGRESS.md` → Environment shows Canva, build the deck in Canva so it gets Canva's templates, icons, shapes, charts and frames, and the team can edit it together. Tool names vary by version, so read the Canva tool descriptions in this session first. The flow that works:
1. **Brand:** list brand kits and ask the user once whether to use one. If not, pass the colors and fonts from `design/DIRECTION.md` in the query.
2. **Assets first:** upload the real screenshots and the logo (upload-asset-from-url for public URLs, or create-upload-url to upload a local file). Keep the asset IDs. Generate or fetch extra visuals only where a screenshot can't tell the story (generate-image for an illustration, remove-background for a product cutout).
3. **Outline with content:** write the outline from section 2 with the real headline, proof, numbers + sources and speaker notes for every slide. If the session has an outline-review step, show it to the user before generating.
4. **Generate the presentation** with the outline, the brand kit and the asset IDs in order, so Canva places real screenshots into its layouts and adds matching icons, shapes and charts. Pick the strongest candidate, then create the design from it.
5. **Inspect and fix with read and edit tools:** read the design page by page. Fix text overflow, swap any generic stock image for the uploaded screenshot, replace placeholder text, keep images in frames (crop to fill, not stretch), add a chart for any slide with 3+ numbers, and make sure every slide follows the section 2 table. Ask Canva for its own design feedback if a review tool exists.
6. **Export** PDF (submission) and PPTX (backup), keep the edit link, and record both in `PITCH.md`. Check the PDF page by page.
- Alternative: build the HTML deck first, export it to PDF, then import it into Canva (import-design-from-url) to finish it with Canva elements.

**To connect Canva** (a minute, needs a Canva account), either install Canva's official plugin (in Claude Code run `/plugin`, open **Discover** and search "Canva"; it adds editing and brand-check skills) or add just the server:
```bash
claude mcp add --transport http Canva https://mcp.canva.com/mcp
```
Restart Claude Code, run `/mcp`, choose Canva and sign in. Don't block on it: without Canva, use Option B and mention Canva as an upgrade.

### Option B: the HTML deck (always works, offline)
Copy the whole `<skill-dir>/assets/templates/deck/` folder (deck.html + img/) to `submission/` and replace the sample content (a piano-practice app called "Cadence") with the project's.
- Each `<section class="slide" data-seconds="…">` takes its budget from the time plan. The built-in timer (`T`) turns red when a slide or the whole talk runs long.
- Restyle it by changing the `:root` tokens to match `design/DIRECTION.md`. The deck should look like the product.
- Use real product screenshots in `.frame` blocks (see Images above). The sample ships with screenshots in `img/`; replace them with yours.
- Run `python3 <skill-dir>/scripts/deck_audit.py submission/deck.html --minutes <n>` and fix every ✗ (empty slides, missing proof, stretched or missing images, timing).
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
- [ ] Real 2× screenshots in frames, nothing stretched or blurry
- [ ] Every main slide has a claim headline and proof; `deck_audit.py` shows no ✗
- [ ] Team names and roles on the close slide, with a URL or QR
- [ ] 2–4 appendix slides for likely questions
- [ ] Exported PDF checked page by page
- [ ] A backup demo video is ready in case the live demo fails
