/* IndexedDB replaces the desktop filesystem. Promises resolve after commit. */
const database = new Promise((resolve, reject) => {
  const request = indexedDB.open('port2browser-electron-beacon', 1);
  request.onupgradeneeded = () => request.result.createObjectStore('saves');
  request.onsuccess = () => resolve(request.result);
  request.onerror = () => reject(request.error);
  request.onblocked = () => reject(new Error('Save database upgrade blocked'));
});
async function transaction(mode, value) {
  const db = await database;
  return new Promise((resolve, reject) => {
    const tx = db.transaction('saves', mode), store = tx.objectStore('saves');
    const request = mode === 'readwrite' ? store.put(value, 'beacon') : store.get('beacon');
    tx.oncomplete = () => resolve(request.result);
    tx.onabort = () => reject(tx.error || new Error('Save transaction aborted'));
    tx.onerror = () => reject(tx.error);
  });
}
window.beaconPlatform = {
  load: () => transaction('readonly'),
  save: value => transaction('readwrite', value),
  menu: async () => 'Continue with arrows, Space, and S.'
};
