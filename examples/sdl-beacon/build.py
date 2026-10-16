"""Build the original fixture. Development only; no installed-skill dependencies."""
import argparse
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('target', choices=['web', 'native'])
args = parser.parse_args()
out = ROOT / 'build' / args.target
out.mkdir(parents=True, exist_ok=True)
if args.target == 'web':
    version = subprocess.check_output(['emcc', '--version'], text=True).splitlines()[0]
    if '4.0.16' not in version:
        parser.error('use the pinned Emscripten 4.0.16 SDK')
    command = ['emcc', str(ROOT / 'game.c'), '-O1', '-g', '-sUSE_SDL=2', '-sASSERTIONS=1',
               '-sFORCE_FILESYSTEM=1', '-lidbfs.js', '--shell-file', str(ROOT / 'shell.html'),
               '-o', str(out / 'index.html')]
else:
    flags = shlex.split(subprocess.check_output(['sdl2-config', '--cflags', '--libs'], text=True))
    command = [os.environ.get('CC', 'cc'), str(ROOT / 'game.c'), '-std=c99', '-Wall', '-Wextra', *flags, '-lm', '-o', str(out / 'beacon')]
subprocess.run(command, check=True)
print(out)
