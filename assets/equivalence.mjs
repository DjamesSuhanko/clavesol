const values=[1,2,4,8,16];
const names={1:'semibreve',2:'mínima',4:'semínima',8:'colcheia',16:'semicolcheia'};
export const duration=figures=>figures.reduce((sum,den)=>sum+16/den,0);
const bag=figures=>[...figures].sort((a,b)=>a-b).join(',');
export function generate(rng=Math.random){
  const single=values[Math.floor(rng()*4)],figures=[single];
  const splits=1+Math.floor(rng()*5);
  for(let i=0;i<splits;i++){
    const choices=figures.map((den,index)=>({den,index})).filter(f=>f.den<16);
    if(!choices.length)break;
    const {den,index}=choices[Math.floor(rng()*choices.length)];
    figures.splice(index,1,den*2,den*2);
  }
  for(let i=figures.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[figures[i],figures[j]]=[figures[j],figures[i]];}
  return {figures,rest:rng()<.5};
}
export function grade(question,answer){
  if(!answer.length)return 'empty';
  if(!answer.every(den=>values.includes(den)))return 'invalid';
  if(bag(question)===bag(answer))return 'copy';
  const difference=duration(answer)-duration(question);
  return difference===0?'correct':difference<0?'short':'long';
}
if(typeof document!=='undefined'&&document.getElementById('equivalence')){
  const get=id=>document.getElementById('eq-'+id);
  let question,answer=[],round=0,responded=0,correct=0,tried=false,solved=false;
  function draw(target,figures){
    target.replaceChildren();
    figures.forEach(den=>{
      const li=document.createElement('li');
      li.append(document.querySelector(`[data-value="${den}"][data-rest="${question.rest}"] svg`).cloneNode(true));
      const text=document.createElement('span');text.textContent=(question.rest?'Pausa de ':'')+names[den];li.append(text);target.append(li);
    });
  }
  function render(){
    draw(get('answer'),answer);get('empty').hidden=answer.length>0;
    get('check').disabled=solved||!answer.length;get('undo').disabled=get('clear').disabled=solved||!answer.length;
    for(const button of document.querySelectorAll('[data-value]'))button.disabled=solved;
  }
  function edit(){get('feedback').textContent='';get('feedback').className='';get('answer').classList.remove('correct','wrong');render();}
  function next(){
    question=generate();answer=[];round++;tried=false;solved=false;
    get('round').textContent='Exercício '+round;get('prompt').textContent=question.rest?'Transforme estas pausas':'Transforme estas notas';
    for(const group of document.querySelectorAll('[data-kind]'))group.hidden=group.dataset.kind!==String(question.rest);
    draw(get('question'),question.figures);edit();
  }
  for(const button of document.querySelectorAll('[data-value]'))button.addEventListener('click',()=>{
    if(solved)return;
    if(answer.length>=32){get('feedback').textContent='Limite de 32 figuras. Desfaça ou limpe a resposta.';return;}
    answer.push(Number(button.dataset.value));edit();
  });
  get('undo').addEventListener('click',()=>{answer.pop();edit();});
  get('clear').addEventListener('click',()=>{answer=[];edit();});
  get('check').addEventListener('click',()=>{
    if(solved)return;
    const result=grade(question.figures,answer);
    if(!tried){responded++;if(result==='correct')correct++;tried=true;}
    const messages={copy:'Você repetiu as figuras do enunciado. Trocar a ordem não muda a combinação: agrupe ou divida os valores.',short:'Ainda falta duração na resposta. Ajuste as figuras e tente novamente.',long:'A resposta ultrapassa a duração do enunciado. Ajuste as figuras e tente novamente.',correct:'✓ Correto! Você escreveu a mesma duração com uma combinação diferente.'};
    solved=result==='correct';get('feedback').textContent=messages[result]||'Monte uma resposta válida.';
    get('feedback').className=solved?'correct':'wrong';get('answer').classList.add(solved?'correct':'wrong');
    get('score').textContent=`${correct} acertos de primeira em ${responded} respondidos`;render();
  });
  get('next').addEventListener('click',()=>{next();document.querySelector('[data-kind]:not([hidden]) button').focus();});
  document.getElementById('equivalence').hidden=false;next();
}
