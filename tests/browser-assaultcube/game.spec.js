const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { PNG } = require('pngjs');
const root = path.resolve(__dirname, '../..');
const source = process.env.ASSAULTCUBE_DATA || path.join(root, 'examples/assaultcube/build/upstream');
let data;
test.beforeAll(() => {
  if (!fs.existsSync(path.join(source, 'packages/maps/official/ac_desert.cgz'))) {
    throw new Error('Set ASSAULTCUBE_DATA to the pinned v1.3.0.2 folder (see example README).');
  }
  data = fs.mkdtempSync(path.join(os.tmpdir(), 'assaultcube-local-'));
  for (const folder of ['packages', 'config', 'bot']) fs.cpSync(path.join(source, folder), path.join(data, folder), { recursive: true });
  fs.writeFileSync(path.join(data, 'private-test-sentinel.txt'), 'This unlisted local file must not be read or uploaded.');
});
test.afterAll(() => { if (data) fs.rmSync(data, { recursive: true, force: true }); });
const state = page => page.evaluate(() => JSON.parse(Module.ccall('ac_snapshot', 'string', [], [])));
async function load(page) {
  await page.goto('/');
  await expect(page.locator('#status')).toHaveText('Choose the v1.3.0.2 game folder.', { timeout: 60000 });
  await page.locator('#gamefiles').setInputFiles(data);
  await expect(page.locator('#start')).toBeEnabled();
  await page.locator('#start').click();
  await expect(page.locator('#match')).toBeEnabled({ timeout: 90000 });
}
function rendered(buffer) {
  const png = PNG.sync.read(buffer), colors = new Set();
  let lit = 0;
  for (let y = 0; y < png.height; y += 8) for (let x = 0; x < png.width; x += 8) {
    const i = (y * png.width + x) * 4;
    colors.add(`${png.data[i]},${png.data[i+1]},${png.data[i+2]}`);
    if (png.data[i] + png.data[i+1] + png.data[i+2] > 90) lit++;
  }
  return { colors: colors.size, lit };
}

test('real local assets: render, bots, movement, aim, fire, focus and settings reload', async ({ page, browser }, info) => {
  const logs = [], errors = [], requests = [];
  page.on('console', message => logs.push({ level: message.type(), text: message.text() }));
  page.on('pageerror', error => errors.push(error.stack || error.message));
  page.on('request', request => requests.push({ method: request.method(), url: request.url() }));
  const report = { browser: browser.version(), platform: process.platform, phases: {} };
  try {
    await load(page);
    expect(await page.evaluate(() => Module.FS.analyzePath('/private-test-sentinel.txt').exists)).toBe(false);
    await page.locator('#match').click();
    await expect.poll(async () => (await state(page)).mode).toBe(8);
    await expect.poll(async () => (await state(page)).bots).toBe(3);
    // Keep player-input checks repeatable; this is the upstream bot practice option.
    await page.evaluate(() => Module.ccall("ac_command", null, ["string"], ["botsshoot 0"]));
    report.test_configuration = "upstream botsshoot 0 during input checks; bots still navigate";
    report.phases.started = await state(page);
    const botStart = report.phases.started.bot_motion;
    await expect.poll(async () => (await state(page)).bot_motion, { timeout: 10000 }).not.toBe(botStart);
    const canvas = page.locator('canvas');
    await canvas.scrollIntoViewIfNeeded();
    await canvas.click();
    await expect.poll(() => page.evaluate(() => document.pointerLockElement?.id)).toBe('canvas');
    await expect.poll(() => page.evaluate(() => Module.audioState())).toBe('running');
    // Space also performs the game's normal respawn if the bots killed us.
    await page.keyboard.press('Space');
    const before = await state(page);
    await page.keyboard.down('w');
    await page.waitForTimeout(600);
    await page.keyboard.up('w');
    await page.keyboard.down('d');
    await page.waitForTimeout(600);
    await page.keyboard.up('d');
    const afterMove = await state(page);
    expect(Math.hypot(afterMove.x - before.x, afterMove.y - before.y)).toBeGreaterThan(0.2);
    const bounds = await canvas.boundingBox();
    await page.mouse.move(bounds.x + bounds.width/2, bounds.y + bounds.height/2);
    const beforeAim = await state(page);
    await page.mouse.move(bounds.x + bounds.width/2 + 65, bounds.y + bounds.height/2 + 10, { steps: 8 });
    await expect.poll(async () => (await state(page)).yaw).not.toBe(beforeAim.yaw);
    const beforeFire = await state(page);
    await page.mouse.down(); await page.waitForTimeout(350); await page.mouse.up();
    await expect.poll(async () => (await state(page)).shots).toBeGreaterThan(beforeFire.shots);
    const fired = await state(page);
    expect(fired.magazine).toBeLessThan(beforeFire.magazine);
    expect(fired.sounds).toBeGreaterThan(0);
    report.phases.gameplay = fired;
    report.phases.audioContext = await page.evaluate(() => Module.audioState());
    await page.keyboard.press('Escape');
    await expect.poll(() => page.evaluate(() => document.pointerLockElement)).toBe(null);
    const image = await canvas.screenshot();
    const pixels = rendered(image);
    expect(pixels.colors).toBeGreaterThan(200);
    expect(pixels.lit).toBeGreaterThan(1000);
    report.phases.rendered = pixels;
    await info.attach('gameplay.png', { body: image, contentType: 'image/png' });
    // Trigger a real page focus loss while a movement key is held.
    await canvas.click();
    await page.keyboard.down('w');
    const other = await page.context().newPage();
    await other.goto('about:blank'); await other.bringToFront();
    await expect.poll(async () => (await state(page)).moving).toBe(0);
    await other.close(); await page.bringToFront(); await page.keyboard.up('w');
    await page.evaluate(() => document.exitPointerLock());
    await page.locator('#nickname').fill('web-tester');
    await page.locator('#save').click();
    await expect(page.locator('#status')).toContainText('Settings saved.');
    await load(page); // full document navigation, new Wasm instance and IDBFS restore
    expect(await page.evaluate(() => Module.ccall('ac_player_name', 'string', [], []))).toBe('web-tester');
    report.phases.restored = await state(page);
    expect(errors).toEqual([]);
    expect(logs.filter(item => /WebGL: INVALID_|Aborted\(|SHADER COMPILE/.test(item.text))).toEqual([]);
    expect(requests.every(request => request.method === 'GET' && new URL(request.url).origin === 'http://127.0.0.1:8878')).toBe(true);
    report.result = 'pass';
  } finally {
    report.errors = errors; report.requests = requests; report.logs = logs;
    await info.attach('browser-evidence.json', { body: JSON.stringify(report, null, 2), contentType: 'application/json' });
  }
});

test('rejects incomplete or mismatched local data before running the engine', async ({ page }) => {
  const invalid = fs.mkdtempSync(path.join(os.tmpdir(), 'assaultcube-invalid-'));
  try {
    fs.writeFileSync(path.join(invalid, 'README.txt'), 'not a game');
    await page.goto('/');
    await page.locator('#gamefiles').setInputFiles(invalid);
    await expect(page.locator('#status')).toContainText('Missing or different version:');
    await expect(page.locator('#start')).toBeDisabled();
  } finally { fs.rmSync(invalid, { recursive: true, force: true }); }
});

test('rejects same-length modified media by hash before engine startup', async ({ page }) => {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'examples/assaultcube/build/web/assets.json'), 'utf8'));
  const entry = manifest.files.find(file => file.bytes > 0);
  const filename = path.join(data, entry.path);
  const original = fs.readFileSync(filename);
  const changed = Buffer.from(original); changed[0] ^= 1;
  try {
    fs.writeFileSync(filename, changed);
    await page.goto('/');
    await page.locator('#gamefiles').setInputFiles(data);
    await expect(page.locator('#start')).toBeEnabled();
    await page.locator('#start').click();
    await expect(page.locator('#status')).toContainText('Modified file: ' + entry.path);
    expect(await page.evaluate(() => Module.ccall('ac_snapshot', 'string', [], []))).toContain('"map_bytes":0');
  } finally { fs.writeFileSync(filename, original); }
});
