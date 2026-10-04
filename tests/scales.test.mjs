import assert from 'node:assert/strict';
import {keys,scale,chord,matches} from '../assets/scales.mjs';
for(let k=0;k<keys.length;k++){
 const {notes}=scale(k);assert.equal(notes.length,8);
 assert.deepEqual(notes.slice(1).map((n,i)=>n.midi-notes[i].midi),[2,2,1,2,2,2,1]);
 assert.equal(new Set(notes.slice(0,7).map(n=>n.name.replace(/[♯♭]/g,''))).size,7);
 assert(notes.every(n=>n.midi>=60&&n.midi<=84));
 assert.deepEqual(chord(notes).map(m=>m-notes[0].midi),[0,4,7]);
 notes.forEach((n,i)=>{assert(matches(notes,i,n.midi));assert(!matches(notes,i,n.midi+12));});
 assert(!matches(notes,8,notes[0].midi));
}
assert.deepEqual(scale(2).notes.map(n=>n.name),['Ré','Mi','Fá♯','Sol','Lá','Si','Dó♯','Ré']);
assert(scale(6).notes.some(n=>n.name==='Mi♯'));
assert(scale(7).notes.some(n=>n.name==='Si♯'));
assert(scale(14).notes.some(n=>n.name==='Fá♭'));
console.log('15 escalas maiores: intervalos, grafia, oitavas e acordes corretos.');
