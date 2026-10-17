# Macroquad Beacon

Original MIT Rust game: move, collect a beacon, hear a generated tone and restore
saved progress after reload. Rendering/input remain in Macroquad; the browser
adapter supplies Web Audio and awaited IndexedDB commits instead of native sound
and filesystem calls. No third-party game assets are required.

## Pinned inputs and build

Use Rust **1.85.1**, Macroquad **0.4.14**, checked-in Cargo.lock and the matching
JS bundle from upstream revision `2c60f754b0c0e053f4c5b272fee696fb45e5aca8`.
The build script verifies the loader SHA-256. Fontdue is locked to **0.9.3** because
0.9.4 uses integer APIs unavailable in this compiler; upgrading either is a new
build/test decision. Cargo crate checksums remain in the lockfile.

```sh
rustup toolchain install 1.85.1 --profile minimal
rustup target add wasm32-unknown-unknown --toolchain 1.85.1
python3 examples/macroquad-beacon/build.py native
python3 examples/macroquad-beacon/build.py web
python3 scripts/serve.py examples/macroquad-beacon/build/web --port 8000
```

`CARGO` can name an absolute rustup-managed cargo executable. Builds stay under
`build/`. Native compilation may require the platform's audio/build libraries
(e.g. Linux `libasound2-dev`); run `build/native/macroquad-beacon` to play natively.
Native execution was not included in the browser evaluation.

In the browser click Start, press Right eight times, Space, then S. Expect x=120,
collected=1 and an awaited save; a full reload must restore x/collection. Native
controls additionally accept Enter to start; `P2B_SAVE_PATH` changes its save file.
The [verification plan](verification.json) also checks focus at x=132 and saves
that position. It waits for each Rust frame's observed movement before pressing
again, because frame-polled input can coalesce unrealistically rapid automation.

## Reproduce evidence

Install root `npm ci` plus matching Playwright Chromium/Firefox, then:

```sh
python3 tools/test_runtime_examples.py --examples macroquad-beacon --output /path/to/new-evidence
```

Use `--headed` under an actual display (Linux CI uses Xvfb/Mesa/PulseAudio).
See the [completed report](port-report.md), [machine evidence](browser-evidence.json)
and [notices](NOTICE.md). Browser packages contain generated third-party notices
for engine/crate/font dependencies. Manual listening, physical mobile devices,
Safari/WebKit, long sessions and GPU profiling remain untested for this game.
