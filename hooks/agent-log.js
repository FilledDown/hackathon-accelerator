#!/usr/bin/env node
// Claude Code hooks for hackathon-accelerator. Never blocks: errors are swallowed, exit code is always 0.
//   start   (PreToolUse on Agent/Task)  -> append a start line to <project>/.hackathon/agent-log.jsonl
//   stop    (SubagentStop)              -> append a stop line with the agent's summary
//   session (SessionStart)              -> in a hackathon project, add a short reminder to Claude's context
//                                          so the team, the UI defaults and real delegation apply automatically.
//   prompt  (UserPromptSubmit)          -> when a message matches a task (ideas, build, deck, video, explain, Q&A,
//                                          game jam), add a one-line routing hint naming the agents to spawn.
//                                          Silent otherwise; can never block a prompt.
// Only active in projects that have PROGRESS.md or HACKATHON_BRIEF.md. Prints nothing anywhere else.
const fs = require("fs");
const path = require("path");

const MODES = ["start", "stop", "session", "prompt"];
const mode = MODES.includes(process.argv[2]) ? process.argv[2] : "start";

function sessionContext() {
  const skill = path.join(__dirname, "..", "skills", "hackathon-accelerator");
  const ui = path.join(__dirname, "..", "skills", "hackathon-ui");
  return [
    "This folder is a hackathon project managed by the hackathon-accelerator plugin.",
    `Accelerator skill: ${skill}${path.sep}SKILL.md · UI skill: ${ui}${path.sep}SKILL.md`,
    "Apply these automatically, without the user naming a skill or asking for them:",
    "1. Route every request through the hackathon-accelerator skill (load it if it isn't loaded). Coding stays in this thread under its coding protocol.",
    "2. Any UI work follows the hackathon-ui skill with its defaults ON: a chosen style, tokens, component animations on every interactive element, licensed images where the page has visual subjects, loading/empty/error states, mobile layout, reduced-motion support, screenshots and ui_audit.py. Never wait to be asked for these.",
    "3. Delegation is real: when a step names specialist agents (judging, idea critique, research, QA, pitch review), spawn them with the Agent tool (subagent_type hackathon-accelerator:<name>). Never write their verdicts yourself or present your own opinion as theirs. If you answer without agents, say so plainly.",
    "4. Ideas are generated and critiqued by the idea agents automatically (never brainstorm alone); planned features go to the builder agents; you integrate and verify.",
    "5. Read .hackathon/brain/BRAIN.md before exploring code (refresh: python <skill>/scripts/brain.py . --quiet). Save durable facts with --note.",
    "6. After agents run, show who did what from the real log: python <skill>/scripts/team_log.py . --last 10 (use python3 on macOS/Linux).",
  ].join("\n");
}

const ROUTES = [
  [/\b(game ?jam|ludum dare|gmtk|itch\.io|roblox|godot|unity|unreal)\b/i,
    "Game jam mode: game-designer leads. First confirm the engine is connected to Claude Code (/mcp); if not, give the steps in references/game-jam.md Step 0."],
  [/\b(idea|ideas|brainstorm|what (should|could) we build|pivot|concept)\b/i,
    "Spawn the idea agents (problem-discovery-researcher, idea-generator, then originality-critic + feasibility-analyst + idea-scoring-analyst) with the Agent tool. Don't brainstorm alone."],
  [/\b(judge|judging|score|critique|rate|feedback on|is (this|it) good|would (we|it) win)\b/i,
    "Spawn real critics with the Agent tool (originality-critic, feasibility-analyst, red-team-judge; presentation-critic for pitch material). Don't give the verdict yourself."],
  [/\b(deck|slides?|presentation|pitch)\b/i,
    "Deck: time_plan.py first, then slide-deck-designer (Canva if connected) + judge-qa-coach in parallel; check with deck_audit.py. Dense slides: claim + proof, framed real screenshots."],
  [/\b(demo video|video|trailer|teaser|record( a)? demo)\b/i,
    "Video: demo-video-producer writes the full script + video/shots.json, then runs scripts/demo_video.py (finished ~30 s MP4)."],
  [/\b(q ?& ?a|questions judges|judge questions|practice questions|what will (they|judges) ask)\b/i,
    "Q&A: spawn judge-qa-coach (submission/QA.md), then offer a live drill."],
  [/\b(explain|how does|walk me through|what does (this|the) .{0,30}(do|mean)|understand the code)\b/i,
    "Explain: spawn project-explainer (reads BRAIN.md, writes docs/EXPLAINER.md or a deep dive)."],
  [/\b(implement|build (the|a|an|our|this|it|out)\b|add (a|the)? ?(feature|screen|page|endpoint|api)|create the|make the (app|backend|frontend))/i,
    "Build: delegate BUILD_PLAN items to the builder agents (frontend/backend/ai-ml/database/api-integration) in parallel on disjoint files; you integrate and verify. Small fixes stay in this thread."],
];

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", c => (raw += c));
process.stdin.on("end", () => {
  try {
    let input = {};
    try { input = JSON.parse(raw || "{}"); } catch (_) { input = {}; }
    const root = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();
    const isHackathon = ["PROGRESS.md", "HACKATHON_BRIEF.md"].some(f => fs.existsSync(path.join(root, f)));
    if (mode === "prompt") {
      const text = String(input.prompt || "").slice(0, 2000);
      if (!isHackathon) {
        if (/\b(hackathon|game ?jam|devpost|ludum dare|gmtk)\b/i.test(text))
          process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: "UserPromptSubmit",
            additionalContext: "hackathon-accelerator: this sounds like a hackathon or game jam. Use the hackathon-accelerator skill (start at Phase 1; its agents do the research and ideas)." } }));
        return;
      }
      const hits = ROUTES.filter(([rx]) => rx.test(text)).map(([, hint]) => hint).slice(0, 2);
      if (hits.length)
        process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: "UserPromptSubmit",
          additionalContext: "hackathon-accelerator routing: " + hits.join(" ") } }));
      return;
    }
    if (!isHackathon) return;

    if (mode === "session") {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: sessionContext() },
      }));
      return;
    }

    const clean = s => String(s || "").replace(/^hackathon-accelerator:/, "");
    const entry = { ts: new Date().toISOString(), event: mode, session: input.session_id || null };
    if (mode === "start") {
      const ti = input.tool_input || {};
      entry.agent = clean(ti.subagent_type || "general-purpose");
      entry.task = String(ti.description || "").slice(0, 160);
      entry.tool_use_id = input.tool_use_id || null;
    } else {
      entry.agent = clean(input.agent_type || "unknown");
      entry.agent_id = input.agent_id || null;
      const msg = String(input.last_assistant_message || "").replace(/\s+/g, " ").trim();
      entry.summary = msg.slice(0, 400);
    }
    const dir = path.join(root, ".hackathon");
    fs.mkdirSync(dir, { recursive: true });
    fs.appendFileSync(path.join(dir, "agent-log.jsonl"), JSON.stringify(entry) + "\n", "utf8");
  } catch (_) {
    /* never break the session */
  } finally {
    process.exitCode = 0;
  }
});
