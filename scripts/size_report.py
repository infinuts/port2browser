#!/usr/bin/env python3
"""Bounded, read-only file/gzip accounting with explicit image/audio estimates."""
import argparse
import io
import json
import os
from pathlib import Path
import stat
import struct
import sys
import wave
import zlib

SKIP_DIRS = {'.git', '.svn', 'node_modules', '.venv', 'venv', '__pycache__'}
HEADER_BYTES = 65536


def linked(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def decoded_estimate(header):
    if header.startswith(b'\x89PNG\r\n\x1a\n') and len(header) >= 33 and header[12:16] == b'IHDR':
        width, height = struct.unpack('>II', header[16:24])
        if 0 < width <= 2**31-1 and 0 < height <= 2**31-1:
            return {'kind':'image_rgba8', 'width':width, 'height':height,
                    'bytes':width*height*4, 'basis':'PNG dimensions; one RGBA8 surface, no mips/copies/GPU overhead'}
    if header.startswith(b'RIFF') and header[8:12] == b'WAVE':
        try:
            with wave.open(io.BytesIO(header), 'rb') as stream:
                frames, channels, rate = stream.getnframes(), stream.getnchannels(), stream.getframerate()
                return {'kind':'audio_float32', 'frames':frames, 'channels':channels,
                        'sample_rate':rate, 'bytes':frames*channels*4,
                        'basis':'WAV declared PCM frames as float32; excludes decoder/copies/streaming'}
        except (wave.Error, EOFError, ValueError):
            pass
    return None


def size_report(directory, max_entries=20000, max_depth=32, max_bytes=256*1024*1024, top=20):
    root = Path(directory).absolute()
    info = root.lstat()
    if linked(info) or not stat.S_ISDIR(info.st_mode):
        raise ValueError('input must be a real directory, not a link/reparse point')
    if max_entries < 1 or max_depth < 0 or max_bytes < 0 or top < 0:
        raise ValueError('invalid nonnegative limits or entry budget')
    files, warnings = [], []
    counts = {'entries':0, 'files':0, 'raw_bytes':0, 'sampled_bytes':0,
              'skipped_links':0, 'skipped_directories':0, 'read_errors':0,
              'scan_errors':0, 'gzip_omitted':0, 'warnings_omitted':0}
    truncated = False

    def warn(message):
        if len(warnings) < 100:
            warnings.append(message)
        else:
            counts['warnings_omitted'] += 1

    def visit(directory, depth):
        nonlocal truncated
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if counts['entries'] >= max_entries:
                        truncated = True
                        return
                    counts['entries'] += 1
                    path = Path(entry.path)
                    relative = path.relative_to(root).as_posix()
                    try:
                        info = entry.stat(follow_symlinks=False)
                    except OSError as error:
                        counts['scan_errors'] += 1
                        warn(f'cannot stat {relative}: {error.strerror}')
                        continue
                    if linked(info):
                        counts['skipped_links'] += 1
                        continue
                    if stat.S_ISDIR(info.st_mode):
                        if entry.name in SKIP_DIRS:
                            counts['skipped_directories'] += 1
                        elif depth >= max_depth:
                            truncated = True
                        else:
                            visit(path, depth+1)
                        continue
                    if not stat.S_ISREG(info.st_mode):
                        continue
                    counts['files'] += 1
                    counts['raw_bytes'] += info.st_size
                    row = {'path':relative, 'raw_bytes':info.st_size, 'gzip_bytes':None,
                           'decoded_estimate':None}
                    try:
                        with path.open('rb') as stream:
                            header = stream.read(min(HEADER_BYTES, max(0, max_bytes-counts['sampled_bytes'])))
                            counts['sampled_bytes'] += len(header)
                            row['decoded_estimate'] = decoded_estimate(header)
                            if info.st_size > len(header) + max_bytes-counts['sampled_bytes']:
                                counts['gzip_omitted'] += 1
                            else:
                                encoder = zlib.compressobj(9, zlib.DEFLATED, 31)
                                compressed = len(encoder.compress(header))
                                consumed = len(header)
                                while consumed < info.st_size:
                                    chunk = stream.read(min(65536, info.st_size-consumed))
                                    if not chunk:
                                        raise OSError('file changed while reading')
                                    counts['sampled_bytes'] += len(chunk)
                                    consumed += len(chunk)
                                    compressed += len(encoder.compress(chunk))
                                row['gzip_bytes'] = compressed + len(encoder.flush())
                    except OSError as error:
                        counts['read_errors'] += 1
                        counts['gzip_omitted'] += int(row['gzip_bytes'] is None)
                        warn(f'cannot read {relative}: {error}')
                    files.append(row)
        except OSError as error:
            counts['scan_errors'] += 1
            warn(f'cannot scan {directory.relative_to(root).as_posix()}: {error.strerror}')

    visit(root, 0)
    files.sort(key=lambda row: row['path'])
    measured = [row for row in files if row['gzip_bytes'] is not None]
    return {'schema_version':1, 'root':str(root), 'inventory':counts,
            'limits':{'max_entries':max_entries,'max_depth':max_depth,'max_bytes':max_bytes},
            'completeness':{'traversal_complete':not truncated and not counts['scan_errors'],
                            'gzip_complete':len(measured)==len(files),
                            'readable':not counts['read_errors']},
            'gzip':{'level':9,'zlib_version':zlib.ZLIB_RUNTIME_VERSION,
                    'raw_bytes_measured':sum(r['raw_bytes'] for r in measured),
                    'bytes':sum(r['gzip_bytes'] for r in measured)},
            'files':files, 'largest':sorted(files,key=lambda row:(-row['raw_bytes'],row['path']))[:top],
            'warnings':warnings,
            'limitations':['Gzip is a candidate encoding, not a deployed transfer measurement; already encoded files are also measured.',
                           'PNG/WAV header estimates are not validated decodes or measured peak memory; other formats remain unknown.',
                           'Totals do not identify startup vs later requests, device GPU memory, mipmaps, loader/decoder copies or Wasm heap.',
                           'Keep the tree unchanged; links/reparse points, special files and common dependency directories are skipped.']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--max-entries',type=int,default=20000)
    parser.add_argument('--max-depth',type=int,default=32)
    parser.add_argument('--max-bytes',type=int,default=256*1024*1024,help='total read budget (default 256 MiB)')
    parser.add_argument('--top',type=int,default=20)
    args = parser.parse_args(argv)
    try:
        report = size_report(args.directory,args.max_entries,args.max_depth,args.max_bytes,args.top)
    except (OSError, ValueError) as error:
        parser.exit(2,f'size_report: {error}\n')
    json.dump(report,sys.stdout,indent=2,ensure_ascii=True)
    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
