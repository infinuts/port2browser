# Unity project → Web

Confirm `ProjectSettings/ProjectVersion.txt`, scenes/assets, package lock and
native plugin source. `UnityPlayer.dll`, `_Data`, `GameAssembly.dll` and IL2CPP
metadata describe a shipped build; they do not supply an editor project.

Install/use the matching editor and its Web build module. Inspect the project's
actual build method before invoking batch mode; do not invent a method name.
Test one asset-backed scene before migrating render pipelines or upgrading packages.
Audit managed code stripping/AOT/reflection, native `.jslib`/Wasm replacements,
shaders, middleware, store APIs, sockets and memory. A native desktop plugin needs
a web implementation; renaming its DLL cannot provide one.

The [Unity Web limitations manual](https://docs.unity3d.com/Manual/webgl-technical-overview.html)
reviewed on 2026-10-17 distinguishes managed threading restrictions from native
engine/Burst jobs and documents browser networking constraints. Follow the manual
for the project's exact release rather than treating all Unity versions alike.

Milestone: load the scene, complete its interaction, activate audio and restore
a save in each target browser. Record build/export options and actual host headers.
If only shipped files exist, report the missing project or investigate an
independently proven compatible runtime; asset extraction is not an export route.
Guidance only; no Unity game/browser result is added by this playbook.
