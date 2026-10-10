#!/usr/bin/env python3
"""Gera somente o site público em dist/. Edite site.json e content/."""
from pathlib import Path
from string import Template
from html import escape as E
import json
import shutil
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'


def build():
    config = json.loads((ROOT / 'site.json').read_text())
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / 'assets', OUT / 'assets')
    shutil.copyfile(ROOT / 'CNAME', OUT / 'CNAME')
    (OUT / '.nojekyll').touch()
    app, author, email, description = (E(config[key], quote=True) for key in ('title', 'author', 'email', 'description'))
    origin = 'https://' + config['domain']
    template = Template((ROOT / 'templates/base.html').read_text())
    home = f'<section class="hero"><div><p class="eyebrow">Aplicativos Clave Sol</p><h1>{app}</h1><p class="lead">{description}</p><div class="actions"><a class="button" href="/privacidade/">Política de privacidade</a><a class="text-link" href="/contato/">Entrar em contato</a></div></div><img class="hero-logo" src="/assets/{E(config["logo"])}" alt="{app}" width="300" height="300"></section>'
    home += '<section class="article">' + (ROOT / 'content/home.html').read_text() + '</section>'
    privacy = '<article class="article">' + (ROOT / 'content/privacy.html').read_text() + '</article>'
    contact = f'<article class="article contact"><p class="eyebrow">{app} · Clave Sol</p><h1>Contato</h1><h2>{author}</h2><p><a class="contact-mail" href="mailto:{email}">{email}</a></p></article>'
    pages = [('/', config['title'], home), ('/privacidade/', 'Política de privacidade', privacy), ('/contato/', 'Contato', contact), ('/404.html', 'Página não encontrada', '<article class="article"><h1>Página não encontrada</h1><a href="/">Voltar ao início</a></article>')]
    for route, title, body in pages:
        nav = ''.join(f'<a href="{url}"' + (' aria-current="page"' if url == route else '') + f'>{label}</a>' for url, label in [('/', app), ('/privacidade/', 'Privacidade'), ('/contato/', 'Contato')])
        rendered = template.substitute(title=E(title), description=description, base='', origin=origin, canonical=route, logo=E(config['logo']), app=app, author=author, robots='<meta name="robots" content="noindex,follow">' if route == '/404.html' or (route == '/privacidade/' and not config['privacy_ready']) else '', navigation=nav, body=body)
        path = OUT / (route.lstrip('/') + ('index.html' if route.endswith('/') else ''))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered)
    (OUT / 'privacy.html').write_text((OUT / 'privacidade/index.html').read_text())
    (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + origin + '/sitemap.xml\n')
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + E(origin + route) + '</loc></url>' for route, _, _ in pages if route != '/404.html' and (route != '/privacidade/' or config['privacy_ready'])) + '</urlset>')
    print('Site gerado em', OUT)

if __name__ == '__main__':
    build()
