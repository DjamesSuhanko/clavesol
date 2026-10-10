"""Catálogo independente de aplicativos com destino externo."""
import html
import json
from urllib.parse import urlsplit


def validate_url(value):
    url = urlsplit(value)
    if url.scheme not in ('https', 'http') or not url.hostname or url.username or any(c.isspace() for c in value):
        raise ValueError('Informe um link http:// ou https:// válido.')
    return value


def apps_body(root, base):
    cards = []
    for app in json.loads((root / 'apps.json').read_text()):
        url = html.escape(validate_url(app['url']), quote=True)
        image = (root / 'assets' / app['image']).resolve()
        if not image.is_relative_to((root / 'assets').resolve()) or not image.is_file():
            raise ValueError(f'Capa inexistente: {app["image"]}')
        title, description, cover = (html.escape(app[k], quote=True) for k in ('title', 'description', 'image'))
        cards.append(f'<article class="card"><a class="card-picture" href="{url}" aria-label="{title}"><img src="{base}/assets/{cover}" alt="" loading="lazy"></a><div class="card-body"><span class="eyebrow">APLICATIVOS CLAVE SOL</span><h3><a href="{url}">{title}</a></h3><p>{description}</p><a class="read" href="{url}">Conhecer o aplicativo <span aria-hidden="true">→</span></a></div></article>')
    return '<section class="category-page"><p class="eyebrow">CLAVE SOL / APPS</p><h1>Aplicativos Clave Sol<span>.</span></h1><p class="lead">Ferramentas para estudar, praticar e cuidar dos instrumentos.</p><div class="cards">' + ''.join(cards) + '</div></section>'
