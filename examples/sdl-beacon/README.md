# SDL Beacon

Original MIT-licensed code; all shapes and sound are generated. Walk from x=24
to the beacon at x=120, press Space, then S. One press moves 12 pixels. Holding
a key does not auto-repeat; this deliberately avoids frame-rate-dependent input.

## Tools and build

Use Python 3.10+, Emscripten **4.0.16**, and SDL2 **2.32.10** for the native
reference build. The web build uses the SDL2 port bundled with that SDK.
Record `emcc --version` and `sdl2-config --version` when testing another version.
Install the pinned SDK following [Emscripten's instructions](https://emscripten.org/docs/getting_started/downloads.html).

From the repository root, after activating that SDK:

```sh
python3 examples/sdl-beacon/build.py web
python3 scripts/serve.py examples/sdl-beacon/build/web --port 8000
```

Open `http://127.0.0.1:8000/`, click **Start audio and play**, press Right eight
times, Space, and S. Wait for `Save ready`, then reload: x=120 and the collected
beacon must persist. Browser saves belong to that origin; changing ports changes
storage. No isolation headers or external assets are required.

For native builds, install SDL2 development headers/libraries and put
`sdl2-config` on PATH (Linux/macOS; Windows via WSL). Then:

```sh
python3 examples/sdl-beacon/build.py native
examples/sdl-beacon/build/native/beacon
```

Enter starts audio. Native saves use SDL's per-user preference directory. Set
`P2B_SAVE_PATH` to override it. A disposable smoke check is:

```sh
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy P2B_SAVE_PATH=/tmp/beacon-test-save.txt examples/sdl-beacon/build/native/beacon --smoke
```

The smoke check writes that file; use a fresh path. It checks the native renderer,
movement, PCM queue and filesystem save/load, without claiming audible playback.

## Browser development tests

Node.js 22+, npm, and Playwright are optional development dependencies:

```sh
npm ci
npx playwright install chromium firefox
npm run test:browser -- --grep sdl-beacon
```

Build web first. Tests launch a loopback server on port 8765 and check gameplay,
canvas pixels, actual audio-context state, sound triggers, focus loss and durable
storage. Logs and browser versions are attached to `test-results/results.json`;
failed tests also retain screenshots and traces. Manual listening remains a
separate check. See [the port report](port-report.md) for observed results.

## Platform boundary

`game.c` shares gameplay and drawing. Native uses an SDL loop and file saves;
Emscripten uses animation-frame scheduling and `/saves` on IDBFS. Startup waits
for IDBFS restore, and saving is not complete until its asynchronous flush
finishes. The HTML start gesture activates SDL audio. No game logic is rewritten.
