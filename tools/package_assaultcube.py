"""Copy only the asset-free AssaultCube launcher/runtime to a static site."""
import json
from pathlib import Path
import shutil

FILES = ('index.html', 'launcher.js', 'ac.js', 'ac.wasm', 'assets.json', 'NOTICE.md', 'version.json')
LICENSES = ('AssaultCube.txt', 'Cube.txt', 'ENet.txt', 'Emscripten.txt')


def package_client(source, target, revision):
    source, target = Path(source), Path(target)
    if target.exists():
        raise ValueError('choose a new AssaultCube output directory')
    if list(source.glob('*.data')):
        raise ValueError('media-preloaded builds must never be published by this packager')
    manifest = json.loads((source / 'assets.json').read_text())
    if not manifest.get('files') or any(not item['path'].startswith(('packages/', 'config/', 'bot/'))
                                       or '..' in item['path'].split('/') for item in manifest['files']):
        raise ValueError('invalid upstream asset manifest')
    names = list(FILES) + ['licenses/' + name for name in LICENSES]
    for name in names:
        path = source / name
        if not path.is_file() or path.is_symlink() or path.parent.is_symlink():
            raise ValueError('missing or linked client file: ' + name)
    target.mkdir(parents=True)
    for name in names:
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, path)
    page = target / 'index.html'
    page.write_text(page.read_text().replace('/tree/assaultcube-demo/', '/tree/' + revision + '/'))
    version = json.loads((target / 'version.json').read_text())
    version['skill_revision'] = revision
    version['files'] = {name: (target / name).stat().st_size for name in FILES if name != 'version.json'}
    (target / 'version.json').write_text(json.dumps(version, indent=2) + '\n')
