---
name: port2browser-platform
description: Adapt cross-engine game platform services to the browser. Use for rendering backends, frame scheduling, input/focus, audio gestures, persistent saves, threads, networking and large-game capability budgets.
license: MIT
---

# Adapt the platform boundary

Work from an identified engine/runtime and required gameplay behavior. Keep a
capability ledger: native requirement, web implementation, exact version/browser,
verification method, result and remaining blocker. Modern engines need this per
dependency rather than a single engine-level compatibility flag.

- Rendering: use an actual WebGL/WebGPU backend; audit shaders, texture formats,
  limits, render targets and device/context loss. Supply reduced-fidelity modes
  only with an explicit scope decision and gameplay comparison.
- Scheduling: use browser frame callbacks/workers, account for visibility throttling
  and preserve simulation timing. Avoid blocking waits on the main thread.
- Input: bind capture/fullscreen/audio to gestures; release all held keys/buttons
  on blur or capture loss. Check pointer lock, keyboard layout and gamepad support
  on the requested devices rather than assuming desktop OS behavior.
- Audio: check context activation and real sound submissions; manual listening is
  a separate result. Audit codec support and resource use through scene changes.
- Saves: await asynchronous storage writes, handle quotas/denial and migrations,
  then verify a new page instance restores state. An in-memory save is not durable.
- Threads: require the runtime's Wasm threading model and hosting isolation where
  needed. Workers do not supply arbitrary native pthread/OS behavior automatically.
- Networking: map HTTP/WebSocket/WebRTC to protocol requirements. Raw UDP and
  platform store APIs need an implemented compatible boundary or a blocker.

Estimate startup transfer, later streamed bytes, peak decoded/heap/GPU memory,
shader warm-up and measured frame times on stated hardware. LOD, smaller textures,
asset streaming and fewer workers can reduce costs but do not guarantee a large
modern game fits. Record lost features and unavailable middleware/services.

Prove the hardest boundary in the agreed slice, then rerun actual gameplay after
changes. Handoff the adapter, capability ledger, hosting contract and evidence.
