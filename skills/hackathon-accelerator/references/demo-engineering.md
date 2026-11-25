# Demo Engineering

The demo is the product, as far as judges are concerned. Engineer it the way you'd engineer production.

## The demo path
Write the exact click-by-click path in `submission/DEMO_SCRIPT.md` early, in Phase 3. Every engineering priority after that serves this path. Anything a judge won't see during the demo is lower priority.

## Reliability techniques
1. **Seeded, realistic data.** A seed script that creates believable users, content and history. Realistic data makes impact obvious. Lorem ipsum makes it look unfinished.
2. **Demo mode flag** (for example `DEMO_MODE=1`): deterministic inputs, cached external responses, fixed random seeds, a pre-logged-in demo user. The live path still runs normally. Demo mode is a safety net, not a fake.
3. **Fallbacks on every external call**: a timeout of 5–10 seconds, then a cached or canned response with a subtle indicator. Tag fallback behavior `SIMULATED` in PROGRESS.md and be honest about it if asked.
4. **Pre-warm** serverless functions, model endpoints and caches before presenting.
5. **Offline plan.** Venue Wi-Fi fails. Know what still works offline. Have a phone hotspot available. Keep a recorded backup video ready.
6. **Cold-start rehearsal.** Run the demo from a fresh browser profile and a freshly restarted server three times in a row. That's the Phase 6 gate.
7. **Reset script.** One command that restores the demo state between judge visits.

## Making the differentiator land
- Build up to it: show the problem state first, then the moment the product changes it.
- Make the work visible: progress indicators, intermediate results, a "behind the scenes" toggle that shows what the model or algorithm did.
- Keep it under 10 seconds of waiting, or fill the wait with narration or a visible process.

## Recording the demo video
- Follow the event's length limit exactly. Many cap at 2–3 minutes, and judges may stop watching early anyway.
- Record at 1080p or higher. Zoom or crop so text is readable. Use a clean browser with no bookmarks bar or notifications.
- Narrate problem → demo → how it works → impact. The script goes in `DEMO_SCRIPT.md`, with timestamps.
- If the rules say "live demo", a recording is only a backup. Don't present it as live.
