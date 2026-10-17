(()=>{
/* Browser platform boundary: actual Rust state/renderer, Web Audio and awaited IndexedDB commits. */
let audio, restored={x:24,collected:0};
const canvas=document.querySelector('canvas'), start=document.querySelector('#start');
const database=new Promise((resolve,reject)=>{
  const request=indexedDB.open('port2browser-macroquad-beacon',1);
  request.onupgradeneeded=()=>request.result.createObjectStore('saves');
  request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error);
});
async function storage(mode,value) {
  const db=await database;
  return new Promise((resolve,reject)=>{
    const tx=db.transaction('saves',mode),store=tx.objectStore('saves');
    const request=mode==='readonly'?store.get('beacon'):store.put(value,'beacon');
    tx.oncomplete=()=>resolve(request.result);tx.onabort=()=>reject(tx.error);tx.onerror=()=>reject(tx.error);
  });
}
window.exampleState=()=>typeof wasm_exports?.p2b_x==='function'?{
  ready:1,x:wasm_exports.p2b_x(),collected:wasm_exports.p2b_collected(),started:wasm_exports.p2b_started(),
  sounds:wasm_exports.p2b_sounds(),saving:wasm_exports.p2b_saving(),saves:wasm_exports.p2b_saves(),audioState:audio?.state||'unavailable'
}:{ready:0};
miniquad_add_plugin({name:'beacon_platform',version:1,register_plugin(imports) {
  imports.env.p2b_load_x=()=>restored.x;
  imports.env.p2b_load_collected=()=>restored.collected;
  imports.env.p2b_sound=()=>{
    const oscillator=audio.createOscillator(),gain=audio.createGain();
    oscillator.frequency.value=440;gain.gain.value=.15;
    oscillator.connect(gain).connect(audio.destination);oscillator.start();oscillator.stop(audio.currentTime+.2);
  };
  imports.env.p2b_save=(x,collected)=>{storage('readwrite',{x,collected}).then(()=>wasm_exports.p2b_saved(1),error=>{wasm_exports.p2b_saved(0);console.error(error);});};
},on_init(){start.disabled=false;document.querySelector('#status').textContent='Ready';}});
start.onclick=async()=>{audio ||= new AudioContext();await audio.resume();wasm_exports.p2b_start();canvas.focus();};
for(const key of ['ArrowLeft','ArrowRight','Space']) canvas.addEventListener('keydown',event=>{if(event.code===key)event.preventDefault();});
storage('readonly').then(value=>{
  if(value&&Number.isInteger(value.x)&&value.x>=0&&value.x<=288&&[0,1].includes(value.collected))restored=value;
  load('macroquad-beacon.wasm');
}).catch(error=>{document.querySelector('#status').textContent='Storage unavailable';console.error(error);});

})();
