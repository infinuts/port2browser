from pathlib import Path
import tempfile
import unittest
from tools.build_demo import build_demo

class DemoPackagingTests(unittest.TestCase):
    def test_only_dedicated_build_files_are_published(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.mkdir()
            for name in ('index.html','index.js','index.wasm','private-save.txt'):
                (source/name).write_text('<h1>SDL Beacon</h1>' if name.endswith('html') else 'fixture')
            out=root/'out';build_demo(source,out,'abc123')
            self.assertEqual({p.name for p in out.iterdir()},{'index.html','index.js','index.wasm','version.json','.nojekyll'})
            self.assertIn('abc123',(out/'version.json').read_text())
            self.assertIn('Tested port report',(out/'index.html').read_text())
            with self.assertRaises(ValueError):build_demo(source,out,'abc123')

class ShowcasePackagingTests(unittest.TestCase):
    def test_packed_payloads_round_trip_and_reference_is_separate(self):
        import gzip
        import hashlib
        from tools.build_demo import build_showcase
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'game';source.mkdir()
            (source/'index.html').write_text('<script async src="index.js"></script>')
            (source/'index.js').write_bytes(b'original runtime;'*300)
            (source/'index.wasm').write_bytes(b'\x00asm'+bytes(range(256))*50)
            (source/'private-save.txt').write_text('never publish')
            first=build_showcase(source,root/'out1','abc123',source,source)
            build_showcase(source,root/'out2','abc123',source,source)
            for original,packed in [('index.js','runtime.bin'),('index.wasm','engine.bin')]:
                decoded=gzip.decompress((root/'out1'/packed).read_bytes())
                self.assertEqual(decoded,(source/original).read_bytes())
                self.assertEqual((root/'out1'/packed).read_bytes(),(root/'out2'/packed).read_bytes())
                self.assertEqual(first['packed_files'][packed]['decoded_sha256'],hashlib.sha256(decoded).hexdigest())
            self.assertEqual(first['packed_startup_bytes'],sum((root/'out1'/p).stat().st_size for p in first['startup_files']))
            self.assertFalse(list((root/'out1').rglob('private-save.txt')))
            self.assertTrue((root/'out1/beacon/index.wasm').is_file())
            self.assertNotIn('index.js"',(root/'out1/index.html').read_text())
            with self.assertRaises(ValueError):build_showcase(source,root/'out1','abc123',source)
