import {eventAt} from './music-timing.mjs';
const zoom=document.getElementById('score-zoom');
const sheets=[...document.querySelectorAll('.score-sheet')];
const audio=document.getElementById('score-audio');
const cursor=document.getElementById('score-cursor');
const status=document.getElementById('playback-status');
const followCursor=document.getElementById('follow-cursor');
let timeline,frame,lastIndex=-1,lastMeasure=-1;
zoom?.addEventListener('change',()=>{for(const sheet of sheets)sheet.style.width=`${zoom.value}%`;});
function draw(follow=false){
  if(!timeline||!cursor)return;
  const index=eventAt(timeline.events,audio.currentTime);
  cursor.hidden=index<0||audio.currentTime>=timeline.duration;
  if(index<0)return;
  const event=timeline.events[index];
  const sheet=sheets[(event.page??1)-1];
  if(!sheet){cursor.hidden=true;return;}
  if(cursor.parentElement!==sheet)sheet.append(cursor);
  const viewport=sheet.closest('.score-viewport');
  cursor.style.left=`${event.x}%`;cursor.style.top=`${event.y-0.8}%`;
  cursor.style.width=`${Math.max(event.width,0.4)}%`;cursor.style.height=`${event.height+1.6}%`;
  if(event.measure!==lastMeasure){document.getElementById('current-measure').textContent=`Compasso ${event.measure}${Number(audio.dataset.measures)?` de ${audio.dataset.measures}`:''}`;lastMeasure=event.measure;}
  if(follow&&index!==lastIndex&&followCursor?.checked&&!cursor.hidden){
    const box=cursor.getBoundingClientRect(),view=viewport.getBoundingClientRect();
    if(box.left<view.left+20||box.right>view.right-20)viewport.scrollLeft+=box.left-view.left-viewport.clientWidth*.3;
    if(box.top<0||box.bottom>innerHeight-40)cursor.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'});
  }
  lastIndex=index;
}
function animate(){draw(true);if(!audio.paused&&!audio.ended)frame=requestAnimationFrame(animate);}
if(audio){
audio.addEventListener('play',()=>{status.textContent='Reproduzindo';cancelAnimationFrame(frame);animate();});
audio.addEventListener('pause',()=>{cancelAnimationFrame(frame);status.textContent=audio.ended?'Reprodução concluída':'Pausado';draw();});
audio.addEventListener('ended',()=>{cancelAnimationFrame(frame);if(cursor)cursor.hidden=true;status.textContent='Reprodução concluída';});
audio.addEventListener('timeupdate',()=>draw());
audio.addEventListener('seeked',()=>draw(!audio.paused));
audio.addEventListener('error',()=>{status.textContent='Não foi possível carregar o áudio. Recarregue a página para tentar novamente.';});
document.getElementById('restart-score').addEventListener('click',()=>{audio.pause();audio.currentTime=0;lastIndex=-1;draw();status.textContent='Pronto para reproduzir';});
document.getElementById('playback-speed').addEventListener('change',event=>{audio.playbackRate=Number(event.target.value);});
if(audio.dataset.timing)try{
  const response=await fetch(audio.dataset.timing);
  if(!response.ok)throw new Error('Timing unavailable');
  timeline=await response.json();draw();status.textContent='Pronto para reproduzir';
}catch{status.textContent='Áudio disponível; não foi possível carregar o cursor. Recarregue a página.';}
}
