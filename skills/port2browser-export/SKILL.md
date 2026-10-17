---
name: port2browser-export
description: Export editable game-engine projects to browsers. Use for Unity, Godot, Unreal HTML5 forks, Defold, Cocos Creator, GameMaker, Construct, GDevelop and RenPy web-build workflows.
license: MIT
---

# Export an engine project

Use the actual project's matching editor, exporter/templates and plugin versions.
Work in a copy, preserve native build instructions, and record migrations instead
of upgrading a project implicitly. Confirm that scenes, scripts, import metadata,
packages and required source are present before invoking a build.

Read only the applicable playbook:

- [Unity](references/unity.md)
- [Godot](references/godot.md)
- [Unreal](references/unreal.md)
- [Defold](references/defold.md)
- [Cocos Creator](references/cocos.md)
- [GameMaker, Construct and GDevelop](references/authoring.md)
- [Ren'Py](references/renpy.md)

Build the smallest representative scene with real input and one gameplay goal.
Check the renderer/shader path and each plugin's web implementation before
optimizing assets. Retain build output and log actual exporter failures; an
unsupported native dependency must be replaced with preserved behavior or reported
as a blocker. A shipped archive is not an editable project merely because its
contents can be inspected.

Serve the generated output over HTTP(S) with the engine's required MIME,
compression and isolation settings. Verify gameplay state and rendered output,
audio after a gesture, focus loss, and a save across a full page reload. Record
browser/version and engine logs. State build-only if no browser was exercised.

Handoff: editor/exporter revision, source changes, build/run commands, produced
files, hosting requirements, tested slice and unresolved plugin/feature limits.
These playbooks are investigation guidance; they do not certify the engine's
entire catalog or every game made with it.
