#!/usr/bin/env python3
"""Install the /hackathon-accelerator shortcut for your user account.

Claude Code namespaces plugin skills, so the plugin's skill is /hackathon-accelerator:hackathon-accelerator.
This copies a small forwarding skill to ~/.claude/skills/hackathon-accelerator so that typing
/hackathon-accelerator works in every project. The forwarding skill only runs when you type it
(disable-model-invocation), so it never competes with the plugin skill.

Usage:
  python tools/install_shortcut.py            install
  python tools/install_shortcut.py --force    overwrite an existing ~/.claude/skills/hackathon-accelerator
  python tools/install_shortcut.py --remove   uninstall
Restart Claude Code afterwards.
"""
import argparse
import shutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "shortcut" / "hackathon-accelerator"
DST = Path.home() / ".claude" / "skills" / "hackathon-accelerator"
MARK = "Shortcut that starts or resumes the Hackathon Accelerator plugin"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--remove", action="store_true")
    args = ap.parse_args()

    existing = DST / "SKILL.md"
    is_ours = existing.exists() and MARK in existing.read_text(encoding="utf-8", errors="replace")

    if args.remove:
        if not DST.exists():
            print("Shortcut not installed; nothing to remove.")
        elif is_ours or args.force:
            shutil.rmtree(DST)
            print(f"Removed {DST}. Restart Claude Code.")
        else:
            print(f"{DST} isn't the shortcut (a different skill lives there). Not removing it; use --force if you're sure.")
            return 1
        return 0

    if DST.exists() and not (is_ours or args.force):
        print(f"{DST} already exists and isn't the shortcut. Not overwriting it; use --force to replace it.")
        return 1
    if DST.exists():
        shutil.rmtree(DST)
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, DST)
    print(f"Installed {DST}\nRestart Claude Code, then type /hackathon-accelerator in any project.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
