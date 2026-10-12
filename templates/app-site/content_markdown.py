"""Conteúdo editorial Markdown com apresentação visual Clave Sol."""
from pathlib import Path
import html
import re
import markdown


def read_markdown(path, base=''):
    parser = markdown.Markdown(extensions=['meta', 'fenced_code', 'tables'])
    body = parser.convert(Path(path).read_text().replace('{{BASE}}', base))
    return {key: ' '.join(value) for key, value in parser.Meta.items()}, body


def render_home(path, base=''):
    meta, body = read_markdown(path, base)
    title = html.escape(meta['title'])
    description = html.escape(meta['description'])
    image = html.escape(meta['image'], quote=True)
    if not re.fullmatch(r'[a-zA-Z0-9_. /-]+', meta['image']) or '..' in meta['image'] or meta['image'].startswith('/'):
        raise ValueError('Image deve ser um caminho relativo dentro de assets/.')
    hero = f'<section class="hero" aria-labelledby="app-title"><div><p class="eyebrow">Aplicativos Clave Sol</p><h1 id="app-title">{title}</h1><p class="lead">{description}</p><div class="actions"><a class="button" href="{base}/privacidade/">Política de privacidade</a><a class="text-link" href="{base}/contato/">Entrar em contato</a></div></div><img class="hero-logo" src="{base}/assets/{image}" alt="Logo {title}" width="300" height="300"></section>'
    # A apresentação é prosa contínua, independente dos blocos fixos do index.
    presentation_path = Path(path).with_name('apresentacao.md')
    if presentation_path.exists():
        presentation = markdown.markdown(
            presentation_path.read_text().replace('{{BASE}}', base),
            extensions=['fenced_code', 'tables'])
        if re.search(r'<h1[ >]', presentation):
            raise ValueError('Use títulos ## ou inferiores em apresentacao.md; o topo já contém o título principal.')
        if re.sub(r'<!--.*?-->', '', presentation, flags=re.S).strip():
            hero += '<section class="article app-presentation" aria-label="Sobre o aplicativo">' + presentation + '</section>'
    # O corpo do index mantém os blocos de privacidade e contato existentes.
    sections = re.split(r'(?=<h2[ >])', body)
    intro = sections.pop(0)
    if intro.strip():
        hero += '<section class="article">' + intro + '</section>'
    if sections:
        hero += '<section class="public-links" aria-label="Informações do aplicativo">' + ''.join('<div>' + section + '</div>' for section in sections) + '</section>'
    return hero
