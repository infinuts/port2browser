# Pick the cheapest route that can preserve the game

For engine-specific prerequisites and focused task skills, see the
[engine coverage catalog](engine-coverage.md). Its entries are investigation
routes, not compatibility guarantees.

Start with an engine's existing exporter. For a source port, prove the hardest
dependency early. For a binary-only game, establish a compatible runtime before
planning platform changes. Prefer a maintained port over starting another one,
after checking provenance, license, game version, and whether it really runs
locally in the browser.

## Engine clues and their limits

These are inspection leads, not automatic support claims. Export support and
browser requirements vary by engine version; follow the matching manual.

| Clues | What to confirm | Route and common blocker |
| --- | --- | --- |
| Unity `ProjectSettings/ProjectVersion.txt`, `Assets/`, `Packages/manifest.json` | Editor version and full project availability | Use the matching Web build target; audit native plugins, managed threads, and networking. `UnityPlayer.dll` plus a `_Data` folder identifies a shipped build, not an editable project. |
| Godot `project.godot`, `.tscn`, `.pck` | Project vs exported pack, Godot major version, script language, renderer | Use the matching web exporter/templates. Current Godot 4 web export requires Compatibility rendering; C# projects currently cannot export. A `.pck` alone does not establish recoverable source. |
| Unreal `.uproject`, `Source/`, `Content/`, `.pak` | Exact engine fork and plugins | Investigate an existing compatible HTML5 fork and prove a tiny scene. Do not promise an ordinary current Unreal Web export. Packaged `.pak` files are not a project. |
| RPG Maker `www/js/rpg_core.js` or `js/rmmz_core.js` | MV/MZ runtime, wrapper, plugins, asset paths | Separate the web runtime from NW.js/Node integrations; replace desktop-only plugins. Older RPG Maker generations need a different runtime/route. |
| Ren'Py `.rpy`, `.rpyc`, `.rpa` | SDK/runtime version, source availability, Python extensions/codecs | Try the matching SDK's Web build; inspect documented platform limits. Compiled scripts and archives may lack editable project material. |
| LÖVE `main.lua`, `conf.lua`, `.love` | LÖVE version, native modules, filesystem assumptions | Evaluate the community love.js port for that version; LuaJIT FFI/native modules need replacement. A generic Lua file does not establish LÖVE. |
| GameMaker `.yyp`, `.yy`, `data.win` | Project vs runner data and exporter entitlement | Investigate the matching HTML5 export; runner data alone does not supply the original project. |
| `package.json`, HTML/JS, Electron/NW.js | Dependencies and actual Node/native API usage | Retain browser code; replace IPC, filesystem and native addons with browser interfaces. |
| C/C++ with SDL, OpenGL, CMake/Make | Exact library versions, source for all linked dependencies | Use Emscripten; rebuild dependencies for Wasm and adapt the main loop/renderer. |
| DOS executable, console ROM or disk image | CPU, OS/console, graphics mode, firmware requirements | Evaluate an appropriate browser emulator. A Windows PE file is not a DOS game just because it starts with `MZ`. |

Evidence for version detection can include manifests, export logs, headers,
symbols, import tables, and documented file formats. List conflicting evidence
and uncertainty. Archives may need an explicit, separately bounded inspection;
do not assume their extensions reveal their contents.

## Source port decisions

Use Emscripten for compatible C/C++ source, usually with an existing SDL or GLES
backend. Rebuild every target library for Wasm; host `.dll`, `.so`, `.lib`, and
`.a` binaries cannot simply be linked into a browser build. Keep host tools
(asset compilers/code generators) as separate native builds.

Use WebGL for an established GLES-like path. Investigate WebGPU when the renderer
or engine already supports it or required features justify a larger rewrite;
feature-detect and document the browser/device matrix. DirectX, desktop OpenGL,
Vulkan, and Metal calls need an engine backend or deliberate translation.
WebGPU does not translate them automatically.

For Java, .NET, Python, or Lua games, identify a browser-capable runtime and
library coverage first. Runtime startup does not prove support for desktop GUI,
native extension, reflection/AOT, graphics, or audio dependencies. For large
native games, streaming assets, memory, advanced graphics and middleware can
make the project impractical even with source. State the cost of reduced scope.

## Upstream starting points

- [Unity Web limitations](https://docs.unity3d.com/Manual/webgl-technical-overview.html)
- [Godot Web export](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)
- [Community Unreal HTML5 documentation](https://github.com/UnrealEngineHTML5/Documentation)
- [Ren'Py Web builds](https://www.renpy.org/doc/html/web.html)
- [love.js](https://github.com/Davidobot/love.js)
- [js-dos overview](https://js-dos.com/overview.html)
- [Emscripten build systems](https://emscripten.org/docs/compiling/Building-Projects.html)

These links are entry points. Record the exact versions and documentation used
in the port report; a moving `stable` page may describe a newer engine.
