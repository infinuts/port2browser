'use strict';
const $ = id => document.getElementById(id);
const status = message => { $('status').textContent = message; };
let ready = false, started = false, mediaReady = false, manifest, failure = null;
const logs = [];
function log(...parts) {
  const message = parts.join(' ');
  logs.push(message);
  if (logs.length > 250) logs.shift();
  $('log').textContent = logs.join('\n');
  console.log(message);
}
function fail(error) { failure = error; status('Unable to start: ' + error.message); log(error.stack || error); }
var Module = {
  noInitialRun: true,
  canvas: $('canvas'),
  print: log, printErr: log,
  onAbort(reason) { status('Engine stopped: ' + reason); },
  onRuntimeInitialized() {
    const fs = Module.FS;
    fs.mkdirTree('/profile');
    fs.mount(Module.IDBFS, {}, '/profile');
    fs.syncfs(true, error => {
      if (error) { fail(new Error('Cannot restore browser storage: ' + error)); return; }
      ready = true;
      if (!failure && !$('gamefiles').files.length) status('Choose the v1.3.0.2 game folder.');
      $('start').disabled = !mediaReady;
    });
  }
};
const manifestReady = fetch('assets.json').then(response => {
  if (!response.ok) throw new Error('Missing asset manifest');
  return response.json();
}).then(value => { manifest = value; });
manifestReady.catch(fail);
$('gamefiles').addEventListener('change', async event => {
  $('start').disabled = true;
  mediaReady = false;
  failure = null;
  try {
    await manifestReady;
    const available = new Map();
    for (const file of event.target.files) {
      const segments = file.webkitRelativePath.split('/');
      segments.shift(); // discard the chosen root folder's name
      const path = segments.join('/');
      if (available.has(path)) throw new Error('Duplicate input path: ' + path);
      available.set(path, file);
    }
    // Read only files explicitly listed by the pinned upstream checkout. Profile,
    // authentication keys and arbitrary files outside these paths are ignored.
    for (const entry of manifest.files) {
      const file = available.get(entry.path);
      if (!file || file.size !== entry.bytes) throw new Error('Missing or different version: ' + entry.path);
    }
    mediaReady = true;
    status('Folder selected. Load verifies ' + manifest.files.length + ' local files.');
    $('start').disabled = !ready;
  } catch (error) { fail(error); }
});
$('start').addEventListener('click', async () => {
  if (!ready || !mediaReady || started) return;
  $('start').disabled = true;
  $('gamefiles').disabled = true;
  try {
    const available = new Map([...$('gamefiles').files].map(file => [file.webkitRelativePath.split('/').slice(1).join('/'), file]));
    let index = 0;
    for (const entry of manifest.files) {
      const bytes = new Uint8Array(await available.get(entry.path).arrayBuffer());
      const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(b => b.toString(16).padStart(2, '0')).join('');
      if (digest !== entry.sha256) throw new Error('Modified file: ' + entry.path);
      Module.FS.mkdirTree('/' + entry.path.slice(0, entry.path.lastIndexOf('/')));
      Module.FS.writeFile('/' + entry.path, bytes);
      if (++index % 50 === 0) { status('Verified ' + index + ' / ' + manifest.files.length + ' local files…'); await new Promise(requestAnimationFrame); }
    }
    started = true;
    Module.callMain(['-t0', '-w960', '-h600', '--home=/profile', '--loadmap=ac_desert', '-eautodownload 0; showmenuonstartup 0; mapstartonce = []; consize 0']);
    $('start').textContent = 'Local game loaded';
    const restoredName = Module.ccall('ac_player_name', 'string', [], []);
    if (Module.FS.analyzePath('/profile/config/saved.cfg').exists) $('nickname').value = restoredName;
    $('save').disabled = $('capture').disabled = false;
    setInterval(() => {
      const state = JSON.parse(Module.ccall('ac_snapshot', 'string', [], []));
      $('match').disabled = state.map_bytes <= 0;
      $('telemetry').textContent = `${state.bots} bots / health ${state.health} / ${Module.audioState()} audio`;
    }, 500);
    status('Game loaded. Start the bot match, then click the game to play.');
  } catch (error) { fail(error); if (!started) { $('gamefiles').disabled = false; $('start').disabled = false; } }
});
function command(text) { Module.ccall('ac_command', null, ['string'], [text]); }
$('match').addEventListener('click', () => {
  Module.ccall('ac_start_match', null, [], []);
  status('Starting offline bot deathmatch… Click the game to capture the mouse.');
});
async function capture() {
  if (!started) return;
  try {
    await Module.activateAudio();
    $('canvas').focus();
    await $('canvas').requestPointerLock();
    status('Playing locally. Esc releases the mouse; Space respawns.');
  } catch (error) { status('Click the game again to enable mouse capture: ' + error.message); }
}
$('capture').addEventListener('click', capture);
$('canvas').addEventListener('click', capture);
function release() { if (started) Module.ccall('ac_release_input', null, [], []); }
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && document.pointerLockElement) {
    event.preventDefault(); event.stopImmediatePropagation();
    document.exitPointerLock(); release();
  }
}, true);
window.addEventListener('blur', release);
document.addEventListener('visibilitychange', () => { if (document.hidden) release(); });
document.addEventListener('pointerlockchange', () => { if (!document.pointerLockElement) release(); });
$('save').addEventListener('click', async () => {
  $('save').disabled = true;
  try {
    const name = $('nickname').value.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 15) || 'browser-player';
    command('name ' + name);
    Module.ccall('ac_write_settings', null, [], []);
    await new Promise((resolve, reject) => Module.FS.syncfs(false, error => error ? reject(error) : resolve()));
    status('Settings saved. Reload, reselect the folder and load to restore them.');
  } catch (error) { fail(error); }
  finally { $('save').disabled = false; }
});
