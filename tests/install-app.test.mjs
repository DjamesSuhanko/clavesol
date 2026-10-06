import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
const code = readFileSync(new URL('../assets/install-app.js', import.meta.url), 'utf8');
function scenario({standalone=false, ios=false, secure=true}={}) {
  const events={}, clicks={}, mediaEvents={};
  const button={hidden:true,disabled:false,addEventListener:(name,fn)=>clicks[name]=fn};
  const dialog={open:false,showModal(){this.open=true;},close(){this.open=false;}};
  const instructions={textContent:''};
  const media={matches:standalone,addEventListener:(name,fn)=>mediaEvents[name]=fn};
  runInNewContext(code,{
    window:{isSecureContext:secure,matchMedia:()=>media,addEventListener:(name,fn)=>events[name]=fn},
    navigator:{userAgent:ios?'iPhone':'Firefox',platform:ios?'iPhone':'Linux',maxTouchPoints:ios?5:0},
    document:{getElementById:id=>({'install-app':button,'install-help':dialog,'install-instructions':instructions})[id]}
  });
  return {button,dialog,instructions,events,clicks,media,mediaEvents};
}
const normal=scenario();
assert.equal(normal.button.hidden,false);
await normal.clicks.click();assert.equal(normal.dialog.open,true);
assert.match(normal.instructions.textContent,/menu do navegador/);
const ios=scenario({ios:true});await ios.clicks.click();assert.match(ios.instructions.textContent,/Tela de Início/);
assert.equal(scenario({standalone:true}).button.hidden,true);
assert.equal(scenario({secure:false}).button.hidden,true);
let prompted=0,prevented=0;
normal.dialog.close();
normal.events.beforeinstallprompt({preventDefault(){prevented++;},async prompt(){prompted++;},userChoice:Promise.resolve({outcome:'dismissed'})});
assert.equal(prompted,0);assert.equal(prevented,1);
await normal.clicks.click();assert.equal(prompted,1);assert.equal(normal.button.disabled,false);assert.equal(normal.button.hidden,false);
await normal.clicks.click();assert.equal(prompted,1);assert.equal(normal.dialog.open,true);
normal.events.appinstalled();assert.equal(normal.button.hidden,true);assert.equal(normal.dialog.open,false);
const accepted=scenario();accepted.events.beforeinstallprompt({preventDefault(){},async prompt(){},userChoice:Promise.resolve({outcome:'accepted'})});
await accepted.clicks.click();assert.equal(accepted.button.hidden,true);
const failed=scenario();failed.events.beforeinstallprompt({preventDefault(){},async prompt(){throw Error('unavailable');}});
await failed.clicks.click();assert.equal(failed.dialog.open,true);assert.equal(failed.button.disabled,false);
const changed=scenario();changed.media.matches=true;changed.mediaEvents.change();assert.equal(changed.button.hidden,true);
console.log('Instalação: gesto do usuário, recusa, aceite, iOS, fallback, erro e modo app: OK');
