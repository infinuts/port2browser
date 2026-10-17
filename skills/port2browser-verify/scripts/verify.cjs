#!/usr/bin/env node
'use strict';
// Optional dependency: caller-provided Playwright + pngjs. Never installs tools.
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');

const ACTIONS = new Set(['click','tap','press','down','up','focus','expect','text','canvas','pixel','audio','reload','capture']);
const PATH = /^[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*$/;
function validPath(value) {
  return typeof value === 'string' && PATH.test(value) && !value.split('.').some(p => ['__proto__','prototype','constructor'].includes(p));
}
function validatePlan(plan) {
  assert.equal(plan.schema_version, 1, 'schema_version must be 1');
  for (const key of Object.keys(plan)) assert(['schema_version','state','canvas','steps','required','timeout_ms','frame_samples'].includes(key), `unknown plan field: ${key}`);
  assert(plan.state && validPath(plan.state.path), 'state.path must be a safe dotted property path');
  assert(typeof plan.state.call === 'boolean', 'state.call must be explicit');
  assert(Object.keys(plan.state).every(k=>['path','call'].includes(k)), 'unknown state descriptor field');
  assert(typeof plan.canvas === 'string' && plan.canvas.length, 'canvas selector required');
  assert(Array.isArray(plan.steps) && plan.steps.length > 0 && plan.steps.length <= 500, '1..500 steps required');
  const fields = {
    click:['selector'],tap:['selector'],focus:['selector'],press:['key','count'],down:['key'],up:['key'],
    expect:['values'],text:['selector','contains'],canvas:['selector'],pixel:['selector','point','rgb','tolerance'],
    audio:['min_starts'],reload:['preserve'],capture:[]
  };
  for (const step of plan.steps) {
    assert(step && ACTIONS.has(step.action), 'unknown action');
    for (const key of Object.keys(step)) assert(['action',...fields[step.action]].includes(key), `unknown ${step.action} field: ${key}`);
    for (const key of ['selector','key','contains']) if (fields[step.action].includes(key) && !(step.action==='canvas' || step.action==='pixel') ) assert(typeof step[key]==='string' && step[key].length, `${key} required`);
    if (step.selector !== undefined) assert(typeof step.selector==='string' && step.selector.length, 'selector must be nonempty');
    if (step.count !== undefined) assert(Number.isInteger(step.count) && step.count>=1 && step.count<=1000, 'count must be 1..1000');
    if (step.action==='expect') {
      assert(step.values && Object.keys(step.values).length, 'nonempty expected state required');
      for (const key of Object.keys(step.values)) assert(validPath(key), 'invalid expected state path');
    }
    if (step.action==='reload') assert(Array.isArray(step.preserve) && step.preserve.length && step.preserve.every(validPath), 'reload.preserve requires state paths');
    if (step.action==='audio') assert(Number.isInteger(step.min_starts) && step.min_starts>0, 'audio.min_starts must be positive');
    if (step.action==='pixel') {
      assert(Array.isArray(step.point) && step.point.length===2 && step.point.every(n=>Number.isFinite(n)&&n>=0&&n<1), 'normalized pixel point required');
      assert(Array.isArray(step.rgb) && step.rgb.length===3 && step.rgb.every(n=>Number.isInteger(n)&&n>=0&&n<=255), 'RGB required');
      if(step.tolerance!==undefined) assert(Number.isFinite(step.tolerance)&&step.tolerance>=0&&step.tolerance<=255, 'invalid tolerance');
    }
  }
  if(plan.timeout_ms!==undefined) assert(Number.isInteger(plan.timeout_ms)&&plan.timeout_ms>=100&&plan.timeout_ms<=30000, 'timeout must be 100..30000 ms');
  if(plan.frame_samples!==undefined) assert(Number.isInteger(plan.frame_samples)&&plan.frame_samples>=0&&plan.frame_samples<=300, 'frame_samples must be 0..300');
  const required=plan.required || ['input','render','state','audio','focus','reload'];
  assert(Array.isArray(required) && required.every(v=>['input','render','state','audio','focus','reload'].includes(v)), 'unknown required category');
  return plan;
}

function installObservers() {
  const observations={contexts:[], starts:0};
  Object.defineProperty(window,'__port2browserAudio',{value:observations});
  for(const name of ['AudioContext','webkitAudioContext']) {
    const Original=window[name];
    if(Original) window[name]=new Proxy(Original,{construct(target,args,newTarget) {
      const instance=Reflect.construct(target,args,newTarget);
      observations.contexts.push(instance);return instance;
    }});
  }
  for(const name of ['AudioBufferSourceNode','OscillatorNode']) {
    const prototype=window[name]?.prototype;
    if(prototype?.start) {
      const original=prototype.start;
      prototype.start=function(...args) { const result=original.apply(this,args);observations.starts++;return result; };
    }
  }
}

async function readState(page, descriptor) {
  return page.evaluate(async ({path,call})=>{
    let value=window, owner=window;
    for(const part of path.split('.')) { owner=value;value=value?.[part]; }
    if(call) { if(typeof value!=='function') throw Error('state observer unavailable'); value=await value.call(owner); }
    const text=JSON.stringify(value);
    if(text===undefined || text.length>1024*1024) throw Error('state must serialize within 1 MiB');
    return JSON.parse(text);
  },descriptor);
}
function at(value, key) {
  for(const part of key.split('.')) {
    if(value===null || value===undefined || !Object.hasOwn(value,part)) throw Error(`missing observed state: ${key}`);
    value=value[part];
  }
  return value;
}
async function poll(check, timeout) {
  const deadline=Date.now()+timeout;let error;
  do { try { return await check(); } catch(e) { error=e; } await new Promise(resolve=>setTimeout(resolve,40)); } while(Date.now()<deadline);
  throw error;
}
async function profile(page, samples) {
  return page.evaluate(async samples=>{
    const navigation=performance.getEntriesByType('navigation')[0];
    const resources=performance.getEntriesByType('resource');
    const result={navigation:navigation?{dom_content_loaded_ms:navigation.domContentLoadedEventEnd,load_ms:navigation.loadEventEnd}:null,
      resources:{count:resources.length,transfer_bytes:resources.reduce((n,r)=>n+r.transferSize,0),encoded_bytes:resources.reduce((n,r)=>n+r.encodedBodySize,0)},
      frame_callback_intervals:{status:'untested',samples:0}};
    if(!samples) return result;
    const times=[];let previous,done=false;
    await new Promise(resolve=>{
      const deadline=setTimeout(()=>{done=true;resolve();},6000);
      function frame(now) {
        if(done)return;
        if(previous!==undefined) times.push(now-previous);
        previous=now;
        if(times.length>=samples){done=true;clearTimeout(deadline);resolve();} else requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    });
    times.sort((a,b)=>a-b);
    result.frame_callback_intervals=times.length?{status:'measured',samples:times.length,
      p50_ms:times[Math.floor((times.length-1)*0.5)],p95_ms:times[Math.floor((times.length-1)*0.95)],max_ms:times.at(-1)}:
      {status:'untested',samples:0,reason:'no frame callbacks before deadline'};
    return result;
  },samples);
}

async function verifyPage(page, url, plan, output) {
  validatePlan(plan);
  const timeout=plan.timeout_ms || 5000;
  page.setDefaultTimeout(timeout);
  page.setDefaultNavigationTimeout(30000);
  const report={schema_version:1,url,plan_sha256:crypto.createHash('sha256').update(JSON.stringify(plan)).digest('hex'),
    result:'fail',coverage:Object.fromEntries(['input','render','state','audio','focus','reload'].map(k=>[k,'untested'])),
    steps:[],logs:[],errors:[],events_omitted:0,manual_listening:'untested',limitations:[
      'Configured checks only; passing does not establish full game playability or engine compatibility.',
      'Frame callback intervals are not GPU/game frame times. Transfer sizes may be zero for cache/opaque resources.',
      'Web Audio instrumentation observes contexts and oscillator/buffer starts; it is not audible-output measurement.',
      'Device profiles emulate browser parameters, not physical phones or shipping Safari.']};
  const append=(list,value)=>{ if(list.length<200)list.push(value);else report.events_omitted++; };
  page.on('console',message=>{append(report.logs,{type:message.type(),text:message.text()});if(message.type()==='error')append(report.errors,message.text());});
  page.on('pageerror',error=>append(report.errors,String(error)));
  page.on('requestfailed',request=>append(report.errors,`${request.url()}: ${request.failure()?.errorText}`));
  page.on('response',response=>{if(response.status()>=400)append(report.errors,`${response.status()} ${response.url()}`);});
  await fs.mkdir(output,{recursive:true});
  await page.addInitScript(installObservers);
  const started=Date.now();
  try {
    await page.goto(url,{waitUntil:'load'});
    report.navigation_wall_ms=Date.now()-started;
    const {PNG}=require('pngjs');
    for(const [index,step] of plan.steps.entries()) {
      const row={index,action:step.action,result:'fail'};report.steps.push(row);
      const selector=step.selector || plan.canvas;
      if(['click','tap'].includes(step.action)) {await page.locator(selector)[step.action]();report.coverage.input='pass';}
      if(['press','down','up'].includes(step.action)) {
        for(let i=0;i<(step.count||1);i++)await page.keyboard[step.action](step.key);
        report.coverage.input='pass';
      }
      if(step.action==='focus') {
        await page.locator(selector).focus();
        row.active_element=await page.evaluate(()=>({tag:document.activeElement.tagName,id:document.activeElement.id}));
        assert.equal(await page.locator(plan.canvas).evaluate(c=>c===document.activeElement),false,'canvas retained focus');
        row.scope='element focus loss';report.coverage.focus='pass';
      }
      if(step.action==='expect') {
        row.state=await poll(async()=>{
          const state=await readState(page,plan.state);
          for(const [key,value] of Object.entries(step.values))assert.deepEqual(at(state,key),value,`state.${key}`);
          return state;
        },timeout);report.coverage.state='pass';
      }
      if(step.action==='text') await poll(async()=>assert((await page.locator(selector).innerText()).includes(step.contains),'expected visible text'),timeout);
      if(['canvas','pixel'].includes(step.action)) {
        const screenshot=await page.locator(selector).screenshot();
        const png=PNG.sync.read(screenshot);
        const pixel=(x,y)=>Array.from(png.data.subarray((y*png.width+x)*4,(y*png.width+x)*4+4));
        if(step.action==='canvas') {
          const colors=new Set();
          for(let y=0;y<png.height;y+=Math.max(1,Math.floor(png.height/32)))for(let x=0;x<png.width;x+=Math.max(1,Math.floor(png.width/32)))colors.add(pixel(x,y).join(','));
          row.sample_colors=colors.size;assert(colors.size>=2,'canvas screenshot is uniform/blank');
        } else {
          row.pixel=pixel(Math.floor(step.point[0]*png.width),Math.floor(step.point[1]*png.height));
          for(let c=0;c<3;c++)assert(Math.abs(row.pixel[c]-step.rgb[c])<=(step.tolerance||0),'rendered pixel mismatch');
        }
        row.screenshot=`step-${index}.png`;await fs.writeFile(path.join(output,row.screenshot),screenshot);
        report.coverage.render='pass';
      }
      if(step.action==='audio') {
        row.audio=await poll(async()=>{
          const audio=await page.evaluate(()=>({states:window.__port2browserAudio.contexts.map(c=>c.state),starts:window.__port2browserAudio.starts}));
          assert(audio.states.includes('running'),'no running observed Web Audio context');
          assert(audio.starts>=step.min_starts,'no required sound starts');return audio;
        },timeout);report.coverage.audio='pass';
      }
      if(step.action==='reload') {
        const before=await readState(page,plan.state);
        row.before=Object.fromEntries(step.preserve.map(k=>[k,at(before,k)]));
        await page.reload({waitUntil:'load'});
        row.after=await poll(async()=>{
          const after=await readState(page,plan.state);
          for(const key of step.preserve)assert.deepEqual(at(after,key),row.before[key],`restored ${key}`);
          return Object.fromEntries(step.preserve.map(k=>[k,at(after,k)]));
        },timeout);report.coverage.reload='pass';
      }
      if(step.action==='capture') {row.screenshot=`step-${index}.png`;await page.screenshot({path:path.join(output,row.screenshot)});}
      row.result='pass';
    }
    report.performance=await profile(page,plan.frame_samples===undefined?60:plan.frame_samples);
    for(const required of plan.required || Object.keys(report.coverage))assert.equal(report.coverage[required],'pass',`required ${required} check missing`);
    assert.equal(report.errors.length,0,'browser errors recorded');
    assert.equal(report.events_omitted,0,'event evidence cap exceeded');
    report.result='pass';
  } catch(error) {
    report.error=String(error);
    await page.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});
  }
  report.elapsed_ms=Date.now()-started;
  await fs.writeFile(path.join(output,'evidence.json'),JSON.stringify(report,null,2)+'\n');
  return report;
}

async function verifyTarget({url,plan,browser='chromium',device,output,headless=true}) {
  validatePlan(plan);
  assert(['http:','https:'].includes(new URL(url).protocol),'URL must be HTTP(S)');
  let playwright;
  try { playwright=require('playwright');require('pngjs'); }
  catch(error) {
    const report={schema_version:1,url,result:'untested',reason:`Optional browser dependencies unavailable: ${error}`,physical_device:'untested',shipping_safari:'untested'};
    await fs.mkdir(output,{recursive:true});await fs.writeFile(path.join(output,'evidence.json'),JSON.stringify(report,null,2)+'\n');return report;
  }
  assert(['chromium','firefox','webkit'].includes(browser),'unknown browser');
  if(device)assert(playwright.devices[device],'unknown device profile');
  let instance;
  try { instance=await playwright[browser].launch({headless}); }
  catch(error) {
    const report={schema_version:1,browser,device:device||null,result:'untested',reason:String(error),physical_device:'untested',shipping_safari:'untested'};
    await fs.mkdir(output,{recursive:true});await fs.writeFile(path.join(output,'evidence.json'),JSON.stringify(report,null,2)+'\n');return report;
  }
  let context;
  try {
    const options=device?{...playwright.devices[device]}:{};delete options.defaultBrowserType;
    try { context=await instance.newContext(options); }
    catch(error) {
      const report={schema_version:1,url,browser,device:device||null,result:'untested',reason:`Browser context unavailable: ${error}`,physical_device:'untested',shipping_safari:'untested'};
      await fs.mkdir(output,{recursive:true});await fs.writeFile(path.join(output,'evidence.json'),JSON.stringify(report,null,2)+'\n');return report;
    }
    const page=await context.newPage();
    const report=await verifyPage(page,url,plan,output);
    Object.assign(report,{browser,browser_version:instance.version(),playwright_version:require('playwright/package.json').version,
      node_version:process.version,os:process.platform,os_release:require('node:os').release(),architecture:process.arch,date:new Date().toISOString(),device:device||null,physical_device:'untested',shipping_safari:'untested'});
    await fs.writeFile(path.join(output,'evidence.json'),JSON.stringify(report,null,2)+'\n');
    await context.close();return report;
  } finally { await instance.close(); }
}

async function main(args=process.argv.slice(2)) {
  const options={};
  for(let i=0;i<args.length;i++) {
    const key=args[i];assert(['--url','--plan','--output','--browser','--device','--headed'].includes(key),`unknown option: ${key}`);
    options[key]=key==='--headed'?true:args[++i];
  }
  assert(options['--url']&&options['--plan']&&options['--output'],'Usage: node verify.cjs --url URL --plan JSON --output NEW_DIRECTORY [--browser chromium|firefox|webkit] [--device NAME] [--headed]');
  const output=path.resolve(options['--output']);
  await fs.mkdir(output,{recursive:false}); // Never overwrite an evidence run.
  const plan=JSON.parse(await fs.readFile(options['--plan'],'utf8'));
  const report=await verifyTarget({url:options['--url'],plan,output,browser:options['--browser']||'chromium',device:options['--device'],headless:!options['--headed']});
  console.log(JSON.stringify({result:report.result,evidence:path.join(output,'evidence.json')}));
  return report.result==='pass'?0:report.result==='untested'?2:1;
}
module.exports={validatePlan,readState,verifyPage,verifyTarget,main};
if(require.main===module)main().then(code=>{process.exitCode=code;}).catch(error=>{console.error(String(error));process.exitCode=2;});
