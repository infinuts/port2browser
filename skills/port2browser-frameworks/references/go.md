# Go / Ebitengine

Identify Go/module versions, `go.mod`, `go.sum`, game source and non-Go libraries.
An executable or Go Wasm compiler alone does not supply the game's graphics or
OS integrations.

The [Ebitengine WebAssembly guide](https://ebitengine.org/en/documents/webassembly.html),
reviewed 2026-10-17, documents a `GOOS=js GOARCH=wasm` source build and matching
Go `wasm_exec.js`. Copy the loader from the same toolchain that built the module;
its location varies across Go versions. Serve the dedicated output with correct
Wasm MIME and base paths. Inspect build scripts and use locked versions rather
than the guide's floating demonstration commands for reproducible ports.

Audit CGO/native modules, filesystem assumptions, sockets, worker usage, shader
compatibility, audio activation and storage. Keep host content-generation tools
native. Do not assume a desktop-supported package has a browser implementation.

First probe: load real resources, move, interact, activate sound, lose focus and
restore saved progress after a full reload in each requested browser. Record
source/tool/loader hashes and actual failures. RequestAnimationFrame callback
intervals are not GPU performance measurements. Guidance only; no new Go browser
compatibility result is implied by this note.
