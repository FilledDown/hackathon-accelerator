# playful-builder

**Inspired by:** Framer, Webflow, Lovable, Replit, Figma
**Feels:** creative, optimistic, energetic, capable. "You can make this."
**Demo page:** `assets/showcase/playful-builder.html`

## What makes it work (reverse-engineered)
- **Vivid but controlled color:** a saturated primary (Figma's multi-color, Lovable's warm pink-orange gradient, Framer's electric blue) on a clean white or black base.
- **The canvas is the hero:** an editor UI showing something being made, with layers panels, selection handles, cursors with name tags, and a prompt box generating a site.
- **Big friendly type** with personality: geometric grotesks, tight tracking, sometimes mixed weights in one headline.
- **Rounded, tactile components:** 12–20px radius, chunky buttons, sticker-like badges, slight rotations.
- Showcases of things people made: a gallery or marquee of templates and community work.

## Tokens
```css
:root {
  --font-sans: "Manrope Variable", "DM Sans Variable", system-ui, sans-serif;
  --font-display: "Space Grotesk Variable", "Manrope Variable", sans-serif;
  --font-mono: "JetBrains Mono Variable", monospace;
  --bg: #ffffff; --surface: #ffffff; --surface-2: #f5f5f7; --surface-3: #ececf0;
  --border: #e7e7ec; --border-strong: #d2d2da;
  --text: #0e0e12; --text-2: #55555f; --text-3: #8b8b96;
  --accent: #ff4f8b;            /* swap: #0d6efd electric blue, #7c3aed violet, #ff7a1a orange */
  --accent-2: #ffb547;
  --accent-fg: #ffffff;
  --sel: #2f80ff;               /* selection handles, multiplayer cursor */
  --radius-sm: 8px; --radius: 12px; --radius-lg: 20px; --radius-full: 999px;
  --shadow: 0 1px 2px rgba(14,14,18,.06), 0 8px 24px rgba(14,14,18,.08);
  --shadow-pop: 0 2px 0 rgba(14,14,18,.9);   /* sticker-style hard shadow */
}
```

## Type
- Hero: 60–84px / 1.0, Space Grotesk 600–700, tracking -0.04em. Highlight one word with a gradient fill or a hand-drawn underline.
- Body: 17–18px Manrope, `--text-2`.
- Labels: 13px weight 600, sometimes in colored pill badges.

## Layout signatures
- Centered hero with a **prompt box** ("Describe the app you want…") or a big editor screenshot with live cursors and selection handles.
- Template gallery in a 3–4 column grid or a slow marquee, with cards that tilt slightly on hover.
- Feature sections as large rounded panels in soft tints (pink-50, blue-50) with an illustration or UI inside.

## Components
- **Prompt box:** 56–64px tall, radius 16–20, soft shadow, an attach icon, a send button in the accent gradient, example chips under it.
- **Buttons:** pill, chunky (44–48px), accent or black fill. A hard "sticker" shadow variant for playful moments.
- **Multiplayer cursors:** arrow + name tag pill in distinct colors.
- **Selection box:** 1px `--sel` outline with square handles at the corners and a size label.

## Motion
Springy and alive: spring physics on hovers and drags, cursors that move around the canvas, a gradient that slowly rotates on the CTA, cards that tilt toward the pointer. Keep durations short so it never feels slow.

## Signature moves (pick 2–3)
1. Prompt box hero with example chips.
2. Canvas screenshot with named cursors and selection handles.
3. One gradient-filled headline word.
4. Tilting template gallery.

## Don'ts
- Don't let playful turn childish: keep layout disciplined and type tight.
- Not more than 2 bright colors plus the selection blue.
- Avoid clip-art illustrations. The product canvas is the illustration.

## Starter prompt
> Build [screen] for [product] in the playful-builder style: white base, Space Grotesk headlines at -0.04em with one gradient-filled word (`[#ff4f8b → #ffb547]`), Manrope body, rounded 12–20px components, a prompt-box hero with example chips, and an editor canvas showing named multiplayer cursors and selection handles. Springy motion. Creative but disciplined.
