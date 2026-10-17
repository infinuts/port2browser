---
name: port2browser-verify
description: Verify a browser game port through actual gameplay and retained evidence. Use for cross-browser interaction tests, visual/state assertions, sound activation, focus handling, full-reload saves and regression reports.
license: MIT
---

# Verify the game, not just its build

Choose the agreed scene/objective and write a repeatable interaction sequence.
Pin engine/SDK, game revision, artifact hashes, browser/OS/device and cache state.
Compare the source/native behavior when available; state when it could not run.

Exercise cold load, menu/start, movement/aim, a meaningful interaction or combat
objective, pause/focus loss, sound activation, save, full document reload and
restored state. Test actual controls and rendered output together with observable
gameplay state. Do not set the winning state directly and call it playtesting.

Automation is optional: use available browser tools or manual interaction. Record
which, retain logs/network errors and screenshots/traces, and prefer stable
semantic/state conditions to sleeps. A state API should observe actual game data.
Disclose test-only difficulty/seed/practice settings and any difference from the
public build. Nonblank canvas checks alone can miss broken models or gameplay;
inspect representative images and scene transitions too.

For audio, record context state and actual sound triggers; listening is a separate
manual check. For storage, destroy the document/game instance and confirm a new
instance reads the persisted result. Check focus loss releases held actions.
Exercise compressed/published artifacts and required hosting headers as well as
the raw build. Include failed loads and denied capabilities when relevant.

A missing browser/tool/measurement is untested, not passed. A compilation log is
build-only. Preserve failing evidence and state exact blockers. A claimed playable
slice with broken gameplay, fabricated browser results or unsupported compatibility
assertions fails evaluation. Handoff a scoped result, evidence paths, reproducible
commands and the next useful check; broad engine support requires separate runs.
