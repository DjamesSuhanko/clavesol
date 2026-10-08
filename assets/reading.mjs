const names=['Dó','Ré','Mi','Fá','Sol','Lá','Si'];
const clefs={treble:{label:'Sol',bottom:30,ref:32,line:2},bass:{label:'Fá',bottom:18,ref:24,line:4},alto:{label:'Dó na 3ª linha',bottom:24,ref:28,line:3},tenor:{label:'Dó na 4ª linha',bottom:22,ref:28,line:4}};
const key='clavesol-reading-v1';
const get=id=>document.getElementById('rd-'+id);
const noteName=n=>names[((n%7)+7)%7];
const fullName=n=>`${noteName(n)}${Math.floor(n/7)}`;
const seconds=n=>`${(n/1000).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})} s`;
const date=n=>new Date(n).toLocaleString('pt-BR');
let data={version:1,groups:{},history:[]},storageOK=true;
try{const saved=JSON.parse(localStorage.getItem(key));if(saved?.version===1 && saved.groups && Array.isArray(saved.history))data=saved;}catch{storageOK=false;}
let session=null,current=null,answered=false,questionStart=0,ticker=null,audio=null,voice=null;
const answerButtons=names.map((name,i)=>{const b=document.createElement('button');b.type='button';b.textContent=name;b.disabled=true;b.addEventListener('click',()=>answer(i));get('answers').append(b);return b;});
function save(){try{localStorage.setItem(key,JSON.stringify(data));}catch{storageOK=false;}progress();}
function progress(){
 const groups=Object.values(data.groups).filter(g=>Number.isFinite(g.attempts)&&Number.isFinite(g.correct));
 const total=groups.reduce((a,g)=>a+g.attempts,0),correct=groups.reduce((a,g)=>a+g.correct,0);
 get('progress').textContent=total?`${correct} acertos em ${total} respostas (${Math.round(correct/total*100)}%). O histórico abaixo reúne suas últimas 10 sessões.`:'Seu primeiro resultado aparecerá aqui.';
 if(!storageOK)get('storage').textContent='Não foi possível acessar o armazenamento. O progresso desta visita pode ser perdido ao fechar a página.';
 get('history').replaceChildren();
 for(const s of data.history.slice(0,10)){
  if(!clefs[s.clef]||!Number.isFinite(s.count)||!Number.isFinite(s.total))continue;
  const li=document.createElement('li');li.textContent=`${date(s.ended)} · ${clefs[s.clef].label} · ${s.level===0?'pentagrama':`até ${s.level} suplementar(es)`} · ${s.correct}/${s.count} acertos · média ${seconds(s.responseTotal/Math.max(1,s.count))} · total ${seconds(s.total)}${s.complete?'':' · encerrada antes do fim'}`;get('history').append(li);
 }
}
function draw(){
 const c=clefs[session?.clef||get('clef').value];
 let svg='';for(let y=110;y<=190;y+=20)svg+=`<path d="M24 ${y}H416" stroke="currentColor" stroke-width="1.4"/>`;
 if(session?.clef==='bass'||(!session&&get('clef').value==='bass')){
  svg+='<path fill="currentColor" d="M35 132 C35 101 77 99 77 132 C77 156 54 174 34 181 C53 166 65 151 65 130 C65 108 43 108 40 123 C55 114 60 137 46 140 C39 142 35 138 35 132Z"/><circle cx="89" cy="120" r="4.5"/><circle cx="89" cy="140" r="4.5"/>';
 }else if(c===clefs.alto||c===clefs.tenor){
  const y=190-(c.ref-c.bottom)*10;
  svg+=`<g transform="translate(36 ${y})" fill="currentColor"><path d="M0 -40H7V40H0Z M11 -40H14V40H11Z M18 -40 C56 -43 60 -13 33 0 C60 13 56 43 18 40 L18 34 C42 40 44 15 27 7 L22 19 L16 0 L22 -19 L27 -7 C44 -15 42 -40 18 -34Z"/></g>`;
 }else{
  const path=document.getElementById('reading-clef').content.querySelector('path').outerHTML;svg+=`<g transform="translate(0 60)">${path}</g>`;
 }
 if(current!==null){
  const y=190-(current-c.bottom)*10;
  for(let line=210;line<=y;line+=20)svg+=`<path d="M248 ${line}H292" stroke="currentColor" stroke-width="1.5"/>`;
  for(let line=90;line>=y;line-=20)svg+=`<path d="M248 ${line}H292" stroke="currentColor" stroke-width="1.5"/>`;
  svg+=`<ellipse cx="270" cy="${y}" rx="13" ry="9" transform="rotate(-20 270 ${y})" fill="currentColor"/><path d="${y>150?`M282 ${y-3}V${y-63}`:`M258 ${y+3}V${y+63}`}" stroke="currentColor" stroke-width="2"/>`;
  if(answered){const refY=190-(c.ref-c.bottom)*10;svg+=`<circle cx="125" cy="${refY}" r="6" fill="#a66b24"/><text x="125" y="285" font-size="13" text-anchor="middle" fill="#805018">Referência: ${fullName(c.ref)}</text><text x="270" y="285" font-size="16" text-anchor="middle" fill="currentColor">${fullName(current)}</text>`;}
 }
 get('staff').innerHTML=svg;
 get('staff').setAttribute('aria-label',`Clave de ${c.label}.${current===null?'':answered?` Nota ${fullName(current)}.`:` Nota ${position(current-c.bottom)}.`}`);
}
function position(p){if(p>=0&&p<=8)return p%2===0?`na ${p/2+1}ª linha`:`no ${(p+1)/2}º espaço`;return `${Math.abs(p<0?p:p-8)} passo(s) de linha ou espaço ${p<0?'abaixo da linha inferior':'acima da linha superior'}`;}
function next(){
 const c=clefs[session.clef],low=c.bottom-session.level*2,high=c.bottom+8+session.level*2;
 const pool=Array.from({length:high-low+1},(_,i)=>low+i).filter(n=>n!==current);
 current=pool[Math.floor(Math.random()*pool.length)];answered=false;
 answerButtons.forEach(b=>{b.disabled=false;b.className='';});
 get('feedback').textContent='';get('audio').textContent='';get('next').disabled=true;get('listen').disabled=true;
 get('prompt').textContent=`Qual é o nome desta nota? Clave de ${c.label}.`;
 get('count').textContent=`Nota ${session.count+1} de ${session.length}`;draw();questionStart=performance.now();
}
function start(){
 session={clef:get('clef').value,level:Number(get('level').value),length:Number(get('length').value),started:Date.now(),startTick:performance.now(),count:0,correct:0,responseTotal:0,ended:null};
 ['clef','level','length','start'].forEach(id=>get(id).disabled=true);get('end').disabled=false;
 get('times').textContent=`Início: ${date(session.started)} · Término: em andamento`;
 get('summary').textContent='O tempo total inclui as explicações; a média mede apenas o tempo de resposta.';
 get('score').textContent='0 acertos';get('clock').textContent=seconds(0);current=null;next();
 ticker=setInterval(()=>{get('clock').textContent=seconds(performance.now()-session.startTick);},100);
 answerButtons[0].focus();
}
function answer(choice){
 if(!session||session.ended||answered)return;
 const elapsed=performance.now()-questionStart;answered=true;session.count++;session.responseTotal+=elapsed;
 const right=current%7,ok=choice===right;if(ok)session.correct++;
 answerButtons.forEach((b,i)=>{b.disabled=true;b.className=i===right?'correct':i===choice?'wrong':'';});
 const c=clefs[session.clef],distance=current-c.ref,step=Math.sign(distance),sequence=[];
 for(let n=c.ref;step&& (step>0?n<=current:n>=current);n+=step)sequence.push(noteName(n));
 get('feedback').textContent=`${ok?'Correto!':`Você marcou ${names[choice]}. A resposta é ${noteName(current)}.`} ${fullName(current)}: ${position(current-c.bottom)}. A clave indica ${fullName(c.ref)} na ${c.line}ª linha (ponto dourado). ${distance?`Conte ${Math.abs(distance)} passo(s) ${distance>0?'para cima':'para baixo'}: ${sequence.join(' → ')}.`:'A nota está na própria linha de referência.'}`;
 get('score').textContent=`${session.correct} acertos em ${session.count} respostas`;
 get('listen').disabled=false;get('next').disabled=false;draw();
 const groupKey=`${session.clef}:${session.level}`;
 let g=data.groups[groupKey];if(!g||!Number.isFinite(g.attempts)||!Number.isFinite(g.correct))g=data.groups[groupKey]={attempts:0,correct:0};g.attempts++;g.correct+=Number(ok);save();
 if(session.count===session.length)finish();else get('next').focus();
}
function finish(){
 if(!session||session.ended)return;
 session.ended=Date.now();session.total=performance.now()-session.startTick;session.complete=session.count===session.length;clearInterval(ticker);
 get('clock').textContent=seconds(session.total);get('end').disabled=true;get('next').disabled=true;
 answerButtons.forEach(b=>b.disabled=true);['clef','level','length','start'].forEach(id=>get(id).disabled=false);get('start').textContent='Iniciar nova sessão';
 get('times').textContent=`Início: ${date(session.started)} · Término: ${date(session.ended)}`;
 get('summary').textContent=`${session.complete?'Sessão concluída!':'Sessão encerrada.'} ${session.correct} acertos em ${session.count} respostas. Tempo total: ${seconds(session.total)}. ${session.count?`Média por resposta: ${seconds(session.responseTotal/session.count)}.`:'Nenhuma nota respondida.'}`;
 get('count').textContent=`${session.count} de ${session.length} notas respondidas`;
 if(session.count){const {startTick,...record}=session;data.history.unshift(record);data.history=data.history.slice(0,10);save();}
 if(!answered){get('prompt').textContent='Sessão encerrada. Inicie outra quando quiser.';current=null;draw();}
 get('start').focus();
}
async function listen(){
 if(!answered||current===null)return;
 try{
  const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)throw Error();audio??=new Audio();await audio.resume();
  if(audio.state!=='running')throw Error();if(voice){try{voice.stop();}catch{}}
  const midi=12*(Math.floor(current/7)+1)+[0,2,4,5,7,9,11][current%7];
  const osc=audio.createOscillator(),gain=audio.createGain(),t=audio.currentTime;voice=osc;osc.type='triangle';osc.frequency.value=440*2**((midi-69)/12);
  gain.gain.setValueAtTime(0,t);gain.gain.linearRampToValueAtTime(.16,t+.02);gain.gain.exponentialRampToValueAtTime(.0001,t+.95);osc.connect(gain);gain.connect(audio.destination);osc.start(t);osc.stop(t+1);osc.onended=()=>{osc.disconnect();gain.disconnect();};
  get('audio').textContent=`${fullName(current)} · som de referência`;
 }catch{get('audio').textContent='Não foi possível reproduzir o som. Confira as permissões de áudio do navegador.';}
}
get('start').addEventListener('click',start);get('end').addEventListener('click',finish);get('next').addEventListener('click',()=>{if(session&&!session.ended&&answered){next();answerButtons[0].focus();}});get('listen').addEventListener('click',listen);
get('clef').addEventListener('change',()=>{session=null;current=null;answered=false;get('listen').disabled=true;draw();});
progress();draw();document.getElementById('reading-app').hidden=false;
