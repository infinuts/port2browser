---
name: port2browser-frameworks
description: Assess and port Rust, Java, .NET/XNA/MonoGame/FNA, Haxe, Lua or Python game frameworks to browsers using matching web backends. Use when a language runtime alone is insufficient.
license: MIT
---

# Port the framework, not just the language

Identify the real graphics/windowing/audio/content framework and its exact
versions. A language's Wasm support does not establish desktop library support.
Read the relevant guide:

- [Rust / Bevy / Macroquad](references/rust.md)
- [Java / libGDX](references/java.md)
- [.NET / XNA / MonoGame / FNA](references/dotnet.md)
- [Haxe / OpenFL / Heaps, Lua / LÖVE, Python](references/scripted.md)

Inspect target-specific features and lockfiles; preserve the native build.
Find a maintained browser backend matching the project's version before choosing
an upgrade or replacement. List native extensions, JIT/reflection assumptions,
threads, filesystem calls, graphics bindings and content-pipeline formats.

First port a single asset-backed scene with input, sound and a gameplay state
change. Keep content tools on the host; rebuild runtime libraries for the web.
Replace missing APIs through a platform boundary with tested semantics. Do not
silently remove combat, physics, codecs or saves to make a runtime boot.

Record the backend's provenance, maintenance/version evidence and license.
If an existing browser runtime cannot execute a required library, prove a bounded
substitution or report that dependency as blocked. A decompiled assembly or JVM
bytecode alone does not establish legal, complete, buildable project source.

Handoff: language/framework/backend revisions, target feature choices, patches,
content conversion rules, reproducible commands, browser tests and remaining
native-only features. Report untested routes as investigated, not supported games.

Additional playbooks: [Go/Ebitengine](references/go.md), [HaxeFlixel](references/haxeflixel.md),
and [Flutter/Flame](references/flutter.md).
