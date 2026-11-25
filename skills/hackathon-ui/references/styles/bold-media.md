# bold-media

**Inspired by:** AI music generator landing pages (the "Musicwave" style), streaming and creator tools, gaming sites, rugged automotive and sports retail (the "Mayhem Wheels" style)
**Feels:** loud, kinetic, cinematic, exciting. Turn it up.
**Demo page:** `assets/showcase/bold-media.html`

## What makes it work (reverse-engineered)
- **Extended or condensed display type in all caps** at huge sizes (Unbounded, Archivo Expanded, Druk-like condensed). Paired with an italic or script-like accent line ("*What will you create*" typed out in pink).
- **Cinematic backgrounds:** full-bleed video or a blurred photo, darkened with a vignette and tinted with a brand glow (violet club light, golden-hour truck shot).
- **One hot accent** against dark: electric violet, pink, acid lime, racing red.
- **Social proof as a live ticker:** "48K+ creators · 50K songs last month · royalty-free" with tiny icons, and a marquee of platform logos at the bottom.
- Retail variant (Mayhem): stencil or slab nav buttons with outlined boxes, a vehicle or product finder form in the hero, a huge promo headline with spaced-out numerals ("20% OFF"), and a red CTA.

## Tokens
```css
:root {
  --font-sans: "DM Sans Variable", system-ui, sans-serif;
  --font-display: "Unbounded Variable", "Archivo Variable", sans-serif;   /* use font-stretch: 125% with Archivo */
  --font-mono: "JetBrains Mono Variable", monospace;
  --bg: #07060d; --surface: #12101c; --surface-2: #1b1828;
  --border: rgba(255,255,255,.10);
  --text: #ffffff; --text-2: rgba(255,255,255,.72); --text-3: rgba(255,255,255,.5);
  --accent: #f472d0;            /* swap: #8b5cf6 violet, #d7ff3a lime, #e11d2e racing red */
  --accent-2: #7c5cff;
  --accent-fg: #0b0712;
  --glow: radial-gradient(60% 50% at 50% 0%, rgba(124,92,255,.55), transparent 70%);
  --radius: 999px; --radius-card: 16px;
}
```

## Type
- Display: 72–140px / 0.9, uppercase, weight 700–800, tracking -0.01em to +0.01em (extended faces need little or no tightening).
- Accent line: same size range as h2 (48–64px), italic, accent color, often animated (typed or cycling words).
- Body: 16–18px DM Sans, 72% white. Stats 13–14px with small icons.

## Layout signatures
- Centered hero, display headline stacked over 2 lines, an accent line, one-sentence pitch, one big pill CTA, and a stats row.
- Full-bleed video or image background with a gradient overlay: `linear-gradient(180deg, rgba(7,6,13,.2), #07060d 85%)` plus a color glow.
- Bottom logo marquee. Sections below alternate full-bleed media and dark content grids (cards with cover art, waveform players, track lists).

## Components
- **Buttons:** big pill, white fill with black text, or accent fill. 48–56px tall, 16px weight 600.
- **Media cards:** cover art (square), title, artist or creator, a play button that appears on hover, waveform or progress bar in the accent.
- **Promo bar:** a slim top bar with a countdown ("05d 11h 19m left") and a pill CTA. Use it only for real time-limited events.
- **Retail finder:** a row of selects (Year · Make · Model · Trim) plus a solid action button, in the hero.

## Motion
Kinetic: typed or cycling accent words, an audio-reactive waveform, video background, a marquee of logos, cards that tilt toward the cursor. Keep it at 60fps and pause video when off-screen.

## Signature moves (pick 2–3)
1. Huge extended uppercase headline with an italic accent line that types itself.
2. Cinematic video or photo background with a brand-colored glow.
3. Live stats row with icons.
4. Media cards with playable waveforms.

## Don'ts
- Don't use this for trust-heavy products (finance, health).
- Don't use tiny body text over busy video. Add an overlay so contrast passes.
- One hot accent, maybe a second for gradients. Not a rainbow.

## Starter prompt
> Build [screen] for [product] in the bold-media style: near-black `#07060d` with a violet glow and full-bleed [video/image] background under a dark gradient overlay, Unbounded uppercase display at 100px+, an italic accent line in `[#f472d0]` that types itself, DM Sans body, a big white pill CTA, a stats row with small icons, and a logo marquee at the bottom. Cinematic and energetic, contrast still passing.
