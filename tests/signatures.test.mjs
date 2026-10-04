import assert from 'node:assert/strict';
import {tonalities,positions,expected,grade,rowAt} from '../assets/signatures.mjs';
assert.deepEqual(expected(11).map(e=>positions[e.row][0]),['Si','Mi','Lá','Ré']);
assert.deepEqual(expected(5).map(e=>positions[e.row][0]),['Fá','Dó','Sol','Ré','Lá']);
assert.deepEqual(expected(7).map(e=>e.row),[1,4,0,3,6,2,5]);
assert.deepEqual(expected(14).map(e=>e.row),[5,2,6,3,7,4,8]);
assert.equal(grade(0,[]),'correct');
for(let i=0;i<15;i++){
 const answer=expected(i);assert.equal(answer.length,Math.abs(tonalities[i][1]));assert.equal(grade(i,answer),'correct');
 if(answer.length){assert.equal(grade(i,answer.slice(1)),'count');assert.equal(grade(i,answer.map(e=>({...e,kind:e.kind==='sharp'?'flat':'sharp'}))),'kind');assert.equal(grade(i,answer.map(e=>({...e,row:(e.row+1)%10}))),'position');}
}
for(let i=0;i<10;i++)assert.equal(rowAt(40+i*10),i);
console.log('Armaduras: 15 tonalidades, ordem, tipo e posições validados.');
