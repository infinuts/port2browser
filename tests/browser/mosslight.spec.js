const {test,expect}=require('@playwright/test');
const {PNG}=require('pngjs');
const fs=require('node:fs');
for(const variant of ['web','demo']){
 test(`Mosslight ${variant}: explore, hazards, restore lighthouse, compressed parity and durable save`,async({page,browser},testInfo)=>{
  test.setTimeout(90000);
  const errors=[],logs=[],requests=[],navigationAborts=[];const generations=new Map();let generation=0;
  page.on('request',r=>{generations.set(r,generation);requests.push(r.url());});
  page.on('pageerror',e=>errors.push(e.message));page.on('console',e=>logs.push(`${e.type()}: ${e.text()}`));
  page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});
  page.on('requestfailed',r=>{const value=`${r.url()}: ${r.failure()?.errorText}`;if(generations.get(r)<generation&&/^(net::ERR_ABORTED|NS_BINDING_ABORTED)$/.test(r.failure()?.errorText||''))navigationAborts.push(value);else errors.push(value);});
  const state=()=>page.evaluate(()=>mosslightState());
  async function move(key,count){for(let i=0;i<count;i++)await page.keyboard.press(key);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));}
  try{
   await page.goto(`/mosslight/build/${variant}/`);
   await expect(page.locator('#start')).toBeEnabled({timeout:60000});
   const loading=await page.evaluate(()=>({navigation:performance.getEntriesByType('navigation').map(e=>({encodedBodySize:e.encodedBodySize,transferSize:e.transferSize})),resources:performance.getEntriesByType('resource').filter(e=>e.name.startsWith(location.origin)).map(e=>({url:e.name,encodedBodySize:e.encodedBodySize,decodedBodySize:e.decodedBodySize,transferSize:e.transferSize})),readyMs:performance.now()}));
   if(variant==='demo'){
    const manifest=JSON.parse(fs.readFileSync('examples/mosslight/build/demo/size-report.json'));
    for(const file of ['engine.bin','runtime.bin']){
     const entry=loading.resources.find(e=>e.url.endsWith('/'+file));expect(entry).toBeTruthy();expect(entry.encodedBodySize).toBe(manifest.packed_files[file].bytes);
    }
    expect(requests.some(url=>/\/index\.(js|wasm)$/.test(url))).toBe(false);
   }
   await page.locator('#start').click();await expect.poll(async()=>(await state()).started).toBe(1);await expect.poll(async()=>(await state()).audioState).toBe('running');
   await move('ArrowRight',3);await expect.poll(async()=>(await state()).x).toBe(5);await page.keyboard.press('Space');await expect.poll(async()=>(await state()).mask).toBe(1);
   await move('ArrowRight',3);await expect.poll(async()=>(await state()).health).toBe(2);expect((await state()).x).toBe(2);expect((await state()).mask).toBe(1);
   // Wall at 3,9: the eastward move is blocked, preserving position.
   await move('ArrowUp',2);await move('ArrowRight',1);await expect.poll(async()=>(await state()).x).toBe(2);expect((await state()).y).toBe(9);
   await move('ArrowDown',2);await move('ArrowRight',3);await move('ArrowUp',7);await move('ArrowRight',7);await page.keyboard.press('Space');await expect.poll(async()=>(await state()).mask).toBe(3);
   await move('ArrowRight',8);await move('ArrowDown',6);await page.keyboard.press('Space');await expect.poll(async()=>(await state()).mask).toBe(7);
   await move('ArrowUp',8);await move('ArrowRight',1);await page.keyboard.press('Space');await expect.poll(async()=>(await state()).won).toBe(1);
   await expect(page.locator('#hint')).toContainText('You brought the light home');await expect.poll(async()=>(await state()).saving).toBe(0);expect((await state()).saves).toBe(1);expect((await state()).sounds).toBe(5);
   await testInfo.attach('gameplay-screenshot',{body:await page.screenshot({fullPage:true}),contentType:'image/png'});
   const beforeReload=await state();generation++;await page.reload();await expect(page.locator('#start')).toBeEnabled({timeout:60000});
   const restored=await state();expect(restored).toMatchObject({x:21,y:2,mask:7,health:2,won:1});
   await page.locator('#start').click();
   await expect.poll(async()=>{const pixels=PNG.sync.read(await page.locator('canvas').screenshot());const x=Math.floor(pixels.width*(21*32+16)/768),y=Math.floor(pixels.height*(2*32+20)/448);return Array.from(pixels.data.subarray((y*pixels.width+x)*4,(y*pixels.width+x)*4+3));},{timeout:10000}).toEqual([41,196,190]);
   await page.locator('#reset').click();await expect.poll(async()=>(await state()).mask).toBe(0);await expect.poll(async()=>(await state()).saving).toBe(0);
   await page.keyboard.down('ArrowRight');await expect.poll(async()=>(await state()).x>2).toBe(true);await page.locator('#resume').focus();await page.keyboard.up('ArrowRight');const stopped=(await state()).x;await page.waitForTimeout(400);expect((await state()).x).toBe(stopped);
   expect(errors).toEqual([]);expect(requests.filter(url=>/^https?:/.test(url)&&!url.startsWith('http://127.0.0.1:8765/'))).toEqual([]);
   await testInfo.attach('gameplay-evidence',{body:JSON.stringify({variant,browser:browser.version(),loading,beforeReload,restored,manualListening:'untested',peakMemory:'untested'}),contentType:'application/json'});
  }finally{await testInfo.attach('browser-log',{body:JSON.stringify({logs,errors,navigationAborts,requests}),contentType:'application/json'});}
 });
}
test('Mosslight rejects a corrupt compressed game instead of reporting ready',async({page})=>{
 await page.route('**/engine.bin',route=>route.fulfill({status:200,contentType:'application/octet-stream',body:'not gzip'}));
 await page.goto('/mosslight/build/demo/');await expect(page.locator('#status')).toContainText('Startup failed');await expect(page.locator('#start')).toBeDisabled();expect(await page.evaluate(()=>mosslightState())).toEqual({ready:false});
});
