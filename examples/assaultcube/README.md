# AssaultCube browser field test

A real source port of **AssaultCube 1.3.0.2**, not a recreation or remote video
stream. The first slice is `ac_desert`, offline bot deathmatch, keyboard/mouse
controls, WebAudio, and browser-persistent settings. Stock media are selected
from a local folder; they are never uploaded or included in the public output.

AssaultCube is by Rabid Viper Productions and contributors. Engine code and
media have different licenses: read [NOTICE.md](NOTICE.md) before distribution.
This example is development-only and is not copied into the installed skill.

## Build from a clean checkout

Requirements: Python 3.10+, Git, and **Emscripten 4.0.16**. Activate the SDK as in
the SDL example. Node 22 and Playwright 1.56.1 are optional test dependencies.
There are no new Python packages or installed-skill dependencies.

From the port2browser repository root, with the pinned SDK activated:

```sh
python3 examples/assaultcube/build.py
python3 scripts/serve.py examples/assaultcube/build/web --port 8878
```

The build checks out upstream tag `v1.3.0.2` and requires commit
`1ece5af7533983bb8f827616381d282470793d90`. It keeps the original at
`examples/assaultcube/build/upstream` and applies [browser.patch](browser.patch)
to a separate `build/engine` copy. It compiles the pinned client sources and
bundled ENet directly, without running upstream installers or build scripts.
`--source /absolute/path/to/AC` uses an existing clean checkout at that commit;
`--debug` builds a separate `build/debug-web` client with symbols.

Expected build output: `Built browser client: …/build/web`, followed by the
local game-folder path. Open <http://127.0.0.1:8878/>, select that **upstream root
folder**, then click **Load local game**, **Start / restart bot match**, and the
game canvas. The launcher accepts only the exact files and SHA-256 hashes from
the pinned checkout. A release installer or a different revision may not match;
use the checkout the build printed, or extract the GitHub source ZIP for this tag.

Use WASD, mouse look/left click, Space for jump/respawn, and R to reload.
Escape releases the pointer. **Save settings** stores the nickname and native
settings via IDBFS. Reload the page, reselect the folder, and load to restore.
The active match is not a native save feature and is not resumed.

The browser client is intentionally offline. Native Internet multiplayer uses
UDP/ENet, which is not provided by a static browser page; no relay is introduced.
The local server, physics, weapons and bot AI remain the upstream implementations.

## Repeat the browser checks

```sh
npm ci
npx playwright install chromium firefox
npm run test:assaultcube
```

The suite uses **headed browsers** to exercise real pointer lock and focus.
On Linux, install Playwright's system dependencies, Mesa, Xvfb and a PulseAudio
sink, then run `xvfb-run -a npm run test:assaultcube` (see CI). `ASSAULTCUBE_DATA`
can point to the pinned upstream folder when built using `--source`.

Checks load the actual local media, reject invalid folders, verify map/mode and
three moving bots, move/aim/fire through browser input, check ammunition and
sound-trigger counters plus a running audio context, inspect rendered pixels,
release input on focus loss, and restore settings after a full document reload.
For repeatable player-input checks the test uses upstream `botsshoot 0`; bots
still navigate. This does not establish combat balance or long-session stability.
Logs, request records, snapshots, screenshots and traces are attached under
`test-results/`. Manual listening remains a separate, untested check.

## Static hosting and size

The Pages workflow builds this client and packages it under `/assaultcube/`,
linked from Mosslight. [tools/package_assaultcube.py](../../tools/package_assaultcube.py)
allows only the runtime, launcher, notices, version and asset hash manifest.
It rejects media-preloaded `.data` builds. Upstream media and private profiles
never enter the publication directory. No isolation headers or threads are needed.
Serve JS as JavaScript and Wasm as `application/wasm`; HTTPS or loopback is
required for file hashing and normal browser storage/audio/pointer APIs.

The optimized JS/Wasm size and separately selected local media size are reported
in the [port report](port-report.md). A smaller runtime is not a compressed full
game. This example does not claim an arbitrary asset-compression ratio.

## Adaptation notes

- Use `requestAnimationFrame` through `emscripten_set_main_loop`; do not block
  the browser in the native loop or FPS limiter.
- Service the existing local authentication queue cooperatively. Internet
  connection entry points, socket creation and DNS resolution are disabled.
- Replace display-list caching with direct draws and interleave indexed model
  attributes. Disable the quad-merging optimization; retain triangle strips.
- Emit a complete current color/UV for each immediate-mode vertex. Work around
  the pinned SDK's texture-JIT regex bug without changing the global SDK.
- Read shadow pixels as RGBA. Use the existing geometry intersection with the
  far-plane crosshair ray instead of unsupported desktop depth readback.
- Use gesture-bound pointer lock/audio activation, release held input on blur,
  and restore/flush the native settings directory with IDBFS.

See the [port report](port-report.md) for tested scope and known limits.
The original, unpatched checkout remains suitable for the upstream native
build (`make -C source/src client` with its documented system dependencies).
Native compilation of AssaultCube is not claimed by this browser example.
