# Agent Collaboration Protocol

How the council works together without wasting context or causing merge conflicts.

## Contents
1. Mechanics: what Claude Code actually supports
2. Delegation brief (what every agent gets)
3. Handoff report (what every agent returns)
4. File ownership and parallel work
5. Disagreement and escalation
6. Agent Teams (optional)
7. Anti-patterns

## 1. Mechanics

- Subagents run in their own context. They see only the brief you give them plus the files they read. **They cannot spawn other subagents and they cannot talk to the user.** All coordination goes through the main session (the orchestrator) and the shared project files.
- So "agent A communicates with agent B" really means: A writes findings to a file or its report, and the orchestrator passes the relevant part to B.
- Several Agent tool calls in one message run in parallel. Use that only for work that is truly independent (§4).
- An agent's tool permissions come from its frontmatter. Research and review agents have restricted tools. Builder agents inherit all tools, including any MCP servers, so they can use Context7, Serena, Playwright and the like when those are installed.

## 2. Delegation brief

Every delegation should include the following. Short is fine. Missing context is the main reason agents produce generic work.

```
ROLE TASK: <one sentence, the specific deliverable>
PROJECT ROOT: <path>
READ FIRST: <specific files: PROGRESS.md, HACKATHON_BRIEF.md §Judging, src/api/...>
CONTEXT: <2-5 lines: idea, deadline/time left, rubric priorities, relevant decisions>
CONSTRAINTS: <files you may edit / must not edit; time box; stack>
INTERFACES: <contract with parallel agents, if any>
OUTPUT: <file path to write, or "report only">, format expectations
DONE WHEN: <objective completion condition>
```

## 3. Handoff report

Every agent ends with this structure, kept tight:

```
## Result
<what was produced; file paths>
## Status of claims
VERIFIED: <things actually run/checked, with the command or source>
UNVERIFIED / ASSUMED: <things believed but not checked>
## Issues & risks
<anything that threatens score, demo or deadline>
## Disagreements
<where this agent thinks a prior decision is wrong, with evidence>
## Recommended next steps
<max 3; may name another agent: "recommend security-reviewer check auth.ts">
```

The orchestrator summarizes this for the user in a few lines and updates `PROGRESS.md` and `DECISION_LOG.md`. Agents must not paste whole reports at the user.

## 4. File ownership and parallel work

Run agents in parallel only when **all** of these hold:
1. Their editable file sets don't overlap (for example `frontend-engineer` owns `app/web/**` and `backend-engineer` owns `app/api/**`).
2. Every shared interface (API routes and payloads, shared types, DB schema, env var names) is **written down before** they start, usually in `ARCHITECTURE.md` §Interfaces or a `shared/types` file that one agent owns.
3. Neither agent needs the other's output to finish.

Otherwise run them one after another. A good default for engineering is: architect defines the contract → backend and frontend build in parallel → integration is done by one agent (or the main thread) → QA.

Write the ownership down in the brief: "You may edit only: X. Treat Y as read-only. If Y must change, report it, don't edit it."

Research and review agents may run in parallel freely, because they don't edit shared code. Each one writes only to its own report file under `research/` or `reviews/`.

## 5. Disagreement and escalation

- Agents are expected to challenge weak assumptions, including the orchestrator's and the user's. A disagreement goes in the report's "Disagreements" section with evidence. Opinion alone doesn't count.
- The orchestrator resolves it using expected judging score per remaining hour, with heavy penalties for demo risk. See SKILL.md §6.
- Log the decision in `DECISION_LOG.md`:

```
## D-007 — <short title> (<date time>)
Context: ...
Options: A) ... B) ... C) ...
Evidence: <agent>: ..., <agent>: ...
Decision: B, because ...
Owner: orchestrator | user-override
Revisit if: <condition>
```

## 6. Agent Teams (optional)

Some Claude Code versions have an experimental Agent Teams feature, where teammates message each other directly. It's usually turned on with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Check whether it's available before relying on it. When it is, it's worth using for real debates, such as Phase 2 idea critique (generator vs originality critic vs feasibility analyst) or Phase 8 judge panels. Everything else works fine with ordinary subagents, and the whole system works without Teams.

## 7. Anti-patterns

- Activating the whole council for one question.
- Two agents editing the same file at the same time.
- Giving an agent a one-line brief and expecting project-specific output.
- Agents that restate the brief instead of producing the deliverable.
- Re-running research that already exists in `research/` or the brief.
- Agent reports copied to the user verbatim.
