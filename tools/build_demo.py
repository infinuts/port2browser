"""Package original demos for public static hosting (development only)."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def build_demo(source, target, revision):
    if target.exists():
        raise ValueError('choose a new demo output directory')
    target.mkdir(parents=True)
    # Explicit allowlist: never copy the game repository, private saves or dev tools.
    for name in ('index.html','index.js','index.wasm'):
        path=source/name
        if not path.is_file() or path.is_symlink():
            raise ValueError('missing or linked web build file: '+name)
        shutil.copy2(path,target/name)
    page=target/'index.html'
    navigation='<nav><a style="color:#7dd3fc" href="https://github.com/infinuts/port2browser">port2browser source</a> · <a style="color:#7dd3fc" href="https://github.com/infinuts/port2browser/blob/'+revision+'/examples/sdl-beacon/port-report.md">Tested port report</a></nav>'
    page.write_text(page.read_text().replace('<h1>SDL Beacon</h1>',navigation+'<h1>SDL Beacon</h1>'))
    (target/'version.json').write_text(json.dumps({'revision':revision,'example':'sdl-beacon','emscripten':'4.0.16'},indent=2)+'\n')
    (target/'.nojekyll').touch()

def build_showcase(source, target, revision, reference, debug=None):
    """Package the game for header-free static hosting; preserve raw comparisons."""
    import gzip
    import hashlib
    import io
    import platform
    import zlib
    names=('index.html','index.js','index.wasm')
    def read_files(directory):
        result={}
        for name in names:
            path=directory/name
            if not path.is_file() or path.is_symlink():
                raise ValueError('missing or linked game build file: '+str(path))
            result[name]=path.read_bytes()
        return result
    release=read_files(source)
    baseline=read_files(debug) if debug else None
    original=read_files(reference)
    if target.exists():
        raise ValueError('choose a new demo output directory')
    markers=[b'<script async src="index.js"></script>',b'<script async src=index.js></script>']
    found=[m for m in markers if release['index.html'].count(m)==1]
    if len(found)!=1:
        raise ValueError('expected the pinned SDK runtime script tag exactly once')
    marker=found[0]
    target.mkdir(parents=True)
    packed={}
    for source_name, destination in [('index.js','runtime.bin'),('index.wasm','engine.bin')]:
        stream=io.BytesIO()
        with gzip.GzipFile(filename='',fileobj=stream,mode='wb',compresslevel=9,mtime=0) as archive:
            archive.write(release[source_name])
        data=stream.getvalue()
        if gzip.decompress(data)!=release[source_name]:
            raise ValueError('compressed content mismatch')
        (target/destination).write_bytes(data)
        packed[destination]={'bytes':len(data),'decoded_bytes':len(release[source_name]),'decoded_sha256':hashlib.sha256(release[source_name]).hexdigest()}
    loader=(ROOT/'examples/mosslight/packed-loader.js').read_bytes()
    (target/'packed-loader.js').write_bytes(loader)
    html=release['index.html'].replace(marker,b'<script src="packed-loader.js"></script>')
    html=html.replace(b'The development build loads uncompressed JS and Wasm.',b'This is the complete gzip release. <a href="uncompressed/">Try uncompressed</a> / <a href="beacon/">Minimal Beacon</a> / <a href="size-report.json">Size manifest</a>.')
    html=html.replace(b'/blob/codex/demo-evals-godot/',('/blob/'+revision+'/').encode()).replace(b'/tree/codex/demo-evals-godot/',('/tree/'+revision+'/').encode())
    core_bytes=len(html)+len(loader)+sum(v['bytes'] for v in packed.values())
    html=html.replace(b'Original artwork &amp; generated sound.',b'Original artwork & generated sound.')
    html=html.replace(b'Original artwork & generated sound.',f'{core_bytes/1024:.1f} KiB game payload / gzip release'.encode())
    # Recalculate after adding the badge; manifest counts exactly what is fetched.
    core_bytes=len(html)+len(loader)+sum(v['bytes'] for v in packed.values())
    (target/'index.html').write_bytes(html)
    for directory,files in [('uncompressed',release),('beacon',original)]:
        out=target/directory;out.mkdir()
        for name,data in files.items():(out/name).write_bytes(data)
    report={'schema_version':1,'revision':revision,'example':'mosslight','emscripten':'4.0.16',
            'compression':'gzip level 9; deterministic headers; application decoding',
            'packing_tools':{'python':platform.python_version(),'zlib':zlib.ZLIB_RUNTIME_VERSION},
            'debug_raw_bytes':sum(map(len,baseline.values())) if baseline else None,
            'release_raw_bytes':sum(map(len,release.values())),
            'packed_startup_bytes':core_bytes,'packed_files':packed,
            'startup_files':['index.html','packed-loader.js','runtime.bin','engine.bin'],
            'scope':'Entire original procedural game; no external art/audio or later asset packs. Raw/reference copies are separate optional downloads.',
            'measurements':{'browser_transfer':'see browser evidence; numbers here are file bytes before HTTP overhead','peak_memory':'untested','manual_listening':'untested'}}
    (target/'size-report.json').write_text(json.dumps(report,indent=2)+'\n')
    (target/'version.json').write_text(json.dumps({'revision':revision,'example':'mosslight','emscripten':'4.0.16'},indent=2)+'\n')
    (target/'.nojekyll').touch()
    return report

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'work/demo')
    args=parser.parse_args()
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    debug=ROOT/'examples/mosslight/build/debug-web'
    report=build_showcase(ROOT/'examples/mosslight/build/web',args.output.resolve(),revision,ROOT/'examples/sdl-beacon/build/web',debug if debug.is_dir() else None)
    print(json.dumps(report,indent=2))
