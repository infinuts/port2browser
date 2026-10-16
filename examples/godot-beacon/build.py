"""Original Godot fixture build and native smoke (development only)."""
import argparse
import os
from pathlib import Path
import subprocess
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('target', choices=['web', 'native-smoke'])
args = parser.parse_args()
godot = os.environ.get('GODOT', 'godot')
version = subprocess.check_output([godot, '--version'], text=True).strip()
if not version.startswith('4.5.1.stable.'):
    parser.error('use the pinned Godot 4.5.1 standard editor and export templates')
with tempfile.TemporaryDirectory(prefix='godot-beacon-build-') as temporary:
    project = Path(temporary) / 'project'
    shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns('build', '.godot', '*.uid'))
    if os.environ.get('GODOT_WEB_TEMPLATE'):
        preset = project / 'export_presets.cfg'
        preset.write_text(preset.read_text() + '\ncustom_template/release="' + Path(os.environ['GODOT_WEB_TEMPLATE']).resolve().as_posix() + '"\n')
    subprocess.run([godot, '--headless', '--path', str(project), '--editor', '--import'], check=True)
    if args.target == 'web':
        out = ROOT / 'build/web'
        out.mkdir(parents=True, exist_ok=True)
        subprocess.run([godot, '--headless', '--path', str(project), '--export-release', 'Web', str(out / 'index.html')], check=True)
        print(out)
    else:
        env = dict(os.environ, P2B_GODOT_SAVE_PATH=str(Path(temporary) / 'beacon.json'))
        subprocess.run([godot, '--headless', '--path', str(project), '--audio-driver', 'Dummy', '--', '--smoke'], env=env, check=True, timeout=30)
