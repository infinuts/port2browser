---
name: port2browser-native
description: Port rebuildable C or C++ game source to WebAssembly with Emscripten. Use for SDL, OpenGL/GLES, custom native engines, legacy renderers and native middleware dependency audits.
license: MIT
---

# Port native source

Map executable entrypoint, frame loop, renderer, assets, input, audio, saves,
threads and networking. Separate host tools (asset compilers/code generators)
from libraries that must be rebuilt for Wasm. Native DLLs, archives and drivers
cannot be linked into a browser binary. Keep an untouched native checkout.

Prove the renderer and most difficult dependency in one scene. Read
[renderer and middleware decisions](references/renderers.md) before attempting a
large modern engine. An existing GLES/WebGL/WebGPU backend is preferable to a
rewrite when it preserves required features. A proprietary renderer DLL with no
source is a concrete dependency, not a reason to substitute an empty function.

Inspect build hooks and configure probes, pin the toolchain and dependency
revisions, and produce a separate web target. For an established CMake project,
`emcmake cmake` selects a toolchain; the project still needs an actual web target.
Do not import arbitrary flags from an unrelated demo.

Move the native loop to browser frame scheduling. Adopt explicit asynchronous
loading/platform interfaces. Choose Asyncify or JSPI only for an identified call
boundary and matching browser support; neither supplies missing OS services.
Audit stack/heap use, function-pointer casts, alignment, threads and worker data
ownership. Preserve physics timing and input semantics through focus loss.

Build with useful diagnostics first. Compare a repeatable gameplay sequence with
the native version when available. Verify the release build again after LTO,
stripping, asset conversion or compression. Retain patches, exact commands,
source revisions, download/decoded-memory measurements and browser evidence.
