/* Browser implementation of the original asynchronous Electron bridge. */
(() => {
  'use strict';
  let database;
  function openDatabase() {
    if (!database) {
      database = new Promise((resolve, reject) => {
        const request = indexedDB.open('electron-beacon', 1);
        request.onupgradeneeded = () => {
          request.result.createObjectStore('saves');
        };
        request.onerror = () => reject(request.error);
        request.onblocked = () => reject(new Error('Save database upgrade blocked'));
        request.onsuccess = () => {
          const db = request.result;
          db.onversionchange = () => { db.close(); database = undefined; };
          resolve(db);
        };
      });
    }
    return database;
  }

  async function transact(mode, value) {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      // A successful put request is not yet a committed, durable save.
      const transaction = mode === 'readwrite'
        ? db.transaction('saves', mode, { durability: 'strict' })
        : db.transaction('saves', mode);
      const store = transaction.objectStore('saves');
      const request = mode === 'readwrite'
        ? store.put(value, 'beacon')
        : store.get('beacon');
      transaction.oncomplete = () => resolve(mode === 'readonly' ? request.result ?? null : undefined);
      transaction.onabort = () => reject(transaction.error || new Error('Save transaction aborted'));
      transaction.onerror = () => reject(transaction.error || request.error || new Error('Save transaction failed'));
    });
  }

  window.beaconPlatform = Object.freeze({
    load: () => transact('readonly'),
    save: async value => {
      if (!value || !Number.isInteger(value.x) || value.x < 0 || value.x > 288 || ![0, 1].includes(value.collected)) {
        throw new Error('Invalid save');
      }
      // Snapshot before asynchronous database opening, as IPC did at invocation.
      const snapshot = structuredClone(value);
      await transact('readwrite', snapshot);
    },
    menu: async () => 'Continue with arrows, Space, and S.'
  });
})();
