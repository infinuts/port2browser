# Changelog

## Unreleased

- Add an optional reusable JSON-plan browser verifier with retained state/render,
  Web Audio, focus, reload and limited timing evidence; unavailable tools stay untested.
- Add shared-action touch controls to Electron Beacon and separate WebKit/mobile
  emulation regressions, without claiming shipping-Safari or physical-device support.

- Pin emsdk checkout and compiler installation through one CI setup action.
- Add a security reporting policy and Dependabot for Actions/npm updates.
- Add single-byte-range GETs and optional per-response throttling to the local
  server, retaining compressed MIME/encoding, isolation and path restrictions.
- Add bounded stdlib raw/gzip size reports with explicit PNG/WAV memory estimates,
  and link an actual agent-produced port report from the README.

- Split porting guidance into a router and 12 independently packageable task
  skills, with version-scoped playbooks for 28 engine/runtime routes.
- Add bounded Defold, Construct, GDevelop and Rust dependency clues, plus
  investigation-only task navigation in schema-version-1 inspection reports.
- Add bundle/collection packaging checks and include task modules in evaluation
  treatment copies and revision hashes. No new agent benchmark is claimed.
- Add an AssaultCube 1.3.0.2 browser field test: patched upstream C++ engine,
  offline bots, gesture-bound controls/audio and IDBFS settings. Stock media
  are selected and verified locally; the public package contains no game media.
- Add separate Chromium/Firefox gameplay checks and publication-boundary tests.

- Add Mosslight, an original C++/SDL exploration game with hazards, collectibles,
  generated art/audio, completion and durable saves, as the live demo.
- Add measured debug/release/gzip size comparisons and a static-host decoder.
- Extend the skill with content/code/asset size reduction, Brotli/gzip hosting,
  demand-loading and honest transfer/memory accounting guidance.

## v0.1.0-rc.1 — 2026-10-16

First evaluation candidate; the four ordered improvement PRs await review.
The release tag identifies the full candidate commit, not the current main branch.

- Add an original SDL2 native/Wasm game with generated audio and durable saves.
- Add an original Electron filesystem/IPC wrapper and browser adaptation.
- Add optional Chromium/Firefox gameplay checks with retained evidence artifacts.
- Extend schema-version-1 inspection reports with bounded observed metadata,
  omission counts, scan errors and separate completeness indicators.
- Add synthetic Unity/Godot assessment inputs and explicit evaluation checklists.
- Extend helper CI to macOS and document tested routes and remaining limits.

See [recorded evaluations](tests/evaluation-results/2026-10-16.md) and each example's
port report for measured results. Manual listening, Safari/mobile, long sessions,
performance profiling, and unseen-game agent success are not established.

### Install, update, or reproduce this candidate

Keep SKILL.md, references/, scripts/ and LICENSE together. For example:

```sh
git clone --branch v0.1.0-rc.1 https://github.com/infinuts/port2browser.git ~/.agents/skills/port2browser
```

For an existing clone, review local changes first, then:

```sh
git -C /path/to/port2browser fetch --tags origin
git -C /path/to/port2browser checkout v0.1.0-rc.1
```

A tag checkout is detached and reproducible. Return to your tracked branch before
using `git pull --ff-only` for ongoing updates. Restart your agent session after
installation. Claude Code uses its own skill directory as described in README.md.
Optional examples/dev dependencies are not required to load the skill.
