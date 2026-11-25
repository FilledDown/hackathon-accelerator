# data-dashboard

**Inspired by:** Datadog, Grafana, Tremor, PostHog, Mixpanel, Retool, Observable, Vercel and Stripe dashboards
**Feels:** clear, dense, trustworthy, in control. You can make a decision in 5 seconds.
**Demo page:** `assets/showcase/data-dashboard.html`

## What makes it work (reverse-engineered)
- **Hierarchy of numbers:** one primary metric big and labeled, supporting KPIs smaller, details in tables. The eye knows where to land.
- **Neutral chrome, colorful data.** The UI is grayscale. Color is reserved for series, status and thresholds.
- **Charts with real labels:** clear axes, units, comparison periods ("vs last week"), annotations on events (deploys, incidents).
- **Density without clutter:** 13px text, tight 36px rows, 16px panel padding, consistent 12px gaps on a strict grid.
- Filters and time range pickers are always visible at the top. Everything responds to them.

## Tokens
```css
:root {
  --font-sans: "Inter Variable", system-ui, sans-serif;
  --font-mono: "JetBrains Mono Variable", ui-monospace, monospace;
  /* light default; dark variant below */
  --bg: #f7f7f8; --surface: #ffffff; --surface-2: #f2f2f4;
  --border: #e6e6ea; --border-strong: #d4d4da;
  --text: #16161a; --text-2: #5a5a66; --text-3: #8d8d99;
  --accent: #4f46e5;
  --series-1: #4f46e5; --series-2: #0ea5e9; --series-3: #10b981; --series-4: #f59e0b; --series-5: #ec4899;
  --good: #10b981; --warn: #f59e0b; --bad: #ef4444;
  --grid-line: rgba(22,22,26,.06);
  --radius: 8px; --radius-lg: 10px;
}
.dark { --bg: #0b0c0f; --surface: #111318; --surface-2: #171a21; --border: #22252e; --text: #e8e9ed; --text-2: #9a9eab; --text-3: #6b6f7c; --grid-line: rgba(255,255,255,.06); }
```

## Type
- Primary metric: 32–44px, weight 600, tabular nums, with a delta chip next to it (▲ 12.4% in `--good`).
- Panel titles: 13–14px weight 600. Axis labels 11px `--text-3`.
- Everything numeric uses `font-variant-numeric: tabular-nums`. IDs and queries in mono.

## Layout signatures
- App shell: a slim sidebar (icons + labels), a top bar with breadcrumb, a time range picker and a filter chips row.
- A 12-column grid of panels: a hero chart spanning 8 columns plus a KPI stack in 4, then a table full-width.
- Panels have a title row (title, info tooltip, overflow menu), a body and an optional footer ("View all →").

## Components
- **KPI tile:** label, big number, delta chip, a 32px sparkline in the series color.
- **Chart panel:** legend at the top-left with series dots, crosshair tooltip, an annotation line for events.
- **Table:** sortable headers, inline bars for magnitude, status dots, sticky first column on mobile.
- **Time range picker:** segmented control (1h · 24h · 7d · 30d) plus a custom range.
- **Heatmap / status grid:** small squares colored by threshold (uptime, contributions, cohort retention).

## Motion
Data transitions matter more than decoration. Lines morph between ranges (300ms), numbers tick, new rows flash a subtle highlight, and skeletons hold layout while loading. No bouncy entrances.

## Signature moves (pick 2–3)
1. One hero chart with an annotated event ("Deploy v2.3 →").
2. KPI tiles with delta chips and sparklines.
3. A table with inline magnitude bars.
4. A status heatmap grid.

## Don'ts
- No 3D charts, no pie charts with 6+ slices, no gradients inside bars.
- Don't make every tile the same size. Hierarchy is the point.
- Don't invent precision. Round sensibly and show units.

## Starter prompt
> Build [screen] for [product] in the data-dashboard style: neutral `#f7f7f8` chrome with white panels and `#e6e6ea` borders, Inter 13px UI with tabular numbers, one primary metric at 40px with a delta chip, a hero line chart (8 columns) with an annotated event, KPI tiles with sparklines (4 columns), and a full-width table with inline bars and status dots. Color only for data. Realistic numbers about [domain].
