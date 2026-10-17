# Macroquad Beacon port report

Status: **playable slice** — original one-scene regression game, scoped below.
Recorded: 2026-10-17. Source base `8c8ccc86e3f5c08f494a2cd9bb066226ba2674c4` plus the
worktree files identified by SHA-256 in [machine evidence](browser-evidence.json).
These results do not describe an already merged revision or other games.

## Input and route

Rust 1.85.1, Macroquad 0.4.14/miniquad 0.4.8, fontdue 0.9.3; matching checksummed JS bundle.

Recompile original Rust gameplay/input/rendering to wasm32-unknown-unknown. Native filesystem/audio become an explicit IndexedDB/Web Audio adapter; the native target retains native sound and file saves.

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

Native Rust compilation passed; running the native game is **untested**.
RequestAnimationFrame callback intervals and navigation timing are observations
in the machine report, not GPU frame-time or device performance benchmarks.
The Rust game and engine crates were compiled; the matching upstream JS loader
is a pinned build input. Shipping Safari, WebKit, mobile hardware/touch, long sessions,
manual listening, production hosting and detailed profiling are **untested**.
A scene working in these versions does not establish broad engine compatibility.
