const { app, BrowserWindow, ipcMain } = require('electron');
const fs = require('node:fs/promises');
const path = require('node:path');
let window;
app.whenReady().then(async () => {
  const savePath = path.join(app.getPath('userData'), 'beacon.json');
  ipcMain.handle('beacon:load', async () => {
    try { return JSON.parse(await fs.readFile(savePath, 'utf8')); }
    catch (error) { if (error.code === 'ENOENT') return null; throw error; }
  });
  ipcMain.handle('beacon:save', async (_, value) => {
    if (!value || !Number.isInteger(value.x) || value.x < 0 || value.x > 288 || ![0,1].includes(value.collected)) throw new Error('Invalid save');
    await fs.mkdir(path.dirname(savePath), { recursive: true });
    await fs.writeFile(savePath, JSON.stringify(value), 'utf8');
  });
  ipcMain.handle('beacon:menu', async () => 'Continue with arrows, Space, and S.');
  window = new BrowserWindow({ width: 760, height: 540, show: !process.argv.includes('--smoke'), webPreferences: {
    preload: path.join(__dirname, 'preload.cjs'), nodeIntegration: false, contextIsolation: true, sandbox: true
  }});
  window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  window.webContents.on('will-navigate', event => event.preventDefault());
  await window.loadFile(path.join(__dirname, 'index.html'));
  if (process.argv.includes('--smoke')) {
    try {
      const result = await window.webContents.executeJavaScript(`(async () => {
        const sample = {x:120,collected:1};
        await beaconPlatform.save(sample);
        return {save: await beaconPlatform.load(), menu: await beaconPlatform.menu()};
      })()`);
      if (result.save.x !== 120 || result.save.collected !== 1 || !result.menu.startsWith('Continue')) throw new Error('IPC smoke failed');
      console.log('Electron filesystem save/load and IPC menu passed'); app.exit(0);
    } catch (error) { console.error(error); app.exit(1); }
  }
}).catch(error => { console.error(error); app.exit(1); });
app.on('window-all-closed', () => app.quit());
