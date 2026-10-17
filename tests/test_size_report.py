import gzip
import io
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import wave

from scripts.size_report import decoded_estimate, size_report


class SizeReportTests(unittest.TestCase):
    def test_sizes_and_decoded_estimates_with_unknown_formats(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            raw=b'original original original '*200
            (root/'game.js').write_bytes(raw)
            png=b'\x89PNG\r\n\x1a\n'+struct.pack('>I',13)+b'IHDR'+struct.pack('>II',16,8)+b'\x08\x06\0\0\0'+b'\0'*4
            (root/'image.png').write_bytes(png)
            audio=io.BytesIO()
            with wave.open(audio,'wb') as stream:
                stream.setnchannels(2);stream.setsampwidth(2);stream.setframerate(8000)
                stream.writeframes(b'\0'*800)
            (root/'sound.wav').write_bytes(audio.getvalue())
            report=size_report(root,top=1)
            rows={r['path']:r for r in report['files']}
            self.assertEqual(rows['game.js']['raw_bytes'],len(raw))
            self.assertEqual(rows['game.js']['gzip_bytes'],len(gzip.compress(raw,compresslevel=9,mtime=0)))
            self.assertIsNone(rows['game.js']['decoded_estimate'])
            self.assertEqual(rows['image.png']['decoded_estimate']['bytes'],16*8*4)
            self.assertEqual(rows['sound.wav']['decoded_estimate']['bytes'],200*2*4)
            self.assertEqual(report['largest'][0]['path'],'game.js')
            self.assertTrue(report['completeness']['gzip_complete'])
            self.assertEqual(report['inventory']['raw_bytes'],sum(r['raw_bytes'] for r in rows.values()))
            self.assertEqual(report['gzip']['bytes'],sum(r['gzip_bytes'] for r in rows.values()))

    def test_budgets_partial_walk_and_read_errors_are_distinct(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/'game.dat').write_bytes(b'x'*1000)
            (root/'nested').mkdir();(root/'nested/child').write_bytes(b'child')
            report=size_report(root,max_bytes=20)
            self.assertLessEqual(report['inventory']['sampled_bytes'],20)
            self.assertFalse(report['completeness']['gzip_complete'])
            self.assertTrue(report['completeness']['traversal_complete'])
            report=size_report(root,max_depth=0)
            self.assertFalse(report['completeness']['traversal_complete'])
            self.assertEqual(size_report(root,max_entries=1)['inventory']['entries'],1)
            with patch.object(Path,'open',side_effect=PermissionError(13,'denied')):
                report=size_report(root)
            self.assertFalse(report['completeness']['readable'])
            self.assertEqual(report['inventory']['read_errors'],2)
            self.assertTrue(report['warnings'])

    def test_empty_and_malformed_headers_and_excluded_paths(self):
        self.assertIsNone(decoded_estimate(b'RIFF\x00\x00\x00\x00WAVE'))
        self.assertIsNone(decoded_estimate(b'not-an-image'))
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/'empty').write_bytes(b'')
            (root/'node_modules').mkdir();(root/'node_modules/ignored').write_bytes(b'private')
            report=size_report(root,max_bytes=0)
            self.assertEqual(len(report['files']),1)
            self.assertEqual(report['files'][0]['gzip_bytes'],20)
            self.assertEqual(report['inventory']['skipped_directories'],1)
            outside=root.parent/(root.name+'-outside')
            outside.write_bytes(b'private')
            self.addCleanup(outside.unlink)
            try:(root/'linked').symlink_to(outside)
            except OSError:return
            report=size_report(root)
            self.assertEqual(report['inventory']['skipped_links'],1)
            self.assertEqual(len(report['files']),1)
