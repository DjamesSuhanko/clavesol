"""Musicool's rhythm calculator adapted to the Clave Sol website."""
NAMES = {1: 'Semibreve', 2: 'Mínima', 4: 'Semínima', 8: 'Colcheia', 16: 'Semicolcheia'}


def symbol(den, rest=False):
    if not rest:
        fill = 'fill="none" stroke="currentColor" stroke-width="3"' if den in (1, 2) else 'fill="currentColor"'
        body = f'<ellipse cx="23" cy="44" rx="10" ry="6" transform="rotate(-20 23 44)" {fill}/>'
        if den != 1:
            body += '<path d="M32 42V8" fill="none" stroke="currentColor" stroke-width="3"/>'
        if den >= 8:
            body += '<path d="M32 8c0 10 18 11 10 26 2-12-10-10-10-15" fill="currentColor"/>'
        if den == 16:
            body += '<path d="M32 18c0 10 18 11 10 26 2-12-10-10-10-15" fill="currentColor"/>'
    elif den in (1, 2):
        body = f'<path d="M12 30h34" stroke="currentColor" stroke-width="2"/><path d="M19 {30 if den == 1 else 23}h20v7H19z" fill="currentColor"/>'
    elif den == 4:
        body = '<path d="M27 7l10 12-8 11 9 13c-16-10-18 2-9 10-17-5-15-20-2-19l-10-12 10-9z" fill="currentColor"/>'
    else:
        body = '<path d="M38 16L26 51" stroke="currentColor" stroke-width="3"/><path d="M37 17c-7 9-16 11-18 4-2-7 9-9 10-2 2 3 5 1 8-2" fill="currentColor"/>'
        if den == 16:
            body += '<path d="M33 30c-7 9-16 11-18 4-2-7 9-9 10-2 2 3 5 1 8-2" fill="currentColor"/>'
    return f'<svg viewBox="0 0 60 60" aria-hidden="true" focusable="false">{body}</svg>'


def calculator_card(base):
    url = f'{base}/gem/calculadora-de-compasso/'
    return f'<article class="card"><a class="card-picture compass-cover" href="{url}" aria-label="Calculadora de Compasso"><span aria-hidden="true">{symbol(4)}<b>+</b>{symbol(8)}<b>=</b><span>?</span></span></a><div class="card-body"><span class="eyebrow">GEM · FERRAMENTA INTERATIVA</span><h3><a href="{url}">Calculadora de Compasso</a></h3><p>Some notas e pausas, explore figuras pontuadas e confira a duração da sua sequência.</p><a class="read" href="{url}">Abrir calculadora <span aria-hidden="true">＋</span></a></div></article>'


def calculator_body(base):
    groups = ''
    for rest, title in [(False, 'Notas'), (True, 'Pausas')]:
        buttons = ''.join(f'<button type="button" class="compass-key" data-den="{den}" data-rest="{str(rest).lower()}" aria-label="Adicionar {"pausa de " if rest else ""}{name.lower()}">{symbol(den, rest)}<span>{name}</span><small>1/{den}</small></button>' for den, name in NAMES.items())
        groups += f'<fieldset><legend>{title}</legend><div class="compass-keys">{buttons}</div></fieldset>'
    return f'''<link rel="stylesheet" href="{base}/assets/compass.css">
<section class="category-page compass-page">
<a class="text-link" href="{base}/gem/">← Voltar ao GEM</a>
<p class="eyebrow">GEM · APRENDER NA PRÁTICA</p><h1>Calculadora de<br><em>Compasso.</em></h1>
<p class="lead">Monte uma sequência de notas e pausas. Veja como cada figura contribui para a duração total.</p>
<noscript><p>Ative o JavaScript do navegador para usar a calculadora.</p></noscript>
<div id="compass-calculator" class="compass-layout"><div class="compass-workspace">{groups}
<div class="compass-edit"><button type="button" id="compass-dot" disabled>Ponto de aumento ·</button><button type="button" id="compass-undo" disabled>Desfazer</button><button type="button" id="compass-clear" disabled>Limpar</button></div>
<p class="compass-hint">O ponto acrescenta metade do valor da última figura. Um ponto por figura, como no Musicool.</p>
<div class="compass-sequence-heading"><h2>Sua sequência</h2><span id="compass-count">0 figuras</span></div>
<ol id="compass-sequence" aria-label="Sequência de figuras"></ol><p id="compass-empty">Escolha uma figura acima para começar.</p><p id="compass-notice" role="status"></p></div>
<aside class="compass-result" aria-label="Resultado da calculadora"><p class="eyebrow">A SOMA DO SEU RITMO</p>
<div id="compass-signature" class="compass-signature" aria-hidden="true"><span>—</span></div><p id="compass-result-text" role="status" aria-live="polite" aria-atomic="true">Adicione notas ou pausas para calcular.</p>
<label for="compass-unit">Unidade de contagem</label><select id="compass-unit"><option value="auto">Automática (como no Musicool)</option><option value="1">Semibreve · /1</option><option value="2">Mínima · /2</option><option value="4">Semínima · /4</option><option value="8">Colcheia · /8</option><option value="16">Semicolcheia · /16</option><option value="32">Fusa · /32</option></select>
<dl><div><dt>Total em semibreves</dt><dd id="compass-total">0</dd></div><div><dt>Equivalência em semínimas</dt><dd id="compass-quarters">0</dd></div></dl><p class="compass-hint">No modo automático, a calculadora prefere a semínima quando a soma permite.</p></aside></div>
<section class="compass-explanation"><p class="eyebrow">PARA EXPERIMENTAR</p><h2>Uma soma, diferentes leituras.</h2><p>Três semínimas e seis colcheias têm a mesma duração total. Isso não torna 3/4 e 6/8 o mesmo compasso: o agrupamento e os acentos são diferentes. A calculadora mostra uma equivalência de duração; a fórmula de compasso depende também da organização da música.</p>
<div class="compass-examples"><button type="button" data-example="3/4">Experimentar 3/4</button><button type="button" data-example="4/4">Experimentar 4/4</button><button type="button" data-example="6/8">Experimentar 6/8</button></div>
<p class="compass-hint">Os exemplos substituem a sequência atual. Notas e pausas de uma mesma figura têm a mesma duração. Aqui, a pausa de semibreve vale uma semibreve; a pausa de compasso inteiro pode ter outro valor conforme a fórmula.</p><p class="compass-credit">Adaptada da calculadora do Musicool para o GEM do Clave Sol.</p></section></section>
<script type="module" src="{base}/assets/compass.mjs"></script>'''
