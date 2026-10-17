# Mosslight port report

Status: **playable slice** — complete original island game, tested scope below.
Target: desktop Chromium and Firefox; native C++ and raw/compressed Wasm.

Recorded 2026-10-17 on macOS 15.7.4 arm64. This is an implementation regression,
not a blind agent benchmark or evidence for porting arbitrary games.
[Machine-readable evidence](browser-evidence.json) records source SHA-256 values,
actual browser versions, network sizes, states, logs and startup observations.

## Route and preserved behavior

Original MIT C++17/SDL2 game, using the same source for native and web. Emscripten
4.0.16; native SDL2 2.32.10; SDK SDL2 2.32.8. All art and short PCM tones are
procedural. Three sunstones, wall collisions, vitality/thorn damage and camp
respawn, northeast lighthouse completion, movement, generated audio and saves
are preserved. No proprietary data, reconstruction, remote video or game server.

Native uses SDL's event loop, software renderer, audio queue and preference-file
save. Wasm uses animation-frame scheduling and IDBFS; startup waits for restore,
and saves finish only after the asynchronous flush callback. A user gesture
activates the real SDL audio context. The native smoke tests collection, hazard,
completion, audio submission and save/load with a disposable save path.

## Measured size reduction

| Local build / package | Bytes | Decimal MB |
| --- | ---: | ---: |
| Debug HTML + JS + Wasm (`-O1 -g`, assertions) | 3,611,695 | 3.612 |
| Optimized HTML + JS + Wasm (`-Oz -flto -g0`) | 855,080 | 0.855 |
| Published startup: HTML + loader + two gzip payloads | 260,288 | 0.260 |

The compressed startup is **92.8% smaller than debug** and
**69.6% smaller than the raw optimized release** in this measurement.
Gzip level 9 uses fixed headers/time. The packager verifies decoded bytes and
retains decoded hashes. HTML and the custom loader are included in the startup
number; `size-report.json`/`version.json` metadata and optional raw/reference
copies are separate. These are file bytes before HTTP headers. Actual per-file
Resource Timing sizes from fresh browser contexts are retained in evidence;
compressed response bytes were asserted against the manifest in both browsers.
Debug sizes may vary with embedded build paths. This tiny procedural game has
no downloaded textures, music, videos or later level packs; its ratio does not
predict compression of asset-heavy commercial games.

The header-free static package uses application gzip: `runtime.bin` and
`engine.bin` are fetched fully, then decoded with `DecompressionStream('gzip')`.
Wasm bytes are supplied to Emscripten; decoded JS runs through a temporary Blob
URL. This avoids depending on custom GitHub Pages Content-Encoding headers.
This path buffers compressed and decoded code at startup; the runtime may retain
decoded bytes. Heap/decoded/GPU peaks are
**untested**, not inferred from the 0.260 MB download. Do not set HTTP gzip headers
on these application-compressed bytes. The uncompressed release remains under
`uncompressed/`; minimal Beacon remains under `beacon/`.

## Browser evidence and reproduction

Chromium **141.0.7390.37** and Firefox **142.0.1**, Playwright **1.56.1**:
raw release and compressed package both pass movement, wall collision, thorn
respawn with retained stone, all three collections, real audio-context running
state plus five sound submissions, tower completion, full reload restoring
position/stones/vitality/completion, rendered player pixels, reset and focus
loss. Requests stay on the test origin. Corrupt gzip is explicitly rejected
with Start disabled. Browser logs and screenshots are retained by the test
report; failed CI runs additionally retain traces. File compression alone is
not treated as successful gameplay.

Follow [build/run instructions](README.md). The tests live in
`tests/browser/mosslight.spec.js`; CI builds native/debug/release/package from a
clean checkout, and runs the same checks in Chromium and Firefox. Linux uses
Xvfb/Mesa and a PulseAudio null sink. CI records its own versions/results; local
results do not stand in for a future CI or public deployment.

Manual listening, mobile/Safari, long-session behavior, throttled-network
benchmarks and peak memory are untested. C++ release optimization and lossy
asset compression have different tradeoffs; this demo does not demonstrate
reducing GTA V or any other commercial game to a particular size.
