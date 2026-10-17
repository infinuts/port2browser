# Defold → HTML5

Inspect `game.project`, bootstrap collection, scripts, resources, dependencies
and native extensions. Record editor/engine revision and extension revisions.
Use its matching HTML5 bundle workflow, preserving the original native target.

The [Defold HTML5 manual](https://defold.com/manuals/html5/), reviewed on
2026-10-17, is the starting point for bundle output, WebGL configuration and web
filesystem behavior. Check each native extension's HTML5 implementation and
build requirements rather than assuming native code is portable. Audit blocking
Lua/C APIs, socket use, codecs and platform service integrations.

First build a collection with input, a collision/interaction, and sound. Test
asset URLs and case sensitivity over HTTP(S). Verify saved state after a full
reload, focus behavior and denied storage/audio capabilities when relevant.
Use the editor's preview server for development, then replay the packaged bundle
on its intended host. Keep all generated bundle files byte-preserved; text-mode
copying or newline conversion can invalidate binary data sizes.

Handoff project/exporter/extension versions, bundle commands or UI procedure,
output manifest and browser evidence. An extension with no viable HTML5 backend
is a named blocker until a tested replacement exists. This is documented routing
coverage, not a recorded Defold port result.
