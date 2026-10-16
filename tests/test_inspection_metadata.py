"""Contract checks for observed metadata and partial inventories."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.inspect_game import inspect_game


class MetadataTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def write(self, path, content=b''):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def test_observed_values_keep_provenance_and_conflicting_clues(self):
        self.write('ProjectSettings/ProjectVersion.txt', b'm_EditorVersion: 2022.3.0f1\n')
        self.write('sample/ProjectSettings/ProjectVersion.txt', b'm_EditorVersion: 6000.0.1f1\n')
        self.write('project.godot', b'config_version=5\n[application]\nconfig/features=PackedStringArray("4.3", "GL Compatibility")\n')
        self.write('package.json', b'{"dependencies":{"electron":"^32.0.0","phaser":"~3.80.0"}}')
        report = inspect_game(self.root)
        self.assertEqual(report['schema_version'], 1)
        self.assertTrue(all(c['confidence'] == 'inferred' for c in report['candidates']))
        values = {(m['path'], m['field']): m['value'] for m in report['metadata']}
        self.assertEqual(values['ProjectSettings/ProjectVersion.txt', 'editor_version'], '2022.3.0f1')
        self.assertEqual(values['sample/ProjectSettings/ProjectVersion.txt', 'editor_version'], '6000.0.1f1')
        self.assertEqual(values['project.godot', 'config_version'], '5')
        self.assertEqual(values['project.godot', 'features'], ['4.3', 'GL Compatibility'])
        self.assertEqual(values['package.json', 'dependencies.electron'], '^32.0.0')
        self.assertTrue(report['completeness']['traversal_complete'])

    def test_malformed_and_oversized_metadata_are_nonfatal(self):
        self.write('ProjectSettings/ProjectVersion.txt', b'm_EditorVersion: nonsense')
        self.write('project.godot', b'config_version=x\nconfig/features=bad')
        self.write('tools/package.json', b'{bad')
        self.write('large/project.godot', b' ' * 65537)
        self.write('unicode/ProjectSettings/ProjectVersion.txt', b'\xff')
        self.write('shape/package.json', b'[]')
        self.write('group/package.json', b'{"dependencies":[]}')
        self.write('features/project.godot', b'config_version=5\nconfig/features=PackedStringArray("4.3",42)')
        self.write('bad/package.json', b'{"dependencies":{"electron":12}}')
        report = inspect_game(self.root)
        self.assertEqual(report['metadata'], [{'engine':'godot', 'path':'features/project.godot', 'field':'config_version', 'value':'5'}])
        self.assertGreaterEqual(len(report['warnings']), 6)
        self.assertEqual(report['completeness']['metadata_sample_limits'], 1)
        self.assertFalse(report['truncated'])

    def test_every_output_cap_is_accounted_for(self):
        for i in range(105):
            self.write(f'{i}/package.json', b'{"dependencies":{"electron":"1"}}')
            self.write(f'{i}/game.wasm', b'\0asm\x01\0\0\0')
            self.write(f'{i}/bad/project.godot', b'invalid')
        report = inspect_game(self.root)
        self.assertFalse(report['truncated'])
        self.assertTrue(report['completeness']['output_capped'])
        self.assertEqual(report['omitted']['build_files'], 5)
        self.assertEqual(report['omitted']['binaries'], 5)
        self.assertEqual(report['omitted']['metadata'], 5)
        self.assertEqual(report['omitted']['warnings'], 5)
        self.assertEqual(report['omitted']['evidence'], 190)
        for candidate in report['candidates']:
            self.assertEqual(candidate['evidence_omitted'], 95)

    def test_unreadable_sample_and_directory_are_distinct(self):
        self.write('package.json', b'{}')
        with patch.object(Path, 'open', side_effect=PermissionError(13, 'denied')):
            report = inspect_game(self.root)
        self.assertEqual(report['scan_errors']['read'], 1)
        self.assertTrue(report['completeness']['traversal_complete'])
        self.assertFalse(report['completeness']['samples_readable'])
        with patch('scripts.inspect_game.os.scandir', side_effect=PermissionError(13, 'denied')):
            report = inspect_game(self.root)
        self.assertEqual(report['scan_errors']['directory'], 1)
        self.assertFalse(report['completeness']['traversal_complete'])
        self.assertFalse(report['truncated'])

    def test_stat_error_is_reported(self):
        class Entry:
            name = 'gone'
            path = str(self.root / 'gone')
            def stat(self, **kwargs):
                raise FileNotFoundError(2, 'gone')
        class Entries:
            def __enter__(self): return iter([Entry()])
            def __exit__(self, *args): pass
        with patch('scripts.inspect_game.os.scandir', return_value=Entries()):
            report = inspect_game(self.root)
        self.assertEqual(report['scan_errors']['stat'], 1)
        self.assertFalse(report['completeness']['traversal_complete'])

    def test_limits_remain_separate_from_output_caps(self):
        self.write('deep/project.godot')
        report = inspect_game(self.root, max_depth=0)
        self.assertTrue(report['truncated'])
        self.assertFalse(report['completeness']['traversal_complete'])
        self.assertFalse(report['completeness']['output_capped'])

    def test_representative_reports(self):
        fixtures = Path(__file__).parent / 'reports'
        for name in ('complete', 'limited'):
            self.write('project.godot', b'config_version=5\n')
            self.write('nested/extra.txt')
            report = inspect_game(self.root, max_depth=0 if name == 'limited' else 32)
            report['root'] = '<game-directory>'
            expected = json.loads((fixtures / (name + '.json')).read_text())
            self.assertEqual(report, expected)
