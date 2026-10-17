# raylib source → web

Start with rebuildable game code, exact raylib revision, resources and native
extensions. A `raylib.h` copy can belong to tools rather than the game.

Use the matching [upstream web build guide](https://github.com/raysan5/raylib/wiki/Working-for-Web-%28HTML5%29),
reviewed 2026-10-17. Rebuild raylib itself for its web platform with the selected
Emscripten release; a desktop `libraylib.a` is not a Wasm library. Prefer the
project's existing web example/build system and pin compiler, library and flags.
Inspect the version's platform define and graphics API instead of assuming every
raylib release uses identical options.

Give the frame update/draw function to the browser scheduler, retain simulation
timing, and replace blocking file/network operations. Audit custom GLSL, texture
formats, audio loading, native plugins, callbacks and storage. Gesture-bound audio
and asynchronous durable saves need actual target-browser checks.

First probe: a resource-backed room with movement, a collision/interaction, a
sound and a save restored after a new document loads. Check focus and the deployed
base URL. Record missing native dependencies or unsupported shaders precisely;
a window opening or a successful link is build evidence only. This route is
documented guidance, not a newly evaluated raylib game.
