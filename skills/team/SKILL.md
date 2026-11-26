---
name: team
description: "Show the hackathon team and which agents did what in this project."
disable-model-invocation: true
---

Show the user their hackathon team and its activity.

1. Run `python3 <team-dir>/../hackathon-accelerator/scripts/team_log.py . --roster` from the project root. `<team-dir>` is this skill's base directory. On Windows, use `python` if `python3` isn't found.
2. Show the output as is: the activity table, the most active agents, and the roster. Don't add commentary beyond one line.
3. If the user passed a request with the command ($ARGUMENTS), answer it from the log. For example, "what did the security reviewer find?": read the matching row, then the report file in `reviews/` or `research/`.
4. If nothing has been logged yet, say that agents get logged automatically once they run in a project with `PROGRESS.md`, and suggest starting with `/hackathon-accelerator:hackathon-accelerator`.
