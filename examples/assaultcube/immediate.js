// Adapt legacy current attributes to Emscripten's per-vertex immediate buffer.
addToLibrary({
  glColor4f: (r,g,b,a) => { GLImmediate.clientColor.set([r,g,b,a].map(v=>Math.max(0,Math.min(1,v)))); },
  glTexCoord2i: (u,v) => { GLImmediate.acTexCoord=[u,v]; },
  glVertex4f: (x,y,z,w) => {
    const p=GLImmediate.vertexCounter*4,c=GLImmediate.clientColor,t=GLImmediate.acTexCoord||[0,0];
    for(let i=0;i<4;i++)GLImmediate.vertexDataU8[p+i]=Math.round(c[i]*255);
    GLImmediate.vertexCounter++;
    GLImmediate.addRendererComponent(GLImmediate.COLOR,4,GLctx.UNSIGNED_BYTE);
    GLImmediate.vertexData[GLImmediate.vertexCounter++]=t[0];
    GLImmediate.vertexData[GLImmediate.vertexCounter++]=t[1];
    GLImmediate.addRendererComponent(GLImmediate.TEXTURE0,2,GLctx.FLOAT);
    for(const v of [x,y,z,w])GLImmediate.vertexData[GLImmediate.vertexCounter++]=v;
    GLImmediate.addRendererComponent(GLImmediate.VERTEX,4,GLctx.FLOAT);
  },
  glVertex2f__deps:['glVertex4f'],
  glVertex2f:(x,y)=>_glVertex4f(x,y,0,1),
  glVertex3f__deps:['glVertex4f'],
  glVertex3f:(x,y,z)=>_glVertex4f(x,y,z,1)
});
