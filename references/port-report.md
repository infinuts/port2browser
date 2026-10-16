# Port report template

Copy the useful fields into the game project and replace bracketed prompts with
observed facts. Keep the report short; link logs and patches instead of pasting
large inventories. Use `unknown` or `untested` when evidence is missing.

```markdown
# Browser port: [game and version]

Status: [playable slice | tested port with scope | build only / untested | blocked]
Target: [browsers/devices, controls, scene and acceptance criteria]
Inputs: [source/project/binaries/data, provenance, original kept at ...]

## Findings
| Finding | Evidence | Confidence / unresolved question |
| --- | --- | --- |
| [engine/version, architecture, subsystem/dependency] | [path, symbol, log] | [confirmed/inferred/unknown] |

## Route
[Chosen route and why; plausible alternatives and concrete reasons rejected.]
First experiment: [action, pass/fail criterion, result and evidence].
Blockers: [essential missing source, dependency, rights, performance or service].

## Build and run
- Tool versions and source revisions: [...]
- Commands from a clean checkout: [...]
- Output directory and local URL: [...]
- Hosting headers, asset paths, compression and isolation: [...]
- Original/native build and regression check: [... or not applicable]

## Changes
[Gameplay/platform boundary changes, patches/commits, reduced scope.]

## Verification
| Test / repeatable interaction | Environment | Result and evidence |
| --- | --- | --- |
| [startup, play, controls/audio, save and reload] | [browser/version/OS/device] | [pass/fail/untested, log or recording] |

Measurements: [download size, startup, frame times, peak memory; method/device].
Known regressions and untested areas: [...].

## Distribution
[Separate code/assets/engine/middleware licenses or permissions, required notices,
user-supplied data, and unresolved release conditions.]

## Next step
[Smallest useful next action, or the resource/decision needed to unblock it.]
```
