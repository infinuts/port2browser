#!/usr/bin/env python3
"""Run explicit JSON-plan checks against dedicated copied runtime example builds."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from threading import Thread

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node',default='node')
    parser.add_argument('--examples',nargs='+',choices=('macroquad-beacon','love-beacon'),default=['macroquad-beacon','love-beacon'])
    parser.add_argument('--browsers',nargs='+',choices=('chromium','firefox'),default=['chromium','firefox'])
    parser.add_argument('--headed',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    output=args.output.absolute();output.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('p2b_serve',ROOT/'scripts/serve.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    records=[]
    with tempfile.TemporaryDirectory(prefix='p2b-runtime-') as temporary:
        root=Path(temporary)
        for game in args.examples:
            shutil.copytree(ROOT/'examples'/game/'build/web',root/game)
        with module.make_server(root,port=0) as server:
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                for game in args.examples:
                    for browser in args.browsers:
                        destination=output/(game+'-'+browser)
                        command=[args.node,str(ROOT/'skills/port2browser-verify/scripts/verify.cjs'),'--url',f'http://127.0.0.1:{server.server_port}/{game}/',
                                 '--plan',str(ROOT/'examples'/game/'verification.json'),'--output',str(destination),'--browser',browser]
                        if args.headed:command.append('--headed')
                        process=subprocess.run(command,cwd=ROOT)
                        evidence=destination/'evidence.json'
                        result=json.loads(evidence.read_text()) if evidence.exists() else {'result':'untested','reason':'helper did not retain a report'}
                        records.append({'example':game,'browser':browser,'exit_code':process.returncode,'result':result['result'],
                                        'evidence':destination.name+'/evidence.json','headed':args.headed})
            finally:server.shutdown();thread.join(timeout=5)
    (output/'summary.json').write_text(json.dumps({'schema_version':1,'runs':records},indent=2)+'\n')
    return 0 if all(r['result']=='pass' and r['exit_code']==0 for r in records) else 1


if __name__=='__main__':raise SystemExit(main())
