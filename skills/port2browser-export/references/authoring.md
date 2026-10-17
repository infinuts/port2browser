# GameMaker, Construct and GDevelop

Identify project generation and exporter availability before interpreting runner
data as source. Retain extension/plugin versions and original build settings.

| Input | First experiment | Dependency to resolve |
| --- | --- | --- |
| GameMaker `.yyp`/`.yy` project | Matching HTML5 export of one room | Exporter entitlement, native extensions, shaders, buffers and save paths; `data.win` alone is runner data |
| Construct `.c3p`/folder project or older `.capx` | Matching version's Web export of one layout | Missing addons, third-party behaviors, platform-only integrations and unsupported plugin versions |
| GDevelop project with events/layouts/resources | Web export of one event-driven scene | Native-only extensions, runtime JS, external assets and platform services |

Primary entry points reviewed on 2026-10-17:
[GameMaker](https://gamemaker.io/en/get),
[Construct publishing](https://www.construct.net/en/make-games/manuals/construct-3/overview/publishing-projects),
[GDevelop Web publishing](https://wiki.gdevelop.io/gdevelop5/publishing/web/).
Use the actual editor/plan documentation; export packaging and entitlements can
change. No universal CLI invocation is assumed.

Test event/room transitions, collision, gameplay objective, menu, audio activation
and a full-reload save. Keep runtime plugin failures visible. A generated HTML
page does not establish that custom behaviors survived. Record the exact editor,
exporter, addons and browser versions. These are documented routes, not evaluated
ports for all three engines.
