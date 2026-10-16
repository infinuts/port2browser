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

Static inspection can use file headers, imports, strings, disassemblers and
decompilers. [REA](https://github.com/morluto/rea) is an optional investigation
tool; use it if available and appropriate. It is not required by this skill.
Treat decompiler output as a hypothesis: names, types, ownership and intent may
be missing or wrong. Preserve offsets/symbols and trace observations back to the
original file/version. Compare reconstructed behavior against test cases;
do not claim the pseudocode is the original source.

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
