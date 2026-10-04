"""Interactive practice for equivalent note and rest values."""
from compass_page import NAMES, symbol


def equivalence_card(base):
    url = f'{base}/gem/correspondencia-de-valores/'
    return f'<article class="card"><a class="card-picture compass-cover" href="{url}" aria-label="Correspondência de Valores"><span aria-hidden="true">{symbol(8)}{symbol(8)}<b>=</b>{symbol(4)}</span></a><div class="card-body"><span class="eyebrow">GEM · EXERCÍCIO INTERATIVO</span><h3><a href="{url}">Correspondência de Valores</a></h3><p>Transforme um grupo de figuras em outra combinação com a mesma duração.</p><a class="read" href="{url}">Praticar agora <span aria-hidden="true">＋</span></a></div></article>'


def equivalence_body(base):
    keys = ''
    for rest in (False, True):
        buttons = ''.join(f'<button type="button" class="compass-key" data-value="{den}" data-rest="{str(rest).lower()}" aria-label="Adicionar {"pausa de " if rest else ""}{name.lower()}">{symbol(den,rest)}<span>{name}</span></button>' for den,name in NAMES.items())
        keys += f'<div class="compass-keys" data-kind="{str(rest).lower()}" hidden>{buttons}</div>'
    return f'''<link rel="stylesheet" href="{base}/assets/compass.css"><link rel="stylesheet" href="{base}/assets/equivalence.css">
<section class="category-page compass-page equivalence-page"><a class="text-link" href="{base}/gem/">← Voltar ao GEM</a>
<p class="eyebrow">GEM · PRATICAR OS VALORES</p><h1>Correspondência<br><em>de Valores.</em></h1>
<p class="lead">Monte uma resposta com a mesma duração do grupo apresentado. Você pode usar uma única figura ou uma combinação diferente.</p>
<noscript><p>Ative o JavaScript para praticar.</p></noscript>
<div id="equivalence" hidden><div class="equivalence-toolbar"><span id="eq-round"></span><span id="eq-score">0 acertos de primeira em 0 respondidos</span></div>
<div class="compass-workspace"><h2 id="eq-prompt">Transforme estas figuras</h2><ol class="eq-sequence" id="eq-question" aria-label="Figuras do enunciado"></ol>
<p class="compass-hint">Mantenha o tipo: notas correspondem a notas; pausas, a pausas. Copiar as mesmas figuras, mesmo em outra ordem, não vale.</p>
<fieldset><legend>Monte sua resposta</legend>{keys}</fieldset>
<ol class="eq-sequence eq-answer" id="eq-answer" aria-label="Sua resposta"></ol><p id="eq-empty">Escolha as figuras nos botões acima.</p>
<div class="compass-edit"><button id="eq-check" type="button" disabled>Conferir resposta</button><button id="eq-undo" type="button" disabled>Desfazer</button><button id="eq-clear" type="button" disabled>Limpar</button></div>
<p id="eq-feedback" role="status" aria-live="polite" aria-atomic="true"></p>
<button id="eq-next" type="button">Próximo exercício →</button></div></div>
<section class="compass-explanation"><h2>O valor é o mesmo. A escrita muda.</h2><p>Duas colcheias correspondem a uma semínima; quatro semínimas, a uma semibreve. As pausas seguem os mesmos valores. Aqui, a pausa de semibreve representa o valor da figura, não uma pausa de compasso inteiro.</p><p>Cada carregamento e cada clique em “Próximo exercício” geram um novo grupo aleatório. Sempre existe uma solução com uma única figura, mas outras combinações equivalentes também são aceitas.</p><a class="text-link" href="{base}/gem/calculadora-de-compasso/">Revisar com a calculadora →</a></section></section>
<script type="module" src="{base}/assets/equivalence.mjs"></script>'''
