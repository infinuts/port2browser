import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.inspect_game import inspect_game


class RuntimeClueTests(unittest.TestCase):
    def test_headers_and_suffixes_are_inferred_with_explicit_ambiguity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            for name,data in {'base.wad':b'IWAD'+b'\0'*8,'mod.pk3':b'PK\x03\x04','game.nes':b'NES\x1a'+b'\0'*12,
                              'game.gba':b'unknown','disk.iso':b'unknown','disk.dsk':b'unknown','tiny.com':b'\xb8\0\x4c\xcd\x21',
                              'game.swf':b'CWS\x09\x08\0\0\0','launcher/package.json':b'{"dependencies":{"electron":"1"}}'}.items():
                p=root/name;p.parent.mkdir(exist_ok=True);p.write_bytes(data)
            report=inspect_game(root)
            self.assertEqual({c['engine'] for c in report['candidates']},{'open-engine','emulation','flash','electron'})
            self.assertTrue(all(c['confidence']=='inferred' for c in report['runtime_clues']))
            self.assertEqual(len(report['runtime_clues']),8)
            self.assertTrue(any('platform unknown' in c['format'] for c in report['runtime_clues']))
            self.assertIn({'engine':'flash','path':'game.swf','field':'swf_version','value':9},report['metadata'])
            self.assertTrue(all(h['status']=='investigate' for h in report['task_hints']))

    def test_confirmed_pe_is_not_a_dos_route_and_mz_is_not_confirmed_dos(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            pe=bytearray(256);pe[:2]=b'MZ';pe[60:64]=(128).to_bytes(4,'little');pe[128:132]=b'PE\0\0';pe[132:134]=(0x8664).to_bytes(2,'little')
            (root/'modern.exe').write_bytes(pe)
            (root/'native.dll').write_bytes(b'MZ'+b'\0'*80)
            (root/'incomplete.exe').write_bytes(b'MZ')
            self.assertFalse(inspect_game(root)['runtime_clues'])
            (root/'unresolved.exe').write_bytes(b'MZ'+b'\0'*80)
            report=inspect_game(root)
            self.assertEqual(len(report['runtime_clues']),1)
            self.assertIn('DOS/NE/PE unresolved',report['runtime_clues'][0]['format'])

    def test_caps_errors_and_malformed_headers_are_visible(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            for i in range(105):(root/f'{i}.wad').write_bytes(b'IWAD')
            (root/'bad.swf').write_bytes(b'bad')
            report=inspect_game(root)
            self.assertEqual(len(report['runtime_clues']),100)
            self.assertEqual(report['omitted']['runtime_clues'],6)
            self.assertTrue(report['completeness']['output_capped'])
            self.assertFalse(report['truncated'])
            self.assertTrue(any('SWF header' in w for w in report['warnings']))
            with patch.object(Path,'open',side_effect=PermissionError(13,'denied')):
                report=inspect_game(root)
            self.assertGreater(report['scan_errors']['read'],0)
            self.assertFalse(report['completeness']['samples_readable'])
            self.assertTrue(all(c['basis'].startswith('filename') for c in report['runtime_clues']))
