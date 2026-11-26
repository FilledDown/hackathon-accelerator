#!/usr/bin/env node
// Claude Code hooks for hackathon-accelerator. Never blocks: errors are swallowed, exit code is always 0.
//   start   (PreToolUse on Agent/Task)  -> append a start line to <project>/.hackathon/agent-log.jsonl
//   stop    (SubagentStop)              -> append a stop line with the agent's summary
//   session (SessionStart)              -> in a hackathon project, add a short reminder to Claude's context
//                                          so the team, the UI defaults and real delegation apply automatically.
// Only active in projects that have PROGRESS.md or HACKATHON_BRIEF.md. Prints nothing anywhere else.
const fs = require("fs");
const path = require("path");

const MODES = ["start", "stop", "session"];
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
    "4. After agents run, show who did what from the real log: python <skill>/scripts/team_log.py . --last 10 (use python3 on macOS/Linux).",
  ].join("\n");
}

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", c => (raw += c));
process.stdin.on("end", () => {
  try {
    let input = {};
    try { input = JSON.parse(raw || "{}"); } catch (_) { input = {}; }
    const root = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();
    const isHackathon = ["PROGRESS.md", "HACKATHON_BRIEF.md"].some(f => fs.existsSync(path.join(root, f)));
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
