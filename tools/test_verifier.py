#!/usr/bin/env python3
"""Serve allowlisted synthetic fixtures and run optional browser helper regressions."""
import argparse
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
from threading import Thread

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node',default='node')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    output=args.output.absolute()
    output.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('p2b_server',ROOT/'scripts/serve.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='p2b-verify-') as temporary:
        root=Path(temporary)
        game=root/'electron-beacon';game.mkdir()
        shutil.copytree(ROOT/'examples/electron-beacon/web',game/'web')
        shutil.copy2(ROOT/'examples/electron-beacon/game.js',game/'game.js')
        blank=root/'blank';blank.mkdir()
        (blank/'index.html').write_text('<!doctype html><link rel="icon" href="data:,"><canvas width="100" height="100"></canvas><script>window.exampleState=()=>({});</script>')
        with module.make_server(root,port=0) as server:
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                return subprocess.run([args.node,str(ROOT/'tools/verify_examples.cjs'),f'http://127.0.0.1:{server.server_port}',str(output)],cwd=ROOT).returncode
            finally:
                server.shutdown();thread.join(timeout=5)


if __name__=='__main__':raise SystemExit(main())
