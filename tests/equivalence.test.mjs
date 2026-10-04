import assert from 'node:assert/strict';
import {generate,grade,duration} from '../assets/equivalence.mjs';
assert.equal(grade([8,8],[4]),'correct');
assert.equal(grade([2,4,4],[1]),'correct');
assert.equal(grade([2,4,4],[4,2,4]),'copy');
assert.equal(grade([2,4,4],[4,4,4,4]),'correct');
assert.equal(grade([4,4],[4]),'short');
assert.equal(grade([4,4],[1]),'long');
assert.equal(grade([4,4],[]),'empty');
assert.equal(grade([4,4],[0]),'invalid');
let seed=123;const rng=()=>((seed=(seed*1664525+1013904223)>>>0)/4294967296);
const kinds=new Set(),totals=new Set();
for(let i=0;i<5000;i++){
 const q=generate(rng),single=16/duration(q.figures);
 assert(q.figures.length>=2&&q.figures.length<=6);
 assert([1,2,4,8].includes(single));
 assert.equal(grade(q.figures,[single]),'correct');
 assert.equal(grade(q.figures,[...q.figures].reverse()),'copy');
 kinds.add(q.rest);totals.add(single);
}
assert.equal(kinds.size,2);assert.equal(totals.size,4);
console.log('Correspondência: 5000 grupos solucionáveis; cópias e reordenações rejeitadas.');
