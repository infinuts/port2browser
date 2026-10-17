# Data-driven and legacy runtime routes

Filename/header clues stay inferred. Identify the exact platform, game/data
revision, runtime/backend and dependencies before executing anything. A WAD/PK3
may be a mod, texture archive or unrelated format; an ISO/DSK does not identify a
platform. Do not extract untrusted archives just to invent a compatibility answer.

## Flash / Ruffle

For SWF, inspect the bounded FWS/CWS/ZWS header/version without decompressing it.
Match the actual ActionScript APIs and external resources to a pinned
[Ruffle](https://github.com/ruffle-rs/ruffle) build (primary project reviewed
2026-10-17). Ruffle targets the web but remains incomplete: assess the particular
movie/game rather than treating all AS3 inputs as supported. Test real input,
rendering, sound, network/resource loading and durable SharedObject behavior.
Keep media rights separate and report unsupported APIs or missing server data.
A video or animation playing is not a completed game objective.

## Java applets / CheerpJ

Preserve the applet/JAR version, HTML parameters, dependencies and resource paths.
[CheerpJ's applet guide](https://cheerpj.com/docs/getting-started/Java-applet.html)
is a version-specific investigation path, reviewed 2026-10-17. Check its current
license/deployment terms and loader requirements; it is optional and not bundled.
A JNI library, native graphics backend or obsolete external service remains a
separate blocker. Prove the actual game's renderer/input, audio and save behavior.
Do not infer applet compatibility from libGDX/GWT source support or a JVM starting.

## ScummVM

Match the exact game edition and required data files to the selected runtime's
[compatibility list](https://www.scummvm.org/compatibility/) and
[platform documentation](https://docs.scummvm.org/), reviewed 2026-10-17.
ScummVM reimplements supported game engines; it is not a general executable
emulator. Confirm the chosen browser build includes that engine and codecs, with
separate code/media permissions. First probe a room interaction, dialogue,
scene change, audio and save restored by a new page instance. Unsupported game
variants, plugins or missing data need a specific blocked report.

## Adventure Game Studio

Distinguish an editable AGS project from compiled game data. Investigate the
matching [AGS engine/editor release](https://github.com/adventuregamestudio/ags)
and its Emscripten/Web output; review release notes for version-specific fixes
(primary repository reviewed 2026-10-17). Check game-data compatibility, native
plugins, codecs and runtime packaging instead of assuming any `.ags` input works.
Prefer a matching editor export when source exists. Prove an interactive room,
script/inventory transition, sound and durable reload save with real data. Use
compatible local data when redistribution is unresolved. No AGS port is newly
evaluated here.

## DOS, ROMs and disks

Use a compatible maintained backend for the exact CPU/system and game version.
A raw `.com` has no identifying magic. MZ may wrap DOS, NE or PE code; a modern
PE signature is not a DOS route. Disk/ROM extensions are triage clues, not proof
of bootability, BIOS availability, permissions or performance. Pin frontend and
backend separately. Verify gameplay, controls, sound, disk/file writes and a
full-document reload, rather than only observing an emulator boot screen.
