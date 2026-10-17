#!/usr/bin/env python3
"""Package the original Lua game with a pinned, explicitly adapted love.js runtime."""
import argparse
import base64
import io
import tarfile
import urllib.request
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target',choices=('web','native'))
    args=parser.parse_args()
    output=HERE/'build'/args.target;output.mkdir(parents=True,exist_ok=True)
    if args.target=='native':
        # A .love archive is the native distributable, executed by matching LÖVE.
        with zipfile.ZipFile(output/'beacon.love','w',compression=zipfile.ZIP_DEFLATED) as archive:
            for name in ('conf.lua','main.lua'):
                info=zipfile.ZipInfo(name,(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(info,(HERE/'game'/name).read_bytes())
            info=zipfile.ZipInfo('LICENSE',(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,(HERE.parents[1]/'LICENSE').read_bytes())
    else:
        cache=HERE/'build/vendor/love.js-11.4.1'
        cache.mkdir(parents=True,exist_ok=True)
        hashes={'love.js':'12db012a5cf4e0661f9eaf154c4c10c3cba7a7db31e6a36856028bbaf5f942f0',
                'love.wasm':'ecc9e098bb8af918d20fbe3f26d23495c5184ff6b5d203d2e4b27bf17a771d6f'}
        if not all((cache/name).is_file() for name in (*hashes,'LICENSE')):
            with urllib.request.urlopen('https://registry.npmjs.org/love.js/-/love.js-11.4.1.tgz',timeout=60) as response:
                data=response.read(32*1024*1024+1)
            expected='NLMD2GpIHOCsflgulr18p4+Crizfixgo5ZMbJmDrqVuR7jdketbUDL7X+LCR2o2uMkVU8ZwXnRwT86S7A75yhA=='
            if base64.b64encode(hashlib.sha512(data).digest()).decode()!=expected:raise ValueError('love.js package integrity mismatch')
            with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:
                for name in (*hashes,'LICENSE'):
                    member=archive.getmember('package/'+('LICENSE' if name=='LICENSE' else 'src/compat/'+name))
                    if not member.isfile() or member.size>20*1024*1024:raise ValueError('unexpected runtime member')
                    (cache/name).write_bytes(archive.extractfile(member).read())
        for name,digest in hashes.items():
            data=(cache/name).read_bytes()
            if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('runtime checksum mismatch: '+name)
            (output/name).write_bytes(data)
        # Original bounded preloader: no npm packaging tools or their dependencies execute.
        payload=bytearray();files=[]
        for name in ('conf.lua','main.lua'):
            data=(HERE/'game'/name).read_bytes();files.append({'name':name,'start':len(payload),'end':len(payload)+len(data)});payload.extend(data)
        (output/'game.data').write_bytes(payload)
        preload="Module.preRun=[function(){Module.addRunDependency('beacon-data');fetch('game.data').then(r=>{if(!r.ok)throw Error('game.data '+r.status);return r.arrayBuffer();}).then(b=>{const data=new Uint8Array(b);for(const f of "+json.dumps(files)+")Module.FS_createDataFile('/',f.name,data.subarray(f.start,f.end),true,true);Module.removeRunDependency('beacon-data');}).catch(e=>{console.error(e);});}];"
        (output/'game.js').write_text(preload+'\n')
        loader=output/'love.js'
        original=loader.read_text()
        marker='FS.staticInit();'
        if original.count(marker)!=1:raise ValueError('unexpected loader; adaptation must be reviewed')
        # Export only the boundary APIs needed for observation and durable saves.
        exports='Module.FS_readFile=FS.readFile;Module.FS_syncfs=FS.syncfs;Module.p2bResumeAudio=function(){return Promise.all(Object.values(AL.contexts).map(function(c){return c.audioCtx.resume();}));};'
        unload='window.addEventListener("beforeunload",function(event){FS.syncfs(false,function(err){if(err){Module["printErr"](err)}})})'
        if original.count(unload)!=1:raise ValueError('unexpected automatic unload-sync hook')
        loader.write_text(original.replace(marker,marker+exports).replace(unload,''))
        for name in ('index.html','platform.js'):shutil.copy2(HERE/name,output/name)
        (output/'runtime-adaptation.json').write_text(json.dumps({'package':'love.js','version':'11.4.1','mode':'compatibility/no pthreads','unmodified_loader_sha256':hashlib.sha256(original.encode()).hexdigest(),'patched_loader_sha256':hashlib.sha256(loader.read_bytes()).hexdigest(),'changes':['export read-only journal access','explicit asynchronous IDBFS commit','gesture-bound OpenAL context resume','remove unreliable unload sync; await explicit save commit']},indent=2)+'\n')
        shutil.copy2(cache/'LICENSE',output/'love.js-LICENSE')
        shutil.copy2(HERE/'THIRD-PARTY-LICENSES.txt',output/'THIRD-PARTY-LICENSES.txt')
        shutil.copy2(HERE/'NOTICE.md',output/'NOTICE.md')
        shutil.copy2(HERE.parents[1]/'LICENSE',output/'LICENSE')
    print(output)


if __name__=='__main__':main()
