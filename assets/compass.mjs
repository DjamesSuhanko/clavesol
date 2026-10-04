// Exact arithmetic in 1/32 of a whole note, including one augmentation dot.
const names={1:'Semibreve',2:'Mínima',4:'Semínima',8:'Colcheia',16:'Semicolcheia'};
const gcd=(a,b)=>b?gcd(b,a%b):a;
export function fraction(n,d){if(!n)return '0';const g=gcd(n,d);return d/g===1?String(n/g):n/g+'/'+(d/g);}
export class CompassCalculator {
  entries=[];
  add(den,rest=false){if(!Object.hasOwn(names,den)||this.entries.length>=128)return false;this.entries.push({den:Number(den),rest:Boolean(rest),dotted:false});return true;}
  dot(){const last=this.entries.at(-1);if(!last||last.dotted)return false;last.dotted=true;return true;}
  undo(){const last=this.entries.at(-1);if(!last)return;if(last.dotted)last.dotted=false;else this.entries.pop();}
  clear(){this.entries=[];}
  get ticks(){return this.entries.reduce((sum,e)=>sum+32/e.den*(e.dotted?1.5:1),0);}
  signature(unit='auto'){
    const ticks=this.ticks;if(!ticks)return null;
    const den=unit==='auto'?[4,2,1,8,16,32].find(d=>ticks*d%32===0):Number(unit);
    if(![1,2,4,8,16,32].includes(den)||ticks*den%32!==0)return null;
    return {num:ticks*den/32,den};
  }
}
if(typeof document!=='undefined'&&document.getElementById('compass-calculator')){
  const calc=new CompassCalculator(),get=id=>document.getElementById('compass-'+id);
  const sequence=get('sequence'),unit=get('unit');
  function render(){
    sequence.replaceChildren();
    for(const [i,entry] of calc.entries.entries()){
      const li=document.createElement('li');
      const svg=document.querySelector('[data-den="'+entry.den+'"][data-rest="'+entry.rest+'"] svg').cloneNode(true);
      li.append(svg);
      if(entry.dotted){const dot=document.createElement('b');dot.textContent='·';dot.setAttribute('aria-hidden','true');li.append(dot);}
      li.setAttribute('aria-label',(i+1)+'. '+(entry.rest?'Pausa de ':'')+names[entry.den].toLowerCase()+(entry.dotted?' pontuada':''));
      sequence.append(li);
    }
    get('empty').hidden=calc.entries.length>0;
    get('count').textContent=calc.entries.length+' figura'+(calc.entries.length===1?'':'s');
    get('dot').disabled=!calc.entries.length||calc.entries.at(-1).dotted;
    get('undo').disabled=get('clear').disabled=!calc.entries.length;
    get('total').textContent=fraction(calc.ticks,32);get('quarters').textContent=fraction(calc.ticks,8);
    const signature=calc.signature(unit.value);get('signature').replaceChildren();
    for(const value of signature?[signature.num,signature.den]:['—']){const span=document.createElement('span');span.textContent=value;get('signature').append(span);}
    get('result-text').textContent=signature?'Duração equivalente a '+signature.num+'/'+signature.den+'.':calc.ticks?'Esta soma não forma um número inteiro na unidade escolhida. Experimente outra unidade ou o modo automático.':'Adicione notas ou pausas para calcular.';
  }
  for(const button of document.querySelectorAll('[data-den]'))button.addEventListener('click',()=>{
    const added=calc.add(Number(button.dataset.den),button.dataset.rest==='true');get('notice').textContent=added?'':'Limite de 128 figuras. Desfaça uma figura ou limpe a sequência para continuar.';render();
  });
  get('dot').addEventListener('click',()=>{calc.dot();render();});
  get('undo').addEventListener('click',()=>{calc.undo();get('notice').textContent='';render();});
  get('clear').addEventListener('click',()=>{calc.clear();get('notice').textContent='';render();});
  unit.addEventListener('change',render);
  for(const button of document.querySelectorAll('[data-example]'))button.addEventListener('click',()=>{
    const [num,den]=button.dataset.example.split('/').map(Number);calc.clear();for(let i=0;i<num;i++)calc.add(den);unit.value=String(den);get('notice').textContent='';render();
  });
  render();
}
