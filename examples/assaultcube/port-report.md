# AssaultCube — browser port report

**Result: playable offline slice**, tested locally on 2026-10-17. This is an
unofficial platform adaptation of upstream AssaultCube 1.3.0.2 at
`1ece5af7533983bb8f827616381d282470793d90`. It is not a full-game compatibility
claim, an agent evaluation, or evidence of a public deployment.

## Tested target and evidence

- Emscripten **4.0.16**, bundled SDL2 **2.32.8**, SDL_image **2.6.0**, ENet
  **1.3.6** from the pinned AssaultCube source, WebGL 1 and Emscripten OpenAL.
- Playwright **1.56.1**, **headed Chromium 141.0.7390.37** and **headed Firefox
  142.0.1**, macOS **15.7.4**. Headed operation is needed for pointer-lock/focus
  checks; an early headless Chromium attempt could not capture the pointer.
- Six checks pass: three per browser. The exact source hashes, browser logs,
  requests and gameplay snapshots are in [browser-evidence.json](browser-evidence.json).
- Reproduce with the [build and gameplay instructions](README.md). CI runs the
  separate suite with Xvfb, Mesa and PulseAudio; each run retains its own evidence.

| Browser | Verified gameplay | Audio | Full page reload |
| --- | --- | --- | --- |
| Chromium | `ac_desert` revision 19, BDM mode 8, three navigating bots; player moved and changed aim; 3 shots, magazine 20 → 17; 4,065 sampled pixel colors | Context running; 18 sound starts at gameplay snapshot | Native nickname `web-tester` restored from IDBFS |
| Firefox | Same map/mode/bot count; player moved and changed aim; 5 shots, magazine 20 → 15; 7,373 sampled pixel colors | Context running; 32 sound starts at gameplay snapshot | Same nickname restored from a new game instance |

Both browsers released held movement on real page focus loss. Both rejected an
incomplete folder and a same-length, hash-modified media file before gameplay.
All observed requests were local-origin GETs; no file upload or external game
service was used. No JavaScript page errors or `WebGL: INVALID_*` messages were
observed in the successful run. SDK emulation notices and GPU performance
warnings remain in the recorded logs rather than being suppressed.

The test uses upstream `botsshoot 0` during repeatable player-input checks;
bots still navigate. The ordinary launcher starts three `good` bots with their
normal shooting enabled. The checks establish controls, state changes, sound
submission and presentation, not combat balance, every damage interaction or
long-session AI stability. Manual listening is **untested**.

## Route and adaptations

Compile the original C++ engine/game and bundled ENet to Wasm. Retain the native
local server, physics, weapons, bot AI, map format and game scripts. The original
checkout remains untouched; [browser.patch](browser.patch) adapts a build copy.
No reconstruction or binary reverse engineering was necessary because source
was available. Remote streaming and an engine/gameplay rewrite were rejected as
unnecessary for this slice.

The browser adaptations cover the frame scheduler, cooperative local handshake,
legacy immediate attributes, interleaved indexed models, display-list removal,
triangle-strip rendering, RGBA shadow readback, geometry-traced crosshair targeting,
pointer lock/audio gestures, focus release and IDBFS settings. A bounded
[texture-JIT workaround](runtime_fixes.py) handles a reproducible regex bug in
this SDK's legacy GL shader generator. It checks the expected code before
changing the generated runtime; it does not modify the SDK installation.

Internet socket creation, DNS and client connection entry points are disabled.
Internet multiplayer, account authentication and a UDP/WebSocket relay are not
part of this static demo. This restriction is explicit in the launcher.

## Media and size accounting

- The selected, hash-verified local media/config/bot inputs contain **1,857 files,
  53,524,892 bytes**. These bytes are read from the player's device, not downloaded
  from this demo's host or uploaded to a server.
- Optimized JS: **407,401 bytes**; Wasm: **1,949,208 bytes** (file sizes before HTTP
  compression/overhead). HTML, launcher and asset-hash JSON are additional files;
  their measured sizes are recorded in the evidence JSON.
- The public packager allowlists code/metadata/notices and rejects media-preloaded
  `.data` builds. It does not ship the upstream checkout, stock media, profile,
  authentication keys or build tools. The smaller runtime is not a full-game
  compression ratio. Throttled transfer/load-time, peak decoded/GPU memory and
  frame-time distributions are **untested**.

Upstream engine/Cube/ENet notices are preserved. Game media have individual
licenses and remain locally supplied. See [NOTICE.md](NOTICE.md), including the
upstream licensing source and linked dependency notices. The port2browser MIT
license does not replace the game engine's license or license its media.

## Limits and next useful checks

Native AssaultCube compilation, Safari/mobile, the editor, mapshot export, all
other maps/modes, multiplayer and long sessions are **untested or outside scope**.
Mapshot export is explicitly unavailable in the adaptation. Settings persistence
is verified; resuming the live match is not implemented or claimed.

The next expansion should exercise an actual combat objective over a longer
session, then sample additional maps and their rendering/audio requirements.
Before broadening public asset distribution, establish separate permission or
an individually licensed media set; do not infer it from the engine license.
