# calm-workspace

**Inspired by:** Notion, Attio, Notion Calendar (Cron), Pitch, Loom
**Feels:** warm, focused, friendly, intelligent. A tool you'd happily open every morning.
**Demo page:** `assets/showcase/calm-workspace.html`

## What makes it work (reverse-engineered)
- **Warm off-white backgrounds** (`#fbfaf8`) and true-white cards, with soft gray hairlines. It feels like paper, not a screen.
- **Approachable type**: a clean sans for UI and often a serif or rounded display for headlines (Notion's illustrated warmth, Attio's crisp modernity, Pitch's color pops).
- **Product UI as the hero** in clean light windows: calendars with colored event blocks, databases, CRM records, slide canvases.
- **Soft pastels** for categories (event colors, tags) with one stronger brand color for actions.
- Generous whitespace and calm motion. Nothing screams.

## Tokens
```css
:root {
  --font-sans: "Inter Variable", system-ui, sans-serif;
  --font-display: "Newsreader Variable", Georgia, serif;   /* alt: Fraunces, or Inter Tight for a crisper Attio look */
  --font-mono: "JetBrains Mono Variable", ui-monospace, monospace;
  --bg: #fbfaf8; --surface: #ffffff; --surface-2: #f5f4f1; --surface-3: #eeece8;
  --border: #ebe9e4; --border-strong: #dcd9d2;
  --text: #1f1e1c; --text-2: #5f5d58; --text-3: #94918a;
  --accent: #2f6fed;            /* swap: #e8590c warm orange, #7c5cff violet */
  --accent-fg: #ffffff;
  --tag-blue: #e3edfd; --tag-green: #e1f3e8; --tag-yellow: #fbf1d3; --tag-pink: #fbe4ec; --tag-purple: #ece6fd;
  --tag-blue-fg: #1f56c8; --tag-green-fg: #1f7a45; --tag-yellow-fg: #8a6408; --tag-pink-fg: #b4235a; --tag-purple-fg: #5b3fd1;
  --success: #2f9e6a; --warning: #c98a12; --danger: #d4483b;
  --radius-sm: 6px; --radius: 10px; --radius-lg: 14px;
  --shadow: 0 1px 2px rgba(31,30,28,.04), 0 6px 20px rgba(31,30,28,.06);
  --shadow-lg: 0 2px 4px rgba(31,30,28,.04), 0 20px 50px rgba(31,30,28,.10);
}
```

## Type
- Hero: 52–68px / 1.05, serif display at weight 400–500 with tracking -0.02em (serifs need less tightening), **or** Inter Tight 600 at -0.035em.
- Italic serif for one emphasized word in the headline is a nice warm touch ("Your week, *finally* calm").
- UI: 14px. Section labels 12px weight 500 `--text-3`.

## Layout signatures
- Centered or left hero with a big, light product window below, slightly overlapping a soft beige-to-white section.
- Feature sections use **tabs that swap a product view** ("Plan · Schedule · Share") rather than static grids.
- Testimonial and customer sections with real names and photos in soft circles.

## Components
- **Calendar blocks:** pastel fill + darker same-hue text, 6px radius, a 2px left border in the full hue.
- **Database rows:** 36px, emoji or icon optional *only if the product lets users set them* (that's Notion's thing), tags as pastel pills.
- **Buttons:** dark (`--text`) fill or accent fill, radius 8–10, 36px. Friendly verbs ("Try it free", "Plan my week").
- **Avatars:** stacked, 24px, 2px white ring.

## Motion
Gentle: 200–300ms ease-out, cards fade up, tabs crossfade the product view, cursor-style "multiplayer" pointers moving in the hero for collaboration products.

## Signature moves (pick 2–3)
1. Serif headline with one italic word.
2. A light calendar or database window with pastel category colors.
3. Tabs that swap product screenshots.
4. Live "multiplayer" cursors with name labels.

## Don'ts
- No dark heavy hero, no neon, no aggressive gradients.
- Pastels are for categories only. Actions use one strong color.
- Don't overload with illustrations. One small spot illustration per section at most.

## Starter prompt
> Build [screen] for [product] in the calm-workspace style: warm off-white `#fbfaf8` page, white cards with `#ebe9e4` hairlines and soft shadows, Newsreader serif headlines with one italic word, Inter 14px UI, pastel category tags, one accent `[color]` for actions. Show the real [calendar/database/editor] UI with realistic data about [domain]. Calm, friendly, generous whitespace.
