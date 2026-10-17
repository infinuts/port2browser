# Reduce download size without losing the game

Use this after a working slice exists, or when a measured size/memory budget
blocks it. Preserve an untouched input and debug build. Optimize a separate
release output and rerun the same gameplay sequence after each material change.
Choose the smallest build that meets the agreed quality and performance budget;
do not promise an extreme compression ratio for arbitrary games.

## Measure the right quantities

Record bytes for the original distribution, selected content, uncompressed web
release, compressed payload, cold-start transfer, later level downloads, and
persistent browser cache separately. State MB (decimal) or MiB (binary). Record
which levels, languages, textures, audio and video remain. A small launcher or
initial chunk is not the complete game; streamed assets still cost transfer,
cache storage and memory. Remote video streaming is a different route.

Use a fresh browser context and record response sizes/encodings and all asset
origins through a reproducible gameplay sequence. Disable or report caches;
compare startup and later loads. Retain a manifest of paths, sizes, hashes and
tool versions. Measure startup/decode time and peak heap/decoded/GPU memory where
possible; mark unavailable measurements untested. Compressed network bytes do
not bound decompressed memory. Website marketing or a loading counter alone is
not evidence of a complete game at the advertised size.

## Reduce content and code first

- Inventory the largest files, duplicates and reachable assets. Exclude editor
  caches, debug symbols, unused packages and duplicate resources from release.
  Keep original assets/symbols elsewhere. Do not remove required content merely
  to meet a number; disclose optional languages/levels and reduced scope.
- Compare Emscripten `-Os`/`-Oz`, link-time optimization (`-flto`) and a build
  without shipped debug symbols/assertions against the working debug baseline.
  Rebuild dependent libraries consistently. Do not disable exceptions, RTTI,
  filesystem or required codecs unless the game works without them. See
  [Emscripten optimization](https://emscripten.org/docs/optimizing/Optimizing-Code.html).
- For large assets, compare texture resolution/mips and supported compressed
  texture formats; deduplicate atlases/materials/meshes; compare mesh/animation
  quantization and suitable audio/video codecs. Check target browser/runtime
  decoders, transparency, loops, latency and visual/audio quality. A tiny
  encoded texture can still expand substantially on the CPU/GPU.
- Load level/region packs on demand when the engine supports it. Use bounded
  prefetching, cancellation and cache eviction. Test a cold region transition
  and missing-network behavior. Report initial and total content sizes; do not
  describe demand loading as lossless compression of the entire game.

## Compress for the actual host

Compare high-quality Brotli and gzip on compressible JS/Wasm/text/data, keeping
only useful results. Already compressed media may barely shrink or grow. Pin
tool versions/settings; use deterministic output and verify decoded hashes.
Avoid repeatedly recompressing archives. Apply archive unpacking byte/file/path
limits to untrusted inputs, including decompression bombs.

Prefer HTTP `Content-Encoding: br`/`gzip` with the correct decoded MIME type
(`application/wasm` for Wasm), cache variants and `Vary: Accept-Encoding` when
negotiating. Verify final CDN responses and both browsers: wrong headers can
produce a small download that never starts. Brotli support for HTTP encoding and
support in a game's own decompressor are separate capabilities.

If a static host cannot set encoding headers, use the engine's supported fallback
loader or an explicit application decoder. For example, Mosslight's demo fetches
opaque gzip payloads and uses browser `DecompressionStream('gzip')` before
initializing Emscripten. The `.bin` files are application-compressed bytes, not
HTTP-encoded JS/Wasm. Do not also set `Content-Encoding: gzip` for those bytes:
the browser would decode once before the loader. This fallback buffers decoded
code, so measure its startup/memory tradeoff; it is not a universal large-game
loader. See [DecompressionStream](https://developer.mozilla.org/en-US/docs/Web/API/DecompressionStream).

## Acceptance and reporting

Verify identical required scenes, inputs, collisions, menus, audio activation,
saves across full reload, and representative later content in the target
browsers. Include before/after byte tables, reduction method, removed or reduced
content, exact tools, cold/warm cache state and known quality/performance costs
in the port report. Label unrun tests explicitly. A smaller broken build fails.

A third-party claim such as “GTA V in 700 MB” needs its own reproducible inventory,
network capture and scope verification before it can be used as a benchmark.
This skill does not claim that result or redistribute that site's game files.
