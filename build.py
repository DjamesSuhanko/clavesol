from list_search import add_search
from pathlib import Path
import os,shutil,html,json
import markdown
from music_pages import build_music, featured_score
from score_catalog import load_catalog
from cache_assets import finish_build
from seo import finish_seo
from compass_page import calculator_card, calculator_body
from rhythm_page import exercise_card, exercise_body
from equivalence_page import equivalence_card, equivalence_body
from scales_page import scales_card, scales_body
from signatures_page import signatures_card, signatures_body
ROOT=Path(__file__).parent; OUT=ROOT/'dist'; BASE=os.environ.get('BASE_PATH','').rstrip('/')
catalog = load_catalog(ROOT)
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir();shutil.copyfile(ROOT/'app.webmanifest',OUT/'app.webmanifest');shutil.copytree(ROOT/'assets',OUT/'assets')
for score in catalog.scores:
 if score.sequence:
  folder=OUT/'assets'/score.assets
  (folder/'sequence.json').write_text(json.dumps(score.sequence,separators=(',',':')))
  # Generated playback does not publish the much larger optional recordings.
  for name in (() if any(other.assets == score.assets and other.playback == 'recorded' for other in catalog.scores) else ('score.mp3','score.ogg')):
   target=folder/name
   if target.exists():target.unlink()
E=html.escape
cats={'gem':('GEM','Grupo de Ensino Musical','Fundamentos, leitura e prática para aprender em conjunto.'),'artigos':('Artigos','Tudo sobre música','Ideias e ferramentas para a música na orquestra e em casa.'),'luthier':('Luthier','Serviços de luthier','O cuidado com o instrumento também faz parte da música.'),'links':('Links','Aplicativos musicais','Ferramentas para escrever, ouvir e compreender o som.'),'tutoriais':('Tutoriais','Dicas e técnicas','Um passo de cada vez. Mais confiança a cada ensaio.')}
def page(title,body):
 body=add_search(body,BASE)
 nav=''.join(f'<a href="{BASE}/{k}/">{v[0]}</a>' for k,v in cats.items())
 return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Clave Sol: partituras, ensino musical, artigos, luthier e aplicativos para a orquestra e para casa."><meta name="theme-color" content="#123b35"><title>{E(title)} · Clave Sol</title><link rel="icon" href="{BASE}/assets/icon.svg"><link rel="stylesheet" href="{BASE}/assets/style.css"><link rel="manifest" href="{BASE}/app.webmanifest"><link rel="apple-touch-icon" href="{BASE}/assets/app-icon-192.png"></head><body><a class="skip" href="#conteudo">Pular para o conteúdo</a><div class="topline">MÚSICA PARA APRENDER, PRATICAR E COMPARTILHAR</div><header><a class="brand" href="{BASE}/"><img class="brand-logo" src="{BASE}/assets/logo-clavesol.webp" alt="" width="70" height="80"><span>Clave Sol<small>UM ENCONTRO COM A MÚSICA</small></span></a><nav aria-label="Principal">{nav}<a class="nav-score" href="{BASE}/partituras/">Partituras</a></nav></header><main id="conteudo">{body}</main><footer><a class="brand" href="{BASE}/"><img class="brand-logo" src="{BASE}/assets/logo-clavesol.webp" alt="" width="70" height="80"><span>Clave Sol<small>APRENDER. TOCAR. COMPARTILHAR.</small></span></a><p>Da primeira nota ao próximo ensaio.<br>Um espaço musical de Djames Suhanko.</p><a class="social-link" href="https://www.youtube.com/@ClaveSolMusic"><svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false"><rect x="1" y="4" width="22" height="16" rx="5" fill="currentColor"/><path d="M10 8l6 4-6 4z" fill="var(--paper)"/></svg><span>Clave Sol Music<small>Nosso canal no YouTube</small></span></a></footer><script defer src="{BASE}/assets/updates.js" data-version="__CLAVESOL_VERSION__" data-manifest="{BASE}/version.json"></script></body></html>'''
def save(route,title,body):
 target=OUT/route; target.mkdir(parents=True,exist_ok=True);(target/'index.html').write_text(page(title,body))
articles=[]
for source in sorted((ROOT/'content').glob('*.md')):
 md=markdown.Markdown(extensions=['meta','fenced_code','tables','toc']);content=md.convert(source.read_text());m=md.Meta
 a={k:m.get(k,[''])[0] for k in ['title','description','category','image','date','socialimage','socialimagealt']};a.update(slug=source.stem,content=content,toc=md.toc);articles.append(a)
def card(a):
 picture=f'<img src="{BASE}/assets/{E(a["image"])}" alt="" loading="lazy">' if a['image'] else '<div class="type-art" aria-hidden="true">𝄞</div>'
 return f'<article class="card"><a class="card-picture" aria-label="{E(a['title'])}" href="{BASE}/artigos/{a["slug"]}/">{picture}</a><div class="card-body"><span class="eyebrow">{cats[a["category"]][0]}</span><h3><a href="{BASE}/artigos/{a["slug"]}/">{E(a["title"])}</a></h3><p>{E(a["description"])}</p><a class="read" href="{BASE}/artigos/{a["slug"]}/">Ler conteúdo <span aria-hidden="true">＋</span></a></div></article>'
def scorecard():
 return featured_score(catalog, BASE)
categorylinks=''.join(f'<a class="topic" href="{BASE}/{k}/"><span class="topic-number">0{i+1}</span><strong>{v[0]}</strong><span>{v[1]}</span></a>' for i,(k,v) in enumerate(cats.items()))
body=f'''<section class="hero"><div class="hero-copy"><p class="eyebrow">SEU ESPAÇO DE CULTURA MUSICAL</p><h1>A música nos une.<br><em>O conhecimento<br>nos transforma.</em></h1><p class="lead">Partituras, descobertas e boas ideias para levar do estudo em casa à próxima apresentação.</p><div class="actions"><a class="button" href="{BASE}/partituras/">Explorar partituras</a><a class="text-link" href="{BASE}/gem/">Conhecer o GEM</a></div><p class="hero-note">PARA QUEM APRENDE. PARA QUEM ENSINA. PARA QUEM TOCA.</p></div><div class="hero-photo"><img src="{BASE}/assets/clarinet.jpg" alt="Detalhe das chaves e do corpo de um clarinete"><div class="photo-caption"><span>DA PRIMEIRA NOTA<br>À MÚSICA QUE FICA.</span><span aria-hidden="true">𝄞</span></div></div></section><div class="topics">{categorylinks}</div><section class="section"><div class="section-heading"><div><p class="eyebrow">LEITURAS PARA O SEU REPERTÓRIO</p><h2>Entre notas e ideias<span>.</span></h2></div><a class="text-link" href="{BASE}/artigos/">Todos os artigos</a></div><div class="cards">{''.join(card(a) for a in articles[:3])}</div></section><section class="score-feature"><div><p class="eyebrow">ESTANTE DE PARTITURAS</p><h2>Sua próxima prática<br>começa aqui.</h2><p>Abra a partitura, ouça cada passagem e encontre o seu tempo. Música para estudar com atenção.</p><a class="text-link" href="{BASE}/partituras/">Conhecer o acervo</a></div>{scorecard()}</section><section class="gem-banner"><div><p class="eyebrow">GEM · GRUPO DE ENSINO MUSICAL</p><h2>Crescer na música.<br>Aprender em conjunto.</h2></div><div><p>Leitura, ritmo e escuta: uma base para cada novo músico. Materiais de apoio para acompanhar o aprendizado dentro e fora da aula.</p><a class="button" href="{BASE}/gem/">Acessar o material de estudo</a></div></section>'''
save('', 'Partituras, aprendizado e inspiração',body)
for a in articles:
 save('artigos/'+a['slug'],a['title'],f'<section class="article-layout"><a class="text-link" href="{BASE}/{a["category"]}/">{cats[a["category"]][0]}</a><p class="eyebrow">CADERNO CLAVE SOL</p><h1>{E(a["title"])}</h1><p class="lead">{E(a["description"])}</p><div class="article-grid"><article class="prose">{a["content"].replace("{{BASE}}",BASE)}</article><aside><h2>Nesta leitura</h2>{a["toc"]}<a href="{BASE}/partituras/">Estante de partituras</a></aside></div></section>')
save('gem/calculadora-de-compasso','Calculadora de Compasso',calculator_body(BASE))
save('gem/exercicio-de-compasso','Exercício de Compasso',exercise_body(BASE))
save('gem/correspondencia-de-valores','Correspondência de Valores',equivalence_body(BASE))
save('gem/escalas-maiores','Escalas Maiores',scales_body(BASE))
save('gem/armaduras-de-clave','Armaduras de Clave',signatures_body(BASE))
for key,(name,subtitle,desc) in cats.items():
 matches=articles if key=='artigos' else [a for a in articles if a['category']==key]
 extra=''
 if key=='gem':extra=f'<div class="section-heading"><h2>Pratique com a partitura</h2></div>{scorecard()}'
 if key=='luthier' and not matches:extra=f'<div class="luthier-panel"><img src="{BASE}/assets/violin.jpg" alt="Detalhe de um instrumento de cordas"><div><p class="eyebrow">CUIDADO QUE SE OUVE</p><h2>Serviços de luthier</h2><p>Este espaço reunirá informações sobre avaliação, regulagem e manutenção de instrumentos.</p><p>Os serviços disponíveis, a região de atendimento e os contatos serão publicados aqui em breve.</p></div></div>'
 if key=='tutoriais':extra+='<div class="video-panel"><span class="video-symbol" aria-hidden="true">▷</span><div><p class="eyebrow">PARA VER E PRATICAR</p><h2>MuseScore em vídeo</h2><p>Tutoriais oficiais para começar a escrever partituras e explorar o programa. Conteúdo em inglês.</p><a class="button" href="https://musescore.org/en/tutorials">Assistir aos tutoriais oficiais</a></div></div>'
 listing='<div class="cards">'+''.join(card(a) for a in matches)+'</div>'
 if key=='gem':
  tools=calculator_card(BASE)+exercise_card(BASE)+equivalence_card(BASE)+scales_card(BASE)+signatures_card(BASE)
  listing=f'<section class="gem-region" aria-labelledby="gem-tools"><div class="section-heading"><div><p class="eyebrow">APRENDER FAZENDO</p><h2 id="gem-tools">Ferramentas e exercícios</h2></div></div><div class="cards">{tools}</div></section><section class="gem-region" aria-labelledby="gem-articles"><div class="section-heading"><div><p class="eyebrow">PARA LER E APROFUNDAR</p><h2 id="gem-articles">Artigos do GEM</h2></div></div>{listing}</section>'
 save(key,name,f'<section class="category-page"><p class="eyebrow">CLAVE SOL / {name.upper()}</p><h1>{subtitle}<span>.</span></h1><p class="lead">{desc}</p>{listing}{extra}</section>')
external_hymns = json.loads((ROOT/'external_hymns.json').read_text())
build_music(OUT,BASE,page,catalog,external_hymns)
page_aliases = json.loads((ROOT/'page_aliases.json').read_text())
for old, new in page_aliases.items():
 target = OUT/old/'index.html'
 source = OUT/new/'index.html'
 if target.exists() or not source.is_file():
  raise ValueError(f'Alias de página inválido: {old} -> {new}')
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(source.read_text())

(OUT/'404.html').write_text(page('Página não encontrada',f'<section class="category-page"><p class="eyebrow">PAUSA NA LEITURA · 404</p><h1>Esta página não está na estante.</h1><a class="button" href="{BASE}/">Voltar ao início</a></section>'))
(OUT/'.nojekyll').touch();print(f'{len(list(OUT.rglob("*.html")))} páginas geradas em {OUT}')

seo_metadata = {'artigos/' + a['slug']: {**a, 'type': 'article'} for a in articles}
seo_metadata.update({key: {'description': values[2]} for key, values in cats.items()})
seo_metadata.update({'partituras/' + key: {'description': group.description} for key, group in catalog.groups.items()})
seo_metadata.update({score.route: {'description': score.description} for score in catalog.scores})
seo_aliases = {'musica': 'partituras', 'musica/msa': 'partituras/msa'}
seo_aliases.update(page_aliases)
seo_aliases.update({score.legacy: score.route for score in catalog.scores if score.legacy})
finish_seo(OUT, BASE, json.loads((ROOT/'seo.json').read_text()), seo_metadata, seo_aliases)
# Keep shared score URLs usable after moving the collections to separate sites.
from external_hymns import write_redirects
write_redirects(OUT, BASE, external_hymns)
finish_build(OUT, BASE)
