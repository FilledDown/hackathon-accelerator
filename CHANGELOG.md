# Changelog

All notable changes to this plugin. Versions follow [semantic versioning](https://semver.org): fixes bump the last number, new features the middle one, breaking changes the first.

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
