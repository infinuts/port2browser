# Engine and framework coverage

The task skills cover assessment and version-specific porting workflows. This is
**documented routing coverage**, not a claim that every engine or most modern
games have been ported. Existing evaluated examples remain in the README's
evidence table; no new engine/browser gameplay benchmark was run for this change.

Primary starting points were reviewed on 2026-10-17. Before using a route, verify
the exact project/runtime version and current matching documentation. Modern
proprietary, online-only or native-middleware games can remain blocked even when
their engine has some browser backend.

| Engine/framework family | Task/playbook | Required material or first gate |
| --- | --- | --- |
| Unity | [port2browser-export](../skills/port2browser-export/references/unity.md) | Complete matching editor project; web-compatible plugins |
| Godot | [port2browser-export](../skills/port2browser-export/references/godot.md) | Matching editor/templates, supported renderer/language/extensions |
| Unreal | [port2browser-export](../skills/port2browser-export/references/unreal.md) | Exact compatible HTML5 fork and editable project; UE5 not assumed |
| Defold | [port2browser-export](../skills/port2browser-export/references/defold.md) | Complete collection/project and HTML5-compatible extensions |
| Cocos Creator | [port2browser-export](../skills/port2browser-export/references/cocos.md) | Matching Creator generation, project and web plugins |
| GameMaker | [port2browser-export](../skills/port2browser-export/references/authoring.md) | Editable project, exporter access and compatible extensions |
| Construct | [port2browser-export](../skills/port2browser-export/references/authoring.md) | Matching project generation/addons and Web exporter |
| GDevelop | [port2browser-export](../skills/port2browser-export/references/authoring.md) | Complete events/layouts/resources and compatible extensions |
| RenPy | [port2browser-export](../skills/port2browser-export/references/renpy.md) | Matching editable project/SDK and supported Python/codecs |
| LOVE | [port2browser-frameworks](../skills/port2browser-frameworks/references/scripted.md) | Version-compatible love.js backend; native modules audited |
| Pygame/Python | [port2browser-frameworks](../skills/port2browser-frameworks/references/scripted.md) | Matching pygame-web runtime and Wasm-built modules |
| OpenFL | [port2browser-frameworks](../skills/port2browser-frameworks/references/scripted.md) | Haxe project and HTML5-compatible libraries |
| Heaps | [port2browser-frameworks](../skills/port2browser-frameworks/references/scripted.md) | Haxe source, compatible JS backend and resources |
| Bevy | [port2browser-frameworks](../skills/port2browser-frameworks/references/rust.md) | Rust source/lockfile and chosen web renderer/features |
| Macroquad | [port2browser-frameworks](../skills/port2browser-frameworks/references/rust.md) | Rust source and matching Wasm/JS bundle |
| libGDX | [port2browser-frameworks](../skills/port2browser-frameworks/references/java.md) | Source and compatible GWT/HTML module/libraries |
| MonoGame/XNA | [port2browser-frameworks](../skills/port2browser-frameworks/references/dotnet.md) | Rebuildable source and proven browser framework/content backend |
| FNA | [port2browser-frameworks](../skills/port2browser-frameworks/references/dotnet.md) | Source and proven browser graphics/audio/native-library backend |
| Electron | [port2browser-web](../skills/port2browser-web/SKILL.md) | Browser gameplay source and replacements for desktop services |
| NW.js | [port2browser-web](../skills/port2browser-web/SKILL.md) | Browser runtime plus compatible Node/native API substitutions |
| RPG Maker MV/MZ | [port2browser-web](../skills/port2browser-web/SKILL.md) | Matching JavaScript runtime and browser-compatible plugins |
| Phaser | [port2browser-web](../skills/port2browser-web/SKILL.md) | Browser entrypoint, plugins, physics and complete resources |
| PixiJS | [port2browser-web](../skills/port2browser-web/SKILL.md) | Actual game logic/runtime around renderer library and complete resources |
| Three.js | [port2browser-web](../skills/port2browser-web/SKILL.md) | Actual game/runtime, graphics features and complete resources |
| SDL/C/C++ | [port2browser-native](../skills/port2browser-native/references/renderers.md) | Rebuildable game/dependencies and viable renderer |
| Custom native engines | [port2browser-native](../skills/port2browser-native/references/renderers.md) | Full dependency graph, source/rights and actual web backend |
| Compatible open engines | [port2browser-open-runtime](../skills/port2browser-open-runtime/SKILL.md) | Exact game/data format compatibility and separate rights |
| Legacy emulation | [port2browser-open-runtime](../skills/port2browser-open-runtime/SKILL.md) | Exact platform/backend support, game data/firmware rights and usable performance |

For every game, prove an actual scene before expanding scope. Record renderer,
plugins, OS/services, threading, asset/decoded-memory budgets, data rights and
browser evidence. Web export availability is distinct from project availability,
rebuildable dependencies, feasible performance and preserved gameplay.

The machine-readable [catalog](engine-routes.json) supplies identifiers and
prerequisites, not scores or a `supported` boolean. Inspector task hints remain
inferred leads. Unknown engines still enter recon/route selection rather than
being excluded or assigned invented compatibility.

The task-folder/playbook organization is inspired by
[universal-modder](https://github.com/rehan-remade/universal-modder/tree/b8675c10d7091d7e4e00a2e40a15c601040b69a8)
(revision b8675c1). Port2browser's instructions are written for browser porting;
no universal-modder code, tools, hooks, MCP configuration or paid asset service is
bundled. Modding or native hooks do not establish a browser runtime. Optional
[REA](https://github.com/morluto/rea) remains an investigation resource.
