# Browser port: sdl-beacon

Status: **playable slice** (one original scene; tested scope below).
Target: desktop Chromium/Firefox, keyboard, audio activation and durable saves.
Inputs: original MIT code and generated shapes/tone. No external game assets.

## Findings and route

SDL2/C → Emscripten 4.0.16, bundled SDL2 2.32.8 → WebAssembly. Native reference uses SDL2 2.32.10 and Apple clang 17.0.0.
See [source and commands](README.md). Browser adaptation preserves movement,
beacon interaction and save data. A renderer rewrite or emulator is unnecessary
for these available sources. This is a supplied reference port, not evidence
that an agent can automatically port an unrelated game.

## Verification — 2026-10-16

Environment: macOS 15.7.4 arm64, Playwright 1.56.1; fresh browser contexts,
loopback HTTP, no persistent browser cache reused between tests.

| Interaction | Chromium 141.0.7390.37 | Firefox 142.0.1 |
| --- | --- | --- |
| Start, move eight steps, collect | Pass | Pass |
| Canvas player pixel matches gameplay | Pass | Pass |
| Audio context running and sound triggered | Pass | Pass |
| Focus loss/release causes no extra movement | Pass | Pass |
| Save commits, full reload restores x=132 and collected state | Pass | Pass |
| JS/network failures | None observed | None observed |

Audio evidence checks SDL queue submission and the running browser context.
Manual listening: **untested**. Safari/mobile/offline installation: **untested**.
Native SDL dummy video/audio smoke passed: movement, collect, PCM queue, save/load. Real native listening and desktop interaction remain untested.

Evidence: [browser versions, state, startup observations and logs](browser-evidence.json).
Hashes identify the tested source content. Reproduce with the commands in the
README; CI uploads logs, screenshots and failure traces under `browser-evidence`.

## Measurements and limits

Uncompressed served example files: 3570233 bytes, measured by summing file sizes.
Startup observations are `performance.now()` when the Start button becomes usable
in the automated run, recorded per browser in the evidence. They include test
polling overhead and are not a performance benchmark. Frame-time and peak-memory
measurements: **untested**. Test play duration is a short interaction sequence;
long-session reliability and whole-game compatibility are not claimed.

## Hosting and distribution

Serve the dedicated output over HTTP(S). Saves are scoped to the same origin.
No COOP/COEP is required for this single-threaded example. Production HTTPS,
CDN behavior and quotas are untested. Own code/assets use the repository MIT
license; SDL/Emscripten/Electron/Playwright retain their upstream licenses.

## Next step

Listen to the tone on the intended device and measure longer sessions before
expanding the claimed target or scope.
