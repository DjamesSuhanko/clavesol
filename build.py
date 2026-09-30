from pathlib import Path
import os,shutil,html,json
import markdown
from music_pages import build_music, featured_score
from score_catalog import load_catalog
from cache_assets import finish_build
ROOT=Path(__file__).parent; OUT=ROOT/'dist'; BASE=os.environ.get('BASE_PATH','').rstrip('/')
catalog = load_catalog(ROOT)
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir();shutil.copytree(ROOT/'assets',OUT/'assets')
E=html.escape
cats={'gem':('GEM','Grupo de Ensino Musical','Fundamentos, leitura e prática para aprender em conjunto.'),'artigos':('Artigos','Tudo sobre música','Ideias e ferramentas para a música na orquestra e em casa.'),'luthier':('Luthier','Serviços de luthier','O cuidado com o instrumento também faz parte da música.'),'links':('Links','Aplicativos musicais','Ferramentas para escrever, ouvir e compreender o som.'),'tutoriais':('Tutoriais','Dicas e técnicas','Um passo de cada vez. Mais confiança a cada ensaio.')}
def page(title,body):
 nav=''.join(f'<a href="{BASE}/{k}/">{v[0]}</a>' for k,v in cats.items())
 return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Clave Sol: partituras, ensino musical, artigos, luthier e aplicativos para a orquestra e para casa."><meta name="theme-color" content="#123b35"><title>{E(title)} · Clave Sol</title><link rel="icon" href="{BASE}/assets/icon.svg"><link rel="stylesheet" href="{BASE}/assets/style.css"></head><body><a class="skip" href="#conteudo">Pular para o conteúdo</a><div class="topline">MÚSICA PARA APRENDER, PRATICAR E COMPARTILHAR</div><header><a class="brand" href="{BASE}/"><span class="clef" aria-hidden="true">𝄞</span><span>Clave Sol<small>UM ENCONTRO COM A MÚSICA</small></span></a><nav aria-label="Principal">{nav}<a class="nav-score" href="{BASE}/partituras/">Partituras</a></nav></header><main id="conteudo">{body}</main><footer><a class="brand" href="{BASE}/"><span class="clef" aria-hidden="true">𝄞</span><span>Clave Sol<small>APRENDER. TOCAR. COMPARTILHAR.</small></span></a><p>Da primeira nota ao próximo ensaio.<br>Um espaço musical de Djames Suhanko.</p></footer><script defer src="{BASE}/assets/updates.js" data-version="__CLAVESOL_VERSION__" data-manifest="{BASE}/version.json"></script></body></html>'''
def save(route,title,body):
 target=OUT/route; target.mkdir(parents=True,exist_ok=True);(target/'index.html').write_text(page(title,body))
articles=[]
for source in sorted((ROOT/'content').glob('*.md')):
 md=markdown.Markdown(extensions=['meta','fenced_code','tables','toc']);content=md.convert(source.read_text());m=md.Meta
 a={k:m.get(k,[''])[0] for k in ['title','description','category','image','date']};a.update(slug=source.stem,content=content,toc=md.toc);articles.append(a)
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
for key,(name,subtitle,desc) in cats.items():
 matches=articles if key=='artigos' else [a for a in articles if a['category']==key]
 extra=''
 if key=='gem':extra=f'<div class="section-heading"><h2>Pratique com a partitura</h2></div>{scorecard()}'
 if key=='links':extra='''<div class="app-list"><a href="https://musescore.org/pt-br"><b>01</b><div><h2>MuseScore Studio</h2><p>Escrita de partituras · MusicXML · Código aberto</p></div><span>Visitar site oficial</span></a><a href="https://www.audacityteam.org/"><b>02</b><div><h2>Audacity</h2><p>Gravação e edição de áudio · Windows, macOS e Linux</p></div><span>Visitar site oficial</span></a><a href="https://friture.org/"><b>03</b><div><h2>Friture</h2><p>Análise de áudio em tempo real · Espectro e harmônicos</p></div><span>Visitar site oficial</span></a></div>'''
 if key=='luthier':extra=f'<div class="luthier-panel"><img src="{BASE}/assets/violin.jpg" alt="Detalhe de um instrumento de cordas"><div><p class="eyebrow">CUIDADO QUE SE OUVE</p><h2>Serviços de luthier</h2><p>Este espaço reunirá informações sobre avaliação, regulagem e manutenção de instrumentos.</p><p>Os serviços disponíveis, a região de atendimento e os contatos serão publicados aqui em breve.</p></div></div>'
 if key=='tutoriais':extra+='<div class="video-panel"><span class="video-symbol" aria-hidden="true">▷</span><div><p class="eyebrow">PARA VER E PRATICAR</p><h2>MuseScore em vídeo</h2><p>Tutoriais oficiais para começar a escrever partituras e explorar o programa. Conteúdo em inglês.</p><a class="button" href="https://musescore.org/en/tutorials">Assistir aos tutoriais oficiais</a></div></div>'
 save(key,name,f'<section class="category-page"><p class="eyebrow">CLAVE SOL / {name.upper()}</p><h1>{subtitle}<span>.</span></h1><p class="lead">{desc}</p><div class="cards">{"".join(card(a) for a in matches)}</div>{extra}</section>')
build_music(OUT,BASE,page,catalog)
(OUT/'404.html').write_text(page('Página não encontrada',f'<section class="category-page"><p class="eyebrow">PAUSA NA LEITURA · 404</p><h1>Esta página não está na estante.</h1><a class="button" href="{BASE}/">Voltar ao início</a></section>'))
(OUT/'.nojekyll').touch();print(f'{len(list(OUT.rglob("*.html")))} páginas geradas em {OUT}')

finish_build(OUT, BASE)
