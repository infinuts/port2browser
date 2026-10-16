# Electron Beacon 1.0.0 browser port

Status: **build only / untested**. Output: `build-web/index.html` with adjacent `game.js` and `platform.js`. Desktop keyboard/mouse Chromium and Firefox are the targets. All work remained in this disposable workspace; input files were only read. No network, package installation, Electron execution, or other projects were used.

## Observed findings

| Finding | Evidence | Confidence |
| --- | --- | --- |
| Editable JavaScript game inside Electron; manifest declares Electron 44.8.0 | `input/package.json`, `input/main.cjs` | Confirmed declaration; installed runtime/version unknown, upstream documentation not accessed under the no-network constraint |
| Renderer uses canvas, DOM keyboard events and gesture-started Web Audio; no external assets, native addons, threads or network calls in supplied code | `input/game.js`, `input/index.html` | Confirmed by source inspection |
| Electron boundary is asynchronous load/save/Menu IPC, with JSON file persistence and validation | `input/preload.cjs`, `input/main.cjs` | Confirmed |
| Inspection helper completed | `evidence/inspection.json` | Candidate detections only, verified against source above |
| Original gameplay and observability retained verbatim; DOM and CSS unchanged | `evidence/source-check.txt` | Confirmed; only platform script inserted before game script |

## Route and changes

Chosen route: replace only the Electron bridge with browser APIs. No engine export, Wasm, emulation, dependencies, or gameplay reconstruction are needed because all game logic is already browser JavaScript. `build-web/platform.js` exposes the same asynchronous `beaconPlatform.load/save/menu` methods. Menu returns the exact original text. IndexedDB replaces the filesystem; writes use strict durability and resolve only after transaction completion. Saves snapshot invocation data, retain original validation, and reject storage failures so the original game can show failed status. Missing saves return null. Reads and writes share an origin-scoped database and object store. Native input files are untouched.

Movement limits/steps, repeat suppression, Space collection, the 440 Hz 0.25-second tone, Start/Menu buttons, S saving, and `exampleState()` are retained in the byte-identical renderer. Existing Electron filesystem saves cannot be automatically imported by a sandboxed browser; no native save file was supplied.

## Build and verification

This is a static, dependency-free output: no compilation or install is required. Exact tools: `evidence/tool-versions.txt` (Node v24.19.0, Python 3.9.6). Check commands from workspace root:

```sh
node --check build-web/game.js
node --check build-web/platform.js
node checks/platform-contract.cjs
```

The contract test uses a controlled IndexedDB double, not a browser. It checks missing saves, validation, invocation snapshots, waiting for transaction commit, load, rejection on abort, preservation of the prior save on failure, and exact Menu text. Results: `evidence/contract-check.txt`. Source preservation and input SHA-256 inventory: `evidence/source-check.txt`. JavaScript syntax checks exited successfully.

For handoff, serve only the output directory over a stable HTTP(S) origin. Example (not executed in this session):

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory build-web
```

Open `http://127.0.0.1:8000/`. This standard-library command also works with the observed Python 3.9, whereas the skill's optional helper specifies Python 3.10+. No isolation headers, external assets or runtime are required. Keep the same host and port when testing reload persistence. Browser data clearing, private browsing and storage eviction can remove saves; storage denial is reported by the existing game UI.

## Uncertainties and remaining checks

Chromium: **untested**. Firefox: **untested**. No browser sessions were run or browser evidence retained. Browser executables/automation were not found by command lookup; nothing was installed. No Electron runtime is available for native comparison. Actual IndexedDB commit/durability across reload, Web Audio output, rendering, keyboard focus, and browser console/network behavior need independent browser verification. No known gameplay regression was observed through source inspection, which is not a playtest. Startup time, frame time and peak memory are unmeasured. Static payload is 5,909 bytes across three files (`evidence/source-check.txt`).

First real-browser milestone: boot with Start enabled; click Start; press Right eight times from x=24 to x=120; press Space and observe collected=1, sounds=1 and the tone; click Menu and verify its text; focus canvas and press S; wait for saving=0 and saves=1; fully reload on the same origin and verify x=120 and collected=1. Confirm repeat suppression and bounds at 0 and 288. Repeat in Chromium and Firefox, retaining browser versions, console logs and state captures. A successful build/contract test does not establish this milestone.

## Distribution scope

The renderer identifies itself as an original MIT fixture (`input/game.js` comment), but no full game license text was supplied. Package metadata is private. All visuals and sound are generated in code; system fonts are used and no external assets or middleware were added. The skill's MIT license covers the skill only. This local adaptation is authorized by the request; broader redistribution rights remain unverified. No public release or commit was made.
