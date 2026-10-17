"""Media boundaries and the pinned legacy GLSL workaround need explicit regression checks."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from tools.package_assaultcube import package_client, FILES, LICENSES

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ac_runtime_fixes', ROOT / 'examples/assaultcube/runtime_fixes.py')
fixes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixes)


class AssaultCubePackagingTests(unittest.TestCase):
    def fixture(self, root):
        source = root / 'source'
        source.mkdir()
        for name in FILES:
            (source / name).write_text('fixture')
        (source / 'assets.json').write_text(json.dumps({'files': [{'path': 'packages/map.cgz', 'bytes': 3, 'sha256': 'fixture'}]}))
        (source / 'version.json').write_text('{}')
        (source / 'licenses').mkdir()
        for name in LICENSES:
            (source / 'licenses' / name).write_text('original notice')
        return source

    def test_never_copies_assets_or_private_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.fixture(root)
            (source / 'private.cfg').write_text('local settings')
            (source / 'packages').mkdir()
            (source / 'packages/map.cgz').write_text('game media')
            package_client(source, root / 'public', 'abc123')
            files = {p.relative_to(root / 'public').as_posix() for p in (root / 'public').rglob('*') if p.is_file()}
            self.assertEqual(files, set(FILES) | {'licenses/' + name for name in LICENSES})
            self.assertEqual(json.loads((root / 'public/version.json').read_text())['skill_revision'], 'abc123')
            with self.assertRaises(ValueError):
                package_client(source, root / 'public', 'abc123')

    def test_rejects_a_media_preload_even_though_it_is_not_allowlisted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.fixture(root)
            (source / 'ac.data').write_bytes(b'game media')
            with self.assertRaisesRegex(ValueError, 'media-preloaded'):
                package_client(source, root / 'public', 'abc123')
            self.assertFalse((root / 'public').exists())

    def test_rejects_manifest_path_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.fixture(root)
            (source / 'assets.json').write_text(json.dumps({'files': [{'path': 'packages/../../private.cfg'}]}))
            with self.assertRaisesRegex(ValueError, 'manifest'):
                package_client(source, root / 'public', 'abc123')

    def test_texture_optimizer_matches_complete_matrix_expression(self):
        script = '\n'.join('var pattern = ' + pattern + ';' for pattern in fixes.OLD)
        result = fixes.fix_texture_jit(script)
        self.assertEqual(result.count(fixes.NEW), 2)
        pattern = re.compile(fixes.NEW[1:-2])
        sample = 'texture2D(u_texUnit0, (u_textureMatrix0 * v_texCoord0).xy)'
        self.assertEqual(pattern.search(sample + '.rgb * v_color.rgb;').group(1), sample)
        self.assertEqual(pattern.search('texture2D(u_texUnit0, v_texCoord0.xy)').group(1), 'texture2D(u_texUnit0, v_texCoord0.xy)')
        with self.assertRaises(ValueError):
            fixes.fix_texture_jit('a different SDK')
