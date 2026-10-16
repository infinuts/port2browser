# Electron Beacon

Original MIT-licensed companion fixture. `game.js` is shared unchanged by the
Electron wrapper and the web adaptation. Generated rectangles and a 440Hz tone;
no external assets. Controls match SDL Beacon: Start, Right eight times, Space,
S; wait for Save ready and reload. Menu must display the control instructions.

## Browser adaptation

From the repository root:

```sh
python3 scripts/serve.py examples --port 8000
```

Open `http://127.0.0.1:8000/electron-beacon/web/`. The web adapter replaces
filesystem saves with IndexedDB transactions and replaces the IPC menu with a
local asynchronous action. A save resolves only after the transaction commits.
A storage failure remains visible; the game does not pretend it saved.

```sh
npm ci
npx playwright install chromium firefox
npm run test:browser -- --grep electron-beacon
```

The browser tests share the movement, rendering, audio, focus and reload checks
with SDL Beacon, and exercise Menu. See [the port report](port-report.md).

## Original desktop wrapper

Node.js 22+, npm and Electron **44.8.0**:

```sh
cd examples/electron-beacon/desktop
npm ci
npm start
```

`main.cjs` handles filesystem load/save under Electron's user-data directory and
the IPC menu. `preload.cjs` exposes only those three operations; renderer Node
integration is disabled. To test IPC and filesystem persistence without changing
your normal save, choose a fresh absolute user-data directory:

```sh
npm run smoke -- --user-data-dir=/tmp/beacon-electron-test
```

This hidden-window smoke check writes and reads one test save and invokes Menu.
It is not a desktop gameplay or listening test. Browser code never imports
Electron or Node. Do not serve `desktop/` as your public deployment; publish
`web/` with `game.js` at the referenced parent path, or adjust that asset path
when packaging. The repository-wide example server is for local development.
