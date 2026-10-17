# Build, test, and diagnose

## Reproducible builds

Record engine/editor, export templates, SDK/toolchain and dependency versions.
Use a separate web output directory and preserve native build instructions.
Check that a clean checkout can follow the commands without private absolute
paths. Do not hide missing dependencies with dummy functions that change game
behavior. Debug with assertions and symbols first; optimize after the slice works.

For an existing CMake C/C++ project after reviewing its build scripts:

```sh
# Activate the chosen emsdk environment first; verify emcc --version.
emcmake cmake -S . -B build-web -DCMAKE_BUILD_TYPE=Debug
cmake --build build-web
```

This selects the Emscripten toolchain; the project must still define a web target,
output format, appropriate libraries and assets. It does not translate native
libraries or platform code. For configure/Make projects, investigate `emconfigure`
and `emmake`; inspect configure-time probes and native code generators. See
[Emscripten build systems](https://emscripten.org/docs/compiling/Building-Projects.html).

For a small SDL2 source file that already uses an Emscripten-compatible loop:

```sh
# Illustrative only: main.c and assets/ belong to the game being ported.
emcc main.c -O0 -g -sASSERTIONS=1 -sUSE_SDL=2 -sMAX_WEBGL_VERSION=2 \
  --preload-file assets@/assets -o build-web/index.html
```

Create `build-web` first and adapt flags to the pinned SDK and actual libraries.
Mounting assets at `/assets` must agree with the game's file paths. Add Asyncify
only for a demonstrated synchronous-call migration need; measure its cost.
Choose memory limits/growth from observed requirements and the target devices.
Never treat raising the heap limit as proof of acceptable peak memory.

For measured release-size reduction, asset optimization and compressed hosting,
read [Size and compression](size-and-compression.md).

## Serve the output

The optional helper uses Python 3.10+ and the standard library:

```sh
python /path/to/port2browser/scripts/serve.py ./build-web --port 8000
# For runtimes requiring SharedArrayBuffer:
python /path/to/port2browser/scripts/serve.py ./build-web --port 8000 --isolate
```

Open `http://127.0.0.1:8000/` and stop with Ctrl+C. Serve only a dedicated build
directory. The helper binds loopback, refuses symlinks/junction paths and hidden
files, disables caching, sets Wasm MIME and gzip/Brotli headers, and optionally
adds COOP/COEP. It does not provide TLS, CORS configuration, byte ranges, content
compression, a service worker, or production hosting. It serves already compressed
files when explicitly requested by URL. Use the engine's own server when it
requires additional behavior. Isolation does not fix incompatible remote assets.

## Playtest the agreed slice

Record a short repeatable sequence and expected outcomes, such as boot, start,
move, interact, pause, save, reload, and continue. Run it with actual browser
automation or manual interaction; record which. Capture console/network output
and gameplay evidence. Keep any proprietary screenshots/logs private as needed.

| Check | Evidence to retain |
| --- | --- |
| Cold start and asset loading | Browser/OS/device, URL, cache state, request failures, time to first interaction |
| Graphics and timing | Scene comparison, shader errors, resize/fullscreen, measured frame times at stated resolution |
| Controls | Inputs used, canvas focus, pointer-lock escape, blur/resume, touch/gamepad if in scope |
| Audio | User gesture to activate, music/effects, pause/resume and mute |
| Save durability | Save action, completed flush, full reload, restored state on the same origin |
| Resources | Download bytes, peak memory measurement/tool, slow scene and representative play duration |
| Compatibility | Browser names and exact tested versions, threaded fallback if promised |
| Offline mode, if requested | Installed cache version, network disabled, reload and save behavior |
| Native regression, if relevant | Original build/test command and repeatable gameplay comparison |

Use one Chromium browser and Firefox for the default desktop slice; test Safari
and mobile on real relevant devices when claimed as supported. Emulation of a
mobile viewport alone cannot establish Safari/iOS compatibility. If a browser or
measurement tool is unavailable, report it as untested; do not silently substitute
a different target. An automated boot check does not prove gameplay.

## Troubleshoot from the first observable failure

| Symptom | First checks |
| --- | --- |
| Wasm decode/streaming error | Wasm URL returns binary rather than an HTML error page; MIME, Content-Encoding, response body |
| Black canvas | First JS/Wasm error, context creation, shader logs, unsupported extensions, asset failures |
| Frozen page before frame one | Blocking main loop, synchronous IO, main-thread waits, initialization deadlock |
| Silent audio | Play gesture, AudioContext state, codec/network errors, engine mixer initialization |
| Missing assets on hosting | Case/URL/base-path mismatch, preload mount, HTTP status, CORS/COEP and compression headers |
| Save lost after reload | Memory-only filesystem, mount path, completed restore/flush callbacks, origin change or quota errors |
| SharedArrayBuffer unavailable | Secure context, crossOriginIsolated, COOP/COEP on the final response, embeds and worker URLs |
| Undefined symbols/link failure | Missing Wasm rebuild of a dependency, target flags, link order, native-only API |
| Out of memory/tab killed | Peak heap plus GPU/decoded asset copies, preload size, target-device limits, repeated allocations |
| Works locally, fails remotely | HTTPS, asset URL base, isolation, MIME/encoding, CDN cache and stale service worker |
| Wrong speed or stuck keys | Delta/fixed-step handling, refresh-rate assumptions, focus and key-release handling |

Save the failing command or interaction and its exact output, isolate a small
reproducer, then rerun that check after the fix. Once the route is disproved,
return to the feasibility decision instead of stacking speculative flags.
