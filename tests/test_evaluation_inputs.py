"""Synthetic assessment fixtures remain data and preserve uncertainty."""
from pathlib import Path
import unittest
from scripts.inspect_game import inspect_game

ROOT = Path(__file__).parent / 'evaluation-inputs'


class AssessmentInputs(unittest.TestCase):
    def test_shipped_unity_does_not_supply_a_project(self):
        report = inspect_game(ROOT / 'shipped-unity')
        self.assertEqual([c['engine'] for c in report['candidates']], ['unity'])
        self.assertEqual(report['candidates'][0]['confidence'], 'inferred')
        self.assertFalse(report['metadata'])
        self.assertFalse((ROOT / 'shipped-unity' / 'Assets').exists())

    def test_godot_extension_has_no_supplied_web_library(self):
        report = inspect_game(ROOT / 'godot-native')
        self.assertEqual(report['candidates'][0]['engine'], 'godot')
        extension = (ROOT / 'godot-native' / 'native.gdextension').read_text()
        self.assertIn('unavailable/', extension)
        self.assertNotIn('web.', extension)
        self.assertTrue(any(m['field'] == 'features' and '4.3' in m['value'] for m in report['metadata']))
