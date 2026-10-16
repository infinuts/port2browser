import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.inspect_game import binary_info, inspect_game, is_link_or_reparse


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write(self, relative, data=b""):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_project_and_shipped_build_remain_inferred(self):
        self.write("ProjectSettings/ProjectVersion.txt", b"m_EditorVersion: 2022.3.0f1")
        self.write("UnityPlayer.dll", b"MZ")
        self.write("src/main.cpp", b"int main() {}")
        self.write("CMakeLists.txt")
        report = inspect_game(self.root)
        unity = report["candidates"][0]
        self.assertEqual(unity["engine"], "unity")
        self.assertEqual(unity["confidence"], "inferred")
        self.assertEqual(unity["evidence_count"], 2)
        self.assertEqual(report["inventory"]["source_extensions"], {".cpp": 1})
        self.assertIn("CMakeLists.txt", report["build_files"])

    def test_unknown_game_has_no_invented_engine(self):
        self.write("mystery.dat", b"unknown")
        self.assertEqual(inspect_game(self.root)["candidates"], [])

    def test_manifests_and_exclusions(self):
        self.write("package.json", json.dumps({"devDependencies": {"electron": "1"}, "dependencies": {"phaser": "3"}}).encode())
        self.write("node_modules/fake/project.godot")
        self.write("tools/package.json", b"{broken")
        report = inspect_game(self.root)
        self.assertEqual([item["engine"] for item in report["candidates"]], ["electron", "phaser"])
        self.assertTrue(any("invalid JSON" in warning for warning in report["warnings"]))

    def test_all_supported_filename_clues(self):
        for path in ("project.godot", "a.uproject", "rmmz_core.js", "game.rpa", "game.love", "data.win"):
            self.write(path)
        self.assertEqual({item["engine"] for item in inspect_game(self.root)["candidates"]},
                         {"godot", "unreal", "rpg-maker", "renpy", "love", "gamemaker"})

    def test_limits_and_large_manifests(self):
        self.write("package.json", b" " * 65537)
        self.write("nested/deeper/project.godot")
        report = inspect_game(self.root, max_depth=0)
        self.assertTrue(report["truncated"])
        self.assertFalse(report["candidates"])
        self.assertTrue(any("manifest exceeds" in warning for warning in report["warnings"]))
        self.assertLessEqual(inspect_game(self.root, max_entries=1)["inventory"]["entries"], 1)

    def test_decoder_nesting_limit_does_not_abort_inventory(self):
        self.write("package.json", b"[" * 2000 + b"]" * 2000)
        self.write("project.godot")
        # Older supported interpreters reject nesting accepted by newer decoders.
        with patch("scripts.inspect_game.json.loads", side_effect=RecursionError("nesting limit")):
            report = inspect_game(self.root)
        self.assertEqual(report["candidates"][0]["engine"], "godot")
        self.assertTrue(any("JSON" in warning for warning in report["warnings"]))

    def test_links_are_not_followed(self):
        target = self.write("real/project.godot")
        try:
            (self.root / "linked.pck").symlink_to(target)
            (self.root / "loop").symlink_to(self.root, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation unavailable on this host")
        report = inspect_game(self.root)
        self.assertEqual(report["inventory"]["skipped_links"], 2)
        self.assertEqual(report["candidates"][0]["evidence_count"], 1)

    def test_windows_junction_attribute(self):
        info = type("Info", (), {"st_mode": 0o40755, "st_file_attributes": 0x400})()
        self.assertTrue(is_link_or_reparse(info))

    def test_love_clue_does_not_follow_linked_main(self):
        target = self.write("real.lua")
        self.write("conf.lua")
        try:
            (self.root / "main.lua").symlink_to(target)
        except OSError:
            self.skipTest("symlink creation unavailable on this host")
        self.assertFalse(inspect_game(self.root)["candidates"])
        (self.root / "main.lua").unlink()
        self.write("main.lua")
        self.assertEqual(inspect_game(self.root)["candidates"][0]["engine"], "love")

    def test_no_execute_or_unbounded_read(self):
        self.write("game.exe", b"MZ" + b"\0" * 8192)
        original = Path.open
        sizes = []

        class Reader:
            def __init__(self, path):
                self.stream = original(path, "rb")
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.stream.close()
            def read(self, size):
                sizes.append(size)
                return self.stream.read(size)

        with patch.object(Path, "open", lambda path, *args: Reader(path)), patch("subprocess.Popen", side_effect=AssertionError("executed a process")):
            inspect_game(self.root)
        self.assertEqual(sizes, [4096])

    def test_cli_json_and_invalid_input(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "inspect_game.py"
        result = subprocess.run([sys.executable, str(script), str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["schema_version"], 1)
        bad = subprocess.run([sys.executable, str(script), str(self.root), "--max-entries", "0"], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertNotIn("Traceback", bad.stderr)

    def test_missing_or_file_root_is_rejected(self):
        with self.assertRaises(OSError):
            inspect_game(self.root / "missing")
        file = self.write("game.exe")
        with self.assertRaises(ValueError):
            inspect_game(file)


class BinaryTests(unittest.TestCase):
    def test_pe_does_not_become_dos(self):
        data = bytearray(256)
        data[:2] = b"MZ"
        data[60:64] = (128).to_bytes(4, "little")
        data[128:134] = b"PE\0\0\x64\x86"
        self.assertEqual(binary_info(data), {"format": "PE", "architecture": "x86-64"})
        self.assertIn("unverified", binary_info(b"MZ")["format"])

    def test_elf_wasm_and_unknown(self):
        data = bytearray(20)
        data[:6] = b"\x7fELF\x02\x01"
        data[18:20] = (183).to_bytes(2, "little")
        self.assertEqual(binary_info(data)["architecture"], "AArch64")
        self.assertEqual(binary_info(b"\0asm\x01\0\0\0")["format"], "WebAssembly")
        self.assertIsNone(binary_info(b"not an executable"))


if __name__ == "__main__":
    unittest.main()
