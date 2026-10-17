// Independent behavioral grader; never copied into an agent's input workspace.
const { chromium, firefox } = require('playwright');
(async () => {
  const results = [];
  for (const [name, type] of [['chromium', chromium], ['firefox', firefox]]) {
    let browser;
    const errors = [];
    try {
      browser = await type.launch();
      const page = await browser.newPage();
      page.setDefaultTimeout(5000);
      page.on('pageerror', error => errors.push(error.message));
      page.on('requestfailed', r => errors.push(r.url()));
      await page.goto(process.argv[2], {timeout:10000});
      await page.locator('#start').click({timeout:5000});
      await page.waitForFunction(() => window.exampleState?.().started === 1, {timeout:5000});
      for (let i=0; i<8; i++) await page.keyboard.press('ArrowRight');
      await page.waitForFunction(() => exampleState().x === 120);
      const rgb = await page.locator('canvas').evaluate(c => Array.from(c.getContext('2d').getImageData(125,110,1,1).data).slice(0,3));
      if (JSON.stringify(rgb) !== '[56,189,248]') throw new Error('Player not drawn at observed position');
      await page.keyboard.press('Space');
      await page.waitForFunction(() => exampleState().collected === 1 && exampleState().sounds === 1 && exampleState().audioState === 'running');
      await page.locator('#menu').click();
      if (!(await page.locator('#menu-result').innerText()).includes('Continue')) throw new Error('Menu broken');
      await page.locator('canvas').focus();
      await page.keyboard.press('s');
      await page.waitForFunction(() => exampleState().saves === 1 && exampleState().saving === 0);
      await page.reload();
      await page.waitForFunction(() => exampleState().x === 120 && exampleState().collected === 1);
      if (errors.length) throw new Error(errors.join('\n'));
      results.push({browser:name, version:browser.version(), result:'pass'});
    } catch(error) { results.push({browser:name,result:'fail',error:String(error),errors}); }
    finally { await browser?.close(); }
  }
  console.log(JSON.stringify(results));
})().catch(error => { console.error(error); process.exit(1); });
