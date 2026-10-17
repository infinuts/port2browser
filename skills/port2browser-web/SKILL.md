---
name: port2browser-web
description: Adapt JavaScript and TypeScript desktop games to browsers. Use for Electron, NW.js, RPG Maker MV/MZ, Phaser, PixiJS, Three.js and browser-runtime projects with desktop dependencies.
license: MIT
---

# Remove the desktop platform boundary

Trace the gameplay renderer, preload/bridge, IPC handlers, filesystem, native
addons, menus, dialogs, account/store calls and saves. Keep browser-native game
logic and timing; substitute only platform services with equivalent behavior.
A dependency declaration can describe tooling rather than the shipped game.

For Electron/NW.js, replace Node access with a small asynchronous interface.
Use IndexedDB/OPFS where supported for persistence and a deliberate file picker
for user-supplied files. Preserve save completion, schema/version migrations,
error handling and full-reload recovery; synchronous stubs can lose saves.

For RPG Maker MV/MZ, confirm the runtime generation and plugin versions. Inspect
plugins for Node, native modules, codec and file-path dependencies. Test map
transfer, an event/battle, menus and save/load; an older RPG Maker executable
requires a different compatible runtime. Preserve asset case and URL-relative
paths. Do not defeat encrypted data or license checks to make an export run.

For Phaser, PixiJS and Three.js, identify the actual entrypoint/bundler, then
verify plugins, physics and graphics features. PixiJS/Three.js are libraries, not
proof of a complete engine or project. Feature-detect required WebGL/WebGPU
features and audit resource lifetimes through scene changes/context loss.

Inspect package scripts before running them; pin the existing lockfile and
produce a dedicated static output. Validate input, gesture-bound audio, blur,
menus, gameplay state and a full-reload save in actual target browsers. Retain
console/network failures and record any online service needed after first load.
Handoff the platform adapter and tested scope, not just a screenshot of the menu.

Primary starting points: [Electron process model](https://www.electronjs.org/docs/latest/tutorial/process-model),
[Phaser](https://docs.phaser.io/phaser/getting-started/what-is-phaser),
[Three.js](https://threejs.org/manual/). Check version-matching manuals in the project.
