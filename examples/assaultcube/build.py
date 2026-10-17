"""Build a pinned AssaultCube browser client. No stock media are published."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
REVISION = '1ece5af7533983bb8f827616381d282470793d90'  # upstream v1.3.0.2
SDK_VERSION = '4.0.16'


def run(*args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def asset_manifest(source):
    files = []
    for folder in ('packages', 'config', 'bot'):
        for path in sorted((source / folder).rglob('*')):
            if path.is_symlink():
                raise ValueError('linked asset: ' + str(path))
            if path.is_file():
                data = path.read_bytes()
                files.append({'path': path.relative_to(source).as_posix(), 'bytes': len(data),
                              'sha256': hashlib.sha256(data).hexdigest()})
    return {'revision': REVISION, 'version': '1.3.0.2', 'files': files,
            'bytes': sum(item['bytes'] for item in files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='existing, clean pinned upstream checkout')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    compiler = shutil.which('em++')
    if not compiler:
        raise SystemExit('Activate Emscripten 4.0.16 first (see README).')
    version = subprocess.check_output([compiler, '--version'], text=True)
    if not re.search(r'\b4\.0\.16\b', version):
        raise SystemExit('This example requires Emscripten 4.0.16.')
    sdk = Path(compiler).resolve().parent
    build = HERE / 'build'
    build.mkdir(exist_ok=True)
    source = (args.source or build / 'upstream').resolve()
    if not source.exists():
        run('git', 'clone', '--depth', '1', '--branch', 'v1.3.0.2',
            'https://github.com/assaultcube/AC.git', source)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=source, text=True)
    if revision != REVISION or dirty:
        raise SystemExit('Use an untouched v1.3.0.2 checkout at ' + REVISION)
    engine = build / 'engine'
    # Keep the original intact; all adaptations are applied to a disposable copy.
    patch = (HERE / 'browser.patch').read_bytes()
    fingerprint = hashlib.sha256(patch + (HERE / 'build.py').read_bytes()).hexdigest()
    stamp = build / 'engine-fingerprint'
    if not stamp.exists() or stamp.read_text() != fingerprint:
        if engine.exists():
            shutil.rmtree(engine)
        shutil.copytree(source / 'source', engine / 'source')
        run('git', 'apply', HERE / 'browser.patch', cwd=engine)
        stamp.write_text(fingerprint)
    src = engine / 'source/src'
    objects = build / ('obj-debug' if args.debug else 'obj')
    objects.mkdir(exist_ok=True)
    output = build / ('debug-web' if args.debug else 'web')
    output.mkdir(exist_ok=True)
    flags = ['-O1', '-g'] if args.debug else ['-Oz', '-g0']
    flags += ['-fsigned-char', '-Wno-c++11-narrowing', '-Wno-deprecated-declarations',
              '-I' + str(src), '-I' + str(src / 'bot'), '-I' + str(engine / 'source/enet/include'),
              '-idirafter', str(engine / 'source/include'), '-sUSE_SDL=2', '-sUSE_SDL_IMAGE=2',
              '-sSDL2_IMAGE_FORMATS=["png","jpg"]', '-sUSE_VORBIS=1', '-sUSE_ZLIB=1']
    names = re.search(r'CLIENT_OBJS= (.*?)\n\nCLIENT_PCH', (src / 'Makefile').read_text(), re.S)
    if not names:
        raise SystemExit('Pinned upstream source list changed.')
    sources = [src / name.replace('.o', '.cpp') for name in names.group(1).replace('\\', '').split()]
    sources.append(HERE / 'web_bridge.cpp')
    headers = b''.join(p.read_bytes() for p in sorted(src.rglob('*.h')))
    common = hashlib.sha256(headers + json.dumps(flags).encode()).digest()

    def compile_cpp(path):
        obj = objects / (path.relative_to(src).as_posix().replace('/', '_') + '.o' if path.is_relative_to(src) else 'web_bridge.o')
        key = hashlib.sha256(common + path.read_bytes()).hexdigest()
        marker = obj.with_suffix('.sha256')
        if not obj.exists() or not marker.exists() or marker.read_text() != key:
            run(compiler, *flags, '-c', path, '-o', obj)
            marker.write_text(key)
        return obj

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        built = list(pool.map(compile_cpp, sources))
    for name in ('callbacks', 'compress', 'host', 'list', 'packet', 'peer', 'protocol', 'unix'):
        obj = objects / ('enet_' + name + '.o')
        cflags = ['-Oz', '-DHAS_SOCKLEN_T=1', '-DHAS_FCNTL=1', '-DHAS_INET_PTON=1',
                  '-DHAS_INET_NTOP=1', '-DHAS_MSGHDR_FLAGS=1', '-I' + str(engine / 'source/enet/include')]
        run(sdk / 'emcc', *cflags, '-c', engine / ('source/enet/' + name + '.c'), '-o', obj)
        built.append(obj)
    run(compiler, *flags, *built, '-lopenal', '-lidbfs.js', '--js-library', HERE / 'immediate.js',
        '--post-js', HERE / 'runtime.js', '-sLEGACY_GL_EMULATION=1', '-sGL_UNSAFE_OPTS=0',
        '-sEMULATE_FUNCTION_POINTER_CASTS=1', '-sALLOW_MEMORY_GROWTH=1',
        '-sINITIAL_MEMORY=134217728', '-sSTACK_SIZE=5242880', '-sSTACK_OVERFLOW_CHECK=2',
        '-sEXPORTED_RUNTIME_METHODS=["ccall","FS","callMain","IDBFS"]',
        '-sFORCE_FILESYSTEM=1', '-sASSERTIONS=1', '-o', output / 'ac.js')
    from runtime_fixes import fix_texture_jit
    runtime = output / 'ac.js'
    runtime.write_text(fix_texture_jit(runtime.read_text()))
    for name in ('index.html', 'launcher.js'):
        shutil.copyfile(HERE / name, output / name)
    (output / 'assets.json').write_text(json.dumps(asset_manifest(source), separators=(',', ':')) + '\n')
    notices = output / 'licenses'
    notices.mkdir(exist_ok=True)
    for name, path in [('AssaultCube.txt', 'source/README.txt'), ('Cube.txt', 'source/README_CUBEENGINE.txt'),
                       ('ENet.txt', 'source/enet/LICENSE')]:
        shutil.copyfile(source / path, notices / name)
    shutil.copyfile(sdk / 'LICENSE', notices / 'Emscripten.txt')
    shutil.copyfile(HERE / 'NOTICE.md', output / 'NOTICE.md')
    (output / 'version.json').write_text(json.dumps({'upstream_revision': REVISION,
        'emscripten': SDK_VERSION, 'media': 'local files only; never included in this output',
        'files': {p.name: p.stat().st_size for p in output.iterdir() if p.is_file() and p.name != 'version.json'}}, indent=2) + '\n')
    print('Built browser client:', output)
    print('Select the pinned game folder in the launcher:', source)


if __name__ == '__main__':
    main()
