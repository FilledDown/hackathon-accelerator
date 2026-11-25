# Foundations

What the best product sites have in common, whatever their style. Get these right and almost any style looks professional.

## Contents
1. Type
2. Spacing and layout
3. Color
4. Radius, borders, elevation
5. Icons and imagery
6. Token file template
7. Free font pairings

## 1. Type

**Use a real scale.** Pick one ratio and stick to it. Most premium SaaS sites use a tight scale for UI and a big jump for display:

| Token | Size / line-height | Use |
|---|---|---|
| `--text-xs` | 12 / 16 | labels, meta, table headers |
| `--text-sm` | 14 / 20 | UI default in apps, secondary text |
| `--text-base` | 16 / 24 | body copy on marketing pages |
| `--text-lg` | 18 / 28 | lead paragraphs |
| `--text-xl` | 20 / 28 | card titles |
| `--text-2xl` | 24 / 32 | section titles in apps |
| `--text-4xl` | 36 / 40 | section headlines |
| `--text-6xl` | 56–64 / 1.0–1.05 | hero headline (desktop) |
| `--text-8xl` | 80–96 / 0.95–1.0 | editorial / poster heroes only |

Rules that make type look expensive:
- **Big headlines get negative tracking.** -0.02em at 36px, -0.035em to -0.045em at 56px and up. Default tracking on large text is the most common "this is AI" tell.
- **Small uppercase labels get positive tracking** (+0.06 to +0.12em) and size 11–12px.
- **Headline line-height 1.0–1.1, body 1.5–1.6.**
- **Weight contrast, not size soup.** Use 2–3 weights (400/500/600 for UI; display can go 600–700). Max ~6 distinct font sizes per page.
- **Measure:** body copy 55–75 characters per line (`max-width: 65ch`).
- **Tabular numbers** for anything that updates or lines up: `font-variant-numeric: tabular-nums`.
- **Balance headlines:** `text-wrap: balance`. **Pretty paragraphs:** `text-wrap: pretty`.
- Headlines say something specific. "The incident tracker that writes your postmortem" beats "Revolutionize your workflow".

## 2. Spacing and layout

- **4px base, 8px rhythm.** Tokens: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128. Nothing in between.
- **Section padding:** 96–160px vertical on desktop marketing pages, 64px on mobile. Apps: 16–24px panel padding.
- **Container:** 1120–1280px max width for marketing, centered, with 24px gutters (mobile 16–20px). Text blocks narrower (~640–720px).
- **Group with space, not boxes.** Related items sit 8–16px apart, unrelated groups 32–64px apart. Only add borders or cards when space alone isn't enough.
- **Alignment:** one strong left edge beats centered everything. Linear, Vercel and Stripe heroes are left-aligned or have a clear axis. Center only short, poster-like heroes (Raycast, Squarespace).
- **12-column grid** for marketing, with content snapping to it. Bento grids use 2–4 columns with spans.
- **App shell:** sidebar 220–260px, top bar 44–56px, content max ~1200px or full-bleed for data.

## 3. Color

Build a palette in this order:
1. **Neutrals first.** An 11-step ramp (50 → 950) does 90% of the work. Pure black (#000) and pure white backgrounds look cheap in apps. Use near-black (#08090a, #0b0c0e, #111214) and off-white (#fafaf9, #f7f6f3).
2. **One accent.** Used for the primary action, focus rings, key data and selection. That's it. Raycast is red, Supabase green, Linear indigo, the spec-sheet portfolio red on paper.
3. **Semantic colors** (success, warning, danger, info) are muted in the UI and only saturated for badges and alerts.
4. **Text contrast:** primary text ≥ 7:1, secondary ≥ 4.5:1, disabled can drop lower. On dark backgrounds, use ~92% white for primary, ~60% for secondary, ~40% for tertiary. Don't use pure white body text on pure black.
5. **Dark mode isn't inverted light mode.** Raise surfaces with lighter fills (#0f1011 → #16171a → #1d1e21) instead of shadows, and use 1px borders at 6–10% white.

Gradients: one purposeful gradient (a hero glow, a brand mesh) per page, slow and subtle. Avoid the default `from-purple-500 to-blue-500`.

## 4. Radius, borders, elevation

- **Pick a radius personality and stay consistent.** Sharp (0–4px): editorial, spec-sheet, industrial. Crisp (6–8px): Linear, Vercel, Stripe. Soft (12–16px): Notion, Raycast cards, consumer. Pill buttons are fine in any style.
- **Nested radius:** inner radius = outer radius − padding. A 12px card with 4px padding holds 8px-radius children.
- **Hairline borders** (1px, low contrast) define premium UI more than shadows do. Dark: `rgba(255,255,255,0.08)`. Light: `rgba(0,0,0,0.08)` or a neutral-200.
- **Shadows are layered and soft**, never one big blur:
  `0 1px 2px rgba(0,0,0,.06), 0 4px 12px rgba(0,0,0,.06), 0 16px 40px rgba(0,0,0,.08)`.
  In dark UIs, add an inner top highlight to raised surfaces: `inset 0 1px 0 rgba(255,255,255,0.06)`.

## 5. Icons and imagery

- **One icon set, one stroke width.** Lucide (1.5–2px), Phosphor, or Heroicons. Size 16px in dense UI, 20px in normal UI. Icons never replace labels on primary actions.
- **The best hero image is your real product UI**, shown in a framed window at a slight angle or with a glow (Linear, Raycast, Resend, Attio). A screenshot of the real working app also proves the app is real.
- **No stock photos of people pointing at laptops.** If you need imagery, use the product, abstract brand shapes, data visualizations, or one striking photo with an art-directed crop (editorial style).
- **Emoji are not icons.** Keep them out of headings, nav and buttons unless the brand is playful and it's deliberate.

## 6. Token file template

```css
:root {
  /* type */
  --font-sans: "Inter Variable", ui-sans-serif, system-ui, sans-serif;
  --font-display: var(--font-sans);
  --font-mono: "JetBrains Mono Variable", ui-monospace, SFMono-Regular, monospace;

  /* neutrals (light) */
  --bg: #fafaf9; --surface: #ffffff; --surface-2: #f4f4f3;
  --border: rgba(0,0,0,.08); --border-strong: rgba(0,0,0,.14);
  --text: #111113; --text-2: #55565b; --text-3: #8a8b91;

  /* accent */
  --accent: #5e6ad2; --accent-fg: #ffffff; --accent-soft: color-mix(in oklab, var(--accent) 14%, transparent);

  /* semantic */
  --success: #2f9e6a; --warning: #c98a12; --danger: #d4483b;

  /* shape */
  --radius-sm: 6px; --radius: 8px; --radius-lg: 12px; --radius-full: 999px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.06);
  --shadow: 0 1px 2px rgba(0,0,0,.05), 0 4px 12px rgba(0,0,0,.06);
  --shadow-lg: 0 1px 2px rgba(0,0,0,.05), 0 8px 24px rgba(0,0,0,.08), 0 24px 60px rgba(0,0,0,.10);

  /* motion */
  --ease-out: cubic-bezier(.16, 1, .3, 1);
  --ease-in-out: cubic-bezier(.65, 0, .35, 1);
  --dur-fast: 120ms; --dur: 200ms; --dur-slow: 400ms;
}
```

**Tailwind v4** (`@theme` in your CSS) maps tokens to utilities:
```css
@import "tailwindcss";
@theme {
  --color-bg: var(--bg); --color-surface: var(--surface); --color-border: var(--border);
  --color-text: var(--text); --color-text-2: var(--text-2); --color-accent: var(--accent);
  --font-sans: var(--font-sans); --font-mono: var(--font-mono);
  --radius-lg: var(--radius-lg);
}
```
Then use `bg-surface text-text-2 border-border rounded-lg` and never `bg-[#1a1a1a]`.

**Tailwind v3:** put the same mapping in `tailwind.config.js` → `theme.extend.colors` using `var(--token)`.

## 7. Free font pairings

All are free for commercial use (SIL OFL, or the Fontshare free license where noted). Sources: Google Fonts, Fontsource (`npm i @fontsource-variable/<name>`), Vercel's `geist` package.

| Pairing | Feels like |
|---|---|
| Inter Tight (display) + Inter (UI) + JetBrains Mono | Linear / Raycast precision |
| Geist + Geist Mono | Vercel-style engineering |
| Manrope or Inter + tight tracking | Stripe / Ramp fintech crispness |
| Instrument Serif (display) + Inter | Editorial, Aesop / Squarespace templates |
| Newsreader or Fraunces (display) + Inter | Calm, literary workspace (Notion-ish warmth) |
| Space Grotesk + Space Mono / JetBrains Mono | Spec-sheet, industrial, hardware |
| Unbounded or Archivo Expanded (display) + DM Sans | Loud media, music, sports, gaming |
| Satoshi or General Sans (Fontshare, free license) + DM Sans | Friendly modern consumer |

Never ship the browser default serif, and don't use Inter at default tracking for a 64px headline.
