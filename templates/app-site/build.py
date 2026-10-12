#!/usr/bin/env python3
"""Gera somente o site público em dist/. Edite site.json e content/."""
from pathlib import Path
from string import Template
from html import escape as E
import json
import shutil
from content_markdown import read_markdown, render_home
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
    home = render_home(ROOT / 'content/index.md')
    privacy = '<article class="article">' + read_markdown(ROOT / 'content/privacy.md')[1] + '</article>'
    contact = '<article class="article contact">' + read_markdown(ROOT / 'content/contact.md')[1] + '</article>'
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
