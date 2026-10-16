# port2browser

An AI agent skill for bringing offline games to the browser.

Give your coding agent a game project or a directory of game files. port2browser
helps it identify what is there, choose a route, adapt the platform code, and
test a playable browser build. It also helps it explain when the files or tools
are not enough to get there.

The repository is a skill, technical notes, and optional helpers. The agent does
the engineering. There is no universal executable-to-WebAssembly converter.

## Install

Clone this repository into your agent's skill directory, keeping the folder
named `port2browser` and its supporting files together. Git is enough to install
the skill. The optional helpers require Python 3.10+ with no extra packages;
each game route has its own engine/SDK requirements.

For Codex:

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/infinuts/port2browser.git ~/.agents/skills/port2browser
```

For Claude Code:

```sh
mkdir -p ~/.claude/skills
git clone https://github.com/infinuts/port2browser.git ~/.claude/skills/port2browser
```

On Windows, use PowerShell (change `.agents` to `.claude` for Claude Code):

```powershell
$skillParent = Join-Path $env:USERPROFILE '.agents\skills'
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
git clone https://github.com/infinuts/port2browser.git (Join-Path $skillParent 'port2browser')
```

For a project-only install, use `.agents/skills/port2browser` (Codex) or
`.claude/skills/port2browser` (Claude Code) inside that project. To vendor the
skill without a nested Git repository, copy `SKILL.md`, `references/`, `scripts/`
and `LICENSE` into that folder. Keep those paths together when updating.

Start a new session and ask the agent to use port2browser. Other
[Agent Skills](https://agentskills.io/specification) compatible harnesses can
load the same `SKILL.md`, `references/`, and `scripts/` directory. Follow their
skill discovery instructions. See the official [Codex](https://developers.openai.com/codex/skills/)
and [Claude Code](https://code.claude.com/docs/en/skills) skill documentation.

Update a cloned install with `git -C /path/to/port2browser pull --ff-only`.
Pin a reviewed commit with `git -C /path/to/port2browser checkout <commit>` when
you need a repeatable setup. To uninstall, remove that skill folder from your
agent's discovery directory.

## Use it

In Codex:

```text
Use $port2browser on ./my-game. Identify the engine and dependencies, choose
a browser porting route, and get one level playable with keyboard and audio.
Keep the desktop build working. Target desktop Chrome and Firefox first.
```

In Claude Code:

```text
/port2browser Assess ./my-game for a browser port, then build and test the
smallest playable slice. Record blockers and the commands needed to run it.
```

Without source:

```text
Use port2browser to inspect ./game-files without executing them. I have no
source code. Compare compatible browser emulation and open-engine options.
Keep the original assets local and explain what would block a usable port.
```

## What to expect

The agent inventories files and architecture, checks a native web exporter or
other viable route, then proves a small playable slice. Source ports may use
Emscripten and WebAssembly with WebGL or WebGPU. Older games may work through a
browser emulator or a compatible open engine. A binary-only investigation can
take substantial reverse engineering and may end with a feasibility report.

Modern commercial games can depend on unavailable source, desktop middleware,
huge assets, or rendering features that make a browser port impractical. A game
shown in a browser might also be remotely streamed. port2browser makes no claim
to have ported GTA V, Skate, or any other commercial title.

Owning a copy does not establish permission to redistribute its code or assets.
Check game, engine, middleware and asset terms separately. This repository
contains no games, ROMs, BIOS images, or bypass tools.

The handoff includes engine/dependency findings with evidence, a route decision,
reproducible build/run commands, browser test results, and known blockers. A
build that has not been played is reported as untested. No game ports or browser
compatibility benchmarks are bundled with this first version.

## Helpers and references

Run helpers from any working directory using the installed skill's full path.
Quote paths containing spaces. Use `python3` or `py -3` if that is your Python
launcher; the selected interpreter must be Python 3.10 or newer.

```sh
# Read-only inspection; JSON goes to stdout. Write the report outside game-files.
python /path/to/port2browser/scripts/inspect_game.py ./game-files > inspection.json
python /path/to/port2browser/scripts/inspect_game.py ./game-files --max-entries 5000

# Serve only the dedicated build output, never the whole game/repo directory.
python /path/to/port2browser/scripts/serve.py ./build-web --port 8000
# Add --isolate if the chosen runtime requires SharedArrayBuffer.
```

The inspector samples filenames, binary headers, and small dependency manifests.
It leaves archives unopened and never runs the target. Its JSON separates
inferred engine candidates from file counts, binary formats, warnings, and scan
limits. Read `truncated` and `limitations` before drawing conclusions; it is not
a decompiler, full dependency resolver, license checker, or sandbox. Keep the
input tree unchanged during inspection. Output may include private paths and
filenames, so review it before sharing.

The server binds `127.0.0.1` and supports Wasm MIME types, already compressed
gzip/Brotli files, and optional COOP/COEP headers. It is a local test server;
test HTTPS and deployment configuration separately. Stop it with Ctrl+C.

| File | Use it for |
| --- | --- |
| [SKILL.md](SKILL.md) | The agent's workflow and decision boundaries |
| [Approaches](references/approaches.md) | Engine clues, export choices, Wasm, graphics and emulation |
| [Browser platform](references/browser-platform.md) | Main loop, rendering, audio, controls, storage, threads and hosting |
| [Build and test](references/build-and-test.md) | Build patterns, playtest evidence and troubleshooting |
| [Without source](references/no-source.md) | Runtime alternatives, scoped reconstruction and rights |
| [Port report](references/port-report.md) | A concise handoff template |

## Contribute

Useful contributions include a corrected engine clue, a reproducible build fix,
or a documented porting case with game/engine versions and browser evidence.
Keep proprietary files out of fixtures. Prefer focused references over another
framework or installer.

Run the helper and packaging tests with the standard library:

```sh
python -m unittest discover -s tests -v
```

For changes to the workflow, also use the [manual evaluation cases](tests/scenarios.md).
Automated helper tests cannot establish that an agent can port an arbitrary game.
Keep existing helper arguments and JSON fields compatible; add fields within
`schema_version: 1`, and bump that version for a breaking schema change. Commit
related changes together so regressions can be traced and reverted.

## License and inspiration

[MIT](LICENSE), for port2browser's own code and documentation. Game files and
external tools retain their own terms.

Inspired by [REA](https://github.com/morluto/rea)'s practice of grounding reverse
engineering findings in evidence. REA is optional; no REA code is bundled.
