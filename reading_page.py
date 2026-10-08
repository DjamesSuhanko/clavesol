"""Note reading practice, with browser-local progress."""
from pathlib import Path


def reading_card(base):
    url = f'{base}/gem/treinador-de-leitura/'
    return f'<article class="card"><a class="card-picture compass-cover" href="{url}" aria-label="Treinador de leitura"><span aria-hidden="true">𝄞 · 𝄢</span></a><div class="card-body"><span class="eyebrow">GEM · EXERCÍCIO INTERATIVO</span><h3><a href="{url}">Treinador de leitura</a></h3><p>Reconheça notas nas claves de Sol, Fá e Dó. Pratique com cronômetro e acompanhe sua evolução.</p><a class="read" href="{url}">Praticar agora ＋</a></div></article>'


def reading_body(base):
    clef = (Path(__file__).parent / 'assets/treble-clef.svg').read_text()
    return f'''<link rel="stylesheet" href="{base}/assets/reading.css">
<section class="category-page reading-page"><a class="text-link" href="{base}/gem/">← Voltar ao GEM</a>
<p class="eyebrow">GEM · LEITURA MUSICAL</p><h1>Uma nota.<br><em>Um passo adiante.</em></h1>
<p class="lead">Reconheça notas naturais nas claves de Sol, Fá e Dó. Escolha o nome, confira a explicação e ouça a nota depois de responder.</p>
<noscript>Ative o JavaScript para usar o treinador.</noscript>
<div id="reading-app" hidden>
<div class="reading-settings">
<label>Clave<select id="rd-clef"><option value="treble">Sol</option><option value="bass">Fá</option><option value="alto">Dó na 3ª linha</option><option value="tenor">Dó na 4ª linha</option></select></label>
<label>Extensão<select id="rd-level"><option value="0">Somente pentagrama</option><option value="1">Até 1 linha suplementar</option><option value="2">Até 2 linhas suplementares</option><option value="3">Até 3 linhas suplementares</option></select></label>
<label>Notas por sessão<select id="rd-length"><option>10</option><option selected>20</option><option>30</option></select></label>
<button class="button" id="rd-start" type="button">Iniciar sessão</button><button id="rd-end" type="button" disabled>Encerrar</button>
</div>
<div class="reading-stats"><span id="rd-count">Pronto para começar</span><span id="rd-score">0 acertos</span><strong id="rd-clock" aria-label="Tempo total da sessão">0,0 s</strong></div>
<div class="reading-paper">
<p id="rd-prompt">Escolha a clave e inicie uma sessão.</p>
<svg id="rd-staff" viewBox="0 0 440 310" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Pentagrama"></svg>
<div id="rd-answers" class="reading-answers" role="group" aria-label="Nome da nota"></div>
<p id="rd-feedback" role="status" aria-live="polite" aria-atomic="true"></p>
<div class="reading-actions"><button id="rd-listen" type="button" disabled>Ouvir nota</button><button class="button" id="rd-next" type="button" disabled>Próxima nota →</button></div>
<p id="rd-audio" role="status"></p>
</div>
<div class="reading-results"><h2>Sua sessão</h2><p id="rd-times">Início e término aparecerão aqui.</p><p id="rd-summary">O cronômetro começa ao iniciar. A média por resposta mede apenas o tempo para identificar cada nota; o tempo total inclui a leitura das explicações.</p></div>
<div class="reading-results"><h2>Seu progresso</h2><p id="rd-progress"></p><p id="rd-storage">Salvo apenas neste navegador e dispositivo. Limpar os dados do site remove o histórico.</p><ol id="rd-history"></ol></div>
<details class="reading-help"><summary>Como ler e praticar</summary><p>Conte as linhas de baixo para cima. A clave de Sol indica Sol na 2ª linha; a de Fá indica Fá na 4ª. Na clave de Dó, o centro do símbolo indica o dó central, na 3ª ou 4ª linha conforme a escolha.</p><p>Cada linha ou espaço vizinho corresponde ao próximo nome: Dó, Ré, Mi, Fá, Sol, Lá, Si. As linhas suplementares aparecem somente junto à nota, até três acima ou abaixo do pentagrama.</p><p>Responda pelo nome, independentemente da oitava. A correção informa também a oitava: Dó4 é o dó central. O som corresponde à altura escrita, sem transposição. Comece pelo pentagrama e aumente a extensão quando estiver confortável.</p></details>
</div></section><template id="reading-clef">{clef}</template><script type="module" src="{base}/assets/reading.mjs"></script>'''
