# LÖVE Beacon notices

Original Lua gameplay and browser adapter: MIT, covered by the repository LICENSE.
The example uses generated geometry and a generated tone. The native .love archive
contains original conf.lua/main.lua and their MIT license.

The build script pins the npm tarball of love.js 11.4.1 (LÖVE 11.4) by SHA-512
and the compatibility JS/Wasm by SHA-256. No npm packaging dependencies execute.
Its MIT license is copied to the web output. The WebAssembly runtime includes
LÖVE/Emscripten and upstream dependencies under their respective terms; consult
[the pinned package](https://www.npmjs.com/package/love.js/v/11.4.1) and
[LÖVE source licenses](https://github.com/love2d/love/blob/11.4/license.txt).
The stock template's decorative artwork is not used by this example. The loader
adaptation exports existing filesystem/audio boundaries; runtime-adaptation.json
records original/patched hashes and the changes. No third-party game data is used.
