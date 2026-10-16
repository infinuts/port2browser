const {test, expect} = require('@playwright/test');
const {PNG} = require('pngjs');
test('Godot native exporter: gameplay, audio and user:// persistence', async ({page,browser},testInfo) => {
  test.setTimeout(90000);
  const errors=[], logs=[], navigationAborts=[];
  let reloading=false;
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',e=>logs.push(`${e.type()}: ${e.text()}`));
  page.on('requestfailed',r=>{
    const failure=`${r.url()}: ${r.failure()?.errorText}`;
    if(reloading && /ERR_ABORTED|NS_BINDING_ABORTED/.test(r.failure()?.errorText || '')) navigationAborts.push(failure);
    else errors.push(failure);
  });
  try {
    await page.goto('/godot-beacon/build/web/');
    await expect(page.locator('#start')).toBeEnabled({timeout:60000});
    await page.locator('#start').click();
    await expect.poll(()=>page.evaluate(()=>exampleState().started)).toBe(1);
    await expect.poll(()=>page.evaluate(()=>exampleState().audioState)).toBe('running');
    for(let i=0;i<8;i++) await page.keyboard.press('ArrowRight');
    await expect.poll(()=>page.evaluate(()=>exampleState().x)).toBe(120);
    // Screenshot reads the rendered WebGL output, without relying on a 2D context.
    // State publication can precede the next WebGL presentation on CI Firefox.
    // Poll the rendered pixel itself; state alone never satisfies this assertion.
    await expect.poll(async()=>{
      const pixels=PNG.sync.read(await page.locator('canvas').screenshot());
      const x=Math.floor(pixels.width*125/320), y=Math.floor(pixels.height*110/180);
      return Array.from(pixels.data.subarray((y*pixels.width+x)*4,(y*pixels.width+x)*4+3));
    },{timeout:10000}).toEqual([56,189,248]);
    await page.keyboard.press('Space');
    await expect.poll(()=>page.evaluate(()=>exampleState().collected)).toBe(1);
    await expect.poll(()=>page.evaluate(()=>exampleState().sounds)).toBe(1);
    await page.keyboard.down('ArrowRight');
    await expect.poll(()=>page.evaluate(()=>exampleState().x)).toBe(132);
    await page.locator('#start').focus(); await page.keyboard.up('ArrowRight');
    await page.locator('canvas').focus();
    await page.waitForTimeout(100);
    expect(await page.evaluate(()=>exampleState().x)).toBe(132);
    await page.keyboard.press('s');
    await expect.poll(()=>page.evaluate(()=>exampleState().saves)).toBe(1);
    // Godot's FileAccess integration batches filesystem flushes. Allow its sync
    // interval, then prove durability with a full engine restart, never the HUD alone.
    await page.waitForTimeout(2000);
    await testInfo.attach('gameplay-screenshot',{body:await page.screenshot(),contentType:'image/png'});
    const state=await page.evaluate(()=>exampleState());
    reloading=true;
    await page.reload();
    await expect(page.locator('#status')).toContainText('Position 132',{timeout:60000});
    expect(await page.evaluate(()=>exampleState().collected)).toBe(1);
    reloading=false;
    expect(errors).toEqual([]);
    await testInfo.attach('gameplay-evidence',{body:JSON.stringify({browser:browser.version(),state,manualListening:'untested'}),contentType:'application/json'});
  } finally {
    await testInfo.attach('browser-log',{body:JSON.stringify({logs,errors,navigationAborts}),contentType:'application/json'});
  }
});
