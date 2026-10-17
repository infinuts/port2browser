# Reusable verifier regression record

The optional verifier is checked against the original Electron Beacon adaptation,
which has touch buttons invoking the same actions as its keyboard controls.

Reproduce from this checkout with Node 22+, Python 3.10+ and the pinned root npm
lockfile:

```sh
npm ci
npx playwright install chromium firefox webkit
node --test tests/verification/plan.test.cjs
python3 tools/test_verifier.py --output /path/to/new-evidence-directory
```

The runner serves only copied game files and a synthetic blank canvas from a
new temporary directory. It runs desktop Chromium/Firefox/WebKit, Chromium with
the Pixel 7 profile and WebKit with the iPhone 13 profile. Each positive sequence
checks actual controls, visual output, expected state, sound activation/submission,
element focus, menu and persistence after full document reload. Timing samples
are scheduling/navigation observations, not device performance certification.

Negative cases require a uniformly blank canvas and a wrong state expectation to
fail. A deliberately missing browser cache must produce `untested` and exit 2.
The JSON plans are regression inputs; they do not establish blind agent behavior.

[Local results and exact versions](browser-evidence.json) were recorded on
2026-10-17 on macOS arm64: Chromium 141.0.7390.37, Firefox 142.0.1 and WebKit 26.0.
All five positive targets passed; both deliberately invalid gameplay cases failed,
and the absent-browser case was untested with exit 2. Plans, source hashes,
per-step state/audio results and screenshots are retained under `evidence/`.
The tested worktree is identified by the listed source hashes, not represented as
an already committed revision. CI retains its own evidence artifact. Actual iOS/Android devices,
shipping Safari, manual listening and other engines remain untested.
