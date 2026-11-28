<!-- hackathon-accelerator:start -->
## Hackathon project (managed by hackathon-accelerator)
This repository is a hackathon submission.
Accelerator skill dir: {{SKILL_DIR}}

Apply these automatically. The user doesn't need to name a skill or ask for them:
- Route every request through the `hackathon-accelerator` skill (load it if needed). Read `PROGRESS.md` before answering anything about what's built, what's broken, or the deadline.
- Coding: follow the hackathon coding assistant protocol (`{{CODING_ASSISTANT}}`): understand before editing, smallest reliable fix, verify by running, explain briefly, keep `PROGRESS.md` statuses honest (VERIFIED only when actually run).
- UI: always use the `hackathon-ui` skill with its defaults on: animations on every interactive component, licensed images where the page shows visual subjects, loading/empty/error states, mobile layout, screenshots and the audit.
- Ideas, judging, research, QA and pitch review: spawn the real specialist agents with the Agent tool (ideas start automatically after the brief). Never write their verdicts yourself. If no agents ran, say "my own read".
- Planned features go to the builder agents (frontend, backend, ai-ml, database, api-integration) in parallel; you integrate and verify.
- Read `.hackathon/brain/BRAIN.md` before exploring code; refresh it with `brain.py . --quiet`, save durable facts with `--note`.
- Game jam: confirm the engine (Roblox, Godot, Unity, Unreal) is connected to Claude Code first; steps in the skill's `references/game-jam.md`.
- Judge feature requests against `HACKATHON_BRIEF.md` (rubric, deadline) and `PRODUCT_SPEC.md` (frozen scope). Push back briefly when it hurts the submission, respect the user's call, and log major decisions in `DECISION_LOG.md`.
<!-- hackathon-accelerator:end -->
