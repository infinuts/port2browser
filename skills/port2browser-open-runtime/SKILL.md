---
name: port2browser-open-runtime
description: Run game data with a compatible open engine or a browser emulator. Use for licensed data-driven source ports, DOS/legacy platforms and console emulation feasibility, not arbitrary modern PC executables.
license: MIT
---

# Match the runtime to the exact game data

Establish platform, CPU, game/data revision, supported formats and required
firmware. Compare an existing maintained browser build or compatible open engine
against these inputs. Verify provenance and browser evidence rather than relying
on a demo title or a filename. A PE executable beginning with MZ is not thereby
a DOS game; Wine/Proton host compatibility does not imply a browser runtime.

For an open engine, distinguish compatible original-game data from an unrelated
remake. Test one real level with its scripts, objects and audio. Keep code licenses,
game media, trademarks and firmware permissions separate. Where appropriate,
accept locally selected files and keep the originals out of the hosted build.

For emulation, pin frontend and backend separately. Inspect CPU/graphics/audio,
filesystem, input mapping and persistence requirements. [js-dos](https://js-dos.com/overview.html)
is one starting point for specific DOS/legacy configurations, not evidence that
modern Windows games work. Record disk images, firmware needs, peripherals and
any remote storage/service; do not label remote streaming local emulation.

Use a redistributable homebrew input or authorized local data for the first
experiment. Verify boot into gameplay, controls, sound, performance and a durable
save after destroying the page instance. Test cold/cache behavior and total
streamed data separately from startup transfer.

If the runtime does not support the required platform or game version, report
the mismatch and next needed resource. Do not download unauthorized BIOS/ROMs,
keys or protected game packages, or bypass activation/anti-cheat as a port step.
Handoff runtime revisions, input hashes, commands, rights boundaries and evidence.
