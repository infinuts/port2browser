"""Check that a copied skill remains self-contained and runnable."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class DistributionTests(unittest.TestCase):
    def test_current_flat_frontmatter_matches_portable_spec(self):
        # This package deliberately uses only unquoted, single-line scalar fields.
        # This is a check of our manifest, not a general-purpose YAML validator.
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---\n", 2)[1]
        fields = {}
        for line in frontmatter.splitlines():
            key, value = line.split(": ", 1)
            self.assertNotIn(key, fields)
            self.assertNotIn(": ", value, "quote or validate complex YAML fields when adding them")
            fields[key] = value
        self.assertEqual(fields["name"], "port2browser")
        self.assertRegex(fields["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(fields["name"]), 64)
        self.assertTrue(1 <= len(fields["description"]) <= 1024)
        self.assertEqual(fields["license"], "MIT")

    def test_markdown_local_links_resolve(self):
        documents = [ROOT / "README.md", ROOT / "SKILL.md", ROOT / "CONTRIBUTING.md", ROOT / "CHANGELOG.md", *ROOT.glob("references/*.md"), *ROOT.glob("tests/**/*.md"), *ROOT.glob("examples/*/*.md")]
        for document in documents:
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                parsed = urlsplit(link)
                if parsed.scheme or not parsed.path:
                    continue
                target = (document.parent / unquote(parsed.path)).resolve()
                with self.subTest(document=document.name, link=link):
                    target.relative_to(ROOT)
                    self.assertTrue(target.is_file(), f"missing local link: {target}")

    def test_minimal_copied_install_runs_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            install = base / "agent skills" / "port2browser"
            install.mkdir(parents=True)
            for name in ("SKILL.md", "LICENSE"):
                shutil.copy2(ROOT / name, install / name)
            for name in ("scripts", "references"):
                shutil.copytree(ROOT / name, install / name, ignore=shutil.ignore_patterns("__pycache__"))
            game = base / "game files"
            game.mkdir()
            (game / "project.godot").write_text("config_version=5\n", encoding="utf-8")
            result = subprocess.run([sys.executable, "-I", str(install / "scripts" / "inspect_game.py"), str(game)], cwd=base, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["candidates"][0]["engine"], "godot")
            self.assertEqual(report["schema_version"], 1)
            server_help = subprocess.run([sys.executable, "-I", str(install / "scripts" / "serve.py"), "--help"], cwd=base, capture_output=True, text=True)
            self.assertEqual(server_help.returncode, 0, server_help.stderr)
            self.assertIn("--isolate", server_help.stdout)


if __name__ == "__main__":
    unittest.main()
