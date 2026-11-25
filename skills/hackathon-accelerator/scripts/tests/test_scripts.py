#!/usr/bin/env python3
"""Fixture-based tests for the hackathon-accelerator scripts. Run: python3 -m unittest discover -s <this dir>"""
import json
import shutil
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
    p = subprocess.run([sys.executable, "-I", str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True)
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
            man = json.loads((Path(d) / "manifest.json").read_text())
            self.assertEqual([m["status"] for m in man], ["ok", "ok"])
            txt = Path(man[0]["text_path"]).read_text()
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
            ds.write_text(ds.read_text() + ("word " * 600))
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
            (Path(d) / "CLAUDE.md").write_text("# My project rules\n")
            (Path(d) / "PRODUCT_SPEC.md").write_text("mine")
            run("init_project.py", d, "--deadline", "2026-12-01 17:00 America/Denver")
            run("init_project.py", d)
            self.assertEqual((Path(d) / "PRODUCT_SPEC.md").read_text(), "mine")
            cm = (Path(d) / "CLAUDE.md").read_text()
            self.assertTrue(cm.startswith("# My project rules"))
            self.assertEqual(cm.count("hackathon-accelerator:start"), 1)
            self.assertIn(f"Accelerator skill dir: {SCRIPTS.parent}", cm)
            self.assertIn(str(SCRIPTS.parents[2] / "agents" / "hackathon-coding-assistant.md"), cm)
            self.assertTrue((SCRIPTS.parents[2] / "agents" / "hackathon-coding-assistant.md").exists())
            self.assertIn("Deadline: 2026-12-01 17:00 America/Denver", (Path(d) / "PROGRESS.md").read_text())
            for sub in ["research/raw", "reviews", "submission/DEVPOST.md", "app", "tests"]:
                self.assertTrue((Path(d) / sub).exists(), sub)

    def test_detect_environment_writes_section(self):
        with tempfile.TemporaryDirectory() as d:
            run("init_project.py", d)
            code, out, _ = run("detect_environment.py", d, "--write", "--no-mcp-cli", "--json")
            self.assertEqual(code, 0)
            data = json.loads(out.split("\nPROGRESS.md")[0])
            self.assertIn("integrations", data)
            prog = (Path(d) / "PROGRESS.md").read_text()
            self.assertEqual(prog.count("## Environment"), 1)
            self.assertIn("Detected", prog)
            self.assertIn("## Session log", prog)  # following section preserved


if __name__ == "__main__":
    unittest.main()
