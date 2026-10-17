# Rust, Bevy and Macroquad

Read `Cargo.toml`, `Cargo.lock`, target feature configuration, build scripts and
native dependencies. Distinguish native source from prebuilt desktop libraries.
Choose the framework's supported browser backend, not a generic Wasm compiler
command that omits its JS loader/windowing integration.

[Bevy's browser examples](https://bevy.org/examples/) and
[Macroquad's Wasm instructions](https://github.com/not-fl3/macroquad) were reviewed
on 2026-10-17. Pin framework, `wgpu`/windowing, loader and Rust toolchain versions.
For Bevy, choose WebGL2 or WebGPU according to the exact release/features and
requested browser matrix; do not assume an automatic fallback. For Macroquad,
match the generated Wasm to the correct JS bundle rather than a floating CDN.

A `wasm32-unknown-unknown` target is a starting point for compatible projects;
OS threads, sockets, filesystem and native crates still need a web implementation.
Keep build-time code generators native. Inspect project hooks before building.

Prove one asset-backed scene, input, sound and persisted progress. Test the actual
shader/texture path and asynchronous loading. Check file casing and packaged
base URLs. Measure release transfer and decoded memory after feature pruning.
Handoff target/features, toolchain/lockfile, loader revision, patches and browser
evidence. These framework routes are documented here but not newly game-tested.
