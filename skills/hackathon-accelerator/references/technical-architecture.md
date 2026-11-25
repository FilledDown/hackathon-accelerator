# Technical Architecture for Hackathons

Choose boring, fast and familiar everywhere except the differentiator.

## Principles
1. **Use the team's existing skills.** A stack the team knows beats a "better" stack they're learning, unless learning a sponsor tech is the point.
2. **Have as few deployable pieces as possible.** A single full-stack app (for example Next.js with API routes, or FastAPI serving a frontend) is better than separate services until there's a real reason to split.
3. **Use managed services for the undifferentiated parts**: auth, DB, storage, hosting (for example Supabase, Firebase, Vercel, Render, Railway). Confirm free-tier limits and that the service is reachable from the venue.
4. **Spend engineering effort on the differentiator**, and make it visible.
5. **Define interfaces first**: API routes, payload shapes, DB schema and env var names go in `ARCHITECTURE.md` §Interfaces before parallel work starts.
6. **Make it demo-safe by design**: seeded data, deterministic demo mode, timeouts and fallbacks on every external call (see demo-engineering.md).

## ARCHITECTURE.md must contain
- A one-paragraph overview and a diagram (Mermaid is fine).
- Components, and which agent or person owns which directory.
- §Interfaces: routes with request/response examples, shared types, DB schema, events.
- External dependencies: each with a docs link, auth method, rate limits and fallback.
- Env vars: the name and purpose of each (never the values). Keep `.env.example` in sync.
- Demo mode: how to run with seeded data and no external dependencies.
- Known shortcuts (hackathon debt) that are fine for now.

## Verify before you build
Look up every unfamiliar library or API in the official docs (Context7 if detected, otherwise WebFetch the docs) **before** writing integration code. Record the version used. Never assume a method, parameter or model name exists.

## Quick decision guides
- **Real-time** (collaboration, live updates): use a managed realtime product (Supabase Realtime, Firebase, Liveblocks, Pusher, Ably) before building raw WebSockets. Use plain WebSockets only for simple broadcast inside an app you already control.
- **AI features**: call a hosted model API. Stream responses for UX, cache demo responses, and add a timeout with a canned fallback. Training a model is rarely worth hackathon time unless it *is* the differentiator and you have the data.
- **RAG**: start with a small, curated corpus. pgvector or a managed vector database is enough. Evaluate retrieval quality on the demo queries specifically.
- **Mobile**: a responsive web app or PWA is usually better than native unless native capabilities are the point.
- **Data**: SQLite or Postgres with a seed script. The seed script is a demo asset, so make the data realistic.

## Code standards (hackathon-appropriate)
- Use clear module boundaries and small files. Don't build abstraction layers "for later".
- Validate input at the API boundary. Return useful error messages; they help debugging during the demo.
- Keep secrets in env vars only. `.gitignore` the `.env` file from the first commit.
- Each component has a single, documented command to start it. The README's "Run it" section must work on a clean clone.
