# editorial-luxe

**Inspired by:** Aesop, COS, Apple, Porsche, Squarespace's showcase templates (the "Botanica" style storefront)
**Feels:** refined, confident, quiet, tactile. A magazine or a flagship store, not an app.
**Demo page:** `assets/showcase/editorial-luxe.html`

## What makes it work (reverse-engineered)
- **Typography is the brand.** A high-contrast serif at huge sizes (Botanica's full-width wordmark, Aesop's literary headings), or Apple's tight neutral sans at enormous sizes.
- **Restrained palette from the material world:** bone, sand, clay, ink, forest, oxblood. One color sets the mood (the warm amber of the Squarespace hero, Aesop's amber and black).
- **Photography or texture does the heavy lifting.** Art-directed, cropped tight, shot on a single tone. Without photos, use rich flat color fields and type.
- **Sharp corners, thin rules, lots of space.** Small uppercase sans labels at wide tracking. Navigation in small caps.
- Slow, deliberate motion: long fades, parallax on images, text that rises line by line.

## Tokens
```css
:root {
  --font-sans: "Inter Variable", system-ui, sans-serif;
  --font-display: "Instrument Serif", "Fraunces Variable", Georgia, serif;
  --bg: #f3ede4; --surface: #faf6f0; --surface-2: #e9e1d4;
  --ink: #1a1714; --border: rgba(26,23,20,.14);
  --text: #1a1714; --text-2: #5b544b; --text-3: #8c8378;
  --accent: #7a2e1d;            /* swap: #2f3b2b forest, #b5651d amber, #1a1714 pure ink */
  --accent-fg: #faf6f0;
  --radius: 0px; --radius-sm: 2px;
}
```
A dark variant works too: `--bg: #14110e; --text: #efe8dc` with an amber photographic hero.

## Type
- Display: 80–160px / 0.9–0.95, serif weight 400, tracking -0.02em. It can bleed edge to edge as a wordmark.
- Headings: 40–56px serif. Italics for emphasis.
- Labels and nav: 11–13px sans, uppercase, tracking +0.12em.
- Body: 16–17px / 1.6, `--text-2`, max 60ch.

## Layout signatures
- Asymmetric editorial grid: big image left 7 columns, small text block right 4 columns, offset vertically.
- Full-bleed wordmark or headline sections. Product lists as quiet grids with name, short description and price in small sans.
- Thin 1px rules separating sections, with section numbers or small captions ("01 — The Collection").

## Components
- **Buttons:** rectangular, uppercase 12px tracked text, 1px ink border or solid ink fill, 44–48px tall, no radius.
- **Product card:** image (4:5), name in serif 20px, a one-line note in sans 13px `--text-2`, price right-aligned.
- **Nav:** small uppercase links spread across the top, the logo centered (Botanica) or left.

## Motion
Slow: 600–900ms ease-out fades. Headline lines rise one by one. Images scale from 1.04 to 1 as they enter. Hover on links is an underline that draws from left to right.

## Signature moves (pick 2–3)
1. Full-width serif wordmark or headline.
2. One art-directed photo or flat color field with tight cropping.
3. Numbered sections with thin rules and small tracked captions.
4. Line-by-line headline reveal.

## Don'ts
- No rounded cards, no drop shadows, no gradients, no icon grids.
- Never more than 2 typefaces. Never bold the serif.
- Don't crowd. If it feels empty, it's probably right.

## Starter prompt
> Build [screen] for [product] in the editorial-luxe style: bone `#f3ede4` background, ink `#1a1714` text, Instrument Serif display at 96px+ with -0.02em tracking, small uppercase Inter labels at +0.12em, sharp corners, 1px rules, one mood color `[color]`, asymmetric editorial grid, and slow fades. Refined and quiet like a flagship store.
