---
name: hackathon-accelerator
description: Shortcut that starts or resumes the Hackathon Accelerator plugin. Type /hackathon-accelerator, optionally followed by a hackathon URL or a request.
argument-hint: "[hackathon URL or what you need]"
disable-model-invocation: true
---

Load and follow the `hackathon-accelerator:hackathon-accelerator` skill from the hackathon-accelerator plugin for this request:

$ARGUMENTS

If the request above is empty: check the current folder for `PROGRESS.md` or `HACKATHON_BRIEF.md`. If they exist, resume the project and give a status report with the top 3 next actions. If not, start Phase 1 by asking for the hackathon URL, the deadline with timezone, team size and the team's skills.

If the plugin skill isn't available, tell the user to install it with `/plugin marketplace add FilledDown/hackathon-accelerator` and then `/plugin install hackathon-accelerator@hackathon-accelerator`.
