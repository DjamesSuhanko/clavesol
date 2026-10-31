#!/usr/bin/env python3
"""Instala o carrossel em um site Clave Sol existente, sem publicar."""
import argparse
import ast
from datetime import datetime
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / 'templates/hinario-site'
HOOK = '''# Carrossel instalado por adicionar_carrossel.py
from carousel_install import add_carousel
add_carousel(ROOT, OUT, BASE)
'''
INTEGRATION = '''"""Adiciona o banner somente à entrada e às cópias idênticas dessa página."""
from pathlib import Path
import re
import shutil
from carousel import banner, images


def add_carousel(root, out, base):
    entry = out / 'index.html'
    original = entry.read_text(encoding='utf-8')
    if 'class="collection-carousel"' in original:
        raise ValueError('A entrada já contém um carrossel; integração duplicada.')
    marker = re.search(r'<[a-z]+\\b[^>]*class=["\\\'][^"\\\']*\\blist-search\\b[^"\\\']*["\\\'][^>]*>', original)
    if not marker:
        marker = re.search(r'<div\\b[^>]*id=["\\\']hymn-search-controls["\\\'][^>]*>', original)
    if marker:
        position = marker.start()
    else:
        main = re.search(r'<main\\b[^>]*>', original)
        if not main:
            raise ValueError('Página inicial sem <main> para inserir o carrossel.')
        position = main.end()
    html = original[:position] + banner(root, base) + original[position:]
    # Os hinários também publicam a entrada em /partituras/hinos/<coleção>/.
    aliases = [p for p in out.rglob('index.html') if p.read_text(encoding='utf-8') == original]
    for path in aliases:
        path.write_text(html, encoding='utf-8')
    (out / 'carrossel').mkdir(exist_ok=True)
    for name in images(root):
        shutil.copyfile(root / 'carrossel' / name, out / 'carrossel' / name)
    (out / 'assets').mkdir(exist_ok=True)
    for name in ('carrossel.css', 'carrossel.mjs'):
        shutil.copyfile(root / 'assets' / name, out / 'assets' / name)
'''


def install(destination):
    destination = destination.expanduser().resolve()
    build = destination / 'build.py'
    if not build.is_file():
        raise ValueError('O destino precisa ser um site existente com build.py.')
    source = build.read_text(encoding='utf-8')
    ast.parse(source)
    if HOOK in source:
        print('Carrossel já instalado; nenhum arquivo alterado.')
        return
    if 'from carousel import' in source or 'from carousel_install import' in source:
        raise ValueError('Este site já possui integração de carrossel. Nenhum arquivo alterado.')
    tree = ast.parse(source)
    anchor = next((node for node in tree.body if isinstance(node, ast.Expr)
                   and isinstance(node.value, ast.Call)
                   and isinstance(node.value.func, ast.Name)
                   and node.value.func.id in ('finish_seo', 'finish_build')), None)
    if not anchor or not {'ROOT', 'OUT', 'BASE'} <= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}:
        raise ValueError('Build não compatível: esperado ROOT, OUT, BASE e finish_seo/finish_build no nível principal.')
    lines = source.splitlines(keepends=True)
    lines.insert(anchor.lineno - 1, HOOK)
    updated = ''.join(lines)
    ast.parse(updated)
    ast.parse(INTEGRATION)
    files = {name: (TEMPLATE / name).read_bytes() for name in
             ('carousel.py', 'assets/carrossel.css', 'assets/carrossel.mjs')}
    files['carousel_install.py'] = INTEGRATION.encode()
    for name in ('carrossel/padrao.svg', 'carrossel/padrao.txt'):
        if not (destination / name).exists():
            files[name] = (TEMPLATE / name).read_bytes()
    for name, data in files.items():
        target = destination / name
        if target.exists() and (not target.is_file() or target.read_bytes() != data):
            raise ValueError(f'Arquivo existente diferente: {target}. Nada foi alterado.')
    manifest = destination / '.acervo-site.json'
    if manifest.exists():
        state = json.loads(manifest.read_text(encoding='utf-8'))
        state['managed'] = sorted(set(state['managed']) | set(files))
        files['.acervo-site.json'] = (json.dumps(state, ensure_ascii=False, indent=2) + '\n').encode()
    backup = Path.home() / '.local/state/clavesol/carrossel' / (destination.name + '-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    shutil.copy2(build, backup / 'build.py')
    if manifest.exists():
        shutil.copy2(manifest, backup / manifest.name)
    for name, data in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    build.write_text(updated, encoding='utf-8')
    print(f'Carrossel instalado em {destination}\nBackup: {backup}\nExecute o build do site e faça commit/push para publicar.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destino', type=Path, required=True, help='Diretório do site existente')
    args = parser.parse_args()
    try:
        install(args.destino)
    except (ValueError, OSError, SyntaxError, KeyError) as error:
        parser.exit(1, f'Erro: {error}\n')


if __name__ == '__main__':
    main()
