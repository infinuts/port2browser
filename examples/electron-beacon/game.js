/* Original MIT fixture; shared by the Electron wrapper and browser adaptation. */
(async function() {
  const platform = window.beaconPlatform;
  const canvas = document.querySelector('canvas');
  const context = canvas.getContext('2d');
  const start = document.querySelector('#start');
  const status = document.querySelector('#status');
  const state = { x: 24, collected: 0, started: 0, sounds: 0, saving: 0, saves: 0, audioState: 'unavailable', menu: '' };
  let audio;
  function draw() {
    context.fillStyle = '#0f172a'; context.fillRect(0, 0, 320, 180);
    context.fillStyle = state.collected ? '#1eb43c' : '#ffbe3c'; context.fillRect(120, 64, 24, 24);
    context.fillStyle = '#38bdf8'; context.fillRect(state.x, 100, 24, 24);
    status.textContent = `Position ${state.x} · Beacon ${state.collected ? 'collected' : 'waiting'} · Save ${state.saving === 1 ? 'pending' : state.saving === -1 ? 'failed' : 'ready'}`;
  }
  window.exampleState = () => ({ ...state, audioState: audio?.state || 'unavailable' });
  try {
    const saved = await platform.load();
    if (saved && Number.isInteger(saved.x) && saved.x >= 0 && saved.x <= 288 && [0, 1].includes(saved.collected)) {
      state.x = saved.x; state.collected = saved.collected;
    }
    start.disabled = false;
    draw();
  } catch (error) { status.textContent = 'Storage unavailable; reload to retry.'; console.error(error); }
  start.onclick = async () => {
    try {
      audio ||= new AudioContext();
      await audio.resume();
      state.started = 1; canvas.focus(); draw();
    } catch (error) { status.textContent = 'Audio failed'; console.error(error); }
  };
  document.querySelector('#menu').onclick = async () => {
    try {
      state.menu = await platform.menu();
      document.querySelector('#menu-result').textContent = state.menu;
    } catch (error) { console.error(error); }
  };
  async function act(key) {
    if (!state.started) return;
    if (key === 'ArrowRight' && state.x < 288) state.x += 12;
    if (key === 'ArrowLeft' && state.x > 0) state.x -= 12;
    if (key === ' ' && Math.abs(state.x - 120) <= 12 && !state.collected) {
      state.collected = 1;
      const oscillator = audio.createOscillator(), gain = audio.createGain();
      oscillator.frequency.value = 440; gain.gain.value = 0.15;
      oscillator.connect(gain).connect(audio.destination);
      oscillator.start(); oscillator.stop(audio.currentTime + 0.25); state.sounds++;
    }
    if (key.toLowerCase() === 's' && state.saving !== 1) {
      state.saving = 1; draw();
      try { await platform.save({ x: state.x, collected: state.collected }); state.saving = 0; state.saves++; }
      catch (error) { state.saving = -1; console.error(error); }
    }
    draw();
  }
  canvas.addEventListener('keydown', event => {
    if (['ArrowRight', 'ArrowLeft', ' '].includes(event.key)) event.preventDefault();
    if (!event.repeat) void act(event.key);
  });
  for (const button of document.querySelectorAll('[data-action]')) {
    button.onclick = async () => { await act(button.dataset.action); canvas.focus(); };
  }
})();
