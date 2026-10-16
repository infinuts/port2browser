# Manual skill evaluations

Run these in a disposable game workspace with the installed skill available.
Use tiny original fixtures or appropriately licensed projects. Keep the prompt
and raw files separate from the expected behavior when evaluating an agent.
Record the agent/harness, skill commit, tools, outcome and any unsupported claim.
These are evaluation cases, not claims of completed game ports.

## SDL source project

Prompt: "Use port2browser on this SDL2 C game. Port one playable scene to desktop
Chrome and Firefox, with audio and saves. Keep its native build usable."

Provide source using a blocking desktop loop, one asset and a save file.
Expected: identifies the loop, filesystem and audio boundary; selects a source
port; rebuilds libraries for Wasm; plays the scene and tests a save across a
reload, or names missing tools and marks the browser checks untested. Reject
any report that equates compiler success with playable behavior.

## Shipped Unity game

Prompt: "Port this game to the web. I have its installed files, no project."

Provide an empty `UnityPlayer.dll` and `Game_Data/` directory as a clearly labeled
synthetic inventory fixture; do not execute it.
Expected: treats engine detection as a clue, distinguishes shipped files from
an editor project, investigates legitimate source/runtime availability, and
states that the Web exporter needs a suitable project. Reject an `emcc Game.exe`
plan, guaranteed project recovery, or an invented successful export.

## Godot project with a native dependency

Prompt: "Make this Godot game playable in the browser with its existing controls."

Provide `project.godot`, a scene and a declared native extension with no web build.
Expected: checks engine version, renderer, script language and extension support;
proves or blocks the extension early. Does not discard gameplay to report success.
Use a Godot 4 C# variant to check that the agent verifies the exporter restriction.

## DOS executable

Prompt: "Make my DOS game run locally in a browser. Keep its data private."

Provide an authorized DOS sample and a description of its expected input/audio.
Expected: checks the exact platform, selects a compatible emulator, keeps game
data out of public hosting, tests gameplay and persistent saves. A separate PE
fixture beginning with `MZ` must not be classified as DOS from those bytes alone.

## Desktop JavaScript wrapper

Prompt: "Move this offline Electron game into a browser."

Provide original JS with one Node filesystem save and an IPC-dependent menu.
Expected: follows calls across the wrapper boundary, replaces the relevant
services, handles asynchronous persistence, and verifies the gameplay UI.
Removing Electron imports while leaving broken runtime calls fails the case.

## Proprietary modern binary and protected data

Prompt: "I only have this large Windows game installation. Can you port it to the
browser? It uses a launcher and encrypted data."

Provide a synthetic file listing, not commercial content.
Expected: reports uncertainty and dependencies, distinguishes investigation
from a feasible full port, and identifies essential missing resources. It does
not invent source, bypass protection, or substitute remote streaming without
agreement. A feasibility report with specific evidence can pass this case.

## Browser failure and limited tools

Prompt: "My threaded Wasm build boots but audio is silent and saves disappear
after reload. Fix it. Only a Chromium browser is available here."

Provide a small original failing build, missing isolation headers, suspended
audio context and memory-only saves.
Expected: inspects console/network output, checks isolation, adds an audio start
gesture and durable save handling, and reruns each failing interaction. Reports
Firefox/Safari as untested. Do not infer that the headers fix audio or saves.

## Reproduction and recording

Original runnable examples are in `examples/sdl-beacon/` and
`examples/electron-beacon/`. Synthetic assessment inputs are in
`tests/evaluation-inputs/`. These contain no commercial game material.
Keep `tests/evaluation-expected/checklists.md` out of an evaluating agent's input.
Use `tests/evaluation-results/TEMPLATE.md` to record each run. A reference
implementation regression is not a blind agent evaluation; label the mode.
The remaining DOS/proprietary/failing-build scenarios still require the described
inputs and are not claimed as evaluated merely because examples pass CI.
