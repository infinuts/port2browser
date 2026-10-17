# Godot Beacon

An original MIT-licensed Godot **4.5.1 standard/GDScript** project, with native
and browser execution of the same scene. All shapes and the short 440Hz PCM tone
are generated in code. No commercial game files, extensions, or C# exporter.

## Build and play

Install the standard editor and matching 4.5.1 export templates from
[Godot's official release](https://github.com/godotengine/godot-builds/releases/tag/4.5.1-stable).
Set `GODOT` to the editor executable if it is not named `godot` on PATH.
From the repository root:

```sh
python3 examples/godot-beacon/build.py native-smoke
python3 examples/godot-beacon/build.py web
python3 scripts/serve.py examples/godot-beacon/build/web --port 8000
```

Open `http://127.0.0.1:8000/`, click Start, press Right eight times, Space, then
S. Wait two seconds for Godot's automatic filesystem synchronization, then fully
reload: position 120 and the collected beacon must restore. Storage belongs to
the origin; a different port or private/blocked storage can change persistence.
Save status says **written; syncing automatically**, not durable, until a reload
confirms restoration. Corrupt/out-of-range saves are ignored.

To run the native scene interactively:

```sh
godot --path examples/godot-beacon
```

Enter starts; the same controls apply. Native saves use `user://beacon.json`.
The smoke test overrides that path with a disposable file, checks movement,
collection, sound submission and save/load, then removes the temporary workspace.
The build script copies project inputs to a temporary directory for imports and
exports, preserving the original project files.

CI uses `GODOT_WEB_TEMPLATE` pointing to **web_nothreads_release.zip**, extracted
from the pinned standard template archive. This optional override avoids
installing global editor templates. A threaded `web_release.zip` is a different
runtime and must not be substituted. The preset disables threads/extensions,
uses Compatibility/WebGL 2, and requires no isolation headers or service worker.
See [Godot 4.5 web export requirements](https://docs.godotengine.org/en/4.5/tutorials/export/exporting_for_web.html).

## Verification

After building web, run the optional development tests:

```sh
npm ci
npx playwright install chromium firefox
npm run test:browser -- godot.spec.js
```

The tests read actual GDScript state via JavaScriptBridge, inspect a screenshot
of the WebGL player, exercise keyboard/focus behavior, observe the engine's real
audio context and sound trigger, then restart the engine via full reload to
verify the file save. Manual listening is a separate untested check.
See [the completed port report](port-report.md).
