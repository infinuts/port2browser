/* Observe Lua's journal and await explicit IDBFS commits; do not edit gameplay state. */
const canvas=document.querySelector('canvas'),button=document.querySelector('#start');
let saving=false,committed=0,failed=false;
var Module={arguments:['./'],INITIAL_MEMORY:33554432,canvas,print:console.log.bind(console),printErr:console.error.bind(console),
  onRuntimeInitialized(){button.disabled=false;document.querySelector('#status').textContent='Ready; activate audio and press Enter';}};
function observed(){
  try{return JSON.parse(Module.FS_readFile('/home/web_user/love/port2browser-love-beacon/observed.json',{encoding:'utf8'}));}
  catch{return {ready:0};}
}
window.exampleState=()=>{
  const state=observed();
  return {...state,ready:state.x===undefined?0:1,saves:committed,saving:failed?-1:(saving||(state.saves||0)>committed?1:0)};
};
button.onclick=async()=>{await Module.p2bResumeAudio();canvas.focus();};
setInterval(()=>{
  const state=observed();
  if(!failed&&!saving&&state.saves>committed) {
    saving=true;const requested=state.saves;
    Module.FS_syncfs(false,error=>{saving=false;if(error){failed=true;console.error(error);}else committed=requested;});
  }
},50);
canvas.addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','Space'].includes(event.code))event.preventDefault();});
