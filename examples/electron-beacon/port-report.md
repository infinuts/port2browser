# Browser port: electron-beacon

Status: **playable slice** (one original scene; tested scope below).
Target: desktop Chromium/Firefox, keyboard, audio activation and durable saves.
Inputs: original MIT code and generated shapes/tone. No external game assets.

## Findings and route

Electron 44.8.0 wrapper → shared JavaScript gameplay with a browser platform adapter. Filesystem/IPC replaced by IndexedDB/menu promises.
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

Menu interaction also passed in both browsers.
Manual listening: **untested**. Safari/mobile/offline installation: **untested**.
Electron 44.8.0 hidden-window filesystem/IPC smoke passed. Full desktop gameplay/listening remain untested.

Evidence: [browser versions, state, startup observations and logs](browser-evidence.json).
Hashes identify the tested source content. Reproduce with the commands in the
README; CI uploads logs, screenshots and failure traces under `browser-evidence`.

## Measurements and limits

Uncompressed served example files: 4889 bytes, measured by summing file sizes.
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
