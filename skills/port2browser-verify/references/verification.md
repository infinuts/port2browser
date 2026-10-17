# Optional reusable browser verifier

The adjacent `../scripts/verify.cjs` takes an HTTP(S) URL and a small JSON plan.
It runs only the configured checks in a fresh browser context, writes evidence,
and never installs software or logs into a profile. Python helpers remain
stdlib-only. This optional Node.js helper needs caller-provided Playwright
**1.56.1** and **pngjs 7.0.0**, plus matching browser binaries.

From the development checkout:

```sh
npm ci
npx playwright install chromium firefox webkit
node skills/port2browser-verify/scripts/verify.cjs \
  --url http://127.0.0.1:8000/ \
  --plan /path/to/plan.json --output /path/to/new-evidence-directory \
  --browser chromium
```

For a copied standalone skill, keep Node packages in a separate runner directory
and set `NODE_PATH` to that directory's `node_modules`; use the helper's absolute
path. Do not add Node packages to the installed skill. Only execute game URLs the
user has authorized for browser testing. Review evidence for private paths/URLs.

Optional switches: `--headed`, `--browser chromium|firefox|webkit`, and
`--device "Pixel 7"` or `--device "iPhone 13"` using Playwright's registry. Choose a
browser that supports the profile. These are emulated parameters, not physical
Android/iOS devices or the released Safari application. Desktop games requiring a
keyboard do not gain touch gameplay by changing viewport or user agent.

## JSON contract, schema_version 1

```json
{
  "schema_version": 1,
  "state": {"path": "exampleState", "call": true},
  "canvas": "canvas",
  "timeout_ms": 5000,
  "frame_samples": 60,
  "steps": [
    {"action": "click", "selector": "#start"},
    {"action": "press", "key": "ArrowRight", "count": 8},
    {"action": "expect", "values": {"x": 120}},
    {"action": "canvas"},
    {"action": "press", "key": "Space"},
    {"action": "expect", "values": {"collected": 1}},
    {"action": "audio", "min_starts": 1},
    {"action": "focus", "selector": "#menu"},
    {"action": "click", "selector": "canvas"},
    {"action": "press", "key": "s"},
    {"action": "expect", "values": {"saves": 1, "saving": 0}},
    {"action": "reload", "preserve": ["x", "collected"]}
  ]
}
```

Expose an observational state object or zero-argument function in the port; the
helper reads it rather than assigning state. This is a developer testing contract,
not independent proof that the observer tells the truth. Arbitrary source strings
are not accepted as actions. Dotted state/expectation paths exclude prototype and
constructor traversal. Unknown action/plan fields fail validation.

| Action | Meaning |
| --- | --- |
| `click`, `tap` + `selector` | Real mouse or touch input through Playwright |
| `press`, `down`, `up` + `key` | Keyboard input; `press` optionally repeats `count` times |
| `expect` + nonempty `values` | Poll exact partial state, including dotted fields |
| `text` + `selector`, `contains` | Assert visible DOM text |
| `canvas` + optional `selector` | Screenshot and sample colors; uniform output fails |
| `pixel` + normalized `point`, `rgb`, optional `tolerance` | Assert a screenshot pixel independently of state |
| `audio` + positive `min_starts` | Require observed running Web Audio context and successful buffer/oscillator starts |
| `focus` + outside `selector` | Assert the game canvas lost element focus; does not simulate window visibility loss |
| `reload` + nonempty `preserve` paths | Capture values, reload the whole document, then require restored values |
| `capture` | Retain a page screenshot |

A sound submission is not proof of audible output. HTML media, worklets and other
sound mechanisms require their own probes. Manual listening remains untested.
Focus loss must also have a game-specific state/input assertion: element blur
alone cannot prove stuck keys were cleared. A multi-color canvas can still contain
broken gameplay, so combine it with expected pixels and meaningful state changes.

## Evidence and interpretation

`evidence.json` retains a plan hash, browser/tool versions, OS/architecture, device
profile, step outcomes, capped console/network errors, screenshots and category
coverage. Missing requested browsers produce `untested`; they never pass. CLI exit
codes are 0 for all configured required checks passing, 1 for a failed run, and 2
for unavailable tooling or invalid invocation. The output directory must be new.

Default required categories are input, render, state, audio, element focus and
reload persistence. A plan may explicitly set `required` to a subset for a game
without sound/saves; omitted categories stay `untested`. A pass certifies only the
specified sequence. It is not automatically a `playable slice` report or a claim
for the game's whole engine, platform or target devices.

Navigation wall time and Navigation/Resource Timing fields are recorded. Cache,
opaque cross-origin responses and host behavior can affect transfer-byte values.
`frame_callback_intervals` samples up to 60 requestAnimationFrame intervals by
default (0 disables, maximum 300). These are callback scheduling intervals, not
measured simulation/GPU frame time or a performance benchmark. Report hardware,
cache state and test conditions; use a proper profiler for deeper conclusions.

Primary references: [Playwright emulation](https://playwright.dev/docs/emulation),
[Playwright browsers](https://playwright.dev/docs/browsers). No new physical-device
or shipping-Safari compatibility is established by this helper.
