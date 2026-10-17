# .NET / XNA / MonoGame / FNA

Identify source availability, framework/backend version, native libraries,
content pipeline and game assemblies. A .NET browser runtime does not provide
WinForms, desktop graphics, P/Invoke libraries or an XNA-compatible backend by
itself. MonoGame/FNA binary detection is only an inspection lead.

Investigate a compatible maintained browser backend and its exact API/content
coverage. [KNI](https://github.com/kniEngine/kni) is one XNA-derived framework
with a browser/WebGL backend, reviewed on 2026-10-17; it is not a drop-in promise
for every MonoGame or FNA game. Pin its revision and .NET/content tools, and prove
required shaders, texture formats, input and native dependencies before migrating.

Audit reflection/AOT/trimming, serialization, threading, native codecs/physics,
store APIs and save paths. Rebuild required middleware or replace it with preserved
semantics. Retain original content and license notices, and compare numeric/timing
behavior against the native game when available.

Milestone: an asset-backed scene with a gameplay goal, audio activation and a
save restored after full page reload. Keep host content tools separate from the
browser runtime. If only assemblies exist, decompilation is investigation rather
than proof of complete project source or permission to publish recovered code.
Report the first missing backend/library precisely. Guidance only; no new .NET
port/browser result is claimed here.
