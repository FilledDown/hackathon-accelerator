# Component Recipes

These are the patterns premium product sites reuse. The measurements are starting points, so adapt them to your style's tokens. Code is plain CSS with tokens, which translates directly to Tailwind classes.

## Contents
- Marketing: nav · announcement bar · hero · product frame · logo strip · bento grid · feature row · testimonial · pricing · CTA band · footer
- App: shell · sidebar · top bar · command palette · table · detail panel · form · buttons · badges · empty / loading / error · toast · charts

---

## Marketing

### Nav
- Height 56–64px. Logo left, links center or right, 1 ghost button ("Log in") plus 1 solid button ("Sign up" / "Download").
- Links at 14px, weight 500, color `--text-2`, hover `--text`. Gap 24–32px.
- Sticky with a blurred background after scroll: `background: color-mix(in oklab, var(--bg) 72%, transparent); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border);`
- Variant (Raycast): a floating rounded nav container (`radius 14–16px`, border, inset highlight) centered at max-width 1200.

### Announcement bar (optional)
32–40px tall, one line, a small pill label ("New", "Black Friday") and an arrow link. Use it for a real event only.

### Hero
Three proven layouts:
1. **Left-aligned statement + product below** (Linear, Vercel): headline 56–72px tight, a 16–18px subhead in `--text-2` at max ~560px wide, 1–2 buttons, then a full-width product frame 64–96px below.
2. **Centered poster** (Raycast, Squarespace, the music generator): short headline (≤ 6 words) centered, a large brand visual or video behind it, one CTA, a trust line under it.
3. **Split** (Stripe, Ramp): headline and CTA on the left, live product or animated visual on the right (55/45).

The headline is the product's promise in under 10 words. The subhead says how, in one sentence. The CTA verb is specific ("Generate a track", "Try the demo"), not "Get started" twice.

### Product frame (the most important hero element)
Show the *real app* inside a window:
```css
.frame { border: 1px solid var(--border); border-radius: 12px; background: var(--surface);
  box-shadow: 0 0 0 1px rgba(255,255,255,.03) inset, 0 30px 80px rgba(0,0,0,.45); overflow: hidden; }
.frame-glow { position: absolute; inset: -20% 10% auto; height: 60%; filter: blur(80px);
  background: radial-gradient(closest-side, color-mix(in oklab, var(--accent) 35%, transparent), transparent); z-index: -1; }
```
Optional: a perspective tilt (`transform: perspective(2000px) rotateX(8deg)`) that flattens on scroll, and a bottom fade into the page (`mask-image: linear-gradient(#000 70%, transparent)`).

### Logo strip
Only for real logos (integrations you actually use count: "Built with Supabase, OpenAI, Vercel"). Monochrome at 50–60% opacity, 24–28px tall, evenly spaced or as a marquee.

### Bento grid
```css
.bento { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; }
.tile { grid-column: span 2; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 24px; background: var(--surface); }
.tile.wide { grid-column: span 4; } .tile.tall { grid-row: span 2; }
```
Each tile: a short title (16–18px, 600) and one sentence (14px, `--text-2`), plus a **live UI fragment** that fills the tile, such as a real mini-chart, a notification stack, a code block or a command palette. Mix the spans, and have no more than 5–7 tiles.

### Feature row (alternating)
Text block (eyebrow label, title, 2–3 lines, a link) beside a large visual, alternating sides. Generous 120px+ between rows.

### Testimonial
One large quote (24–32px, tight tracking) with a name, role and small avatar. Only use real quotes. In a hackathon, a quote from your user interview with permission counts.

### Pricing
3 columns at most, the recommended one highlighted with an accent border (not a giant badge). Prices in tabular numerals, a feature list with checks in `--text-2`. Hackathon projects rarely need pricing, so skip it unless business viability is judged.

### CTA band
Repeat the hero promise in 4–6 words, with one button. Optionally include a small product glimpse or brand shape.

### Footer
Columns of 14px links in `--text-3`, a small logo, a status dot ("All systems normal") for dev tools, and the copyright. Keep it quiet.

---

## App

### Shell
```
┌──────────┬──────────────────────────────────────────┐
│ sidebar  │ top bar (breadcrumb · actions · search)   │
│ 240px    ├──────────────────────────────┬───────────┤
│          │ main content                  │ details   │
│          │                               │ 300px     │
└──────────┴──────────────────────────────┴───────────┘
```
The background is one step darker or lighter than the panels. The main panel can be an inset card with an 8–12px radius and a 1px border (Linear's look in the screenshot).

### Sidebar
- Workspace switcher at the top (avatar + name + chevron), then search and new-item icon buttons.
- Nav items 28–32px tall, 13–14px text, 16px icons, `--radius-sm` hover fill. The active item gets a subtle fill, not a bright accent block.
- Section labels 11–12px in `--text-3` ("Workspace", "Favorites") with collapsible chevrons.

### Top bar
44–52px tall: breadcrumb or item title (with ID in mono, e.g. `DRV-8852`), quiet icon buttons on the right, and a pager ("1 / 84 ↑ ↓") for keyboard-driven tools.

### Command palette (⌘K)
A centered 560–640px wide modal 15vh from the top, with a search input (no border, 16px), grouped results (12px group labels), arrow-key navigation and kbd hints on the right (`<kbd>` in mono, 1px border). Very high perceived quality for little work.

### Table
Row height 36–44px, 13–14px text, header 12px uppercase `--text-3` or sentence-case 500 weight, a sticky header, zebra striping off, hairline row dividers, numbers right-aligned in tabular nums, a hover row fill, and a checkbox column for bulk actions. Status shown as a dot plus a label, not a rainbow pill.

### Detail panel / properties
Label-value pairs in two columns (label `--text-3` 12–13px, value `--text` 13–14px), grouped under small section headers like "Properties", "Labels", "Activity". Activity feed: avatar 20px, actor bold, action `--text-2`, timestamp `--text-3`, connected with a 1px vertical line.

### Forms
Labels above inputs, 36–40px input height, 1px border, focus ring `0 0 0 3px var(--accent-soft)` plus an accent border, and helper text 12–13px. Validate inline on blur, never only on submit.

### Buttons
| Variant | Style |
|---|---|
| Primary | Accent or high-contrast fill (white on dark, near-black on light), 32–40px tall, 500–600 weight |
| Secondary | Surface fill with a 1px border |
| Ghost | Transparent, with a hover fill |
| Destructive | Danger text, with a fill only on confirm |
Include an icon + label combination and a loading state (spinner replaces the icon, width stays fixed).

### Badges and labels
20–22px tall, 12px text, a colored dot plus a neutral pill (`Performance ●`), as in the Linear screenshot. Avoid fully saturated fills.

### Empty, loading and error states
- **Empty:** a small illustration or icon, one sentence saying what goes here, and the primary action ("Create your first track"). Optionally offer sample data ("Load demo data"), which is great for demos.
- **Loading:** skeletons shaped like the content, with shimmer. For AI calls, show streaming or step progress ("Analyzing tempo… Detecting key… Writing chords…").
- **Error:** what failed in plain words, what to do, and a retry button. Keep stack traces behind a "Details" toggle.

### Toast
Bottom-right (desktop) or top (mobile), 360px wide, auto-dismiss after 4–6s, with an undo action when it's possible.

### Charts
- Use a real chart library (Recharts, Tremor, visx, Chart.js, ECharts) and style it with tokens.
- One accent series plus neutral comparison series. Gridlines at 6% contrast, axis labels 11–12px `--text-3`, and a tooltip with tabular numbers.
- Pick the chart for the question: line for trends, bar for comparisons, area only for cumulative totals, and no pie charts with more than 4 slices.
- Label the key number directly on the chart ("+38% this week") instead of making judges read axes.

---

## Product screens (most hackathon projects need these, not dashboards)

Most hackathon projects are a **product**: a web or mobile app that does one thing well, plus a landing page. These are the screens judges actually see.

### First-run / onboarding
1–3 steps at most, each with one question and big tap targets. Offer "Try with sample data" so a judge sees value in 5 seconds. Show progress dots and keep a skip option.

### Input → magic → result (the core loop of most AI products)
- **Input:** one dominant input (prompt box, drop zone, camera, record button), with example chips under it so nobody faces a blank box.
- **Drop zone:** a dashed border that becomes solid and accent-colored on dragover, a file icon that lifts, and accepted file types in small text. After the drop, show the file chip with a remove ×.
- **Working state:** named steps ("Transcribing… Finding rushed bars… Writing tips…") with progress, or streamed output. Never a bare spinner over 2 seconds.
- **Result:** the answer first (big and scannable), details below or expandable, plus actions: save, share, try again, edit. Show confidence or sources when it's AI output.

### Chat / assistant view
Messages max ~680px wide, the user's messages right-aligned with an accent tint, the assistant's left-aligned on a surface. Stream the tokens. Suggested replies as chips. The input is fixed to the bottom with a send button that animates on press. Render code blocks and tables properly.

### Detail view
A hero area (title, key metadata, primary action), then content in sections, then related items. On mobile, the primary action becomes a sticky bottom bar.

### Mobile app shell (when the project is a mobile or PWA app)
Bottom tab bar with 3–5 icons and labels, 44px+ targets, the active tab tinted, a large title header that collapses on scroll, and bottom sheets instead of modals. Design at 390×844 first.

### Map or place view
A full-bleed map with a list or bottom sheet of results. The selected pin syncs with the selected card. Muted map style (light or dark) so your accent pins pop.

### Before / after
For anything that transforms something (image cleanup, translation, rewriting, design fixes): a draggable comparison slider or a side-by-side toggle. It's one of the most convincing demo visuals there is.

### Sharing / output
Generate a shareable result card (an image or link with OG preview) so the product's output looks good outside the app. Judges love "and here's what you'd post".

### Settings and profile
Keep them minimal or skip them entirely for a hackathon unless the rubric needs them.
