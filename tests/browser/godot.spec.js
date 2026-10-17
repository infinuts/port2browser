const {test, expect} = require('@playwright/test');
const {PNG} = require('pngjs');
test('Godot native exporter: gameplay, audio and user:// persistence', async ({page,browser},testInfo) => {
  test.setTimeout(90000);
  const errors=[], logs=[], navigationAborts=[], wasmStreamCancellations=[];
  const responses=new Map(), requestGenerations=new Map();
  let generation=0;
  page.on('request',request=>requestGenerations.set(request,generation));
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',e=>logs.push(`${e.type()}: ${e.text()}`));
  page.on('response',response=>{
    responses.set(response.request(),response);
    if(response.status()>=400) errors.push(`${response.status()} ${response.url()}`);
  });
  page.on('requestfailed',request=>{
    const failure=`${request.url()}: ${request.failure()?.errorText}`;
    const aborted=/^(net::ERR_ABORTED|NS_BINDING_ABORTED)$/.test(request.failure()?.errorText || '');
    const response=responses.get(request);
    // Godot 4.5.1 clones its streaming Wasm response before instantiation.
    // Chromium can report cancellation of that stream even after HTTP 200.
    // Keep this evidence separate: only this exact asset/MIME/status/abort is
    // eligible, and the assertions below still require a running, rendered
    // engine before AND after reload. Other transport and HTTP failures fail.
    // Failed events from the old document can arrive after the new engine is
    // ready. Attribute requests to their document, not to a transient flag.
    if(aborted && requestGenerations.get(request)<generation) {
      navigationAborts.push({url:request.url(),error:request.failure().errorText,generation:requestGenerations.get(request)});
    } else if(aborted && new URL(request.url()).pathname==='/godot-beacon/build/web/index.wasm' &&
       response?.status()===200 && response.headers()['content-type']?.split(';')[0]==='application/wasm') {
      wasmStreamCancellations.push({url:request.url(),status:response.status(),error:request.failure().errorText,generation:requestGenerations.get(request)});
    } else errors.push(failure);
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
    generation++;
    await page.reload();
    await expect(page.locator('#status')).toContainText('Position 132',{timeout:60000});
    expect(await page.evaluate(()=>exampleState().collected)).toBe(1);
    await expect.poll(async()=>{
      const pixels=PNG.sync.read(await page.locator('canvas').screenshot());
      const x=Math.floor(pixels.width*137/320), y=Math.floor(pixels.height*110/180);
      return Array.from(pixels.data.subarray((y*pixels.width+x)*4,(y*pixels.width+x)*4+3));
    },{timeout:10000}).toEqual([56,189,248]);
    expect(errors).toEqual([]);
    await testInfo.attach('gameplay-evidence',{body:JSON.stringify({browser:browser.version(),state,manualListening:'untested'}),contentType:'application/json'});
  } finally {
    await testInfo.attach('browser-log',{body:JSON.stringify({logs,errors,navigationAborts,wasmStreamCancellations}),contentType:'application/json'});
  }
});
