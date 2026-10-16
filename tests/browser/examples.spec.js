const { test, expect } = require('@playwright/test');
for (const example of ['sdl-beacon/build/web']) {
test(`${example}: gameplay, audio, focus, and durable save`, async ({ page, browser }, testInfo) => {
  const logs = [], errors = [];
  page.on('console', message => logs.push(`${message.type()}: ${message.text()}`));
  page.on('pageerror', error => errors.push(error.message));
  page.on('requestfailed', request => errors.push(`${request.url()}: ${request.failure()?.errorText}`));
  page.on('response', response => { if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`); });
  try {
    await page.goto(`/${example}/`);
    await expect(page.getByRole('button', { name: 'Start audio and play' })).toBeEnabled();
    await page.getByRole('button', { name: 'Start audio and play' }).click();
    const startupMs = await page.evaluate(() => performance.now());
    const canvas = page.locator('canvas');
    await expect.poll(() => page.evaluate(() => exampleState().started)).toBe(1);
    await expect.poll(() => page.evaluate(() => exampleState().audioState)).toBe('running');
    for (let i = 0; i < 8; i++) await page.keyboard.press('ArrowRight');
    await expect.poll(() => page.evaluate(() => exampleState().x)).toBe(120);
    // Check pixels from the software SDL renderer, independently of the HUD.
    const pixel = await canvas.evaluate(c => Array.from(c.getContext('2d').getImageData(125, 110, 1, 1).data));
    expect(pixel.slice(0, 3)).toEqual([56, 189, 248]);
    await page.keyboard.press('Space');
    await expect.poll(() => page.evaluate(() => exampleState().collected)).toBe(1);
    await expect.poll(() => page.evaluate(() => exampleState().sounds)).toBe(1);
    await expect(page.locator('#status')).toContainText('Beacon collected');
    await page.keyboard.down('ArrowRight');
    await expect.poll(() => page.evaluate(() => exampleState().x)).toBe(132);
    await page.locator('#start').focus();
    await page.keyboard.up('ArrowRight');
    await canvas.focus();
    await page.waitForTimeout(100);
    expect(await page.evaluate(() => exampleState().x)).toBe(132);
    if (example.startsWith('electron')) {
      await page.locator('#menu').click();
      await expect(page.locator('#menu-result')).toContainText('Continue');
      await canvas.focus();
    }
    await page.keyboard.press('s');
    await expect.poll(() => page.evaluate(() => exampleState().saves)).toBe(1);
    await expect.poll(() => page.evaluate(() => exampleState().saving)).toBe(0);
    const evidence = { browser: browser.version(), startupMs, state: await page.evaluate(() => exampleState()), manualListening: 'untested' };
    await testInfo.attach('gameplay-screenshot', { body: await page.screenshot(), contentType: 'image/png' });
    await page.reload();
    await expect(page.locator('#status')).toContainText('Position 132');
    expect(await page.evaluate(() => exampleState().collected)).toBe(1);
    expect(errors).toEqual([]);
    await testInfo.attach('gameplay-evidence', { body: JSON.stringify(evidence, null, 2), contentType: 'application/json' });
  } finally {
    await testInfo.attach('browser-log', { body: JSON.stringify({ logs, errors }, null, 2), contentType: 'application/json' });
  }
});
}
