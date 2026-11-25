# MVP Guardrails

Scope discipline. Most hackathon projects lose because they're unfinished, not because the idea was too small.

## The MVP formula
**MVP = one core user journey, end to end + one differentiator + required sponsor integrations + demo fallbacks.**
Everything else is out of scope until the MVP is `VERIFIED`.

## Time budget (as a fraction of the total time remaining)
| Activity | Share |
|---|---|
| Recon + ideation + spec (Phases 1–3) | 10–15% |
| Core build (Phase 4) | 45–55% |
| Polish (Phase 5) | 10–15% |
| QA + fixes (Phase 6) | 10% |
| Pitch, video, submission (Phases 7–8) | 15–20% |

For short events (≤24h), shrink ideation hard, but **never** shrink submission and pitch below about 15%. Teams regularly lose because the video or Devpost entry was rushed in the last 20 minutes.

## Checkpoints (based on % of time used)
- **25%**: the core journey has a skeleton running end to end (it can be ugly, with stubbed parts).
- **50%**: the core journey works for real. If not, cut the differentiator's scope now.
- **70%**: **feature freeze.** After this, only fixes, polish and demo hardening.
- **85%**: submission materials drafted. The video is recorded, or its script is final.
- **95%**: submit. Don't submit in the last 5 minutes, because upload portals get slow.

## Scope-change test
Answer these before adding anything after Phase 3:
1. Which rubric criterion does it raise, and by how much (on the 1–9 scale)?
2. How many hours will it take, realistically ×1.5?
3. Can it be demoed reliably?
4. What gets cut or delayed to make room?
5. Does it risk breaking something already `VERIFIED`?

Add it only if expected score gain per hour beats the next item already in the build plan. Log it in `DECISION_LOG.md` either way.

## When behind schedule: what to cut, in order
1. Nice-to-have features.
2. Settings, profiles, auth (use a seeded demo user instead, unless the rules or the core journey need auth).
3. Breadth of the differentiator: keep one impressive path, drop the variants.
4. Production concerns that judges won't see (scaling, full test coverage). Keep tests on the demo path.
5. **Never cut:** the core journey, required sponsor usage, demo fallback, submission requirements.

## Simulated functionality
Mocking is legitimate for things outside the demo's core claim, such as a fake payment step. It must be:
- marked `SIMULATED` in `PROGRESS.md`
- never described as working in the Devpost or pitch (say "mocked for the demo" when asked)
- never the differentiator itself
