# Changelog

All notable changes to this plugin. Versions follow [semantic versioning](https://semver.org): fixes bump the last number, new features the middle one, breaking changes the first.

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
