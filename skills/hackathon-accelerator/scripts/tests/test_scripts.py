#!/usr/bin/env python3
"""Fixture-based tests for the hackathon-accelerator scripts. Run: python3 -m unittest discover -s <this dir>"""
import json
import shutil
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
FIX = HERE / "fixtures"
NOW = "2026-03-15T12:00:00-07:00"


def run(script, *args):
    p = subprocess.run([sys.executable, "-I", str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout, p.stderr


class Extract(unittest.TestCase):
    def test_html_rules(self):
        code, out, err = run("extract_submission_requirements.py", FIX / "rules_sample.html")
        self.assertEqual(code, 0, err)
        r = json.loads(out)
        crit = {c["name"]: c["weight"] for c in r["judging_criteria"]}
        self.assertEqual(crit, {"Technical Complexity": 30.0, "Impact on Climate Resilience": 25.0, "Originality": 20.0,
                                "Design and User Experience": 15.0, "Presentation": 10.0})
        self.assertEqual((r["team_size"]["min"], r["team_size"]["max"]), (1, 4))
        types = {d["type"]: d for d in r["required_deliverables"]}
        self.assertTrue({"video", "repo", "devpost", "readme"} <= set(types))
        self.assertEqual(types["video"]["video_max_minutes"], 3.0)
        self.assertEqual(r["deadlines"][0]["timezone"], "MST")
        self.assertTrue(any("Pre-existing" in x["evidence"] for x in r["pre_existing_code_policy"]))
        self.assertTrue(any("Open Climate Data API" in x["evidence"] for x in r["technology_requirements"]))
        self.assertEqual(len(r["prize_tracks"]), 3)
        self.assertNotIn("var a=1", out)  # scripts stripped

    def test_plain_text_unweighted(self):
        code, out, _ = run("extract_submission_requirements.py", FIX / "rules_plain.txt")
        r = json.loads(out)
        self.assertEqual([c["name"] for c in r["judging_criteria"]], ["Usefulness", "Creativity", "Technical execution", "Polish"])
        self.assertTrue(all(c["weight"] is None for c in r["judging_criteria"]))
        self.assertTrue(any("no weights" in w for w in r["warnings"]))
        self.assertEqual(r["team_size"]["max"], 3)
        types = {d["type"]: d for d in r["required_deliverables"]}
        self.assertEqual(types["video"]["video_max_minutes"], 2.0)
        self.assertIn("demo_url", types)
        self.assertEqual(r["deadlines"][0]["timezone"], "UTC")
        self.assertTrue(r["disqualification_conditions"])


class Fetch(unittest.TestCase):
    def test_local_file_ingest_and_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            code, out, _ = run("fetch_hackathon_docs.py", FIX / "rules_sample.html", FIX / "rules_plain.txt", "--out", d)
            self.assertEqual(code, 0, out)
            man = json.loads((Path(d) / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual([m["status"] for m in man], ["ok", "ok"])
            txt = Path(man[0]["text_path"]).read_text(encoding="utf-8")
            self.assertIn("# PolarHacks 2026 — Official Rules", txt)
            self.assertIn("## Judging Criteria", txt)
            self.assertNotIn("color:red", txt)
            # extractor accepts the fetched directory and prefers .txt over the .html twin
            code, out, _ = run("extract_submission_requirements.py", d)
            self.assertEqual(len(json.loads(out)["judging_criteria"]), 5 + 4)

    def test_missing_file_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as d:
            code, out, _ = run("fetch_hackathon_docs.py", "/nonexistent/x.html", "--out", d)
            self.assertEqual(code, 1)
            self.assertIn("ERR", out)


class Validate(unittest.TestCase):
    def test_good_project_passes(self):
        code, out, _ = run("validate_submission.py", FIX / "project_good", "--requirements", "requirements.json", "--now", NOW, "--strict")
        self.assertEqual(code, 0, out)

    def test_bad_project_fails_with_expected_findings(self):
        code, out, _ = run("validate_submission.py", FIX / "project_bad", "--requirements", "requirements.json", "--now", NOW, "--json")
        self.assertEqual(code, 1)
        items = json.loads(out)["items"]
        msgs = " ".join(i["message"] for i in items)
        self.assertIn("'SMS notifications' is PLANNED", msgs)
        self.assertIn("placeholder 'TODO'", msgs)
        self.assertIn("placeholder '<link>'", msgs)
        self.assertIn("OpenAI/Anthropic-style key in config.py", msgs)
        self.assertIn(".env exists but is not listed", msgs)
        self.assertIn("'Insurance quote lookup' is SIMULATED", msgs)

    def test_deadline_passed(self):
        code, out, _ = run("validate_submission.py", FIX / "project_good", "--requirements", "requirements.json", "--now", "2026-03-16T09:00:00-07:00")
        self.assertEqual(code, 1)
        self.assertIn("Deadline passed", out)

    def test_video_too_long(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d) / "p"
            shutil.copytree(FIX / "project_good", proj)
            ds = proj / "submission" / "DEMO_SCRIPT.md"
            ds.write_text(ds.read_text(encoding="utf-8") + ("word " * 600), encoding="utf-8")
            code, out, _ = run("validate_submission.py", proj, "--requirements", "requirements.json", "--now", NOW)
            self.assertEqual(code, 1)
            self.assertIn("limit 3", out)

    def test_fresh_template_project_fails(self):
        with tempfile.TemporaryDirectory() as d:
            run("init_project.py", d)
            code, out, _ = run("validate_submission.py", d, "--now", NOW)
            self.assertEqual(code, 1)
            self.assertIn("looks unfilled", out)


class ReportAndInit(unittest.TestCase):
    def test_report(self):
        code, out, _ = run("generate_project_report.py", FIX / "project_good", "--json", "--now", NOW)
        r = json.loads(out)
        self.assertEqual(r["time_remaining"], "9h 0m")
        self.assertEqual(r["pct_elapsed"], 75.0)
        self.assertEqual(r["feature_counts"], {"VERIFIED": 2, "PLANNED": 1, "SIMULATED": 1})
        self.assertEqual(r["demo_critical"], {"total": 2, "verified": 2, "not_verified": []})
        self.assertEqual(r["scorecard"], {"current": 6.0, "projected": 6.8})
        self.assertEqual(len(r["open_risks"]), 1)
        self.assertTrue(any("feature freeze" in w for w in r["warnings"]))

    def test_init_is_idempotent_and_preserves_files(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "CLAUDE.md").write_text("# My project rules\n", encoding="utf-8")
            (Path(d) / "PRODUCT_SPEC.md").write_text("mine", encoding="utf-8")
            run("init_project.py", d, "--deadline", "2026-12-01 17:00 America/Denver")
            run("init_project.py", d)
            self.assertEqual((Path(d) / "PRODUCT_SPEC.md").read_text(encoding="utf-8"), "mine")
            cm = (Path(d) / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertTrue(cm.startswith("# My project rules"))
            self.assertEqual(cm.count("hackathon-accelerator:start"), 1)
            self.assertIn(f"Accelerator skill dir: {SCRIPTS.parent}", cm)
            self.assertIn(str(SCRIPTS.parents[2] / "agents" / "hackathon-coding-assistant.md"), cm)
            self.assertTrue((SCRIPTS.parents[2] / "agents" / "hackathon-coding-assistant.md").exists())
            self.assertIn("Deadline: 2026-12-01 17:00 America/Denver", (Path(d) / "PROGRESS.md").read_text(encoding="utf-8"))
            for sub in ["research/raw", "reviews", "submission/DEVPOST.md", "app", "tests"]:
                self.assertTrue((Path(d) / sub).exists(), sub)

    def test_detect_environment_writes_section(self):
        with tempfile.TemporaryDirectory() as d:
            run("init_project.py", d)
            code, out, _ = run("detect_environment.py", d, "--write", "--no-mcp-cli", "--json")
            self.assertEqual(code, 0)
            data = json.loads(out.split("\nPROGRESS.md")[0])
            self.assertIn("integrations", data)
            prog = (Path(d) / "PROGRESS.md").read_text(encoding="utf-8")
            self.assertEqual(prog.count("## Environment"), 1)
            self.assertIn("Detected", prog)
            self.assertIn("## Session log", prog)  # following section preserved


class TeamLog(unittest.TestCase):
    def test_hook_log_pairs_starts_and_stops(self):
        import json as _j
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "PROGRESS.md").write_text("# Progress", encoding="utf-8")
            log = Path(d) / ".hackathon" / "agent-log.jsonl"
            log.parent.mkdir()
            rows = [{"ts": "2026-11-25T20:00:00Z", "event": "start", "agent": "rules-auditor", "task": "Audit rules"},
                    {"ts": "2026-11-25T20:01:30Z", "event": "stop", "agent": "rules-auditor", "summary": "## Result Wrote research/rules-audit.md. 7 items."},
                    {"ts": "2026-11-25T20:02:00Z", "event": "start", "agent": "frontend-engineer", "task": "Build calendar"}]
            log.write_text("\n".join(_j.dumps(r) for r in rows) + "\n", encoding="utf-8")
            run("team_log.py", d, "--add", "hackathon-coding-assistant", "Fix CORS", "Verified fetch works")
            code, out, _ = run("team_log.py", d, "--json")
            data = _j.loads(out)
            runs = {r["agent"]: r for r in data["runs"]}
            self.assertEqual(runs["rules-auditor"]["status"], "done")
            self.assertEqual(runs["rules-auditor"]["result"], "Wrote research/rules-audit.md.")
            self.assertEqual(runs["frontend-engineer"]["status"], "running")
            self.assertEqual(runs["hackathon-coding-assistant"]["status"], "done (main session)")
            self.assertEqual(sum(len(v) for v in data["roster"].values()), 43)
            code, out, _ = run("team_log.py", d)
            self.assertIn("| **rules-auditor** | strategy | Audit rules | Wrote research/rules-audit.md. | 1m 30s |", out)

    def test_hook_script_logs_only_in_hackathon_projects(self):
        import shutil as _sh
        node = _sh.which("node")
        if not node:
            self.skipTest("node not installed")
        hook = SCRIPTS.parents[2] / "hooks" / "agent-log.js"
        with tempfile.TemporaryDirectory() as d:
            proj, other = Path(d) / "p", Path(d) / "o"
            proj.mkdir(); other.mkdir()
            (proj / "PROGRESS.md").write_text("x", encoding="utf-8")
            for cwd in (proj, other):
                inp = '{"cwd": "%s", "tool_input": {"subagent_type": "hackathon-accelerator:qa-testing-engineer", "description": "Run QA"}}' % cwd.as_posix()
                p = subprocess.run([node, str(hook), "start"], input=inp, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(p.returncode, 0)
                self.assertEqual(p.stdout, "")
            line = (proj / ".hackathon" / "agent-log.jsonl").read_text(encoding="utf-8")
            self.assertIn('"agent":"qa-testing-engineer"', line)
            self.assertFalse((other / ".hackathon").exists())
            p = subprocess.run([node, str(hook), "stop"], input="not json", capture_output=True, text=True)
            self.assertEqual(p.returncode, 0)


    def test_session_hook_adds_context_only_in_hackathon_projects(self):
        import shutil as _sh, json as _j
        node = _sh.which("node")
        if not node:
            self.skipTest("node not installed")
        hook = SCRIPTS.parents[2] / "hooks" / "agent-log.js"
        with tempfile.TemporaryDirectory() as d:
            proj, other = Path(d) / "p", Path(d) / "o"
            proj.mkdir(); other.mkdir()
            (proj / "HACKATHON_BRIEF.md").write_text("x", encoding="utf-8")
            env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
            out = {}
            for name, cwd in (("p", proj), ("o", other)):
                p = subprocess.run([node, str(hook), "session"], input=_j.dumps({"cwd": str(cwd)}),
                                   capture_output=True, text=True, encoding="utf-8", env=env)
                self.assertEqual(p.returncode, 0)
                out[name] = p.stdout
            self.assertEqual(out["o"], "")
            ctx = _j.loads(out["p"])["hookSpecificOutput"]
            self.assertEqual(ctx["hookEventName"], "SessionStart")
            self.assertIn("Delegation is real", ctx["additionalContext"])
            self.assertIn("animations", ctx["additionalContext"])

    def test_claude_block_refreshes_when_outdated(self):
        with tempfile.TemporaryDirectory() as d:
            old = "# Mine\n\n<!-- hackathon-accelerator:start -->\nold text C:\\Users\\x\n<!-- hackathon-accelerator:end -->\n\nkeep me\n"
            (Path(d) / "CLAUDE.md").write_text(old, encoding="utf-8")
            code, out, _ = run("init_project.py", d)
            self.assertEqual(code, 0)
            text = (Path(d) / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("refreshed", out)
            self.assertNotIn("old text", text)
            self.assertIn("Never write their verdicts yourself", text)
            self.assertIn("keep me", text)
            self.assertEqual(text.count("hackathon-accelerator:start"), 1)
            code, out, _ = run("init_project.py", d)
            self.assertIn("block already present", out)


class TimeAndVideo(unittest.TestCase):
    def test_time_plan_budgets_and_check(self):
        code, out, _ = run("time_plan.py", "--minutes", "3", "--format", "live-demo")
        self.assertEqual(code, 0)
        self.assertIn("usable 162s", out)
        self.assertIn("LIVE DEMO", out)
        self.assertIn("appendix slides", out)
        code, out, _ = run("time_plan.py", "--minutes", "2", "--format", "video-only")
        self.assertIn("Hero moment first", out)
        self.assertNotIn("agenda slide", out)               # slide rules don't apply to video-only
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "submission").mkdir()
            (Path(d) / "submission" / "PITCH.md").write_text("# Pitch\n## Script\n" + "word " * 500, encoding="utf-8")
            code, out, _ = run("time_plan.py", "--minutes", "3", "--format", "live-demo", "--check", d)
            self.assertEqual(code, 1)
            self.assertIn("OVER", out)

    def test_make_video_stitches_and_enforces_limit(self):
        import shutil as _sh
        if not (_sh.which("ffmpeg") and _sh.which("ffprobe")):
            self.skipTest("ffmpeg not installed")
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=navy:s=1280x720", "-frames:v", "1", str(d / "card.png")], check=True)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=1280x720:rate=30", "-t", "4", "-c:v", "libvpx-vp9", "-b:v", "1M", str(d / "clip.webm")], check=True)
            code, out, err = run("make_video.py", f"{d / 'card.png'}:2", f"{d / 'clip.webm'}@0.5-3.5", f"{d / 'card.png'}:2",
                                 "--out", d / "out.mp4", "--limit", "60")
            self.assertEqual(code, 0, err + out)
            self.assertIn("Within the 60s limit", out)
            probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height", "-of", "csv=p=0", str(d / "out.mp4")],
                                   capture_output=True, text=True).stdout
            self.assertIn("h264,1920,1080", probe)
            self.assertIn("aac", probe)                      # silent audio track added
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(d / "out.mp4")],
                                       capture_output=True, text=True).stdout)
            self.assertAlmostEqual(dur, 2 + 3 + 2 - 2 * 0.4, delta=0.35)
            code, out, _ = run("make_video.py", f"{d / 'card.png'}:5", "--out", d / "long.mp4", "--limit", "3")
            self.assertEqual(code, 1)
            self.assertIn("OVER", out)


class Shortcut(unittest.TestCase):
    def test_install_reinstall_remove_and_conflict(self):
        import os
        tool = SCRIPTS.parents[2] / "tools" / "install_shortcut.py"
        with tempfile.TemporaryDirectory() as home:
            env = {**os.environ, "HOME": home, "USERPROFILE": home}
            go = lambda *a: subprocess.run([sys.executable, "-I", str(tool), *a], capture_output=True, text=True,  # noqa: E731
                                           encoding="utf-8", env=env)
            dst = Path(home) / ".claude" / "skills" / "hackathon-accelerator" / "SKILL.md"
            self.assertEqual(go().returncode, 0)
            self.assertIn("disable-model-invocation: true", dst.read_text(encoding="utf-8"))
            self.assertEqual(go().returncode, 0)            # reinstall over our own shortcut is fine
            self.assertEqual(go("--remove").returncode, 0)
            self.assertFalse(dst.exists())
            dst.parent.mkdir(parents=True)
            dst.write_text("someone else's skill", encoding="utf-8")
            self.assertEqual(go().returncode, 1)            # never clobbers a different skill
            self.assertEqual(dst.read_text(encoding="utf-8"), "someone else's skill")
            team = Path(home) / ".claude" / "skills" / "hackathon-team" / "SKILL.md"
            self.assertTrue(team.exists())                  # the other shortcut still installed
            self.assertIn("hackathon-accelerator:team", team.read_text(encoding="utf-8"))


class BrainDeckVideo(unittest.TestCase):
    def test_brain_maps_code_incrementally_and_queries(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "PRODUCT_SPEC.md").write_text("# Floody\n## Problem\nFlood alerts arrive too late.\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "api.ts").write_text("import { score } from './score'\napp.get('/alerts', handler)\nexport function handler() {}\n", encoding="utf-8")
            (root / "src" / "score.ts").write_text("// risk scoring\nexport const score = (x) => x * 2\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "junk.js").write_text("function nope(){}", encoding="utf-8")
            code, out, _ = run("brain.py", d)
            self.assertEqual(code, 0)
            self.assertIn("2 files (2 re-read", out)
            brain = (root / ".hackathon" / "brain" / "BRAIN.md").read_text(encoding="utf-8")
            self.assertIn("Floody", brain)
            self.assertIn("GET /alerts", brain)
            self.assertNotIn("junk", brain)
            code, out, _ = run("brain.py", d)
            self.assertIn("(0 re-read", out)
            code, out, _ = run("brain.py", d, "--query", "score")
            self.assertIn("src/score.ts", out)
            code, out, _ = run("brain.py", d, "--file", "src/score.ts")
            self.assertIn("used by: src/api.ts", out)
            run("brain.py", d, "--note", "alerts come from the NOAA API")
            self.assertIn("NOAA", (root / ".hackathon" / "brain" / "BRAIN.md").read_text(encoding="utf-8"))

    def test_deck_audit_passes_template_and_flags_bad_deck(self):
        tpl = SCRIPTS.parent / "assets" / "templates" / "deck" / "deck.html"
        code, out, _ = run("deck_audit.py", str(tpl), "--minutes", "3")
        self.assertEqual(code, 0, out)
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "deck.html"
            bad.write_text('<style>img{width:100%}</style><section class="slide" data-seconds="200"><h2>Hi</h2></section>'
                           '<section class="slide"><img src="x.png"></section>', encoding="utf-8")
            code, out, _ = run("deck_audit.py", str(bad), "--minutes", "3")
            self.assertEqual(code, 1)
            for frag in ("looks empty", "outside a .frame", "image file missing", "object-fit", "timing"):
                self.assertIn(frag, out)

    def test_demo_video_plan_validates_shots(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "video").mkdir()
            ex = SCRIPTS.parent / "assets" / "video" / "shots.example.json"
            shutil.copy(ex, Path(d) / "video" / "shots.json")
            code, out, _ = run("demo_video.py", d, "--plan")
            self.assertEqual(code, 0, out)
            self.assertIn("5 shots", out)
            self.assertIn("★", out)
            (Path(d) / "video" / "shots.json").write_text('{"shots":[{"actions":[{"fly":"x"}]}]}', encoding="utf-8")
            code, out, _ = run("demo_video.py", d, "--plan")
            self.assertEqual(code, 2)
            self.assertIn('unknown action "fly"', out)

    @unittest.skipUnless(os.environ.get("HA_FULL_VIDEO") == "1", "set HA_FULL_VIDEO=1 to record a real video (needs node, ffmpeg, Chrome/Edge, network for npm)")
    def test_demo_video_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "video").mkdir()
            for f in ("shots.example.json", "sample-app.html"):
                shutil.copy(SCRIPTS.parent / "assets" / "video" / f, Path(d) / "video" / f)
            (Path(d) / "video" / "shots.example.json").rename(Path(d) / "video" / "shots.json")
            p = subprocess.run([sys.executable, str(SCRIPTS / "demo_video.py"), d], capture_output=True, text=True, encoding="utf-8", timeout=600)
            self.assertEqual(p.returncode, 0, p.stdout[-2000:] + p.stderr[-2000:])
            mp4 = Path(d) / "submission" / "demo.mp4"
            self.assertTrue(mp4.exists())
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                                       capture_output=True, text=True).stdout)
            self.assertTrue(15 < dur <= 35, dur)
            self.assertTrue((Path(d) / "submission" / "thumbnail.png").exists())

    def test_prompt_hook_routes_only_matching_messages(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        hook = SCRIPTS.parents[2] / "hooks" / "agent-log.js"
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "PROGRESS.md").write_text("x", encoding="utf-8")
            def ask(text, cwd=d):
                p = subprocess.run([node, str(hook), "prompt"], input=json.dumps({"cwd": cwd, "prompt": text}),
                                   capture_output=True, text=True, encoding="utf-8", env=env)
                self.assertEqual(p.returncode, 0)
                return p.stdout
            self.assertIn("idea agents", ask("what should we build?"))
            self.assertIn("slide-deck-designer", ask("make the deck"))
            self.assertIn("game-designer", ask("we are doing a godot game jam"))
            self.assertEqual(ask("fix the typo in the header"), "")
            with tempfile.TemporaryDirectory() as other:
                self.assertIn("hackathon-accelerator skill", ask("help me with my hackathon", other))
                self.assertEqual(ask("hello", other), "")


if __name__ == "__main__":
    unittest.main()
