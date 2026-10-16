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
named `port2browser` and its supporting files together.

For Codex:

```sh
git clone https://github.com/infinuts/port2browser.git ~/.agents/skills/port2browser
```

For Claude Code:

```sh
git clone https://github.com/infinuts/port2browser.git ~/.claude/skills/port2browser
```

Start a new session and ask the agent to use port2browser. Other
[Agent Skills](https://agentskills.io/specification) compatible harnesses can
load the same `SKILL.md`, `references/`, and `scripts/` directory. Follow their
skill discovery instructions. See the official [Codex](https://developers.openai.com/codex/skills/)
and [Claude Code](https://code.claude.com/docs/en/skills) skill documentation.

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

Start with [SKILL.md](SKILL.md). The [approach reference](references/approaches.md)
covers engine clues and route selection; [no-source guidance](references/no-source.md)
covers investigation and release boundaries.

## License and inspiration

[MIT](LICENSE), for port2browser's own code and documentation. Game files and
external tools retain their own terms.

Inspired by [REA](https://github.com/morluto/rea)'s practice of grounding reverse
engineering findings in evidence. REA is optional; no REA code is bundled.
