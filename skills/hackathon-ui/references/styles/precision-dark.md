# precision-dark

**Inspired by:** Linear, Raycast, Vercel, Warp, Cursor, Arc, ray.so
**Feels:** fast, exact, calm, expensive. Keyboard-first software built by people who care.
**Demo page:** `assets/showcase/precision-dark.html`

## What makes it work (reverse-engineered)
- Near-black backgrounds (never #000) with **surfaces one or two steps lighter** and **1px hairline borders at 6–9% white**. Depth comes from borders and fills, not shadows.
- **The product UI is the hero image.** Linear shows a real issue view in an inset window. Raycast shows its launcher. Cursor shows the editor.
- Big headline, **very tight tracking** (-0.04em), weight 600–700, often left-aligned with a short subhead in 60% white.
- **One accent** used sparingly: indigo (Linear), red (Raycast), white (Vercel). Status colors are small dots.
- Tiny details everywhere: kbd hints (`⌘K`), mono IDs (`DRV-8852`), 13px UI text, timestamps in tertiary gray.
- A single soft glow or light beam behind the hero (Raycast's diagonal red bars, Linear's gray spotlight under the product frame).

## Tokens
```css
:root {
  --font-sans: "Inter Variable", system-ui, sans-serif;
  --font-display: "Inter Tight Variable", "Inter Variable", system-ui, sans-serif;
  --font-mono: "Geist Mono Variable", "JetBrains Mono Variable", ui-monospace, monospace;
  --bg: #08090a; --surface: #0f1011; --surface-2: #151618; --surface-3: #1c1d20;
  --border: rgba(255,255,255,.07); --border-strong: rgba(255,255,255,.12);
  --text: #f7f8f8; --text-2: #b4b6bc; --text-3: #7c7f87; --text-4: #55575d;
  --accent: #6e79d6;            /* swap: #ff4d5e (red), #f5f5f5 (mono), #3ecf8e (green) */
  --accent-fg: #ffffff;
  --success: #4cb782; --warning: #f2c94c; --danger: #eb5757;
  --radius-sm: 6px; --radius: 8px; --radius-lg: 12px; --radius-xl: 16px;
  --shadow-frame: 0 0 0 1px rgba(255,255,255,.04) inset, 0 40px 100px rgba(0,0,0,.6);
  --highlight: inset 0 1px 0 rgba(255,255,255,.05);
}
```

## Type
- Hero: 56–72px / 1.04, weight 600, tracking -0.035em (go tighter only with Inter Tight at 500–600), `--font-display`.
- Section titles: 36–44px / 1.1, tracking -0.03em.
- UI: 13–14px, weight 500 for labels and 400 for body. Meta 12px `--text-3`.
- Mono for IDs, shortcuts, code and numbers in tables.

## Layout signatures
- Marketing container 1120–1200px. Hero left-aligned with a "New → feature" link aligned right on the subhead row (Linear) **or** centered short poster headline over a brand shape (Raycast).
- Product frame below the hero: full container width, radius 12–16px, a 1px border, and the app shell inside (sidebar + main + detail column).
- Sections separated by 1px `--border` lines and 120–160px spacing. Feature sections use **bento tiles with real UI fragments**.

## Components
- **Buttons:** primary = `--text` fill with `--bg` text (white button on dark), 32–36px, radius 8 or pill. Secondary = `--surface-2` + border.
- **Nav:** transparent, 14px links in `--text-2`. Or Raycast's floating rounded nav container with a border and inset highlight.
- **Sidebar items:** 28px tall, 13px, icon 16px, active = `--surface-3` fill.
- **Labels:** dot + text in a 1px bordered pill.
- **Kbd:** `font: 11px var(--font-mono); padding: 1px 5px; border: 1px solid var(--border-strong); border-radius: 4px; color: var(--text-3)`.

## Motion
Fast and subtle: 120–200ms, ease-out. Entrances use blur + 8px rise + fade, staggered. Signature: a spotlight border that follows the cursor on tiles, a command palette that opens instantly, and a product frame that untilts on scroll.

## Signature moves to use (pick 2–3)
1. Inset product window with a soft radial glow under it.
2. Diagonal light beams or a blurred brand shape behind centered hero type (Raycast).
3. Activity feed with avatars, mono IDs and relative timestamps.
4. ⌘K command palette in the actual app.
5. Grain or noise overlay at 3–4% opacity on the background.

## Don'ts
- No purple-blue gradients, no glassmorphism cards, no big drop shadows.
- Don't fill sidebars with bright accent colors. Selection is a neutral fill.
- Don't use more than one accent. Status colors stay tiny.

## Starter prompt
> Build [screen] for [product] in the precision-dark style: near-black `#08090a` background, surfaces stepping up to `#1c1d20`, 1px hairline borders at 7% white, Inter Tight display with -0.04em tracking, 13px UI text, one accent `[color]`, mono IDs and kbd hints, the product UI framed as the hero with a soft glow. Realistic data about [domain]. Loading, empty and error states. No gradients except the hero glow.
