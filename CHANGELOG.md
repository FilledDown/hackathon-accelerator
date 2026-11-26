# Changelog

All notable changes to this plugin. Versions follow [semantic versioning](https://semver.org): fixes bump the last number, new features the middle one, breaking changes the first.

## [1.3.1] - 2026-11-25

### Changed
- **Automatic by default.** A new `SessionStart` hook tells Claude, in hackathon projects only, to route every request through the team without a slash command. UI work always gets animations, licensed images, states, a mobile layout and the audit, without being asked. Decks always get a time plan and Q&A slides.
- **Real delegation.** Judging, idea critique, research, QA and pitch review must actually spawn the specialist agents. The orchestrator may not write an agent's verdict itself, labels its own opinions as "my own read", and builds the 👥 summary from the real agent log.
- New "Judge / critique" route: "is this idea good?" spawns `originality-critic`, `feasibility-analyst` and `red-team-judge` in parallel.
- The CLAUDE.md block is rewritten with the same rules and refreshes itself whenever its text changes, not only when the plugin path moves.

### Fixed
- The CLAUDE.md block refresh could crash on Windows paths containing `\U` and similar sequences (regex replacement escaping).

## [1.3.0] - 2026-11-25

### Added
- **Component animations** (`hackathon-ui/references/animations.md`): recipes for buttons, links, cards, images, text, tabs, toggles, inputs, lists, feedback and backgrounds, in CSS, React (Motion) and vanilla (anime.js v4) versions. Covers React Bits and Kokonut UI install patterns, and ECharts for the one chart a product needs. **Motion gallery** demo page with every animation working.
- **Licensed images:** `fetch_images.py` downloads photos from Openverse (no key), Pexels or Unsplash (free keys) and writes `CREDITS.md` automatically. New `references/images.md` covers art direction, optimization and rules.
- **Product-first UI:** new "Product screens" patterns (onboarding, input → work → result, drop zone, chat, mobile shell, before/after, share card). The dashboard style is now a reference for a single data view, not a default.
- **`/hackathon-accelerator:team`** (and `/hackathon-team` with the shortcuts) shows the roster and an activity table of which agent did what, when, the result and how long it took. Logged automatically by a plugin hook (`PreToolUse` on the Agent tool + `SubagentStop`), only in hackathon projects. `team_log.py --add` records main-session work.
- **Timed presentations:** `time_plan.py` budgets a 2/3/5-minute pitch (live demo, recorded demo, or video-only) in seconds, words and slides, and checks your script against it.
- **Pitch deck:** Canva via the Canva MCP when it's connected. Otherwise an offline HTML deck template with a per-slide timer, speaker notes, PDF export and Q&A appendix slides. New `references/presentation.md`.
- **Demo video pipeline:** `record-demo.mjs` (Playwright: drives the real app with a visible cursor, click ripples, captions, spotlight), `render-cards.mjs` + `cards.html` (title, problem, impact and end cards), and `make_video.py` (ffmpeg stitch to 1080p MP4 with crossfades, music or voiceover, and a time-limit check). New `references/demo-video.md`.
- New README art (banner, how-it-works, phases, deck and video previews, an animation GIF), rendered from `docs/src/readme-art.html` with `tools/render-showcases` (`npm run readme-art`).
- Environment detection now finds Canva, ffmpeg and image-generation tools.

### Changed
- **Token usage:** always-loaded agent and skill descriptions cut from about 3,200 to about 1,000 tokens. The orchestrator SKILL.md was rewritten from about 4,750 to about 3,050 tokens while adding the new features. Lean mode is now the default: capped briefs and handoffs, scripts instead of re-reading docs, and the option to run read-only research agents on a cheaper model.
- Phase 7 now covers the time plan, deck (Canva or HTML) and video. The presentation agents and the coding assistant know the new tools.
- The shortcut installer installs every shortcut in `shortcut/` and never overwrites other skills.

### Fixed
- The deck template responds to `#slide` hash changes after load.

## [1.2.0] - 2026-11-25

### Added
- **hackathon-ui skill** (`/hackathon-accelerator:hackathon-ui`): a 7-step UI process (understand → pick a style → tokens → screens → states and motion → screenshot and audit → one polish pass).
- **10 style directions** reverse-engineered from top product sites: precision-dark, fintech-gradient, calm-workspace, dev-platform, editorial-luxe, spec-sheet, bold-media, data-dashboard, playful-builder and immersive. Each has tokens, type, layout signatures, component details, motion, signature moves, don'ts and a starter prompt.
- **9 working demo pages** (original products, invented copy) plus 1440×900 screenshots Claude can look at before choosing a style.
- References: foundations (type scale, spacing, color, radius, tokens, free font pairings), components (nav, hero, product frame, bento, app shell, command palette, tables, states, charts), motion, anti-slop checklist and inspiration sources.
- `ui_audit.py`: flags placeholder copy, the default purple→blue gradient, images without alt text, hardcoded colors, too many font sizes, generic marketing copy, emoji in headings and buttons, removed focus outlines, missing reduced-motion handling, `transition: all` and heavy glassmorphism.
- `design/DIRECTION.md` template, created by `init_project.py`.
- `tools/render-showcases`: regenerates the screenshots with local fonts.
- **Naming guide** (`references/naming.md`): no more generic two-word CamelCase names like "FloodLine" or "RoadReady". Names now come from varied patterns (suffix blends like Roadify, mash-ups like Breathmera, truncations like Engen, real words like Fixit, invented words), and the shortlist is collision-checked before the user picks. Used by the idea generator in Phase 2 and the product manager in Phase 3.

### Changed
- Phases 3 and 5 now use hackathon-ui: the design direction is one of the 10 styles, and the Phase 5 gate requires `ui_audit.py` to show no errors plus a screenshot review at 1440 and 390 wide.
- The design agents, frontend engineer, demo experience engineer, slide designer and coding assistant now load hackathon-ui for UI work.
- README: new "UI that doesn't look AI-generated" section with the style gallery.

### Fixed
- CI: skip Python 3.9 on Ubuntu, because Ubuntu 26.04 runners no longer provide it. Windows and macOS still test 3.9.

## [1.1.0] - 2026-11-25

### Added
- `/hackathon-accelerator` shortcut. Run `python tools/install_shortcut.py`, or ask Claude Code to "install the hackathon-accelerator shortcut". It never overwrites a different skill and can be removed with `--remove`.
- GitHub Actions workflow that runs the script tests on Windows, macOS and Linux (Python 3.9 and 3.13), and runs `claude plugin validate`.
- README rewrite with diagrams, example prompts, the full agent roster, real script output, Windows notes and an FAQ.
- This changelog.

### Fixed
- **Windows:** every file read and write now uses UTF-8 explicitly. Before, the templates (which contain characters like `—` and `✅`) could fail to load with the default Windows encoding.
- **Windows:** script output is forced to UTF-8, so the reports don't crash when printed to a cp1252 console or pipe.
- **Windows:** `detect_environment.py` now finds `claude.cmd`, so it can list MCP servers.
- **Windows:** timezone names like `America/Denver` work without the `tzdata` package, using a built-in table of standard offsets. `init_project.py` warns when it has to fall back.
- The skill now tells Claude to use `python` or `py -3` when `python3` isn't available.

## [1.0.0] - 2026-11-25

### Added
- First release: the orchestrator skill (8 phases, routing, quality gates, live scorecard), 40 specialist agents, 9 reference playbooks, project memory templates, and 6 helper scripts with tests.
