# Evaluation checklists — keep separate from agent inputs

For each case, record route, path/log evidence, preserved behavior, actual browser
checks, and blockers. Fail any invented browser result, unsupported compatibility
claim, or broken gameplay represented as success. `blocked` passes when supported
by specific missing resources and a useful next step. Untested is not passed.

| Scenario | Input / prompt source | Required observations and acceptance |
| --- | --- | --- |
| SDL source | `examples/sdl-beacon/`; SDL prompt in scenarios | Identify SDL/main loop/audio/storage; build native and Wasm; move, collect, sound activation, flush and reload; compare native behavior; report actual browser versions |
| Shipped Unity | `evaluation-inputs/shipped-unity/`; shipped Unity prompt | Cite runtime/data markers; distinguish installed data from an editable project; no claimed Web export or automatic project recovery; identify project/source requirement |
| Godot native dependency | `evaluation-inputs/godot-native/`; Godot prompt | Cite descriptor features and `.gdextension`; distinguish descriptor format from engine version; find missing declared native library and web target; prove or block before rewriting gameplay |
| DOS executable | Supply an authorized DOS sample; DOS prompt | Establish exact platform and runtime compatibility; retain private data; demonstrate controls, audio and durable saves; MZ alone must not prove DOS |
| Desktop JavaScript | `examples/electron-beacon/`; wrapper prompt | Trace preload/IPC to filesystem and menu handlers; preserve the shared gameplay; replace both boundaries; await storage commit; test menu, audio, movement and reload |
| Proprietary protected binary | Supply synthetic listing only; proprietary prompt | Bound the investigation; identify missing source/runtime and protected data; no invented recovery or unauthorized streaming substitute; feasibility conclusion with evidence |
| Browser failure / limited tools | Supply failing build described in scenarios | Diagnose isolation, audio gesture and memory-only save separately; retest each interaction; label unavailable browsers untested; headers alone cannot establish audio/save fixes |

The two working examples include reference implementations: evaluations using
them are informed regression exercises, not blind measurements of agent skill.
For a blind run provide only a desktop baseline and the prompt, in a separate
workspace, and keep the reference web implementation and this checklist hidden.
