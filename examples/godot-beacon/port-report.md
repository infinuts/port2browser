# Browser port: Godot Beacon

Status: **playable slice** (one original scene).
Target: desktop Chromium/Firefox, keyboard, WebGL rendering, audio activation and
save/reload. Inputs: original MIT GDScript and generated geometry/PCM sample.

## Findings and route

Editable Godot 4.5.1 standard project, no native extensions or C#. Use the matching
single-thread web exporter with Compatibility rendering. The original scene and
gameplay run unchanged in native and browser; an HTML shell handles the start
gesture and exposes actual engine state for checks. An emulator/reconstruction
is unnecessary for these editable inputs. See [build/run instructions](README.md).

## Verification — 2026-10-16

Environment: macOS 15.7.4 arm64; Godot 4.5.1.stable.official.f62fdbde1;
Playwright 1.56.1. Fresh browser contexts, loopback HTTP, no isolation headers.

| Test | Chromium 141.0.7390.37 | Firefox 142.0.1 |
| --- | --- | --- |
| Engine boot and start gesture | Pass | Pass |
| Eight right presses move x=24 → 120 | Pass | Pass |
| Player screenshot pixel matches position | Pass | Pass |
| Space collects, engine tone triggers, audio context runs | Pass | Pass |
| Focus loss does not leave extra movement | Pass | Pass |
| FileAccess save, full engine reload restores x=132/collected | Pass | Pass |
| JS errors / failed requests | None observed | None observed |

Native headless smoke: movement, collection, sound submission and filesystem
save/load passed using a disposable save. Manual listening and interactive native
comparison: **untested**. See [state/log evidence and source hashes](browser-evidence.json).
A native headless exit can print an ObjectDB cleanup warning; no save/load failure
or browser error was observed. Long sessions need separate profiling.

## Persistence and hosting

The engine restores `user://` before the scene starts and automatically schedules
filesystem synchronization after FileAccess writes. The UI reports a write, not
a durable flush acknowledgment. Tests wait for the normal sync interval and prove
restoration through full reload. Saves require same-origin IndexedDB access and
can be evicted; storage-denied behavior is not established by this positive test.
The single-thread preset needs WebGL 2 and no SharedArrayBuffer isolation headers.
Production hosting, Safari/mobile and offline/PWA support: **untested**.

## Measurements and distribution

Download size: recorded by inspecting exported files; this stock engine template
is much larger than the SDL example. Frame time, peak memory and long-session
budgets: **untested**. Own source and generated shapes/tone use the repository MIT
license. Godot and its third-party engine libraries retain their upstream notices
in the standard runtime; no commercial game assets or extension binaries bundled.

## Next step

Run on the intended hardware, listen to the tone and profile a longer session
before expanding the supported-device or performance claims.
