# Adapt the platform boundary

Start with the engine's supported web backend. Apply only the sections used by
the game; avoid replacing working abstractions without evidence.

## Main loop and lifecycle

Desktop loops often block until the game exits. Browsers must regain control
between frames to process events and paint. Use the engine's web loop,
`emscripten_set_main_loop[_arg]`, or `requestAnimationFrame`. Keep initialization
alive if the callback needs its state; account for APIs that simulate a
non-returning loop. Do not put an infinite loop or synchronous busy wait on the
browser's main thread. See [Emscripten's runtime model](https://emscripten.org/docs/porting/emscripten-runtime-environment.html).

Use elapsed time with bounded catch-up steps; compare physics and game speed at
different refresh rates. Pause or reset timing on blur/visibility changes and
release held inputs. Background tabs may suspend callbacks. Handle resume and
graphics-context loss without restarting a save unexpectedly. See
[requestAnimationFrame](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame).

## Rendering

Audit the actual graphics calls, shader language, texture compression, framebuffer
formats, maximum texture sizes, readbacks and extensions. WebGL is GLES-like;
desktop fixed-function OpenGL and arbitrary extensions need a supported
compatibility path or rewrite. For Emscripten, first try the existing SDL/GLES
backend; choose an explicit WebGL version and test shader compilation. Read
[Emscripten OpenGL support](https://emscripten.org/docs/porting/multimedia_and_graphics/OpenGL-support.html).

Feature-detect WebGPU and request device limits from the target environment.
Choose it when a compatible backend exists or a measured need justifies the
cost. Keep a fallback when the agreed device matrix requires one. A desktop
GPU API cannot be enabled by changing a compiler flag to WebGPU.

Separate canvas CSS size from drawing-buffer size; bound device-pixel-ratio
scaling to the performance budget. Test resizing, fullscreen, UI scale and
pointer coordinates. Keep an accessible way to leave fullscreen/pointer lock.

## Audio and controls

Use a visible Play/Start interaction to create or resume the audio context; do
not assume autoplay. Test format decoding, sample rate, music looping, latency,
mute, suspension and resume. Check the engine's browser codec support before
transcoding assets. See [MDN autoplay guidance](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay).

Map keyboard/mouse through the game canvas and focus it deliberately. Suppress
browser shortcuts only for gameplay events you consume. Distinguish physical
keys from characters, handle key-up on blur, and let users remap controls.
Pointer lock and fullscreen require appropriate user interaction and permission
handling. Test cancellation and lock loss. Add touch/gamepad controls when those
devices are in scope; keyboard emulation alone does not establish mobile play.

## Files, assets, and saves

Replace absolute paths, drive letters, registry/config paths and case-insensitive
lookups. Browsers use URLs, sandboxed storage and user-selected files. Package
small assets or fetch them asynchronously; avoid shipping the entire game up
front if one level can prove the route. Check URL encoding, case, relative base
paths and CORS when assets live on another origin.

Emscripten's in-memory filesystem is temporary. For IDBFS, mount a save directory,
complete `FS.syncfs(true, callback)` before reading saved state, then serialize
and complete `FS.syncfs(false, callback)` after changes. Handle both callbacks'
errors and overlapping saves. Keep the runtime alive through completion; an
unload callback cannot guarantee the final flush. For a JS/engine-native port,
use its supported IndexedDB/OPFS persistence mechanism and await completion.
See [Emscripten filesystem overview](https://emscripten.org/docs/porting/files/file_systems_overview.html).

Test a save across a full reload on the same origin, including port number.
Browser data may be unavailable, quota-limited or evicted; offer save
export/import when appropriate and report failures. Storage persistence is not
a backup. See [storage quotas and eviction](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria).

## Threads, native services, and networking

Start single-threaded if it can meet the target. Emscripten pthread builds need
compatible compile/link settings, worker resources, SharedArrayBuffer and
cross-origin isolation. Check `self.crossOriginIsolated` in the actual page.
Do not synchronously wait for a worker that needs work from the main thread.
Build separate threaded/non-threaded outputs when a fallback is required. See
[Emscripten pthreads](https://emscripten.org/docs/porting/pthreads.html).

Typical isolation headers are `Cross-Origin-Opener-Policy: same-origin` and
`Cross-Origin-Embedder-Policy: require-corp`. These affect cross-origin assets,
embeds and opener relationships; test the whole page and its dependencies.
Isolation is not a blanket need for every Wasm build. See
[COEP requirements](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy).

Replace native dialogs, clipboard, processes, dynamic libraries and platform SDKs
through explicit interfaces. Browsers do not offer arbitrary raw TCP/UDP sockets;
evaluate fetch, WebSockets or WebRTC and any required protocol/server changes.
Never put server secrets in the client. Offline games that require launcher or
online services may need an authorized alternative or reduced scope.

## Hosting and offline use

Serve Wasm as `application/wasm`. Precompressed `.gz`/`.br` responses also need
the correct `Content-Encoding` and underlying MIME type. Validate deployed
headers and worker/asset URLs. Avoid `file://` for testing. Test HTTPS deployment
separately from localhost; remote insecure HTTP may disable required features.

Running an offline game's port in a browser does not imply offline web access.
If requested, add a service worker/cache strategy with versioned resources,
storage limits, update handling, and explicit asset-license checks. Verify a
reload without a network connection after installation. Keep saves outside
disposable asset caches.
