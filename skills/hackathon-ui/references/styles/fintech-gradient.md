# fintech-gradient

**Inspired by:** Stripe, Mercury, Ramp, Brex, Superhuman
**Feels:** trustworthy, crisp, ambitious, quietly luxurious. Serious money handled beautifully.
**Demo page:** `assets/showcase/fintech-gradient.html`

## What makes it work (reverse-engineered)
- **Light, airy base** with one bold brand moment: Stripe's animated gradient mesh across the top of the hero, Mercury's deep navy and soft light, Ramp's high-contrast black-and-lime accent.
- **Typography carries authority.** Large, confident, tight headlines (Stripe uses about 64–94px with heavy negative tracking). Body copy is calm 17–18px in a slate gray.
- **Product UI as floating cards:** payment forms, cards, dashboards and phone mockups layered with soft, layered shadows and slight overlaps.
- **Diagonal or skewed section edges** and generous whitespace. Precise alignment to a 12-column grid.
- Numbers are a design element: big tabular figures, currency formatting, charts drawn with one accent.

## Tokens
```css
:root {
  --font-sans: "Inter Variable", system-ui, sans-serif;
  --font-display: "Inter Tight Variable", "Inter Variable", sans-serif;   /* alt: Manrope */
  --font-mono: "JetBrains Mono Variable", ui-monospace, monospace;
  --bg: #ffffff; --surface: #ffffff; --surface-2: #f6f9fc; --surface-3: #eef2f7;
  --border: #e3e8ee; --border-strong: #cfd7df;
  --text: #0a2540; --text-2: #425466; --text-3: #6b7c93;
  --accent: #635bff;            /* swap: #0b1b33 navy (Mercury), #e4f222 lime on black (Ramp) */
  --accent-fg: #ffffff;
  --mesh-1: #ffb86b; --mesh-2: #ff5c8a; --mesh-3: #7a5cff; --mesh-4: #41c6ff;
  --success: #09a66d; --warning: #d97917; --danger: #df1b41;
  --radius-sm: 6px; --radius: 8px; --radius-lg: 12px;
  --shadow-card: 0 2px 5px rgba(50,50,93,.08), 0 13px 27px -5px rgba(50,50,93,.18), 0 8px 16px -8px rgba(0,0,0,.2);
}
```

## Type
- Hero: 60–72px / 1.02, weight 600–650, tracking -0.035 to -0.04em (keep it to 3–4 lines), `--text` navy (not black).
- Lead: 18–20px / 1.6, `--text-2`, max 560px.
- Eyebrow: 14–15px, weight 600, accent color, sentence case ("Payments", "Treasury").
- Numbers: tabular, weight 600, often 28–48px in cards.

## Layout signatures
- **Split hero:** copy left (5 columns), a stack of floating product cards right (7 columns) overlapping the gradient.
- **Gradient band:** an animated mesh behind the top 60% of the hero, clipped with a skewed bottom edge (`clip-path: polygon(0 0,100% 0,100% 78%,0 100%)`).
- Sections alternate white and `--surface-2`. Feature grids use 3–4 columns of icon + title + sentence with **real mini-UI** in some cells.
- Dark navy sections (`#0a2540`) for developer or "infrastructure" stories, with code blocks.

## Components
- **Buttons:** pill or 8px radius, accent fill with a hover arrow that slides 2px right ("Start now →"). Secondary is a text link with an arrow.
- **Floating cards:** white, radius 12, `--shadow-card`, slightly rotated or offset, showing a payment form, balance, card or invoice with realistic figures.
- **Stat blocks:** big tabular number, small label, thin divider lines between.

## Motion
Slow, luxurious gradient drift (20–30s loop). Cards float up into place with a stagger. Number tickers on stats. Hover: cards lift 2–4px with a deeper shadow.

## Signature moves (pick 2–3)
1. Animated mesh gradient with a skewed bottom edge.
2. Layered floating product cards with realistic financial data.
3. A dark navy "for developers" section with a syntax-highlighted code sample.
4. Huge tabular metric with a one-line explanation ("$1.4T processed").

## Don'ts
- No neon, grunge or playful illustrations. Trust is the product.
- Don't let the gradient cover body text. Gradients live behind the hero only.
- Avoid pure black text; navy or deep slate reads more premium.

## Starter prompt
> Build [screen] for [product] in the fintech-gradient style: white base with `#f6f9fc` alternating sections, navy `#0a2540` text, Inter Tight headlines at -0.045em, one accent `[color]`, an animated mesh gradient behind the hero with a skewed bottom edge, and floating product cards with layered soft shadows and realistic numbers in tabular figures. Calm, trustworthy, precise.
