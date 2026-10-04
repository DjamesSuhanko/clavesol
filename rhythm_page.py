"""Random time-signature practice for GEM."""
from compass_page import symbol


def exercise_card(base):
    url = f'{base}/gem/exercicio-de-compasso/'
    return f'<article class="card"><a class="card-picture compass-cover" href="{url}" aria-label="Exercício de Compasso"><span aria-hidden="true">{symbol(2)}{symbol(8)}<span>?</span></span></a><div class="card-body"><span class="eyebrow">GEM · EXERCÍCIO INTERATIVO</span><h3><a href="{url}">Exercício de Compasso</a></h3><p>Leia as figuras no pentagrama e escolha a fórmula que completa o compasso.</p><a class="read" href="{url}">Praticar agora <span aria-hidden="true">＋</span></a></div></article>'


def exercise_body(base):
    return f'''<link rel="stylesheet" href="{base}/assets/rhythm.css">
<section class="category-page rhythm-page"><a class="text-link" href="{base}/gem/">← Voltar ao GEM</a>
<p class="eyebrow">GEM · PRATICAR A LEITURA</p><h1>Qual é o<br><em>compasso?</em></h1>
<p class="lead">Some a duração das notas e escolha, entre as duas alternativas, a fórmula que completa este compasso.</p>
<noscript><p>Ative o JavaScript para gerar os exercícios.</p></noscript>
<div id="rhythm-exercise" hidden><div class="rhythm-toolbar"><span id="rhythm-round"></span><span id="rhythm-score">0 acertos de primeira em 0 respondidos</span></div>
<div class="rhythm-paper"><div id="rhythm-staff"></div><details><summary>Ler as figuras em texto</summary><p id="rhythm-notes"></p></details>
<fieldset id="rhythm-options"><legend>Qual fórmula corresponde à duração total?</legend></fieldset>
<p id="rhythm-feedback" role="status" aria-live="polite" aria-atomic="true">Escolha uma alternativa.</p>
<button type="button" id="rhythm-next" class="button">Próximo exercício →</button></div></div>
<section class="rhythm-help"><h2>Olhe para as figuras.</h2><p>A altura das notas não muda sua duração. A semibreve vale quatro semínimas; a mínima, duas; a colcheia, metade. O ponto de aumento acrescenta metade do valor da figura.</p><p>Cada desenho representa um único compasso completo. As alternativas sempre têm durações totais diferentes: fórmulas como 3/4 e 6/8 não são colocadas uma contra a outra, pois a soma sozinha não distingue o agrupamento dos tempos.</p><a class="text-link" href="{base}/gem/calculadora-de-compasso/">Revisar com a Calculadora de Compasso →</a></section></section>
<script type="module" src="{base}/assets/rhythm.mjs"></script>'''
