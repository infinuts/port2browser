"""Deterministic routing/package checks, not agent behavior evaluations."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

from scripts.inspect_game import ENGINE_TASK_SKILLS, TEXT_BYTES, inspect_game
from tools.package_skills import ROOT, package


def check_links(test, root):
    for document in root.rglob('*.md'):
        for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
            parsed = urlsplit(link)
            if parsed.scheme or not parsed.path:
                continue
            target = (document.parent / unquote(parsed.path)).resolve()
            with test.subTest(document=str(document), link=link):
                test.assertTrue(target.is_relative_to(root.resolve()), str(target))
                test.assertTrue(target.is_file(), str(target))


class TaskSkillTests(unittest.TestCase):
    def test_manifests_and_standalone_resources(self):
        modules = sorted((ROOT / 'skills').iterdir())
        self.assertEqual(len(modules), 12)
        for module in modules:
            with self.subTest(skill=module.name):
                text = (module / 'SKILL.md').read_text(encoding='utf-8')
                self.assertTrue(text.startswith('---\n'))
                fields = dict(line.split(': ', 1) for line in text.split('---\n', 2)[1].splitlines())
                self.assertEqual(set(fields), {'name', 'description', 'license'})
                self.assertEqual(fields['name'], module.name)
                self.assertRegex(module.name, r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
                self.assertLessEqual(len(module.name), 64)
                self.assertTrue(1 <= len(fields['description']) <= 1024)
                self.assertNotIn(': ', fields['description'])
                self.assertEqual(fields['license'], 'MIT')
                self.assertEqual((module / 'LICENSE').read_bytes(), (ROOT / 'LICENSE').read_bytes())
                with tempfile.TemporaryDirectory() as temporary:
                    standalone = Path(temporary) / module.name
                    shutil.copytree(module, standalone)
                    check_links(self, standalone)

    def test_catalog_covers_navigation_without_support_claims(self):
        catalog = json.loads((ROOT / 'references/engine-routes.json').read_text())
        self.assertEqual(catalog['schema_version'], 1)
        engines = catalog['engines']
        self.assertEqual(len(engines), 28)
        self.assertEqual(len({e['id'] for e in engines}), len(engines))
        mapping = {}
        for engine in engines:
            self.assertEqual(engine['coverage'], 'documented_route')
            self.assertTrue(engine['requires'])
            self.assertTrue((ROOT / engine['guide']).is_file())
            self.assertTrue((ROOT / 'skills' / engine['task_skill'] / 'SKILL.md').is_file())
            for candidate in engine['candidate_ids']:
                self.assertNotIn(candidate, mapping)
                mapping[candidate] = engine['task_skill']
        self.assertEqual(mapping, ENGINE_TASK_SKILLS)

    def test_both_layouts_are_portable_and_exclude_development_dependencies(self):
        for layout in ('bundle', 'collection'):
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as temporary:
                base = Path(temporary)
                output = package(base / 'copied skills', layout)
                self.assertEqual(len(list(output.glob('*/SKILL.md'))), 1 if layout == 'bundle' else 13)
                check_links(self, output)
                self.assertFalse(any(p.name in {'node_modules', 'examples', 'tools', '.git', '__pycache__'} for p in output.rglob('*')))
                install = output / 'port2browser'
                game = base / 'game'; game.mkdir()
                (game / 'project.godot').write_text('config_version=5\n')
                result = subprocess.run([sys.executable, '-I', str(install / 'scripts/inspect_game.py'), str(game)], cwd=base, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)['task_hints'], [{'engine':'godot','skill':'port2browser-export','status':'investigate'}])
                server = subprocess.run([sys.executable, '-I', str(install / 'scripts/serve.py'), '--help'], cwd=base, capture_output=True, text=True)
                self.assertEqual(server.returncode, 0, server.stderr)
                catalog = json.loads((install / 'references/engine-routes.json').read_text())
                for row in catalog['engines']:
                    self.assertTrue((install / row['guide']).is_file())
                with self.assertRaises(ValueError):
                    package(output, layout)

    def test_packaging_rejects_links_and_outputs_inside_source(self):
        with self.assertRaises(ValueError):
            package(ROOT / 'must-not-create')
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary); source = base / 'source'
            source.mkdir()
            for name in ('SKILL.md', 'LICENSE'):
                shutil.copy2(ROOT / name, source / name)
            for name in ('references', 'scripts', 'skills'):
                (source / name).mkdir()
            outside = base / 'secret'; outside.write_text('private')
            try:
                (source / 'references/linked.md').symlink_to(outside)
            except OSError:
                self.skipTest('symbolic links unavailable')
            with self.assertRaises(ValueError):
                package(base / 'output', source=source)
            self.assertFalse((base / 'output').exists())

    def test_new_clues_remain_inferred_and_preserve_conflicts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'game.project').write_text('[project]\ntitle = Beacon\n[bootstrap]\nmain_collection = /main.collection\n')
            (root / 'game.json').write_text(json.dumps({'gdVersion': {'major':5}, 'layouts':[]}))
            (root / 'scene.c3p').write_bytes(b'not extracted')
            (root / 'Cargo.toml').write_text('[package]\nname="example"\n[dependencies]\nbevy = "0.1"\nmacroquad = {version="0.2"}\n')
            report = inspect_game(root)
            self.assertEqual({e['engine'] for e in report['candidates']}, {'defold','gdevelop','construct','bevy','macroquad'})
            self.assertTrue(all(e['confidence']=='inferred' for e in report['candidates']))
            self.assertTrue(all(e['status']=='investigate' for e in report['task_hints']))
            self.assertFalse(report['warnings'])

    def test_generic_names_comments_and_malformed_metadata_do_not_invent_routes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'game.project').write_text('not a Defold descriptor')
            (root / 'game.json').write_text('{invalid')
            (root / 'Cargo.toml').write_text('[package]\nbevy="name"\n[dependencies]\n# macroquad = "0.1"\n[package.metadata.dependencies]\nbevy="text"\n')
            report = inspect_game(root)
            self.assertFalse(report['candidates'])
            self.assertFalse(report['task_hints'])
            self.assertTrue(any('invalid JSON' in w for w in report['warnings']))
            (root / 'game.json').write_bytes(b' ' * (TEXT_BYTES+1))
            (root / 'Cargo.toml').write_bytes(b'\xff')
            report = inspect_game(root)
            self.assertFalse(report['candidates'])
            self.assertEqual(report['completeness']['metadata_sample_limits'], 1)
            self.assertTrue(any('invalid UTF-8' in w for w in report['warnings']))
