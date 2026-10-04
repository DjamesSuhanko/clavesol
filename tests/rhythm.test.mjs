import assert from 'node:assert/strict';
import {generate,total,label,staffSVG,description} from '../assets/rhythm.mjs';
let seed=1729;
const rng=()=>((seed=(seed*1664525+1013904223)>>>0)/4294967296);
const seen=new Set();
for(let i=0;i<5000;i++){
  const q=generate(rng);
  assert.equal(q.notes.reduce((s,n)=>s+n.ticks,0),total(q.answer));
  assert.equal(q.options.filter(m=>total(m)===total(q.answer)).length,1);
  assert.equal(q.options.length,2);
  assert(q.options.some(m=>label(m)===label(q.answer)));
  assert(q.notes.length>0 && q.notes.length<=12);
  assert(q.notes.every(n=>n.pitch>=0 && n.pitch<=6));
  assert(staffSVG(q.notes).includes('<svg'));
  assert(description(q.notes).length>0);
  seen.add(label(q.answer));
}
assert.equal(seen.size,7);
console.log('Exercícios: 5000 combinações válidas, sem alternativas ambíguas.');
