"""Composer navigation without changing the existing player or asset addresses."""
from html import escape as E
import json
from music_pages import score_card


def build_composers(root,out,base,catalog,page):
    path=root/'compositores.json'
    data=json.loads(path.read_text()) if path.exists() else {}
    mapped=data.get('scores',{})
    groups=data.get('groups',{})
    grouped={}
    for score in catalog.scores:
        key=mapped.get(score.key)
        if key in groups:grouped.setdefault(key,[]).append(score)
    if not grouped:return None
    ungrouped=[s for s in catalog.scores if s.key not in mapped or mapped[s.key] not in groups]
    other='sem-compositor'
    while other in groups:other+='-raiz'
    if ungrouped:grouped[other]=ungrouped
    names={**groups,other:'Outras partituras'}
    cards=[]
    for key in sorted(grouped,key=lambda k:names[k].casefold()):
        name=names[key];scores=grouped[key];url=f'{base}/compositores/{key}/'
        cards.append(f'<article class="card"><div class="card-body"><p class="eyebrow">{len(scores)} partitura(s)</p><h2><a href="{url}">{E(name)}</a></h2><p>Partituras de {E(name)}.</p><a class="text-link" href="{url}">Explorar {E(name)}</a></div></article>')
        body=f'<section class="category-page"><a class="text-link" href="{base}/">Todos os compositores</a><p class="eyebrow">ESTANTE DE PARTITURAS</p><h1>{E(name)}</h1><p class="lead">Encontre uma música nesta coleção.</p><div class="score-list">'+''.join(score_card(s,base,catalog) for s in scores)+'</div></section>'
        target=out/'compositores'/key;target.mkdir(parents=True,exist_ok=True)
        (target/'index.html').write_text(page(name,body))
        for score in scores:
            target=out/score.route/'index.html'
            html=target.read_text()
            marker='<nav class="breadcrumbs" aria-label="Caminho da partitura">'
            html=html.replace(marker,marker+f'<a href="{url}">{E(name)}</a><span>/</span>',1)
            target.write_text(html)
    collection=catalog.groups['hinos/acervo']
    return page(collection.title,f'<section class="category-page"><a class="text-link" href="https://clavesol.com.br/partituras/">Partituras</a><p class="eyebrow">ESTANTE DE PARTITURAS</p><h1>{E(collection.title)}</h1><p class="lead">{E(collection.description)}</p><div class="prose">{collection.body.replace("{{BASE}}",base)}</div><div class="cards">'+''.join(cards)+'</div></section>')
