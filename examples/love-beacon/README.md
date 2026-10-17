# LÖVE Beacon

Original MIT Lua game with movement, a collectible, generated sound and native
filesystem saves. The browser port uses the pinned LÖVE 11.4 compatibility runtime,
an explicit OpenAL context resume and awaited IDBFS saves. Lua still owns gameplay,
rendering and its observation journal; JavaScript reads that journal rather than
assigning game state.

## Build and run

```sh
python3 examples/love-beacon/build.py native
# With matching LÖVE 11.4 installed:
love examples/love-beacon/build/native/beacon.love
python3 examples/love-beacon/build.py web
python3 scripts/serve.py examples/love-beacon/build/web --port 8000
```

The native `.love` archive is deterministic and contains original Lua plus its
MIT license. Its native runtime execution is untested in the browser report.
The web builder needs only Python and network access on first use. It downloads
love.js **11.4.1** from the immutable npm tarball, verifies SHA-512 package integrity
and SHA-256 JS/Wasm hashes, and copies only allowlisted files. No old npm packaging
tools or their dependencies are installed/executed. The current upstream README
may describe 11.5; that is not the version evaluated by this example.

The compatibility runtime is single-threaded and needs no isolation headers.
The guarded loader patch exports read-only observation access, explicit `syncfs`
and gesture-bound audio resume. It removes unreliable automatic unload syncing;
the adapter waits for the save commit before reporting success. The original and
patched loader hashes are recorded in `build/web/runtime-adaptation.json`.

Open the page, activate audio, press Enter, press Right eight times, Space, then
S. Expect x=120, collected=1 and a committed save. Reload restores that progress.
The [verification sequence](verification.json) additionally checks focus and saves
x=132; a plain refresh must restore that state. It records real buffer submissions,
not a claim that somebody listened.

## Reproduce evidence

With root `npm ci` and matching Playwright browsers installed:

```sh
python3 tools/test_runtime_examples.py --examples love-beacon --output /path/to/new-evidence
```

Use `--headed` under a display; Linux CI supplies Xvfb/Mesa/PulseAudio. The
[port report](port-report.md), [browser evidence](browser-evidence.json) and
[notices](NOTICE.md) scope the result. Manual listening, shipping Safari/WebKit,
physical mobile devices, long sessions and performance profiling are untested.
The browser engine's upstream default font and libraries retain their own terms.
