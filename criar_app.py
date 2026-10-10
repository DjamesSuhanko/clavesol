#!/usr/bin/env python3
"""Cria um card em apps.json, copiando sua capa para assets/."""
import argparse
import json
from pathlib import Path
import re
import shutil
import unicodedata
from apps_catalog import validate_url
ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--titulo', required=True)
    parser.add_argument('--texto', required=True)
    parser.add_argument('--imagem', type=Path, required=True)
    parser.add_argument('--link', required=True)
    parser.add_argument('--slug', help='Identificador opcional; padrão derivado do título')
    parser.add_argument('--atualizar', action='store_true', help='Atualizar um card existente com o mesmo slug')
    args = parser.parse_args()
    try:
        validate_url(args.link)
        slug = args.slug or re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', args.titulo).encode('ascii', 'ignore').decode().lower()).strip('-')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            raise ValueError('Slug inválido.')
        if not args.titulo.strip() or not args.texto.strip():
            raise ValueError('Título e texto não podem ser vazios.')
        source = args.imagem.expanduser().resolve(strict=True)
        if source.suffix.lower() not in ('.webp', '.png', '.jpg', '.jpeg'):
            raise ValueError('Use uma capa WebP, PNG ou JPEG.')
        catalog = ROOT / 'apps.json'
        apps = json.loads(catalog.read_text()) if catalog.exists() else []
        existing = next((a for a in apps if a['slug'] == slug), None)
        if existing and not args.atualizar:
            raise ValueError('O card já existe. Use --atualizar para alterá-lo.')
        assets = ROOT / 'assets'
        destination = source if source.is_relative_to(assets.resolve()) else assets / (slug + source.suffix.lower())
        if destination != source and destination.exists() and destination.read_bytes() != source.read_bytes():
            raise ValueError('Já existe uma capa diferente nesse destino; escolha outro nome/slug ou copie manualmente para assets.')
        app = dict(slug=slug, title=args.titulo.strip(), description=args.texto.strip(), image=destination.relative_to(assets).as_posix(), url=args.link)
        if destination != source:
            shutil.copyfile(source, destination)
        if existing:
            apps[apps.index(existing)] = app
        else:
            apps.append(app)
        temporary = catalog.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(apps, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(catalog)
        print(f'Card {slug} pronto. Execute o build do site e revise antes do commit.')
    except (ValueError, OSError) as error:
        parser.error(str(error))

if __name__ == '__main__':
    main()
