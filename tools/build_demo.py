"""Package only the original SDL web output for the public Pages demo."""
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

if __name__=='__main__':
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    build_demo(ROOT/'examples/sdl-beacon/build/web',ROOT/'work/demo',revision)
