"""Compatibility routes for collections hosted in separate Pages repositories."""
from html import escape
from xml.etree import ElementTree as ET

def write_redirects(out, base, collections):
    routes = set()
    for key, collection in collections.items():
        destinations = {'partituras/' + key: collection['url']}
        destinations.update({'partituras/' + key + '/' + slug: collection['url'] + 'partituras/' + key + '/' + slug + '/' for slug in collection['scores']})
        for route, url in destinations.items():
            routes.add(base + '/' + route + '/')
            target = out/route/'index.html'
            target.parent.mkdir(parents=True, exist_ok=True)
            safe = escape(url, quote=True)
            target.write_text(f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url={safe}"><link rel="canonical" href="{safe}"><meta name="robots" content="noindex,follow"><title>Hinário · Clave Sol</title></head><body><p>Este hinário está em seu novo endereço.</p><a href="{safe}">Abrir partitura ou hinário</a></body></html>')
    # Redirect-only routes must not remain in the blog sitemap.
    sitemap = out/'sitemap.xml'
    tree = ET.parse(sitemap)
    from urllib.parse import urlsplit
    for entry in list(tree.getroot()):
        loc = entry.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        if loc is not None and urlsplit(loc.text).path in routes:
            tree.getroot().remove(entry)
    tree.write(sitemap, encoding='utf-8', xml_declaration=True)
