#!/usr/bin/env python3
"""Serve a browser game build on loopback. Local testing only; no dependencies."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import mimetypes
import math
import os
import re
import time
from pathlib import Path
import stat
import sys
from urllib.parse import unquote, urlsplit


def link_or_reparse(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


class GameHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".wasm": "application/wasm",
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".data": "application/octet-stream",
        ".pck": "application/octet-stream",
    }

    def __init__(self, *args, directory, isolate=False, throttle=0, **kwargs):
        self.build_root = Path(directory).resolve()
        self.isolate = isolate
        self.throttle = throttle
        self.byte_range = None
        super().__init__(*args, directory=str(self.build_root), **kwargs)

    def allowed_request(self):
        # Validate URL components before SimpleHTTPRequestHandler normalizes them.
        decoded = unquote(urlsplit(self.path).path)
        if "\\" in decoded or "\0" in decoded:
            return False
        parts = [part for part in decoded.split("/") if part]
        if any(part.startswith(".") or ":" in part for part in parts):
            return False
        path = self.build_root
        for part in parts:
            path /= part
            try:
                if link_or_reparse(path):
                    return False
            except FileNotFoundError:
                break  # The ordinary handler will return 404.
            except OSError:
                return False
        # Resolve as well to defend against platform-specific path interpretations.
        try:
            path.resolve().relative_to(self.build_root)
        except (ValueError, OSError):
            return False
        return True

    def send_head(self):
        if not self.allowed_request():
            self.send_error(403, "Path is outside the build or is hidden/linked")
            return None
        # Directory requests may resolve an index that wasn't part of the URL.
        local_path = Path(self.translate_path(self.path))
        if local_path.is_dir():
            for name in ("index.html", "index.htm"):
                index = local_path / name
                if index.exists() or index.is_symlink():
                    if link_or_reparse(index):
                        self.send_error(403, "Linked index is not served")
                        return None
        # RFC 9110 permits ignoring unsupported/malformed or multipart ranges.
        # If-Range/conditional requests use the base handler's full response;
        # we do not issue a strong validator suitable for resuming changed files.
        self.byte_range = None
        header = self.headers.get("Range", "")
        if (self.command == "GET" and header and len(header) <= 256
                and not any(self.headers.get(h) for h in
                            ("If-Range", "If-Modified-Since", "If-None-Match"))
                and local_path.is_file()):
            match = re.fullmatch(r"bytes=([0-9]*)-([0-9]*)", header.strip())
            if match and any(match.groups()):
                try:
                    stream = local_path.open("rb")
                except OSError:
                    self.send_error(404, "File not found")
                    return None
                info = os.fstat(stream.fileno())
                size = info.st_size
                first, last = match.groups()
                if first:
                    start, end = int(first), min(int(last) if last else size-1, size-1)
                else:
                    length = int(last)
                    start, end = max(0, size-length), size-1
                if start >= size or end < start:
                    stream.close()
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return None
                self.byte_range = (start, end)
                stream.seek(start)
                self.send_response(206)
                self.send_header("Content-Type", self.guess_type(local_path))
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Content-Length", str(end-start+1))
                self.send_header("Last-Modified", self.date_time_string(info.st_mtime))
                self.end_headers()
                return stream
        return super().send_head()

    def copyfile(self, source, outputfile):
        remaining = None if self.byte_range is None else self.byte_range[1]-self.byte_range[0]+1
        started, sent = time.monotonic(), 0
        chunk_size = min(65536, max(1, int(self.throttle / 10))) if self.throttle else 65536
        while remaining is None or remaining > 0:
            data = source.read(chunk_size if remaining is None else min(chunk_size, remaining))
            if not data:
                break
            sent += len(data)
            if self.throttle:
                time.sleep(max(0, sent/self.throttle - (time.monotonic()-started)))
            outputfile.write(data)
            if remaining is not None:
                remaining -= len(data)

    def list_directory(self, path):
        self.send_error(403, "No index.html; directory listing is disabled")
        return None

    def guess_type(self, path):
        # The engine's loader requests .wasm.gz/.js.br explicitly.
        filename = str(path)
        for suffix in (".gz", ".br"):
            if filename.lower().endswith(suffix):
                filename = filename[:-len(suffix)]
                break
        extension = Path(filename).suffix.lower()
        return self.extensions_map.get(extension) or mimetypes.guess_type(filename)[0] or "application/octet-stream"

    def end_headers(self):
        # Encode only successful, explicitly requested compressed resources.
        # send_response stores the current status, including HEAD responses.
        if getattr(self, "response_status", 0) in (200, 206):
            self.send_header("Accept-Ranges", "bytes")
            path = unquote(urlsplit(self.path).path).lower()
            if path.endswith(".gz"):
                self.send_header("Content-Encoding", "gzip")
            elif path.endswith(".br"):
                self.send_header("Content-Encoding", "br")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if self.isolate:
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()

    def send_response(self, code, message=None):
        self.response_status = code
        super().send_response(code, message)


def make_server(directory, port=8000, isolate=False, throttle=0):
    if not math.isfinite(throttle) or throttle < 0:
        raise ValueError("throttle must be finite and nonnegative bytes/second")
    directory = Path(directory).absolute()
    if link_or_reparse(directory) or not directory.is_dir():
        raise ValueError("build directory must be a real directory, not a link/reparse point")
    handler = partial(GameHandler, directory=directory, isolate=isolate, throttle=throttle)
    return ThreadingHTTPServer(("127.0.0.1", port), handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="dedicated web build directory")
    parser.add_argument("--port", type=int, default=8000, help="loopback port (default: 8000; 0 chooses a free port)")
    parser.add_argument("--isolate", action="store_true", help="add COOP/COEP for runtimes using SharedArrayBuffer")
    parser.add_argument("--throttle", type=float, default=0, metavar="KIB_PER_SECOND",
                        help="per-response transfer limit in KiB/s (0 disables; not network latency simulation)")
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")
    try:
        with make_server(args.directory, args.port, args.isolate, args.throttle * 1024) as server:
            print(f"Serving {args.directory.resolve()} at http://127.0.0.1:{server.server_port}/", flush=True)
            print(f"Cross-origin isolation: {'on' if args.isolate else 'off'}. Stop with Ctrl+C.", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError) as error:
        parser.exit(2, f"serve: {error}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
