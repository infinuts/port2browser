# Unreal → investigate a matching HTML5 fork

Determine exact UE version/fork, source availability, `.uproject`, game modules,
plugins, content cooking and middleware. PAK/IoStore data and reflection dumps
are shipped material, not a complete editor project.

Do not assume a normal UE5 editor provides a Web export. The
[community HTML5 documentation](https://github.com/UnrealEngineHTML5/Documentation)
and [4.27 HTML5 ES3 fork](https://github.com/SpeculativeCoder/UnrealEngine-HTML5-ES3)
are version-specific investigation starting points, reviewed on 2026-10-17.
They do not establish compatibility with UE5 projects or arbitrary plugins.
Check source access/engine terms and exact fork/toolchain revisions first.

Prove a minimal cooked scene with a real material, input and physics using the
matching fork. Audit render features, shader cooking, native plugins, audio,
network protocol, asset streaming and memory. Nanite/Lumen or other desktop
features require a demonstrated supported backend or an agreed scope reduction;
a WebGPU API alone does not supply the engine integration.

Keep the original project intact. A downgrade can change assets, Blueprints and
serialization and must not be treated as a build flag. If the required engine,
plugin source or practical rendering path is unavailable, deliver a specific
blocked report. Guidance only; no Unreal browser port is evaluated here.
