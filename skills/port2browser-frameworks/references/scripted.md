# Haxe, Lua and Python families

Match the actual framework/runtime and target, not the language alone.

| Project family | Starting route | First boundary to prove |
| --- | --- | --- |
| OpenFL / Heaps | Version-matched HTML5/JavaScript target | Native extensions, shaders, asset pipeline and browser libraries |
| LÖVE | A compatible community love.js build | LÖVE API version, LuaJIT FFI/native Lua modules, filesystem and threads |
| Pygame / Python | A compatible pygame-web/pygbag runtime | Async main loop, available Wasm wheels and actual SDL/audio bindings |
| Other Lua/Python/Haxe game | Maintained framework backend or bounded source adaptation | Graphics, native modules and OS APIs; interpreter boot is insufficient |

Primary entry points reviewed on 2026-10-17:
[OpenFL](https://www.openfl.org/learn/), [Heaps](https://github.com/HeapsIO/heaps),
[love.js](https://github.com/Davidobot/love.js),
[pygame-web](https://pygame-web.github.io/).
These projects are optional references, not bundled dependencies. Recheck exact
runtime versions and maintenance before selecting a command or package.

Preserve the native project and dependency locks. Build one asset-backed scene,
exercise the actual event loop/input, activate sound and restore a save in a new
page instance. Inspect late resource loads and native module failures. Report
needed code changes, loader/version coupling, missing dependencies and browser
results. A generic Lua file, Python interpreter or Haxe executable does not
identify a complete export route. These are documented routes, not new game tests.
