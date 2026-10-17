const {test}=require('node:test');
const assert=require('node:assert/strict');
const {validatePlan}=require('../../skills/port2browser-verify/scripts/verify.cjs');
const base=require('./electron-keyboard.json');
test('keyboard and touch plans are valid',()=>{
  validatePlan(structuredClone(base));validatePlan(require('./electron-touch.json'));
});
test('typos and unsafe observer paths cannot silently weaken a plan',()=>{
  for(const change of [p=>p.typo=true,p=>p.state.path='window.constructor',p=>p.steps[0].ignored=true,
    p=>p.steps[1].values={},p=>p.steps[2].count=1000000,p=>p.required=['unknown'],
    p=>p.steps.push({action:'evaluate',source:'arbitrary JS'}),p=>p.steps.push({action:'reload',preserve:[]})]) {
    const plan=structuredClone(base);change(plan);assert.throws(()=>validatePlan(plan));
  }
});
test('pixel and timeout budgets are bounded',()=>{
  for(const step of [{action:'pixel',point:[1,0],rgb:[0,0,0]}, {action:'audio',min_starts:0}])
    assert.throws(()=>validatePlan({...structuredClone(base),steps:[step]}));
  assert.throws(()=>validatePlan({...structuredClone(base),frame_samples:1000000}));
  assert.throws(()=>validatePlan({...structuredClone(base),timeout_ms:0}));
});
