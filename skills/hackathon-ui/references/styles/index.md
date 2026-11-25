# Style Directions

Pick one. Each file has tokens, type, layout signatures, component details, motion, signature moves, don'ts and a starter prompt. Each also has a working demo page at `assets/showcase/<name>.html`.

| Style | Looks like | Pick it for | Avoid it for |
|---|---|---|---|
| [`precision-dark`](precision-dark.md) | Linear, Raycast, Vercel, Warp, Cursor, Arc | Dev tools, productivity, AI agents, anything "for builders" | Consumer wellness, kids, food |
| [`fintech-gradient`](fintech-gradient.md) | Stripe, Mercury, Ramp, Brex, Superhuman | Money, B2B platforms, APIs with a business story, trust-heavy products | Playful or underground products |
| [`calm-workspace`](calm-workspace.md) | Notion, Attio, Notion Calendar, Pitch, Loom | Notes, CRM, scheduling, education, collaboration, health admin | High-energy media, gaming |
| [`dev-platform`](dev-platform.md) | Resend, Supabase, Neon, Railway, PlanetScale, Sentry, Clerk | APIs, SDKs, infrastructure, anything with a code snippet as the hero | Non-technical audiences |
| [`editorial-luxe`](editorial-luxe.md) | Aesop, COS, Apple, Porsche, Squarespace templates | Fashion, food, travel, culture, music (classical), premium consumer, portfolios | Data-heavy apps |
| [`spec-sheet`](spec-sheet.md) | Teenage Engineering, Nothing, technical-document portfolios | Hardware, IoT, maker tools, design-forward portfolios, anything "engineered" | Mass-market consumer onboarding |
| [`bold-media`](bold-media.md) | AI music generators, streaming, sports and automotive retail, gaming | Music, video, creator tools, games, events, sports | Enterprise, health, finance |
| [`data-dashboard`](data-dashboard.md) | Datadog, Grafana, Tremor, PostHog, Mixpanel, Retool | Analytics, monitoring, climate/civic data, internal tools | Landing-page-only projects |
| [`playful-builder`](playful-builder.md) | Framer, Webflow, Lovable, Replit, Figma | No-code/AI builders, education, creative tools for beginners, community | Serious B2B, healthcare |
| [`immersive`](immersive.md) | Lusion, Immersive Garden, Spline, Rive, Awwwards winners | Art, storytelling, events, brand experiences, when 3D *is* the product | Short hackathons, data apps, accessibility-critical projects |

## Quick chooser
- **Is the user a developer?** → `dev-platform` (API product) or `precision-dark` (app product).
- **Is the hero moment a number or a chart?** → `data-dashboard` (the app) plus `precision-dark` or `fintech-gradient` (the landing page).
- **Is it about taste: fashion, food, art, music?** → `editorial-luxe` (refined) or `bold-media` (loud).
- **Is it a physical product or a maker tool?** → `spec-sheet`.
- **Does it help ordinary people organize their life or work?** → `calm-workspace`.
- **Do beginners create something with it?** → `playful-builder`.
- **Unsure?** → `precision-dark` for B2B and dev tools, `calm-workspace` for consumer. Both are hard to get wrong.

## Mixing
Lead with one direction and borrow at most one trait from another. Examples:
- A piano practice app: `calm-workspace` structure + `editorial-luxe` serif headlines.
- An AI music tool: `bold-media` landing page + `precision-dark` app shell.
- A climate data project: `data-dashboard` app + `editorial-luxe` storytelling landing page.
