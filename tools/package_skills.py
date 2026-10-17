#!/usr/bin/env python3
"""Build a portable bundle or separately discoverable task-skill collection."""
import argparse
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]


def package(output, layout='bundle', source=ROOT):
    if layout not in ('bundle', 'collection'):
        raise ValueError('unknown layout')
    source = Path(source).resolve()
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise ValueError('output must be a new directory')
    if output.resolve().is_relative_to(source):
        raise ValueError('output must be outside the source tree')
    selected = [source / name for name in ('SKILL.md', 'LICENSE')]
    for directory in ('references', 'scripts', 'skills'):
        base = source / directory
        if base.is_symlink():
            raise ValueError('links are not packaged')
        selected.extend(p for p in base.rglob('*') if '__pycache__' not in p.parts)
    if any(p.is_symlink() for p in selected):
        raise ValueError('links are not packaged')
    mapping = {}
    for path in selected:
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if layout == 'collection' and relative.parts[0] == 'skills':
            target = output.joinpath(*relative.parts[1:])
        else:
            target = output / 'port2browser' / relative
        mapping[path] = target
    output.mkdir(parents=True)
    for path, target in mapping.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        if layout == 'collection' and path.suffix == '.md':
            import os
            def link(match):
                value = match[1]
                if '://' in value or value.startswith('#'):
                    return match[0]
                part, separator, anchor = value.partition('#')
                resolved = (path.parent / part).resolve()
                if resolved not in mapping:
                    return match[0]
                return '](' + Path(os.path.relpath(mapping[resolved], target.parent)).as_posix() + (separator + anchor if separator else '') + ')'
            target.write_text(re.sub(r'\]\(([^)]+)\)', link, path.read_text(encoding='utf-8')), encoding='utf-8')
        elif layout == 'collection' and path.name == 'engine-routes.json':
            import os
            catalog = json.loads(path.read_text(encoding='utf-8'))
            for engine in catalog['engines']:
                engine['guide'] = Path(os.path.relpath(mapping[source / engine['guide']], output / 'port2browser')).as_posix()
            target.write_text(json.dumps(catalog, indent=2) + '\n', encoding='utf-8')
        else:
            shutil.copy2(path, target)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--layout', choices=('bundle', 'collection'), default='bundle')
    args = parser.parse_args()
    try:
        print(package(args.output, args.layout))
    except (OSError, ValueError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
