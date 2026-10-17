---
name: port2browser-assets
description: Optimize and package browser game code and assets with measured size and memory results. Use for compression, texture/audio/model budgets, streaming, user-supplied data and preservation of gameplay/content rights.
license: MIT
---

# Optimize the measured bottleneck

Inventory code and assets by startup necessity, later loading, format, decoded
size and permission to distribute. Keep immutable originals. Choose a measurable
budget for the target devices and preserve a representative gameplay objective.

Separate dead-code/LTO/stripping, content removal, deduplication, lossy asset
conversion, transfer compression and streaming. These operations have different
tradeoffs. A launcher or initial pack size is not the size of the full game.

Prove that an asset is unused before removing it: scene references, dynamic paths,
localization and scripted loads can hide dependencies. Compare texture dimensions,
mips and supported GPU formats; audio sample rate/channels/codecs; model LOD,
materials, animation and collision. Keep required fonts, licenses and attribution.
Generated replacements need their own provenance and cannot silently replace the
requested game's appearance or gameplay.

Build an allowlisted release output. For gzip/Brotli, verify decoded hashes and
correct MIME/Content-Encoding behavior on the real host. Avoid double decoding.
With a header-free application decoder, account for compressed and decoded buffers.
Retest the compressed artifact, not only the development build.

When hosting rights for game media are unresolved, investigate an authorized
local-file loader and validate data versions/paths before use. Keep private saves,
keys and extracted commercial content out of publication. Selecting local files
does not by itself settle all rights questions.

Report baseline/release bytes, startup vs later requests, cold/warm cache, quality
changes, load/frame measurements and peak memory where measured. Keep unavailable
measurements untested. Never promise an arbitrary compression ratio or infer the
size of a commercial game from a landing page or compressed executable alone.
