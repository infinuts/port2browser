# Renderer and middleware gates for native games

Start with the original graphics API/backend and feature use, not the marketing
engine name. Prove one scene including shaders, materials, animation and physics.

| Dependency | Probe before expanding scope |
| --- | --- |
| SDL/windowing + GLES-like renderer | Actual Wasm-built dependency graph, frame/input/audio loop and asset loads |
| Legacy desktop OpenGL | Immediate state, arrays/display lists, texture formats, readback, extensions and function-pointer assumptions |
| Modern DirectX/Vulkan/Metal renderer | Existing web backend or a bounded translation/reimplementation covering the needed rendering/compute features |
| Physics/audio/video middleware | Available source or licensed web binaries, ABI, target features, codecs and preserved behavior |
| Threads/SIMD/shared memory | Version/browser capability detection, synchronization and hosting isolation; target-specific fallbacks |
| Store/auth/anti-cheat/online services | Supported web APIs and protocols, or an explicitly agreed offline slice; missing server behavior remains a blocker |

[Emscripten portability guidance](https://emscripten.org/docs/porting/porting_guidelines.html)
and [WebGPU](https://www.w3.org/TR/webgpu/) are starting points; verify the pinned
runtime/browser capabilities. Neither source availability nor WebGPU guarantees
that a large modern game can be rebuilt or runs within device budgets.

Measure stack, heap/decoded assets and GPU resources separately. Use the actual
crosshair/physics path when desktop depth readback is unavailable. Watch for
renderers that draw the world correctly but corrupt indexed models or silently
ignore unsupported states. Retain representative images and behavioral checks;
never accept gameplay-altering stubs just to finish linking.
