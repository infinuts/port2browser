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
