export const keys=[['Dó',0,0],['Sol',4,0],['Ré',1,0],['Lá',5,0],['Mi',2,0],['Si',6,0],['Fá♯',3,1],['Dó♯',0,1],['Fá',3,0],['Si♭',6,-1],['Mi♭',2,-1],['Lá♭',5,-1],['Ré♭',1,-1],['Sol♭',4,-1],['Dó♭',0,-1]];
const letters=['Dó','Ré','Mi','Fá','Sol','Lá','Si'],natural=[0,2,4,5,7,9,11];
const offsets=[0,2,4,5,7,9,11,12];
export function scale(index){
 const [name,letter,acc]=keys[index],pc=(natural[letter]+acc+12)%12,root=60+pc;
 return {name,notes:offsets.map((offset,i)=>{
  const l=(letter+i)%7,midi=root+offset;
  let alteration=((midi%12)-natural[l]+12)%12;if(alteration>6)alteration-=12;
  return {midi,name:letters[l]+(alteration===1?'♯':alteration===-1?'♭':'')};
 })};
}
export const chord=notes=>[notes[0].midi,notes[2].midi,notes[4].midi];
export function matches(notes,position,midi){return position<notes.length && notes[position].midi===midi;}
// Same triangle-wave timbre and gentle envelope as the score player's synth.
class KeyboardAudio {
 constructor(){this.context=null;this.nodes=new Set();this.muted=false;this.generation=0;}
 stop(){this.generation++;for(const node of this.nodes)try{node.stop();}catch{}this.nodes.clear();}
 async play(events){
  if(this.muted)return;
  const generation=this.generation;
  const Audio=globalThis.AudioContext||globalThis.webkitAudioContext;
  if(!Audio)throw Error('Áudio não disponível neste navegador. Você pode continuar o exercício sem som.');
  this.context??=new Audio();await this.context.resume();
  if(generation!==this.generation||this.muted)return;
  for(const {midi,delay=0,length=.6} of events){
   const osc=this.context.createOscillator(),gain=this.context.createGain(),when=this.context.currentTime+delay;
   osc.type='triangle';osc.frequency.value=440*2**((midi-69)/12);
   gain.gain.setValueAtTime(.0001,when);gain.gain.exponentialRampToValueAtTime(.055,when+.025);gain.gain.setValueAtTime(.055,when+length-.06);gain.gain.exponentialRampToValueAtTime(.0001,when+length);
   osc.connect(gain);gain.connect(this.context.destination);osc.start(when);osc.stop(when+length+.02);this.nodes.add(osc);
   osc.onended=()=>{osc.disconnect();gain.disconnect();this.nodes.delete(osc);};
  }
 }
}
if(typeof document!=='undefined'&&document.getElementById('scales-app')){
 const get=id=>document.getElementById('scales-'+id),audio=new KeyboardAudio();
 let current,position=0,round=0;
 const sound=events=>audio.play(events).catch(error=>{get('audio').textContent=error.message;});
 keys.forEach((key,i)=>{const option=document.createElement('option');option.value=i;option.textContent=key[0]+' maior';get('key').append(option);});
 function progress(){
  get('progress').replaceChildren();current.notes.forEach((note,i)=>{const li=document.createElement('li');li.textContent=i<position?note.name:(i===0?note.name:'—');li.className=i<position?'done':'';li.setAttribute('aria-label',`${i+1}º grau: ${i<position?note.name:'a completar'}`);get('progress').append(li);});
  get('undo').disabled=position===0;get('listen').disabled=position!==8;
 }
 function press(midi,button){
  audio.stop();
  const events=[{midi}];
  if(position===8){sound(events);return;}
  if(matches(current.notes,position,midi)){
   position++;get('status').className='correct';
   get('status').textContent=position===8?`✓ Escala de ${current.name} maior completa! Acorde: ${[0,2,4].map(i=>current.notes[i].name).join(' · ')}.`:`✓ ${current.notes[position-1].name}. Continue subindo.`;
   if(position===8)events.push(...chord(current.notes).map(midi=>({midi,delay:.7,length:1.4})));
   button.classList.remove('wrong');button.classList.add('played');progress();
  }else{get('status').className='wrong';get('status').textContent='Essa não é a próxima nota. Confira o intervalo e tente novamente.';button.classList.add('wrong');}
  sound(events);
 }
 function start(){
  audio.stop();position=0;round++;current=scale(Number(get('key').value));get('title').textContent=current.name+' maior';get('round').textContent='Exercício '+round;get('status').className='';get('status').textContent='Toque a tônica marcada para começar.';
  get('keyboard').replaceChildren();let whites=0;
  for(let midi=60;midi<=84;midi++){
   const pc=midi%12,isWhite=natural.includes(pc),button=document.createElement('button');button.type='button';
   const standard=isWhite?letters[natural.indexOf(pc)]:({1:'Dó♯ / Ré♭',3:'Ré♯ / Mi♭',6:'Fá♯ / Sol♭',8:'Sol♯ / Lá♭',10:'Lá♯ / Si♭'})[pc];
   const note=current.notes.find(n=>n.midi%12===pc),alias=isWhite&&note&&note.name!==standard?' / '+note.name:'';
   button.textContent=standard+alias;button.setAttribute('aria-label',standard+alias+', região '+(Math.floor(midi/12)-1));button.className=isWhite?'white':'black';
   button.style.left=(isWhite?whites*56:whites*56-18)+'px';if(isWhite)whites++;
   if(midi===current.notes[0].midi){const flag=document.createElement('b');flag.textContent='Início';button.append(flag);}
   button.addEventListener('click',()=>press(midi,button));get('keyboard').append(button);
  }
  progress();
 }
 get('key').addEventListener('change',start);
 get('random').addEventListener('click',()=>{const old=Number(get('key').value);get('key').value=(old+1+Math.floor(Math.random()*(keys.length-1)))%keys.length;start();});
 get('restart').addEventListener('click',start);
 get('undo').addEventListener('click',()=>{audio.stop();position=Math.max(0,position-1);get('status').className='';get('status').textContent='Última nota removida. Continue a escala.';for(const b of get('keyboard').querySelectorAll('button'))b.classList.remove('played','wrong');progress();});
 get('mute').addEventListener('change',()=>{audio.muted=get('mute').checked;audio.stop();});
 get('listen').addEventListener('click',()=>{audio.stop();sound([...current.notes.map((n,i)=>({midi:n.midi,delay:i*.45,length:.4})),...chord(current.notes).map(midi=>({midi,delay:3.9,length:1.5}))]);});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)audio.stop();});window.addEventListener('pagehide',()=>audio.stop());
 get('key').value=Math.floor(Math.random()*keys.length);get('app').hidden=false;start();
}
