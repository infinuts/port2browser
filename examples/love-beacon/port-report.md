# LÖVE Beacon port report

Status: **playable slice** — original one-scene regression game, scoped below.
Recorded: 2026-10-17. Source base `8c8ccc86e3f5c08f494a2cd9bb066226ba2674c4` plus the
worktree files identified by SHA-256 in [machine evidence](browser-evidence.json).
These results do not describe an already merged revision or other games.

## Input and route

LÖVE 11.4 via love.js 11.4.1 compatibility runtime; npm tarball/JS/Wasm checksums verified.

Package original Lua with the pinned single-thread prebuilt LÖVE runtime. Export read-only journal access, explicit IDBFS commit and gesture-bound OpenAL resume. Remove automatic unload sync; the save result waits for the commit. No npm packaging dependencies execute.

Original game logic, generated geometry and generated tone are MIT. Engine,
loader, built-in font and other runtime dependencies retain their own licenses;
see [notices](NOTICE.md). No third-party game media or proprietary code is used.

## Reproduce

Follow [build/run instructions](README.md) and the [JSON plan](verification.json).
The common runner copies dedicated web outputs to a temporary serving root and
uses fresh browser contexts. Native/browser builds were repeated from a staged-tree export with no example
build outputs, then both browsers passed against those fresh outputs. Browser
artifact hashes and exact source inputs are recorded separately. The browser tests use the public game code, with no seed,
practice mode, assigned winning state or hidden easier gameplay.

## Observed browser results

- Headed Chromium 141.0.7390.37 and Firefox 142.0.1 on macOS 15.7.4 arm64 passed.
- Actual controls start the game, move x=24→120, collect a beacon and submit a
  generated tone. Screenshot pixel and nonuniform-render checks accompany state.
- Element focus loss is checked during a held action, then movement stays at x=132.
  This is not a window-visibility or physical-device test.
- Save completion is awaited. A full document reload restores x=132/collected=1.
- Web Audio context/start evidence is retained; manual listening is **untested**.
- Console/network failures: none in the passing runs. Per-step state, audio and
  screenshots: [Chromium](evidence/chromium/evidence.json),
  [Firefox](evidence/firefox/evidence.json).

## Build and measurement limits

A deterministic native .love archive was packaged; the native runtime was not
rebuilt or executed.
RequestAnimationFrame callback intervals and navigation timing are observations
in the machine report, not GPU frame-time or device performance benchmarks.
The source of a compatibility/prebuilt runtime was not rebuilt as part of the
LÖVE packaging path. Shipping Safari, WebKit, mobile hardware/touch, long sessions,
manual listening, production hosting and detailed profiling are **untested**.
A scene working in these versions does not establish broad engine compatibility.
