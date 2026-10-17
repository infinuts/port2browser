# Mosslight

An original MIT C++/SDL2 game: explore an island, recover three sunstones, avoid
coral thorns, and restore the northeast lighthouse. Ruins block movement; thorns
cost vitality and return you to camp while preserving collected stones. Artwork
and short tones are generated in code. No commercial game content or remote game
session. Keyboard desktop play; mobile/Safari and manual listening are untested.

## Play

[Play the published demo](https://infinuts.github.io/port2browser/). Click Start
expedition, use arrows (hold to keep moving), Space near a stone/tower, and S to
save. Restoring the lighthouse also saves. Wait for “Progress saved” before a
full reload. The same origin/browser profile restores position, stones, vitality,
trail length and completion. New expedition resets and saves progress.

## Reproduce

Python 3.10+, Emscripten **4.0.16**, native SDL2 **2.32.10**, and a C++17 compiler.
The web build uses that SDK's bundled SDL2 **2.32.8**. Activate the pinned SDK and
record tool versions. Native development headers must expose `sdl2-config`.
From the repository root:

```sh
python3 examples/mosslight/build.py native
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy P2B_SAVE_PATH=/tmp/mosslight-smoke-save.txt examples/mosslight/build/native/mosslight --smoke
python3 examples/mosslight/build.py debug-web
python3 examples/mosslight/build.py web
python3 examples/sdl-beacon/build.py web
python3 tools/build_demo.py --output examples/mosslight/build/demo
python3 scripts/serve.py examples/mosslight/build/demo --port 8000
```

Use a fresh disposable smoke save path. For interactive native play, run
`examples/mosslight/build/native/mosslight` and press Enter. It uses the same
logic/artwork; native saves use SDL's preference directory unless overridden.
The browser restores `/saves` from IDBFS before main and waits for flush completion.

The packager requires a new output directory; remove only your previous generated
output when rebuilding. It publishes allowlisted release files, never debug
symbols, source trees or private saves. `uncompressed/` contains the raw release;
`beacon/` preserves the minimal previous demo. The raw/reference copies are
separate optional downloads, not requested by Mosslight at startup.

## Size reduction

The debug build uses `-O1 -g` and assertions. Release uses `-Oz -flto -g0`, without
assertions. Both include the filesystem and required audio/game behavior.
Packaging compresses JS/Wasm at gzip level 9 with deterministic headers and
verifies decoded bytes/hashes. `size-report.json` records all sizes and scope.

The static-host loader fetches `runtime.bin` and `engine.bin`, decodes gzip with
`DecompressionStream`, then supplies the decoded bytes to Emscripten. Opaque
`.bin` payloads must not have `Content-Encoding: gzip`: that would cause double
decoding. No custom headers, isolation or service worker are required. The loader
buffers code; peak memory is unmeasured. This small procedural game demonstrates
code optimization/transport compression, not extreme shrinkage of large assets.
See [the completed report](port-report.md) for actual results and limitations.

## Automated checks

After the builds/package above, install optional development dependencies:

```sh
npm ci
npx playwright install chromium firefox
npm run test:browser -- mosslight.spec.js
```

Both browsers play the raw and compressed builds, test collisions/hazards,
collect all stones, submit audio, restore the lighthouse, reload saved state,
check rendered pixels, reset, and test focus loss. They verify actual compressed
response sizes and reject corrupted gzip. CI also runs existing examples. Logs,
versions, screenshots and traces are attached to the Playwright JSON report.
