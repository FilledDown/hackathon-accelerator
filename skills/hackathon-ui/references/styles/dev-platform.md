# dev-platform

**Inspired by:** Resend, Supabase, Neon, Railway, PlanetScale, Sentry, Clerk, PostHog
**Feels:** technical, trustworthy, a little cool. "Ship it in five minutes."
**Demo page:** `assets/showcase/dev-platform.html`

## What makes it work (reverse-engineered)
- **Code is the hero.** A syntax-highlighted snippet (5–12 lines) showing how simple the API is, often in tabs (Node, Python, cURL), next to or above a live result.
- Dark (Resend, Supabase, Neon, Railway) or crisp light (Clerk, PlanetScale) base with **one signature brand color**: Supabase green, Neon mint, Railway purple, Clerk violet.
- **Mono everywhere for technical details:** endpoints, env vars, status codes, latency numbers.
- Grid or dot backgrounds, subtle borders, and diagrams of the architecture drawn with lines and nodes.
- Trust signals that devs respect: open source stars, uptime, SOC2, "Built on Postgres", region lists.

## Tokens
```css
:root {
  --font-sans: "Geist Variable", "Inter Variable", system-ui, sans-serif;
  --font-display: "Geist Variable", "Inter Tight Variable", sans-serif;
  --font-mono: "Geist Mono Variable", "JetBrains Mono Variable", ui-monospace, monospace;
  --bg: #0a0a0a; --surface: #111111; --surface-2: #171717; --surface-3: #1f1f1f;
  --border: #262626; --border-strong: #333333;
  --text: #ededed; --text-2: #a1a1a1; --text-3: #737373;
  --accent: #3ecf8e;            /* swap: #00e5bf mint, #a855f7 purple, #6c47ff violet */
  --accent-fg: #052e1a;
  --code-bg: #0d0d0d; --code-key: #79b8ff; --code-str: #9ecbff; --code-fn: #b392f0; --code-com: #6a737d; --code-num: #f8c555;
  --success: #3ecf8e; --warning: #f5a524; --danger: #f04438;
  --radius-sm: 6px; --radius: 8px; --radius-lg: 12px;
  --grid: radial-gradient(circle, rgba(255,255,255,.06) 1px, transparent 1px) 0 0 / 24px 24px;
}
```

## Type
- Hero: 52–64px / 1.05, weight 600, tracking -0.04em. Often a short, punchy promise ("Email for developers", "Postgres in 1 second").
- Mono labels 12px uppercase +0.08em for section eyebrows (`// DEPLOY`, `01 — Send`).
- Code 13–14px / 1.6.

## Layout signatures
- Centered or left hero with **an install command pill** (`npm i postbox` with a copy button) and a primary CTA.
- Code window with tabs + a live result panel side by side (request → response, code → rendered email).
- Feature bento with technical fragments: a log stream, latency chart, region map, webhook payload.
- Dark dot-grid backgrounds and glowing accent lines that connect nodes in a diagram.

## Components
- **Code window:** `--code-bg`, 1px border, radius 12, header with 3 muted dots or file tabs, a copy button, line numbers in `--text-3`.
- **Install pill:** mono 14px, `$` prompt in `--text-3`, copy icon, radius full, 1px border.
- **Status:** dot + mono text ("● 200 OK · 84ms").
- **Buttons:** accent fill with dark text, or white fill on dark. 36px, radius 8.

## Motion
Typing animation in the code block on first view, logs streaming in, a request packet traveling along a diagram line. Keep it under 2 seconds per animation, and loop only the subtle ones.

## Signature moves (pick 2–3)
1. Tabbed code window with a live, matching result.
2. A copyable install command in the hero.
3. Streaming log or event feed with mono timestamps.
4. Architecture diagram with glowing accent connectors.

## Don'ts
- No fake code. The snippet must match the real API you built (judges will read it).
- No stock "developer at laptop" imagery. No cartoon mascots unless they're the brand.
- Don't make the brand color the background. It's an accent.

## Starter prompt
> Build [screen] for [product] in the dev-platform style: `#0a0a0a` background with a subtle dot grid, Geist + Geist Mono, one brand accent `[color]`, a tabbed code window (Node/Python/cURL) showing our real API next to its live result, a copyable install pill, mono status lines like "● 200 OK · 84ms", and hairline `#262626` borders. Technical, concise, credible.
