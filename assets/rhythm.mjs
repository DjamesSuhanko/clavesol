// Durations are exact integer eighth-note units. Distractors never share a total.
export const meters = [{num:2,den:4},{num:3,den:4},{num:4,den:4},{num:6,den:4},{num:2,den:2},{num:3,den:2},{num:6,den:8}];
const figures = [{den:1,ticks:8},{den:2,ticks:4},{den:2,ticks:6,dotted:true},{den:4,ticks:2},{den:4,ticks:3,dotted:true},{den:8,ticks:1}];
const names = {1:'semibreve',2:'mínima',4:'semínima',8:'colcheia'};
const pick = (values,rng) => values[Math.floor(rng()*values.length)];
export const total = meter => meter.num*8/meter.den;
export const label = meter => `${meter.num}/${meter.den}`;
export function generate(rng=Math.random) {
  const answer=pick(meters,rng), notes=[];
  let remaining=total(answer);
  // Fill each beat separately so dots and eighths respect simple/compound grouping.
  const beat=answer.den===8?3:8/answer.den;
  while(remaining>0){
    const room=Math.min(remaining,beat-(total(answer)-remaining)%beat);
    const choices=figures.filter(f=>f.ticks<=room || (f.ticks%beat===0 && f.ticks<=remaining && room===beat));
    const note={...pick(choices,rng),pitch:Math.floor(rng()*7)};
    notes.push(note);remaining-=note.ticks;
  }
  const wrong=pick(meters.filter(m=>total(m)!==total(answer)),rng);
  return {answer,notes,options:rng()<.5?[answer,wrong]:[wrong,answer]};
}
export function description(notes){return notes.map(n=>names[n.den]+(n.dotted?' pontuada':'')).join(', ');}
export function staffSVG(notes){
  const width=Math.max(420,notes.length*65+65), spacing=(width-90)/notes.length;
  let svg='<svg xmlns="http://www.w3.org/2000/svg" style="min-width:'+Math.max(260,notes.length*34+60)+'px" viewBox="0 0 '+width+' 155" aria-hidden="true" focusable="false">';
  for(let y=50;y<=98;y+=12)svg+=`<path d="M15 ${y}H${width-15}" stroke="currentColor" stroke-width="1" opacity=".55"/>`;
  svg+=`<path d="M15 50V98M${width-21} 50V98M${width-15} 50V98" stroke="currentColor" stroke-width="2"/>`;
  notes.forEach((n,i)=>{
    const x=43+i*spacing,y=98-n.pitch*6,up=y>=74;
    svg+=`<ellipse cx="${x}" cy="${y}" rx="8" ry="5.5" transform="rotate(-20 ${x} ${y})" fill="${n.den<=2?'var(--rhythm-paper)':'currentColor'}" stroke="currentColor" stroke-width="2"/>`;
    if(n.den!==1){
      const sx=x+(up?7:-7),end=y+(up?-34:34);
      svg+=`<path d="M${sx} ${y}V${end}" stroke="currentColor" stroke-width="2"/>`;
      if(n.den===8)svg+=up?`<path d="M${sx} ${end}c0 9 16 10 8 25 2-11-8-9-8-15z" fill="currentColor"/>`:`<path d="M${sx} ${end}c0-9 16-10 8-25 2 11-8 9-8 15z" fill="currentColor"/>`;
    }
    if(n.dotted)svg+=`<circle cx="${x+16}" cy="${y%12===2?y-6:y}" r="2.5" fill="currentColor"/>`;
  });
  return svg+'</svg>';
}
if(typeof document!=='undefined' && document.getElementById('rhythm-exercise')){
  const get=id=>document.getElementById('rhythm-'+id);
  let question,round=0,answered=0,correct=0,attempted=false,solved=false;
  function next(){
    question=generate();round++;attempted=false;solved=false;
    get('round').textContent='Exercício '+round;
    get('staff').innerHTML=staffSVG(question.notes);
    get('notes').textContent=description(question.notes)+'.';
    get('feedback').textContent='Escolha uma alternativa.';
    get('feedback').className='';
    for(const old of get('options').querySelectorAll('label'))old.remove();
    question.options.forEach(m=>{
      const option=document.createElement('label'),input=document.createElement('input'),signature=document.createElement('span'),status=document.createElement('span');
      input.type='radio';input.name='rhythm-answer';input.value=label(m);input.setAttribute('aria-label',label(m));
      signature.className='rhythm-signature';signature.setAttribute('aria-hidden','true');
      for(const value of [m.num,m.den]){const s=document.createElement('span');s.textContent=value;signature.append(s);}
      status.className='rhythm-choice-status';option.append(input,signature,status);get('options').append(option);
      input.addEventListener('change',()=>{
        if(solved)return;
        const ok=label(m)===label(question.answer);
        if(!attempted){answered++;if(ok)correct++;attempted=true;}
        option.className=ok?'is-correct':'is-wrong';status.textContent=ok?'✓ Correto':'✕ Tente novamente';
        get('feedback').className=ok?'is-correct':'is-wrong';
        const quarters=total(question.answer)/2;
        get('feedback').textContent=ok?`Correto! As figuras somam ${quarters} semínimas, a duração de ${label(question.answer)}. Não confunda essa equivalência com a unidade de tempo.`:'Ainda não. Some as durações de todas as figuras e tente a outra alternativa.';
        if(ok){solved=true;for(const radio of get('options').querySelectorAll('input'))radio.disabled=true;}
        get('score').textContent=`${correct} acertos de primeira em ${answered} respondidos`;
      });
    });
  }
  get('next').addEventListener('click',()=>{next();get('options').querySelector('input').focus();});
  get('exercise').hidden=false;next();
}
