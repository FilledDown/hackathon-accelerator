# Sponsor Integration

Sponsor prizes are often the most winnable prizes at a hackathon, because fewer teams meet the requirement properly.

## Prize opportunity map
For each sponsor prize, record: prize value, explicit requirements (quoted, with source), judging criteria if separate, integration effort (hours), how naturally it fits the chosen idea (1–5), and how crowded it's likely to be. Rank by (value × fit) ÷ effort. Usually aim for 1–3 sponsor prizes that fit the idea naturally. Stacking unrelated sponsors makes the product muddled.

## Essential vs bolted-on
Test: *If you removed the sponsor's technology, would the core experience break or lose its differentiator?*
- Essential: the sponsor's API performs the core transformation, such as voice synthesis in a voice app or vector search powering the main feature.
- Bolted on: logging an event to the sponsor's analytics, or a single API call that's off the demo path.
Bolted-on integrations rarely win sponsor prizes and can make the whole project look less focused.

## Integration workflow
1. Read the sponsor's official quickstart and API reference (Context7 or WebFetch). Note the SDK version, auth method, rate limits and free credits.
2. Check the event's rules and sponsor page for required usage, such as a specific product, a minimum depth, or "must use the v2 API".
3. Build a minimal "hello world" call first and verify it with real output **before** designing around it.
4. Wrap it behind one module (for example `lib/sponsors/<name>.ts`) with a timeout, retry and demo fallback.
5. Record it in `ARCHITECTURE.md` §External dependencies, and in `PROGRESS.md` as its own feature row.
6. For the submission: name the sponsor tech explicitly, say what it does in the product, and show it in the demo. Include a sentence on why this sponsor's tech was the right choice.

## Common pitfalls
- Free-tier rate limits hit during the live demo. Fix: cache, use demo mode, or pre-warm.
- API keys committed to a public repo. Fix: env vars, and the security-reviewer checks before the repo goes public.
- Using a deprecated endpoint from an old tutorial. Fix: always use the current official docs.
- Claiming a sponsor feature that the code doesn't actually call.
