# Contributing

Keep the installed `SKILL.md`, `references/`, `scripts/`, and `LICENSE` portable.
Optional example toolchains and browser automation belong in development files;
the Python helpers continue to require only Python 3.10+ and the standard library.
Use original or appropriately licensed fixtures. Do not submit proprietary game
data. Keep engine clues inferred until supported by evidence.

## Validate a change

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

For examples, browser platform guidance or server changes, also follow the
[Mosslight build/package instructions](examples/mosslight/README.md),
[SDL build instructions](examples/sdl-beacon/README.md),
[Electron instructions](examples/electron-beacon/README.md), and the
[Godot build instructions](examples/godot-beacon/README.md), then run:

```sh
npm ci
npx playwright install chromium firefox
npm run test:browser
```

Browser CI builds native and web SDL, exports Godot and runs its native smoke,
runs Electron IPC smoke, and exercises all four examples in both
browsers. Linux Firefox needs an audio server: CI starts a PulseAudio null sink;
a running audio context plus submitted samples is not manual listening evidence.
Linux CI uses headed browsers under Xvfb and Mesa software rendering because the
runner's headless Firefox disallows WebGL 2. Pixel assertions still verify the
rendered game. See [Playwright CI guidance](https://playwright.dev/docs/ci).
Artifacts include logs, actual browser versions, screenshots and failure traces.
Do not skip a failing check to establish compatibility.

For inspection changes, preserve existing CLI/JSON fields, add bounded reads,
record omissions/errors, and update the [JSON contract](references/inspection-json.md).
For workflow changes, run relevant [manual scenarios](tests/scenarios.md), compare
against the separate checklists, and commit an honest evaluation record. Distinguish
blind agent evaluation from informed regression. Name unrun scenarios explicitly.

## Pull requests and issue reports

Describe the concrete trigger, observed vs expected behavior, versions, commands,
inspection warnings/limits, and browser evidence. State what remains untested.
Keep changes focused; related tests/docs should accompany behavior changes.

## Release gate

1. Run helper/distribution checks on Linux, Windows and macOS with Python 3.10/3.14.
2. Build the original examples from a clean checkout and pass Chromium/Firefox
   interactions plus native SDL/Mosslight/Godot and Electron filesystem/IPC smoke.
3. Record evaluated skill/source revisions, tool/browser versions, test evidence,
   blockers and unrun agent scenarios. Review all distributable material's rights.
4. Update CHANGELOG.md, create a version tag at the evaluated commit, and publish
   notes linking CI/evaluation evidence. Use a prerelease while the ordered PRs
   await review; never imply those commits are already merged into main.

A CI artifact or example port does not establish support for an arbitrary game.
