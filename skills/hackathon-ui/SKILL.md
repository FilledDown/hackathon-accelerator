---
name: hackathon-ui
description: "Build polished, non-generic product UI with animations, licensed images and states built in by default: 10 style directions, tokens, React or vanilla, anti-slop audit. Use for any UI, page, screen or frontend request."
---

# Hackathon UI

Judges decide in about 30 seconds whether a project feels real. A polished, *specific* interface is the quickest way to earn that. Generic AI output, like purple gradients, three identical icon cards and centered everything, signals "weekend project" before anyone reads the copy.

This skill gives you a design process, 10 concrete style directions, and the craft details that separate a real product from a template. The style files are **reverse-engineered patterns** from the sites listed in each one: layout, type, color logic, spacing, motion. They are **not** copies. Never reuse another company's logo, brand name, illustrations, photos or exact copy. Build an original product in that design language.

**Paths:** `<ui-dir>` is this skill's folder (the base directory shown when it loaded). The files below are relative to it.

## Defaults: always on, never wait to be asked
Every UI this skill produces gets all of these, even when the request is just "build a landing page":
- one chosen style direction, with tokens and no hardcoded colors;
- **animations on every interactive component**: buttons, links, cards, images, tabs, toggles, inputs, plus an entrance stagger and a staged hero moment (`references/animations.md`);
- **real licensed images** wherever the page shows visual subjects (hero, people, places, food, objects), fetched with `scripts/fetch_images.py` and credited. Skip photos only for pure tool UIs where the product's own screens are the visual;
- loading, empty and error states on every data view, realistic domain copy, a mobile layout at 390 wide, visible focus styles and `prefers-reduced-motion`;
- screenshots at 1440 and 390 plus `ui_audit.py`, fixed before you show it.

If the user explicitly says not to (for example "no photos"), follow that. Otherwise don't ask. Mention what you added in one line.

## The process (follow it in order)

### 1. Understand the product and the audience (2 minutes)
Answer these three questions before you write any CSS:
- Who uses this, and how do they feel when they open it? (A stressed on-call engineer is different from a florist browsing.)
- What is the single hero moment the demo must show?
- Is it mostly a **landing page**, an **app**, or **both**? Hackathon judges usually see the app, and the Devpost page shows screenshots.

Almost every hackathon project is a **product**: an app or site that does one thing well. It's rarely a dashboard. Design the product's core loop first (input → work → result) using the "Product screens" section of `references/components.md`. The `data-dashboard` style is a reference for the one data view a product might have, not a default.

### 2. Pick ONE style direction
Read `references/styles/index.md`, choose the direction that fits the audience, and read **only that style file**. Write the choice into `design/DIRECTION.md` along with a one-line reason. Combining two directions is fine only if one clearly leads ("Precision Dark, with the data density of Dashboard").

Look before you choose: Read `assets/showcase/screenshots/<style>.png` for the candidates (each is a 1440×900 render of that style's demo page). If two directions fit equally well, ask the user to pick and name the screenshots. The `.html` demo pages open in any browser.

### 3. Tokens before components
Create the design tokens file first (CSS variables, plus Tailwind theme mapping if the project uses Tailwind). Copy the token block from the style file and adapt the accent color to the product. **Never hardcode a hex value in a component.** Every color, radius, shadow and font comes from a token. This one rule removes most of the inconsistency in AI-generated UI.

Fonts: use the free fonts named in the style file (all are OFL or free-licensed and available on Google Fonts or Fontsource). Load at most 2 families plus 1 mono.

### 4. Build the demo path screens, starting with the most important
Order: the app's hero screen (the differentiator moment) → the landing hero (it doubles as the Devpost cover image) → the other screens on the demo path. Use the recipes in `references/components.md`. Fill every screen with realistic, domain-specific data, never "Lorem ipsum", "John Doe" or "Item 1".

The working demo page for your style (`assets/showcase/<style>.html`) is a reference implementation. Read it to see how the tokens, spacing and details fit together, then build the real thing in the project's framework.

### 5. Add images, states and motion
- **Images (default on):** wherever the page shows visual subjects (hero, product context, places, food, people as generic subjects), follow `references/images.md`. Pull licensed images with `scripts/fetch_images.py`, which records credits automatically, and treat them consistently. The product's own UI is still the best hero image.
- **States:** every data view on the demo path needs loading (skeleton), empty (helpful message plus action) and error (what happened and what to do) states.
- **Motion:** animate every interactive component with the recipes in `references/animations.md`: buttons, links, cards, images, text, tabs, toggles and feedback. Use CSS, Motion for React, or anime.js for vanilla. Stage the hero moment with `references/motion.md`. Respect `prefers-reduced-motion`. `assets/showcase/motion-gallery.html` shows all of it working.

### 6. Verify by looking, not by assuming
- **Screenshot it** at 1440×900 and 390×844 (mobile). With Playwright available: `npx playwright screenshot --viewport-size=1440,900 http://localhost:3000 shot-desktop.png`. Otherwise use a browser MCP or tool. Then Read the PNG and critique it like a judge.
- **Run the audit:** `python3 <ui-dir>/scripts/ui_audit.py <src-dir>` (use `python` on Windows). It flags hardcoded colors, too many font sizes, AI-slop patterns, missing focus styles, placeholder copy and missing alt text. Fix every error. Fix warnings unless there's a reason not to.
- Run the checklist in `references/anti-slop.md`.

### 7. One polish pass
Fix the top 5 visual issues from the screenshot critique: alignment, spacing rhythm, contrast, typographic hierarchy, and anything that looks default. Then stop polishing and go back to the demo. Polish has diminishing returns, and a working demo matters more.

## Time budgets (hackathon)
| Time left | UI ambition |
|---|---|
| < 12 h | One style, tokens, 2–3 polished screens, skeletons. No custom illustration, no 3D. |
| 12–36 h | Add the landing page, motion pass, empty states, dark/light only if trivial. |
| 36 h + | Add a signature interaction (command palette, live preview, animated chart), and maybe light 3D or video in the hero. |

The `immersive` direction (WebGL/3D) is high risk: only pick it with more than 36 hours left, someone on the team who has done it before, and a static fallback.

## Using other design skills
If the environment has **UI/UX Pro Max**, **Taste**, **frontend-design** or similar skills installed (check `PROGRESS.md` → Environment), read their SKILL.md too. They work well for palette and font exploration. This skill still owns the direction choice, the token-first rule and the anti-slop audit, so the result stays consistent. If one of them conflicts with the chosen style file, the style file wins for this project.

## Prompts you can hand to a builder agent
Use these when delegating (fill the brackets):
- *"Build the [screen] for [product] in the [style] direction from the hackathon-ui skill. Read `<ui-dir>/references/styles/[style].md` and `<ui-dir>/assets/showcase/[style].html` first. Use only the tokens in [tokens file]. Realistic data about [domain]. Include loading, empty and error states. Screenshot at 1440 and 390 wide and fix what looks off."*
- *"Audit [src dir] with `ui_audit.py` and the anti-slop checklist. Fix all errors and the 5 most visible warnings. Don't change behavior."*
- *"Make the [hero moment] land: build-up, reveal, visible work happening. Follow `references/motion.md`. Under 10 s of waiting."*

## Reference index
| File | Read when |
|---|---|
| `references/styles/index.md` | Step 2: choosing a direction |
| `references/styles/<style>.md` | After choosing, read only that one |
| `references/foundations.md` | Building tokens, type scale, spacing, color, layout grid |
| `references/components.md` | Building any screen: product screens (onboarding, input→result, chat, drop zone, mobile shell, before/after), marketing sections, app shell, states |
| `references/motion.md` | Timing principles, curves, the hero moment |
| `references/animations.md` | Animating buttons, links, cards, images, text, controls; React Bits, Kokonut UI, anime.js, Motion, ECharts |
| `references/images.md` | Finding, licensing, optimizing and styling photos |
| `assets/showcase/motion-gallery.html` | Every component animation, working |
| `scripts/fetch_images.py` | Download licensed images and write credits |
| `references/anti-slop.md` | Before showing anything to the user; Phase 5 and 6 reviews |
| `references/inspiration.md` | Looking for more references (Mobbin, Godly, Refero…) |
| `assets/showcase/screenshots/*.png` | Step 2: see each style before choosing |
| `assets/showcase/*.html` | A working reference page for each style |
| `scripts/ui_audit.py` | Step 6 |
