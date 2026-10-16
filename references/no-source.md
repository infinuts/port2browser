# Working without source

First distinguish a missing repository from a game that never shipped source.
Look for an official source release, maintained engine reimplementation, existing
browser port, or a documented data-compatible runtime. Verify provenance and
game/version compatibility before adopting it.

## Routes worth testing

| Input | Bounded first experiment | What it cannot establish |
| --- | --- | --- |
| DOS/console game and compatible browser emulator | Boot a legally supplied test image, reach gameplay, test input/audio and a persistent save | Compatibility with other games, versions, or firmware |
| Original data and an open engine | Validate one data file and load one scene with that engine | Permission to redistribute the game data |
| Scripted engine package | Identify the runtime/version and inspect documented data formats | Recovery of the complete original editor project |
| Native binary with symbols or observable behavior | Trace one subsystem and compare a small reconstructed function against recorded cases | Automatic recovery of buildable source or a complete game |
| Large proprietary desktop game | Inventory dependencies and produce a feasibility report | A practical browser port merely because a demo/video exists |

## Investigate before reconstructing

Use this route when source/runtime discovery cannot explain a required subsystem,
not as a prerequisite for ordinary engine exports or source ports. Bound the
question first: for example, how a save is encoded, how an Electron menu reaches
IPC, or how a native function computes movement. Record the exact game version,
artifact hashes, tool/provider versions, offsets or symbols, inputs and outputs.
Keep observed facts, inferred behavior and unresolved dependencies distinct.

[REA (Reverse Engineer Anything)](https://github.com/morluto/rea) is an optional
source of tools and investigation patterns. Its [CLI and Evidence guide](https://github.com/morluto/rea/blob/main/docs/cli.md)
describes static JavaScript/Electron inspection, native analysis through providers,
and saved evidence. Check the installed version's capabilities and provider
requirements before choosing commands. REA and its providers are not bundled or
required; use equivalent tools already available when appropriate. Installing
REA or registering its MCP server is a separate environment change, not an
automatic step when this skill loads.

Follow the smallest relevant calls or data flow. Static inspection can use
headers, imports, strings, disassembly and decompilation; wrapper inspection can
trace renderer → preload → IPC → filesystem. Treat decompiler output as a
hypothesis: names, types and control flow can be wrong. Preserve evidence tied
to the original bytes rather than claiming recovered pseudocode is source.

Implement the isolated behavior in a separate workspace and compare repeatable
cases against the original observations, including boundaries and invalid input.
A matching function is evidence for that function, not for the whole game.
Record mismatches and missing services before expanding the reconstruction.

Only then choose a browser route. Reconstructed C/C++ or a compatible open engine
can be compiled with Emscripten when its dependencies support Wasm; adapt its
main loop, rendering, input, audio and storage as described in
[Source port decisions](approaches.md#source-port-decisions) and
[Browser platform adaptation](browser-platform.md). A browser-capable C++ engine
provides runtime services; it cannot recover missing game logic or data formats.
Verify the reconstructed slice in the target browsers, including full-reload
saves, and label it a reconstruction with its tested scope. Unavailable analysis
tools or insufficient evidence can justify a specific blocked outcome. This route
remains investigation-only in this repository's evidence table until evaluated.

If authorized runtime observation is useful, isolate the target, constrain its
filesystem/network access, and record inputs and observable outputs. Avoid
running unknown installers or modifying the only copy. Unpack archives into a
separate location with traversal, link, file-count and size limits.

## Rights and release boundaries

Inventory code, artwork, music, fonts, trademarks, firmware and third-party
libraries separately. Record each license or permission and whether it covers
modification and distribution for the proposed release. Treat unknown rights
as unresolved. [WIPO's overview](https://www.wipo.int/en/web/copyright/activities/video_games)
describes the multiple kinds of protected material in games; applicable terms
and law depend on the material and jurisdiction. Seek qualified advice when a
release depends on an uncertain legal interpretation.

For proprietary assets, consider a user-supplied local file workflow where
appropriate. It can keep assets out of your repository and hosting, but does
not itself resolve all rights questions. Do not bundle unauthorized ROMs, BIOS
images, keys, cracks, decrypted commercial archives or leaked source. Do not
bypass DRM, activation, anti-cheat or access controls as a porting step. Report
the restriction and investigate an authorized build or a different route.

Stop the dependent experiment when essential source, a usable emulator, required
services, permission, or acceptable performance is unavailable. Deliver the
evidence and the smallest next requirement. A small independently implemented
gameplay study may be a separate agreed project; label it as a reconstruction
and state what it does not reproduce. Remote streaming also needs explicit
scope agreement and must be described as streaming.
