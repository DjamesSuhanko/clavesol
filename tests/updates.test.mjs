import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
const code=readFileSync(new URL('../assets/updates.js',import.meta.url),'utf8');
const old='a'.repeat(20),fresh='b'.repeat(20);
async function scenario(result, hidden=false){
 let now=100000, count=0;
 const nodes=[],events={};
 const document={hidden,currentScript:{dataset:{version:old,manifest:'/version.json'}},body:{append:n=>nodes.push(n)},addEventListener:(name,fn)=>events[name]=fn,createElement:tag=>({tag,children:[],handlers:{},setAttribute(){},append(...children){this.children.push(...children)},addEventListener(name,fn){this.handlers[name]=fn},remove(){this.removed=true}})};
 runInNewContext(code,{document,URL,location:{href:'http://clavesol.com.br/artigos/a/?x=1#trecho'},Date:{now:()=>now},fetch:async(url,options)=>{count++;assert.equal(options.cache,'no-store');assert.equal(url.pathname,'/version.json');assert.ok(url.searchParams.has('check'));if(result instanceof Error)throw result;return {ok:true,json:async()=>({version:result})}}});
 await new Promise(setImmediate);
 return {nodes,document,events,count:()=>count,advance:()=>now+=60001};
}
assert.equal((await scenario(old)).nodes.length,0);
const newer=await scenario(fresh);assert.equal(newer.nodes.length,1);
const notice=newer.nodes[0];assert.equal(notice.children[1].textContent,'Atualizar');
assert.equal(notice.children[1].href,`http://clavesol.com.br/artigos/a/?x=1&_cs=${fresh}#trecho`);
notice.children[2].handlers.click();assert.equal(notice.removed,true);
assert.equal((await scenario(new Error('offline'))).nodes.length,0);
assert.equal((await scenario('bad-version')).nodes.length,0);
const tab=await scenario(old,true);assert.equal(tab.count(),0);tab.document.hidden=false;await tab.events.visibilitychange();assert.equal(tab.count(),1);await tab.events.visibilitychange();assert.equal(tab.count(),1);tab.advance();await tab.events.visibilitychange();assert.equal(tab.count(),2);
console.log('Matching/new releases, explicit update, dismissal, offline and tab throttling: OK');
