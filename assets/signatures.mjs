export const tonalities=[['Dó',0],['Sol',1],['Ré',2],['Lá',3],['Mi',4],['Si',5],['Fá♯',6],['Dó♯',7],['Fá',-1],['Si♭',-2],['Mi♭',-3],['Lá♭',-4],['Ré♭',-5],['Sol♭',-6],['Dó♭',-7]];
// Treble staff: F5 top line at y=50, E4 bottom line at y=130.
export const positions=[['Sol','acima da 5ª linha'],['Fá','5ª linha'],['Mi','4º espaço'],['Ré','4ª linha'],['Dó','3º espaço'],['Si','3ª linha'],['Lá','2º espaço'],['Sol','2ª linha'],['Fá','1º espaço'],['Mi','1ª linha']];
const sharpOrder=[1,4,0,3,6,2,5],flatOrder=[5,2,6,3,7,4,8];
export function expected(index){const count=tonalities[index][1];return (count<0?flatOrder:sharpOrder).slice(0,Math.abs(count)).map(row=>({row,kind:count<0?'flat':'sharp'}));}
export function grade(index,entries){
 const answer=expected(index);
 if(entries.length!==answer.length)return 'count';
 if(entries.some((e,i)=>e.kind!==answer[i].kind))return 'kind';
 if(entries.some((e,i)=>e.row!==answer[i].row))return 'position';
 return 'correct';
}
export function rowAt(y){return Math.max(0,Math.min(9,Math.round((y-40)/10)));}
export function signPath(kind,x,y){return kind==='sharp'?`<g stroke="currentColor"><path d="M${x-5} ${y-18}v36M${x+5} ${y-20}v36" stroke-width="2"/><path d="M${x-10} ${y-5}l20-5M${x-10} ${y+8}l20-5" stroke-width="5"/></g>`:`<path d="M${x-5} ${y-26}v35C${x+16} ${y-1} ${x+12} ${y-15} ${x-5} ${y-3}" fill="none" stroke="currentColor" stroke-width="3"/>`;}
if(typeof document!=='undefined'&&document.getElementById('signature-app')){
 const get=id=>document.getElementById('signature-'+id);
 let entries=[],kind='sharp',solved=false,tried=false,answered=0,correct=0,keyIndex=1+Math.floor(Math.random()*14);
 tonalities.forEach(([name],i)=>{const button=document.createElement('button');button.type='button';button.textContent=name;button.setAttribute('aria-label',name+' maior');button.addEventListener('click',()=>{keyIndex=i;start();});get('keys').append(button);});
 positions.forEach(([name,place],row)=>{const button=document.createElement('button');button.type='button';button.setAttribute('aria-label','Inserir em '+name+' — '+place);const title=document.createElement('strong'),detail=document.createElement('small');title.textContent=name;detail.textContent=place;button.append(title,detail);button.addEventListener('click',()=>add(row));get('positions').append(button);});
 const describe=()=>entries.map((e,i)=>`${i+1}. ${positions[e.row][0]}${e.kind==='sharp'?'♯':'♭'} (${positions[e.row][1]})`).join('; ');
 function render(){
  const staff=get('staff');staff.replaceChildren();
  const paths=[];
  if(!solved&&entries.length<7)paths.push(`<rect x="${92+entries.length*24}" y="18" width="24" height="142" rx="6" fill="#b38a4d" opacity=".13"/>`);
  for(let y=50;y<=130;y+=20)paths.push(`<path d="M20 ${y}H600" stroke="currentColor" stroke-width="1.3" opacity=".65"/>`);
  paths.push('<path d="M20 50v80M600 50v80" stroke="currentColor" stroke-width="1.5"/>');
  entries.forEach((e,i)=>paths.push(signPath(e.kind,104+i*24,40+e.row*10)));
  staff.innerHTML=paths.join('');staff.append(document.getElementById('signature-clef').content.querySelector('path').cloneNode(true));
  const description=describe();staff.setAttribute('aria-label','Pentagrama em clave de Sol. '+(description||'Sem alterações.'));get('written').textContent=description||'Nenhum sinal inserido.';
  get('undo').disabled=get('clear').disabled=solved||entries.length===0;for(const button of get('positions').children)button.disabled=solved||entries.length===7;get('check').disabled=solved;
 }
 function resetFeedback(){get('feedback').textContent='';get('feedback').className='';get('staff').classList.remove('correct','wrong');}
 function add(row){
  if(solved)return;
  if(entries.length>=7){get('feedback').textContent='A armadura aceita até sete sinais. Use Desfazer para corrigir.';return;}
  entries.push({kind,row});resetFeedback();render();
 }
 function start(){Array.from(get('keys').children).forEach((button,i)=>button.setAttribute('aria-pressed',String(i===keyIndex)));entries=[];solved=false;tried=false;resetFeedback();get('title').textContent=tonalities[keyIndex][0]+' maior';get('feedback').textContent='Preencha a armadura e confira. Em Dó maior, deixe o pentagrama sem alterações.';render();}
 for(const type of ['sharp','flat'])get(type).addEventListener('click',()=>{kind=type;for(const t of ['sharp','flat'])get(t).setAttribute('aria-pressed',String(t===type));});
 get('staff').addEventListener('click',event=>{
  const point=get('staff').createSVGPoint();point.x=event.clientX;point.y=event.clientY;
  const p=point.matrixTransform(get('staff').getScreenCTM().inverse());
  if(p.x>=90&&p.x<=600&&p.y>=30&&p.y<=140){add(rowAt(p.y));}
 });
 get('undo').addEventListener('click',()=>{entries.pop();resetFeedback();render();});
 get('clear').addEventListener('click',()=>{entries=[];resetFeedback();render();});
 get('check').addEventListener('click',()=>{
  const result=grade(keyIndex,entries);
  if(!tried){answered++;if(result==='correct')correct++;tried=true;}
  solved=result==='correct';get('feedback').textContent={correct:'✓ Correto! A armadura está completa, na ordem e nas posições certas.',count:'A quantidade de sinais ainda não corresponde à tonalidade. Ajuste e tente novamente.',kind:'Confira o tipo de alteração: esta tonalidade exige outro tipo de sinal.',position:'Confira a ordem dos sinais e suas posições na clave de Sol. Use Desfazer ou Limpar para corrigir.'}[result];
  get('feedback').className=solved?'correct':'wrong';get('staff').classList.toggle('correct',solved);get('staff').classList.toggle('wrong',!solved);
  get('score').textContent=`${correct} acertos de primeira em ${answered} respondidos`;render();
 });
 get('next').addEventListener('click',()=>{keyIndex=(keyIndex+1+Math.floor(Math.random()*14))%15;start();});
 get('app').hidden=false;start();
}
