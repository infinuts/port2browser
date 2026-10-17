"""Build original Mosslight with a pinned Emscripten SDK (development only)."""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('target',choices=['native','web','debug-web'])
args=parser.parse_args()
out=ROOT/'build'/args.target;out.mkdir(parents=True,exist_ok=True)
if args.target!='native':
    if '4.0.16' not in subprocess.check_output(['em++','--version'],text=True).splitlines()[0]:parser.error('use Emscripten 4.0.16')
    options=['-Oz','-flto','-g0','-sASSERTIONS=0'] if args.target=='web' else ['-O1','-g','-sASSERTIONS=1']
    command=['em++',str(ROOT/'game.cpp'),'-std=c++17',*options,'-sUSE_SDL=2','-sENVIRONMENT=web','-sFORCE_FILESYSTEM=1','-lidbfs.js','--shell-file',str(ROOT/'shell.html'),'-o',str(out/'index.html')]
else:
    flags=shlex.split(subprocess.check_output(['sdl2-config','--cflags','--libs'],text=True))
    command=[os.environ.get('CXX','c++'),str(ROOT/'game.cpp'),'-std=c++17','-O2','-Wall','-Wextra',*flags,'-o',str(out/'mosslight')]
subprocess.run(command,check=True);print(out)
