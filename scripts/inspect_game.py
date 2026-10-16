#!/usr/bin/env python3
"""Read-only, bounded game inventory. Names are clues, never portability proof."""

import argparse
from collections import Counter
import json
import os
import re
from pathlib import Path
import stat
import sys

SCHEMA_VERSION = 1
HEADER_BYTES = 4096
TEXT_BYTES = 65536
SKIP_DIRS = {".git", ".svn", "node_modules", ".venv", "venv", "__pycache__"}
BUILD_NAMES = {
    "cmakelists.txt", "makefile", "meson.build", "cargo.toml", "package.json",
    "manifest.json", "sconstruct", "build.gradle", "requirements.txt",
}
SOURCE_SUFFIXES = {".c", ".cpp", ".cc", ".h", ".hpp", ".cs", ".rs", ".java", ".lua", ".py", ".js", ".ts", ".rpy"}
BINARY_SUFFIXES = {".exe", ".dll", ".so", ".wasm", ".bin", ".com"}


def is_link_or_reparse(info):
    """Skip symbolic links and all Windows reparse points (including junctions)."""
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & 0x400
    )


def is_regular_unlinked(path):
    try:
        info = path.lstat()
        return stat.S_ISREG(info.st_mode) and not is_link_or_reparse(info)
    except OSError:
        return False


def binary_info(data):
    if data.startswith(b"\0asm"):
        return {"format": "WebAssembly", "architecture": "wasm (memory model unverified)"}
    if data.startswith(b"\x7fELF") and len(data) >= 20:
        byteorder = {1: "little", 2: "big"}.get(data[5])
        machine = int.from_bytes(data[18:20], byteorder) if byteorder else 0
        architecture = {3: "x86", 62: "x86-64", 40: "ARM", 183: "AArch64"}.get(machine, "unknown")
        return {"format": "ELF", "architecture": architecture}
    if data.startswith(b"MZ"):
        if len(data) >= 64:
            offset = int.from_bytes(data[60:64], "little")
            if offset >= 64 and data[offset:offset + 4] == b"PE\0\0" and len(data) >= offset + 6:
                machine = int.from_bytes(data[offset + 4:offset + 6], "little")
                architecture = {0x14C: "x86", 0x8664: "x86-64", 0xAA64: "AArch64"}.get(machine, "unknown")
                return {"format": "PE", "architecture": architecture}
        return {"format": "MZ (DOS/NE/PE unverified within header sample)", "architecture": "unknown"}
    magic = data[:4]
    if magic in {b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe"}:
        return {"format": "Mach-O", "architecture": "unverified"}
    if magic in {b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca"}:
        return {"format": "ambiguous fat Mach-O / other magic", "architecture": "unverified"}
    return None


def inspect_game(root, max_entries=20000, max_depth=32):
    root = Path(root).absolute()
    if max_entries < 1 or max_depth < 0:
        raise ValueError("max_entries must be positive and max_depth nonnegative")
    if is_link_or_reparse(root.lstat()) or not root.is_dir():
        raise ValueError("game directory must be a real directory, not a link/reparse point")
    candidates = {}
    extensions, source_extensions = Counter(), Counter()
    warnings, build_files, binaries = [], [], []
    counts = {"entries": 0, "files": 0, "bytes": 0, "skipped_directories": 0, "skipped_links": 0}
    truncated = False
    omissions = {"evidence": 0, "build_files": 0, "binaries": 0, "warnings": 0, "metadata": 0}
    scan_errors = {"stat": 0, "read": 0, "directory": 0}
    metadata = []
    metadata_sample_limits = 0

    def warn(message):
        if len(warnings) < 100:
            warnings.append(message)
        else:
            omissions["warnings"] += 1

    def clue(engine, path, reason):
        item = candidates.setdefault(engine, {"engine": engine, "confidence": "inferred", "evidence": [], "evidence_count": 0})
        item["evidence_count"] += 1
        if len(item["evidence"]) < 10:
            item["evidence"].append({"path": path, "reason": reason})
        else:
            omissions["evidence"] += 1
        item["evidence_omitted"] = item["evidence_count"] - len(item["evidence"])

    def read_sample(path, limit):
        # The directory must stay unchanged during inspection; no target is executed.
        try:
            with path.open("rb") as stream:
                return stream.read(limit)
        except OSError as error:
            scan_errors["read"] += 1
            warn(f"cannot read {path.relative_to(root).as_posix()}: {error.strerror}")
            return b""

    def observed(engine, relative, field, value):
        if len(metadata) < 100:
            metadata.append({"engine": engine, "path": relative, "field": field, "value": value})
        else:
            omissions["metadata"] += 1

    def text_metadata(path, info, engine):
        nonlocal metadata_sample_limits
        relative = path.relative_to(root).as_posix()
        if info.st_size > TEXT_BYTES:
            metadata_sample_limits += 1
            warn(f"metadata exceeds sample limit: {relative}")
            return
        data = read_sample(path, TEXT_BYTES)
        try:
            text = data.decode("utf-8-sig")
        except UnicodeError:
            warn(f"invalid UTF-8 metadata: {relative}")
            return
        if not data:
            warn(f"empty or unreadable metadata: {relative}")
            return
        if engine == "unity":
            match = re.search(r"^m_EditorVersion:\s*([^\r\n]+)", text, re.MULTILINE)
            if match and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+[A-Za-z0-9.]*", match[1].strip()):
                observed(engine, relative, "editor_version", match[1].strip())
            else:
                warn(f"missing or invalid Unity editor version: {relative}")
        else:
            match = re.search(r"^config_version\s*=\s*([0-9]+)\s*$", text, re.MULTILINE)
            if match:
                # Descriptor format is not the engine version.
                observed(engine, relative, "config_version", match[1])
            else:
                warn(f"missing or invalid Godot config_version: {relative}")
            match = re.search(r'^config/features\s*=\s*PackedStringArray\(([^\r\n]*)\)\s*$', text, re.MULTILINE)
            if match:
                try:
                    features = json.loads("[" + match[1] + "]")
                    if not all(isinstance(value, str) for value in features):
                        raise ValueError("non-string feature")
                    observed(engine, relative, "features", features)
                except (ValueError, RecursionError):
                    warn(f"invalid Godot features: {relative}")
            elif re.search(r"^config/features\s*=", text, re.MULTILINE):
                warn(f"invalid Godot features: {relative}")

    def visit(directory, depth):
        nonlocal truncated, metadata_sample_limits
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if counts["entries"] >= max_entries:
                        truncated = True
                        return
                    counts["entries"] += 1
                    path = Path(entry.path)
                    relative = path.relative_to(root).as_posix()
                    try:
                        info = entry.stat(follow_symlinks=False)
                    except OSError as error:
                        scan_errors["stat"] += 1
                        warn(f"cannot stat {relative}: {error.strerror}")
                        continue
                    if is_link_or_reparse(info):
                        counts["skipped_links"] += 1
                        continue
                    if stat.S_ISDIR(info.st_mode):
                        if entry.name.lower() in SKIP_DIRS:
                            counts["skipped_directories"] += 1
                        elif depth >= max_depth:
                            truncated = True
                            warn(f"depth limit at {relative}")
                        else:
                            visit(path, depth + 1)
                        continue
                    if not stat.S_ISREG(info.st_mode):
                        continue
                    counts["files"] += 1
                    counts["bytes"] += info.st_size
                    name, suffix = path.name.lower(), path.suffix.lower()
                    parts = [part.lower() for part in path.relative_to(root).parts]
                    extensions[suffix or "(none)"] += 1
                    if suffix in SOURCE_SUFFIXES:
                        source_extensions[suffix] += 1
                    if name in BUILD_NAMES or suffix in {".sln", ".csproj", ".uproject", ".yyp"}:
                        if len(build_files) < 100:
                            build_files.append(relative)
                        else:
                            omissions["build_files"] += 1
                    if name == "projectversion.txt" and "projectsettings" in parts:
                        clue("unity", relative, "Unity editor version file; verify project completeness")
                        text_metadata(path, info, "unity")
                    elif name in {"unityplayer.dll", "globalgamemanagers"}:
                        clue("unity", relative, "shipped Unity runtime/data; not proof of editable source")
                    if name == "project.godot" or suffix == ".pck":
                        clue("godot", relative, "Godot project or possible exported pack; verify format/version")
                        if name == "project.godot":
                            text_metadata(path, info, "godot")
                    if suffix == ".uproject" or (suffix == ".pak" and "paks" in parts):
                        clue("unreal", relative, "Unreal project or possible packaged data")
                    if name in {"rpg_core.js", "rmmz_core.js"}:
                        clue("rpg-maker", relative, "possible MV/MZ JavaScript runtime")
                    if suffix in {".rpy", ".rpyc", ".rpa"}:
                        clue("renpy", relative, "possible Ren'Py script/archive; verify runtime")
                    if suffix == ".love" or (name == "conf.lua" and is_regular_unlinked(path.parent / "main.lua")):
                        clue("love", relative, "possible LÖVE project/package; verify version and contents")
                    if suffix == ".yyp" or name == "data.win":
                        clue("gamemaker", relative, "possible GameMaker project/runner data")
                    if name == "package.json":
                        if info.st_size > TEXT_BYTES:
                            metadata_sample_limits += 1
                            warn(f"manifest exceeds sample limit: {relative}")
                        else:
                            try:
                                manifest = json.loads(read_sample(path, TEXT_BYTES))
                                if not isinstance(manifest, dict):
                                    raise ValueError("manifest must be an object")
                                for group in ("dependencies", "devDependencies"):
                                    dependencies = manifest.get(group, {})
                                    if not isinstance(dependencies, dict):
                                        warn(f"invalid dependency group {group}: {relative}")
                                    else:
                                        for engine in ("electron", "nw", "phaser", "pixi.js", "three"):
                                            if engine in dependencies:
                                                clue(engine, relative, f"declared {engine} dependency (may be tooling)")
                                                declared = dependencies[engine]
                                                if isinstance(declared, str):
                                                    observed(engine, relative, group + "." + engine, declared)
                                                else:
                                                    warn(f"invalid dependency version for {engine}: {relative}")
                            except (ValueError, UnicodeError, RecursionError):
                                warn(f"invalid JSON or decoder nesting limit: {relative}")
                    if suffix in BINARY_SUFFIXES or (not suffix and info.st_mode & stat.S_IXUSR):
                        if len(binaries) < 100:
                            detected = binary_info(read_sample(path, HEADER_BYTES))
                            if detected:
                                binaries.append({"path": relative, **detected})
                        else:
                            # Count uninspected candidates, not invented detected formats.
                            omissions["binaries"] += 1
        except OSError as error:
            scan_errors["directory"] += 1
            warn(f"cannot scan {directory.relative_to(root).as_posix()}: {error.strerror}")

    visit(root, 0)
    if truncated:
        warn("scan limit reached; inventory is partial")
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": sorted(metadata, key=lambda item: (item["engine"], item["path"], item["field"])),
        "omitted": omissions,
        "scan_errors": scan_errors,
        "completeness": {
            "traversal_complete": not truncated and not scan_errors["directory"] and not scan_errors["stat"],
            "samples_readable": not scan_errors["read"],
            "output_capped": any(omissions.values()),
            "metadata_sample_limits": metadata_sample_limits,
        },
        "root": str(root),
        "limits": {"max_entries": max_entries, "max_depth": max_depth, "header_bytes": HEADER_BYTES, "manifest_bytes": TEXT_BYTES},
        "inventory": {**counts, "extensions": dict(sorted(extensions.items())), "source_extensions": dict(sorted(source_extensions.items()))},
        "candidates": sorted(candidates.values(), key=lambda item: item["engine"]),
        "build_files": sorted(build_files),
        "binaries": sorted(binaries, key=lambda item: item["path"]),
        "truncated": truncated,
        "warnings": warnings,
        "limitations": [
            "Filename/dependency clues do not confirm engine, editable source, rights or browser support.",
            "Archives are not opened; dependencies and binary imports are not fully analyzed.",
            "Links/reparse points, special files and common dependency/VCS directories are skipped.",
            "Evidence is capped at 10 paths per candidate; build_files and binaries at 100 each; warnings at 100.",
            "Traversal uses filesystem order; keep the input tree unchanged while scanning.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="game project or unpacked game directory")
    parser.add_argument("--max-entries", type=int, default=20000, help="entry budget, including directories (default: 20000)")
    parser.add_argument("--max-depth", type=int, default=32, help="directory depth budget (default: 32)")
    args = parser.parse_args(argv)
    try:
        report = inspect_game(args.directory, args.max_entries, args.max_depth)
    except (OSError, ValueError) as error:
        parser.exit(2, f"inspect_game: {error}\n")
    # ASCII escapes keep redirected JSON portable across terminal encodings.
    json.dump(report, sys.stdout, indent=2, ensure_ascii=True)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
