"""Major scale keyboard practice for GEM."""
from compass_page import symbol


def scales_card(base):
    url=f'{base}/gem/escalas-maiores/'
    return f'<article class="card"><a class="card-picture compass-cover" href="{url}" aria-label="Escalas Maiores"><span aria-hidden="true">{symbol(4)}<b>→</b>{symbol(4)}<span>♯</span></span></a><div class="card-body"><span class="eyebrow">GEM · TECLADO INTERATIVO</span><h3><a href="{url}">Escalas Maiores</a></h3><p>Monte escalas no teclado, ouça cada nota e termine com o acorde da tônica.</p><a class="read" href="{url}">Praticar agora <span aria-hidden="true">＋</span></a></div></article>'


def scales_body(base):
    return f'''<link rel="stylesheet" href="{base}/assets/scales.css"><section class="category-page scales-page"><a class="text-link" href="{base}/gem/">← Voltar ao GEM</a><p class="eyebrow">GEM · OUVIR E CONSTRUIR</p><h1>Escalas<br><em>Maiores.</em></h1><p class="lead">Toque da tônica até a oitava, em ordem crescente. Ao completar a escala, ouça o acorde maior formado pelo 1º, 3º e 5º graus.</p><noscript><p>Ative o JavaScript para usar o teclado.</p></noscript>
<div id="scales-app" hidden><div class="scales-controls"><label for="scales-key">Tonalidade</label><select id="scales-key"></select><button id="scales-random" type="button">Sortear escala</button><label><input id="scales-mute" type="checkbox"> Sem som</label></div>
<div class="scales-panel"><p class="eyebrow" id="scales-round"></p><h2 id="scales-title"></h2><p>Sequência de intervalos: <strong>T · T · st · T · T · T · st</strong></p><p class="scales-hint">T = tom (dois semitons); st = semitom (distância entre teclas vizinhas). Conte também as teclas pretas.</p><ol id="scales-progress" aria-label="Notas da escala"></ol><p id="scales-status" role="status" aria-live="polite" aria-atomic="true"></p>
<p class="scales-hint">Comece pela tecla marcada “Início”. No celular, deslize o teclado para os lados. Cada tecla também funciona com Tab e Enter ou espaço.</p><div class="scales-keyboard-scroll"><div id="scales-keyboard" aria-label="Teclado musical"></div></div>
<div class="scales-controls scales-actions"><button id="scales-undo" type="button" disabled>Desfazer</button><button id="scales-restart" type="button">Recomeçar</button><button id="scales-listen" type="button" disabled>Ouvir escala e acorde</button></div><p id="scales-audio" role="status"></p></div></div>
<section class="scales-help"><h2>Uma estrutura, todas as tonalidades.</h2><p>As escalas maiores seguem o mesmo padrão de tons e semitons. Sustenidos e bemóis mantêm esse padrão, e cada nome de nota aparece uma vez antes da repetição da tônica.</p><p>Algumas teclas têm mais de um nome: Dó♯ e Ré♭, por exemplo, produzem o mesmo som neste teclado. Em tonalidades como Fá♯ maior ou Dó♭ maior, também aparecem Mi♯ ou Fá♭. O exercício mostra a escrita correta para a escala escolhida.</p></section></section><script type="module" src="{base}/assets/scales.mjs"></script>'''
