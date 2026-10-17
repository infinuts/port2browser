# Local transfer and size reports

The optional helpers use Python 3.10+ and the standard library. Run against a
stable dedicated build directory, not the game source or a folder of private data.

## Range and transfer throttling

```sh
python /path/to/port2browser/scripts/serve.py ./build-web --port 8000 --throttle 512
```

`--throttle` is KiB/s per file response (zero disables). Concurrent responses have
separate limits; it does not simulate bandwidth shared across a connection, RTT,
packet loss, CPU decoding or a physical device. Compare cold and warm requests
using browser tooling and record the actual conditions.

The server supports a single `bytes=start-end`, `bytes=start-` or `bytes=-suffix`
GET range, with `206`, `Content-Range` and bounded streaming. Unsatisfiable ranges
return `416`. HEAD, malformed/multipart ranges and requests with conditional or
If-Range headers use the normal full/conditional response. It does not implement
multipart assembly or strong resume validators. Ranges into `.gz`/`.br` address
the stored encoded bytes and retain Content-Encoding; partial gzip bytes cannot
be decompressed independently. MIME, path restrictions and isolation remain in
force. See [HTTP range semantics](https://www.rfc-editor.org/rfc/rfc9110.html#name-range-requests).

## Size accounting

```sh
python /path/to/port2browser/scripts/size_report.py ./build-web > sizes.json
python /path/to/port2browser/scripts/size_report.py ./build-web --max-bytes 536870912 --top 10
```

Schema version 1 includes `files` with path, stat `raw_bytes`, streamed level-9
candidate `gzip_bytes` (null when unmeasured), and optional `decoded_estimate`.
`largest` orders the biggest raw files; `gzip` sums only measured pairs so a
partial sample cannot produce a false overall ratio. The zlib runtime version is
recorded. Already encoded files are also measured: this is not a recommendation
to double-compress them or evidence of the bytes a deployed host transfers.

PNG dimensions estimate a single RGBA8 surface; PCM WAV metadata estimates frames
as float32 channels. These are header-based estimates, not validated decodes,
verified asset contents or peak memory. JPEG, compressed audio and unknown formats
remain null. Wasm heap, GPU allocation, mipmaps, decoder buffers, duplicates,
streaming and concurrent scenes need separate measurement.

The total read budget defaults to 256 MiB; entry/depth limits default to 20,000/32.
Reads are streamed in chunks of at most 64 KiB. Links/reparse points, special files
and common dependency directories are skipped. `inventory`, `completeness` and
bounded `warnings` distinguish incomplete traversal, unreadable files and omitted
gzip measurements. Keep the tree unchanged throughout. Redirect JSON outside the
input directory and review private paths before sharing it.
