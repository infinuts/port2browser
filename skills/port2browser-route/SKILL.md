---
name: port2browser-route
description: Choose a falsifiable browser-port route from game inspection evidence. Use to compare native exports, source ports, compatible runtimes, emulation and scoped reconstruction, including modern-game feasibility.
license: MIT
---

# Choose a route

Start with the requested game, supplied material and agreed playable slice.
Reuse an existing maintained web backend when its exact version and data formats
match. Read the relevant engine playbook before committing to a build strategy.

| Evidence | First route to prove |
| --- | --- |
| Complete supported editor project | Matching engine's web exporter |
| C/C++ source and rebuildable dependencies | Wasm plus an actual graphics/platform backend |
| Rust, Java, .NET, Haxe, Lua or Python project | A matching browser-capable framework/runtime and its library subset |
| JavaScript desktop wrapper | Separate browser gameplay from Node/native interfaces |
| Game data plus compatible open engine | Validate data version and one scene, with separate data rights |
| Supported legacy executable/image | Exact emulator/backend compatibility, controls, sound and durable storage |
| Native executable only | Source/runtime discovery, then bounded behavioral investigation |

For a modern game, inventory each dependency as reusable, adaptable, unavailable
or unknown: graphics/shaders, native plugins, physics, audio/codecs, threads,
filesystem, asset pipeline, networking, accounts/store APIs, middleware and source
rights. Choose the dependency most likely to invalidate the route and test it
first. Preserve a representative gameplay objective while proposing any reduced
fidelity, offline mode or smaller scene explicitly; a replacement mini-game does
not satisfy a port of the original without agreement.

Write one pass/fail experiment, expected gameplay state, engine/SDK/browser
versions, evidence to capture, and a stopping condition. Revisit the route after
a failed premise instead of adding stubs that hide missing gameplay.

A mod loader, an emulator boot screen, a decompiled method or a Wasm hello-world
is insufficient. DirectX/Vulkan/Metal need a real backend; WebGPU supplies an API,
not automatic translation. UDP/store services need supported web equivalents.
Online-only dependencies, unavailable middleware or missing source can justify a
specific blocked report. Streaming is a separate deliverable requiring agreement.
