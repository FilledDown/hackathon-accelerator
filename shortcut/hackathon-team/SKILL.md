---
name: hackathon-team
description: Shortcut that shows the Hackathon Accelerator team and which agents did what in this project. Type /hackathon-team.
argument-hint: "[optional question, e.g. what did the security reviewer find?]"
disable-model-invocation: true
---

Load and follow the `hackathon-accelerator:team` skill from the hackathon-accelerator plugin. Pass along this request, if any:

$ARGUMENTS

If the plugin skill isn't available, tell the user to install it with `/plugin marketplace add FilledDown/hackathon-accelerator` and then `/plugin install hackathon-accelerator@hackathon-accelerator`.
