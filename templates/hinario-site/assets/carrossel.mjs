// Manual: no unexpected movement, timers or interference with the player.
export function mountCarousel(root){
  const slides=[...root.querySelectorAll('.carousel-slides img')];
  const controls=root.querySelector('.carousel-controls');
  if(slides.length<2||!controls)return;
  let index=0;
  function show(next){index=(next+slides.length)%slides.length;slides.forEach((slide,i)=>{slide.hidden=i!==index;});root.querySelector('[data-count]').textContent=`${index+1} de ${slides.length}`;}
  root.querySelector('[data-prev]').addEventListener('click',()=>show(index-1));
  root.querySelector('[data-next]').addEventListener('click',()=>show(index+1));
  root.addEventListener('keydown',event=>{if(event.key==='ArrowLeft'||event.key==='ArrowRight'){event.preventDefault();show(index+(event.key==='ArrowRight'?1:-1));}});
  controls.hidden=false;show(0);
}
if(typeof document!=='undefined')document.querySelectorAll('.collection-carousel').forEach(mountCarousel);
