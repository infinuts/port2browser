const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('beaconPlatform', {
  load: () => ipcRenderer.invoke('beacon:load'),
  save: value => ipcRenderer.invoke('beacon:save', value),
  menu: () => ipcRenderer.invoke('beacon:menu')
});
