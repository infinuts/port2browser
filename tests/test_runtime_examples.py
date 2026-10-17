import importlib.util
from pathlib import Path
import tempfile
from unittest.mock import patch
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]


class RuntimeExamplePackagingTests(unittest.TestCase):
    def test_love_native_archive_is_deterministic_and_contains_only_original_inputs(self):
        spec=importlib.util.spec_from_file_location('love_build',ROOT/'examples/love-beacon/build.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);here=root/'examples/love-beacon';game=here/'game';game.mkdir(parents=True)
            (game/'conf.lua').write_text('function love.conf(t) end')
            (game/'main.lua').write_text('function love.draw() end')
            (game/'private-save.txt').write_text('must not ship')
            (root/'LICENSE').write_text('Original MIT license')
            with patch.object(module,'HERE',here),patch('sys.argv',['build.py','native']):
                module.main();archive=here/'build/native/beacon.love';first=archive.read_bytes()
                module.main();self.assertEqual(first,archive.read_bytes())
            with zipfile.ZipFile(archive) as data:
                self.assertEqual(set(data.namelist()),{'conf.lua','main.lua','LICENSE'})
                self.assertEqual(data.read('LICENSE'),b'Original MIT license')
