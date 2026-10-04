import assert from 'node:assert/strict';
import {CompassCalculator,fraction} from '../assets/compass.mjs';
const calc=new CompassCalculator();
assert.equal(calc.signature(),null);assert.equal(calc.dot(),false);calc.undo();
for(const rest of [false,true])for(const den of [1,2,4,8,16]){
 calc.clear();calc.add(den,rest);assert.equal(calc.ticks,32/den);
 assert.equal(calc.dot(),true);assert.equal(calc.ticks,48/den);
 assert.equal(calc.dot(),false);assert.equal(calc.ticks,48/den);
 calc.undo();assert.equal(calc.ticks,32/den);assert.equal(calc.dot(),true);
 calc.undo();calc.undo();assert.equal(calc.ticks,0);
}
calc.add(1);assert.deepEqual(calc.signature(),{num:4,den:4});
calc.clear();for(let i=0;i<6;i++)calc.add(8);
assert.deepEqual(calc.signature(),{num:3,den:4});assert.deepEqual(calc.signature(8),{num:6,den:8});
calc.clear();calc.add(16);calc.dot();assert.deepEqual(calc.signature(),{num:3,den:32});
assert.equal(calc.signature(4),null);assert.equal(calc.signature(3),null);
assert.equal(fraction(calc.ticks,32),'3/32');assert.equal(fraction(calc.ticks,8),'3/8');
calc.clear();calc.add(2);calc.add(4,true);assert.deepEqual(calc.signature(),{num:3,den:4});
calc.clear();for(let i=0;i<128;i++)assert.equal(calc.add(16),true);
assert.equal(calc.add(4),false);assert.equal(calc.ticks,256);calc.undo();assert.equal(calc.add(4),true);
assert.equal(calc.add(3),false);assert.equal(fraction(0,32),'0');assert.equal(fraction(32,32),'1');
console.log('Compass: exact sums, notes/rests, dotted values, undo, equivalent units and limits: OK');
