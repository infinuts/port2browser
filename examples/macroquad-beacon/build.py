#!/usr/bin/env python3
"""Build original Macroquad game with locked crate/loader/toolchain versions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request

HERE=Path(__file__).resolve().parent
LOADER_REV='2c60f754b0c0e053f4c5b272fee696fb45e5aca8'
LOADER_SHA256='f4189c03de0b10cef3b710bdcadb22df7b835ccab5de52a3714e896e4fc48cd7'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target',choices=('web','native'))
    args=parser.parse_args()
    cargo=os.environ.get('CARGO','cargo')
    command=[cargo,'+1.85.1','build','--locked','--release','--manifest-path',str(HERE/'Cargo.toml')]
    if args.target=='web':command+=['--target','wasm32-unknown-unknown']
    env={**os.environ,'CARGO_TARGET_DIR':str(HERE/'build/target')}
    subprocess.run(command,cwd=HERE,env=env,check=True)
    output=HERE/'build'/args.target;output.mkdir(parents=True,exist_ok=True)
    if args.target=='native':
        binary='macroquad-beacon'+('.exe' if os.name=='nt' else '')
        shutil.copy2(HERE/'build/target/release'/binary,output/binary)
    else:
        for name in ('index.html','platform.js'):shutil.copy2(HERE/name,output/name)
        shutil.copy2(HERE/'build/target/wasm32-unknown-unknown/release/macroquad-beacon.wasm',output/'macroquad-beacon.wasm')
        with urllib.request.urlopen(f'https://raw.githubusercontent.com/not-fl3/macroquad/{LOADER_REV}/js/mq_js_bundle.js',timeout=60) as response:data=response.read()
        if hashlib.sha256(data).hexdigest()!=LOADER_SHA256:raise ValueError('loader checksum mismatch')
        (output/'mq_js_bundle.js').write_bytes(data)
    metadata_command=[cargo,'+1.85.1','metadata','--locked','--format-version','1','--manifest-path',str(HERE/'Cargo.toml')]
    if args.target=='web':metadata_command+=['--filter-platform','wasm32-unknown-unknown']
    metadata=json.loads(subprocess.check_output(metadata_command,cwd=HERE,env=env))
    notices=[]
    for package in metadata['packages']:
        root=Path(package['manifest_path']).parent
        notices.append(package['name']+' '+package['version']+' | '+str(package.get('license'))+' | '+str(package.get('repository')))
        for file in sorted(root.iterdir()):
            if file.is_file() and file.name.lower().startswith(('license','copying','copyright')):
                notices.extend([file.name,file.read_text(encoding='utf8',errors='replace')])
    notices.extend(['ProggyClean engine font', (HERE/'ProggyClean-LICENSE.txt').read_text()])
    (output/'THIRD-PARTY-LICENSES.txt').write_text('\n\n'.join(notices)+'\n')
    shutil.copy2(HERE/'NOTICE.md',output/'NOTICE.md')
    shutil.copy2(HERE.parents[1]/'LICENSE',output/'LICENSE')
    print(output)


if __name__=='__main__':main()
