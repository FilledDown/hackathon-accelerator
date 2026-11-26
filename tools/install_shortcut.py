#!/usr/bin/env python3
"""Install the plain shortcut commands for your user account.

Claude Code namespaces plugin skills (/hackathon-accelerator:hackathon-accelerator). This copies small
forwarding skills into ~/.claude/skills/ so these work in every project:

  /hackathon-accelerator   start or resume the accelerator
  /hackathon-team          show the team and which agents did what

The shortcuts only run when you type them (disable-model-invocation), so they never compete with the plugin.

Usage:
  python tools/install_shortcut.py            install (or update) all shortcuts
  python tools/install_shortcut.py --force    overwrite existing skills with the same names
  python tools/install_shortcut.py --remove   uninstall
Restart Claude Code afterwards.
"""
import argparse
import shutil
import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent / "shortcut"
DST_ROOT = Path.home() / ".claude" / "skills"
MARK = "Shortcut that"   # every shortcut's description starts with this


def is_ours(dst: Path) -> bool:
    f = dst / "SKILL.md"
    return f.exists() and MARK in f.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--remove", action="store_true")
    args = ap.parse_args()
    code = 0
    for src in sorted(p for p in SRC_ROOT.iterdir() if (p / "SKILL.md").exists()):
        dst = DST_ROOT / src.name
        if args.remove:
            if not dst.exists():
                print(f"/{src.name}: not installed")
            elif is_ours(dst) or args.force:
                shutil.rmtree(dst)
                print(f"/{src.name}: removed")
            else:
                print(f"/{src.name}: {dst} is a different skill, not removing it (use --force if you're sure)")
                code = 1
            continue
        if dst.exists() and not (is_ours(dst) or args.force):
            print(f"/{src.name}: {dst} already exists and isn't this shortcut, skipped (use --force to replace)")
            code = 1
            continue
        if dst.exists():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst)
        print(f"/{src.name}: installed at {dst}")
    print("Restart Claude Code to pick up the changes.")
    return code


if __name__ == "__main__":
    sys.exit(main())
