"""Key signature practice in treble clef."""
from pathlib import Path


def signatures_card(base):
    url=f'{base}/gem/armaduras-de-clave/'
    return f'<article class="card"><a class="card-picture compass-cover" href="{url}" aria-label="Armaduras de Clave"><span aria-hidden="true"><span>♭</span><b>·</b><span>♯</span></span></a><div class="card-body"><span class="eyebrow">GEM · EXERCÍCIO INTERATIVO</span><h3><a href="{url}">Armaduras de Clave</a></h3><p>Preencha o pentagrama com os sinais da tonalidade, na ordem e nas posições corretas.</p><a class="read" href="{url}">Praticar agora <span aria-hidden="true">＋</span></a></div></article>'


def signatures_body(base):
    clef=(Path(__file__).parent/'assets/treble-clef.svg').read_text()
    return f'''<link rel="stylesheet" href="{base}/assets/signatures.css"><section class="category-page signature-page"><a class="text-link" href="{base}/gem/">← Voltar ao GEM</a><p class="eyebrow">GEM · ESCREVER A TONALIDADE</p><h1>Armaduras<br><em>de Clave.</em></h1><p class="lead">Escolha o sinal e preencha a armadura da tonalidade maior indicada. Escreva da esquerda para a direita, na ordem correta. Cada nota é colocada automaticamente na posição convencional da clave de Sol.</p><noscript><p>Ative o JavaScript para praticar.</p></noscript>
<div id="signature-app" hidden><div class="signature-toolbar"><div id="signature-keys" class="signature-key-buttons" role="group" aria-label="Tonalidade"></div><button id="signature-next" type="button">Sortear exercício</button><span id="signature-score">0 acertos de primeira em 0 respondidos</span></div>
<div class="signature-paper"><p class="eyebrow">COMPLETE A ARMADURA</p><h2 id="signature-title"></h2><div class="signature-tools" role="group" aria-label="Escolha o sinal"><button type="button" id="signature-sharp" aria-pressed="true"><span aria-hidden="true">♯</span> Sustenido</button><button type="button" id="signature-flat" aria-pressed="false"><span aria-hidden="true">♭</span> Bemol</button></div>
<p class="signature-hint">Escolha a nota pelos botões ou clique em sua linha ou espaço. A altura do sinal é ajustada à posição convencional da armadura. A faixa dourada marca a próxima coluna. No celular, deslize o pentagrama ou toque nos botões de notas abaixo.</p>
<div class="signature-scroll"><svg id="signature-staff" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 205" role="img" aria-label="Pentagrama em clave de Sol, ainda sem alterações"></svg></div>
<p class="signature-hint">Toque na nota para inserir o sinal na altura convencional:</p><div id="signature-positions" class="signature-position-buttons" role="group" aria-label="Notas da armadura"></div>
<p id="signature-written" class="signature-hint"></p><div class="signature-toolbar"><button type="button" id="signature-check">Conferir armadura</button><button type="button" id="signature-undo" disabled>Desfazer</button><button type="button" id="signature-clear" disabled>Limpar</button></div><p id="signature-feedback" role="status" aria-live="polite" aria-atomic="true">Preencha a armadura e confira. Em Dó maior, deixe o pentagrama sem alterações.</p></div></div>
<details class="signature-help"><summary>Revisar a ordem dos sinais</summary><p><strong>Sustenidos:</strong> Fá · Dó · Sol · Ré · Lá · Mi · Si.</p><p><strong>Bemóis:</strong> Si · Mi · Lá · Ré · Sol · Dó · Fá.</p><p>Linhas e espaços são contados de baixo para cima. O exercício confere também a altura convencional de cada sinal na clave de Sol. Uma armadura usa somente sustenidos ou somente bemóis; Dó maior não usa nenhum.</p></details></section><template id="signature-clef">{clef}</template><script type="module" src="{base}/assets/signatures.mjs"></script>'''
