// Application-level gzip, for static hosts without configurable encoding headers.
// These .bin responses must NOT themselves carry Content-Encoding: gzip.
(async()=>{
  try{
    if(typeof DecompressionStream!=='function')throw new Error('This browser needs gzip DecompressionStream support. Try the uncompressed build.');
    async function unpack(path){const response=await fetch(path);if(!response.ok)throw new Error(`${path}: HTTP ${response.status}`);const compressed=await response.arrayBuffer();const decoded=new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'));return new Response(decoded).arrayBuffer();}
    const [wasm,js]=await Promise.all([unpack('engine.bin'),unpack('runtime.bin')]);
    Module.wasmBinary=new Uint8Array(wasm);
    Module.locateFile=path=>new URL(path,document.baseURI).href;
    const url=URL.createObjectURL(new Blob([js],{type:'text/javascript'}));
    const script=document.createElement('script');script.src=url;script.onload=()=>URL.revokeObjectURL(url);script.onerror=()=>{URL.revokeObjectURL(url);status.textContent='Game runtime failed to load.';console.error(status.textContent);};document.body.appendChild(script);
  }catch(error){status.textContent='Startup failed: '+error.message;console.error(error);}
})();
