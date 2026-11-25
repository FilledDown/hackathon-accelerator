# hackathon-accelerator

A Claude Code plugin that gives you a whole hackathon team: an orchestrator skill plus 40 specialist agents. It takes a project from an empty repo to a competition-ready submission, covering research, idea scoring, architecture, coding help, design polish, QA, the Devpost entry, pitch, demo script and a mock judging round.

## Install

In Claude Code:
```
/plugin marketplace add /hackathon-accelerator
/plugin install hackathon-accelerator@hackathon-accelerator
```
Restart Claude Code and you're set. Python 3 is needed for the helper scripts. They use the standard library only.

To try it locally without GitHub: `claude --plugin-dir /path/to/hackathon-accelerator`.

## Use

Open Claude Code in your hackathon project folder and run:
```
/hackathon-accelerator:hackathon-accelerator help me win https://<hackathon page>
```
You can also just describe what you want ("I'm doing PolarHacks this weekend, help me plan"). The skill triggers on hackathon requests by itself.

It sets up the project memory files, researches the rules and judging criteria, and works through 8 phases: recon → ideas → spec → build → design → QA → pitch & submission → mock judging. You can start at any phase.

**Coding help at any time.** Once the project is set up, ask ordinary questions ("why is my API returning 500?", "add login"). The project `CLAUDE.md` loads the coding-assistant rules in every session. For a session dedicated to coding: `claude --agent hackathon-accelerator:hackathon-coding-assistant`.

Other useful prompts: "where are we?" (time left and next steps), "simulate judging", "run the final submission check".

## What's inside
```
.claude-plugin/          plugin.json + marketplace.json
skills/hackathon-accelerator/
  SKILL.md               orchestrator: routing, phases, quality gates, scorecard
  references/            9 playbooks loaded on demand (rubrics, MVP scope, demo engineering, pitch...)
  scripts/               init_project, detect_environment, fetch_hackathon_docs,
                         extract_submission_requirements, validate_submission, generate_project_report
  assets/templates/      PROGRESS.md, HACKATHON_BRIEF.md, DEVPOST.md, ... (project memory)
agents/                  40 agents: council, strategy, innovation, engineering, design, presentation
evals/                   3 test cases for `claude plugin eval`
```

**Honesty is enforced by a script.** Features are tracked as VERIFIED / IMPLEMENTED / PLANNED / SIMULATED in `PROGRESS.md`. `validate_submission.py` fails the submission if it claims unverified features, leaves placeholders in, is missing a required deliverable, or contains a committed API key.

Optional integrations (Context7, Firecrawl, Playwright, GitHub MCP, Serena, design skills, and others) are used only when `detect_environment.py` finds them installed.

## Development
```bash
python3 skills/hackathon-accelerator/scripts/tests/validate_system.py      # structure check
python3 -m unittest discover -s skills/hackathon-accelerator/scripts/tests # script tests
claude plugin validate .                                                   # Claude Code's validator
```

## License
MIT
