# spec-sheet

**Inspired by:** Teenage Engineering, Nothing, technical-document portfolios (the "staff pass" portfolio with red ink on paper)
**Feels:** engineered, witty, precise, collectible. A product manual designed by an industrial designer.
**Demo page:** `assets/showcase/spec-sheet.html`

## What makes it work (reverse-engineered)
- **Monospace as the primary voice**, uppercase with wide tracking. Information presented like a datasheet: labels in one column, values in the next.
- **One ink color on paper:** red on warm gray (the portfolio screenshot), orange on white (Teenage Engineering), white dots on black (Nothing). Everything else is the paper color.
- **Technical ornaments:** crop marks in the corners, registration crosshairs, barcodes, serial numbers ("№ 0001"), sheet counters ("SHEET 01 / 09"), dashed rules, dot-matrix type.
- **Objects as heroes:** a product, ID card or device rendered flat and centered, sometimes tilted slightly, hanging on a lanyard.
- Playful interactions that feel physical: toggles, knobs, "rub the photo" easter eggs.

## Tokens
```css
:root {
  --font-sans: "Space Grotesk Variable", system-ui, sans-serif;
  --font-mono: "JetBrains Mono Variable", "Space Mono", ui-monospace, monospace;
  --font-display: var(--font-mono);
  --paper: #e9e6df; --paper-2: #f2f0eb; --ink: #d62f2f;    /* swap ink: #ff5a00 orange, #111 black; paper: #0d0d0d for Nothing-dark */
  --bg: var(--paper); --surface: var(--paper-2);
  --text: var(--ink); --text-2: color-mix(in oklab, var(--ink) 75%, var(--paper)); --text-3: color-mix(in oklab, var(--ink) 50%, var(--paper));
  --border: color-mix(in oklab, var(--ink) 35%, transparent);
  --accent: var(--ink); --accent-fg: var(--paper);
  --radius: 0px;
}
```

## Type
- Everything mono, uppercase, 11–13px, tracking +0.12em for labels and nav.
- Names and titles: mono 40–64px, sentence case, tight (Rinat Seif's name on the pass).
- Dot-matrix display for numbers (build it with a CSS radial-gradient mask or an SVG grid) is a strong signature.
- Body: mono 13–14px / 1.7 in sentence case.

## Layout signatures
- Centered composition with wide margins and **crop marks at the viewport corners**.
- Two-column datasheet: an object card left, a spec table or timeline right ("2025– · exactly.ai · DESIGN EXPERT").
- Dashed horizontal rules, sheet and page counters at the bottom, "↓ SCROLL" hints.

## Components
- **Buttons:** rectangular, 1px ink border, uppercase mono 12px, solid ink fill for the primary ("⇩ CV, PDF").
- **Spec rows:** label (`--text-3`, 11px) / value (`--text`, 13px) in a two-column grid with 1px rules.
- **Toggle switches** styled like hardware (pill, ink knob).
- **Barcodes / serials:** decorative, generated with repeating-linear-gradient.

## Motion
Mechanical and snappy: step easings (`steps(6)`), 80–150ms. Elements click into place. A slight swing on a hanging card (rotate ±2° on a 4s ease-in-out loop). Typewriter reveals for labels.

## Signature moves (pick 2–3)
1. Crop marks and registration crosshairs at the corners.
2. An object card (ID pass, device, ticket) with a serial number and barcode.
3. Datasheet table of label/value pairs.
4. Dot-matrix numerals or a sheet counter.

## Don'ts
- Never more than one ink color (plus paper). No gradients, no shadows beyond one flat offset.
- Don't use rounded, friendly UI. Every corner is square.
- Don't let the ornaments make it unreadable. Body copy stays sentence case.

## Starter prompt
> Build [screen] for [product] in the spec-sheet style: warm paper `#e9e6df` background, a single ink color `[#d62f2f]` for all text and lines, JetBrains Mono uppercase labels at +0.12em, crop marks in the corners, a datasheet layout of label/value rows with 1px rules, an object card with a serial number and barcode, square corners, snappy stepped motion.
