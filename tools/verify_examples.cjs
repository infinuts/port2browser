// Regression runner for the reusable optional helper, not a general game grader.
const fs=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
const {verifyTarget}=require('../skills/port2browser-verify/scripts/verify.cjs');
(async()=>{
  const [url,output]=process.argv.slice(2);
  const jobs=[['chromium',null,'keyboard'],['firefox',null,'keyboard'],['webkit',null,'keyboard'],
    ['chromium','Pixel 7','touch'],['webkit','iPhone 13','touch']];
  const results=[];
  for(const [browser,device,kind] of jobs) {
    const name=browser+'-'+(device?device.toLowerCase().replaceAll(' ','-'):'desktop');
    const plan=JSON.parse(await fs.readFile(path.join(__dirname,`../tests/verification/electron-${kind}.json`),'utf8'));
    const report=await verifyTarget({url:url+'/electron-beacon/web/',plan,browser,device,output:path.join(output,name)});
    results.push({name,result:report.result,browser_version:report.browser_version,evidence:`${name}/evidence.json`});
    console.log(name,report.result,report.error||report.reason||'');
  }
  // A visible but uniformly blank canvas must fail even with a cooperative state API.
  const blank={schema_version:1,state:{path:'exampleState',call:true},canvas:'canvas',required:['render'],
    frame_samples:0,steps:[{action:'canvas'}]};
  const bad=await verifyTarget({url:url+'/blank/',plan:blank,browser:'chromium',output:path.join(output,'negative-blank')});
  assert.equal(bad.result,'fail');assert.match(bad.error,/uniform\/blank/);
  const wrong=JSON.parse(await fs.readFile(path.join(__dirname,'../tests/verification/electron-keyboard.json'),'utf8'));
  wrong.timeout_ms=200;wrong.steps=[{action:'expect',values:{x:999}}];
  const state=await verifyTarget({url:url+'/electron-beacon/web/',plan:wrong,browser:'chromium',output:path.join(output,'negative-state')});
  assert.equal(state.result,'fail');assert.match(state.error,/state.x/);
  const {spawnSync}=require('node:child_process');
  const unavailable=spawnSync(process.execPath,[path.join(__dirname,'../skills/port2browser-verify/scripts/verify.cjs'),
    '--url',url+'/electron-beacon/web/','--plan',path.join(__dirname,'../tests/verification/electron-keyboard.json'),
    '--output',path.join(output,'negative-missing-browser')],{env:{...process.env,PLAYWRIGHT_BROWSERS_PATH:path.join(output,'empty-browser-cache')},encoding:'utf8'});
  assert.equal(unavailable.status,2,unavailable.stderr);
  const missing=JSON.parse(await fs.readFile(path.join(output,'negative-missing-browser/evidence.json'),'utf8'));
  assert.equal(missing.result,'untested');
  await fs.writeFile(path.join(output,'summary.json'),JSON.stringify({schema_version:1,results,negative_tests:{blank_canvas:bad.result,wrong_state:state.result,missing_browser:missing.result},
    limitations:['Physical devices, shipping Safari and manual listening remain untested.','These results cover this original Electron game only, not every engine or mobile game.']},null,2)+'\n');
  process.exitCode=results.every(r=>r.result==='pass')?0:1;
})().catch(error=>{console.error(error);process.exitCode=1;});
