# Godot project → Web

Confirm the project, script language, engine revision, renderer and GDExtensions.
`config_version` is the descriptor format, not the engine version. An exported
PCK alone does not establish complete source.

Use matching editor/export templates and a real Web preset. For example, an
existing preset named `Web` can be built with `godot --headless --path <project>
--export-release Web <output>/index.html`; quote paths and use the preset's exact
name. Keep engine-generated filenames together.

The [stable Web guide](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)
reviewed on 2026-10-17 requires Godot 4's Compatibility renderer/WebGL 2 and still
lists C# Web export as unavailable. Recheck version-matching guidance before a
future claim. Audit native extensions for a corresponding web build. Choose
single-thread vs threaded templates deliberately; test required isolation headers
and third-party asset compatibility for threaded output.

Milestone: a rendered scene with movement/interaction, gesture-bound sound and
user storage restored by a new page instance. Forward+/Mobile rendering, C# and
missing extension libraries are separate dependencies, not fixed by swapping a
template. The repository's GDScript example covers its recorded version/slice;
it does not certify arbitrary Godot games.
