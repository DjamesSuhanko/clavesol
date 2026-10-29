#!/usr/bin/env python3
"""Atualiza carrossel e publicacao dos catalogos em sites Clave Sol locais.

Usa recursos locais do template, conserva os dados e as imagens proprias de cada
site, atualiza builds antigos e faz copia de seguranca antes de sobrescrever.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_TEMPLATE = Path('/home/djames/Documents/ClaveSol/SITE/clavesol/templates/hinario-site')
REQUIRED_TEMPLATE_FILES = (
    'carousel.py', 'assets/carrossel.css', 'assets/carrossel.mjs',
    'carrossel/padrao.svg',
)
# Modulos adicionais somente se o build depender deles e nao houver copia local.
OPTIONAL_MODULES = ('composer_pages.py',)
START = '# >>> CLAVE SOL CARROSSEL E CATALOGO - INICIO'
END = '# <<< CLAVE SOL CARROSSEL E CATALOGO - FIM'

# Aplicado antes de finish_build(): fornece os assets (mesmo se nao constarem do
# inventario .acervo-site.json), inclui o banner na entrada e publica JSONs.
INTEGRATION = '''\n''' + START + '''
# Recursos do carrossel e catalogos do Mose; nao altera os MusicXML.
from carousel import banner as _clavesol_banner, images as _clavesol_images
import hashlib as _clavesol_hashlib
import re as _clavesol_re

for _name in ('carrossel.css', 'carrossel.mjs'):
    _src = ROOT / 'assets' / _name
    _dst = OUT / 'assets' / _name
    if not _src.is_file():
        raise FileNotFoundError(f'Recurso do carrossel ausente: {_src}')
    _dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(_src, _dst)

(OUT / 'carrossel').mkdir(parents=True, exist_ok=True)
for _name in _clavesol_images(ROOT):
    shutil.copy2(ROOT / 'carrossel' / _name, OUT / 'carrossel' / _name)

# A entrada pode ser diferente em um hinario antigo, na Harpa ou em musicas.
_clavesol_collection = config['collection']
_clavesol_route = ('partituras/musicas' if _clavesol_collection == 'musicas'
                    else 'partituras/hinos/' + _clavesol_collection)
for _relative in ('index.html', _clavesol_route + '/index.html'):
    _target = OUT / _relative
    if not _target.is_file():
        continue
    _html = _target.read_text(encoding='utf-8')
    if 'class="collection-carousel"' in _html:
        continue  # Evita carrossel duplicado em builds modernos.
    _banner = _clavesol_banner(ROOT, BASE)
    _match = _clavesol_re.search(r'<div\\s+class=["\\\']list-search["\\\'][^>]*>', _html)
    if not _match:
        _match = _clavesol_re.search(r'<div\\s+class=["\\\']prose["\\\'][^>]*>', _html)
    if _match:
        _html = _html[:_match.start()] + _banner + _html[_match.start():]
    elif '<main id="conteudo">' in _html:
        _html = _html.replace('<main id="conteudo">', '<main id="conteudo">' + _banner, 1)
    else:
        raise ValueError(f'Nao foi encontrado o ponto de insercao do carrossel em {_target}')
    _target.write_text(_html, encoding='utf-8')

_clavesol_json = ROOT / 'cardapio.json'
_clavesol_sha = ROOT / 'cardapio.sha256'
if _clavesol_json.is_file() != _clavesol_sha.is_file():
    raise ValueError('cardapio.json e cardapio.sha256 devem existir juntos na raiz do site')
if _clavesol_json.is_file():
    _payload = _clavesol_json.read_bytes()
    json.loads(_payload.decode('utf-8'))
    _expected = _clavesol_sha.read_text(encoding='utf-8').strip().split()[0].lower()
    _actual = _clavesol_hashlib.sha256(_payload).hexdigest()
    if _expected != _actual:
        raise ValueError('cardapio.sha256 nao corresponde ao cardapio.json')
    shutil.copy2(_clavesol_json, OUT / 'cardapio.json')
    shutil.copy2(_clavesol_sha, OUT / 'cardapio.sha256')
else:
    print('Aviso: sem cardapio.json/sha256 na raiz; publicacao do catalogo ignorada')
''' + END + '''\n'''


def legacy_build(source: str) -> bool:
    """O template novo depende de manifesto; builds legados nao."""
    return '.acervo-site.json' not in source and 'from apps_catalog import' not in source


def get_legacy_from_git(destination: Path) -> str | None:
    """Recupera a ultima versao anterior ao template, sem mexer no indice Git."""
    try:
        result = subprocess.run(
            ['git', '-C', str(destination), 'log', '--all', '--format=%H', '--', 'build.py'],
            check=True, capture_output=True, text=True, timeout=15)
        for sha in result.stdout.splitlines()[:80]:
            candidate = subprocess.run(
                ['git', '-C', str(destination), 'show', f'{sha}:build.py'],
                capture_output=True, text=True, timeout=15)
            if candidate.returncode == 0 and legacy_build(candidate.stdout) and 'finish_build(' in candidate.stdout:
                ast.parse(candidate.stdout)
                return candidate.stdout
    except (OSError, subprocess.SubprocessError, SyntaxError):
        return None
    return None


def patch_build(code: str) -> str:
    """Injeta integracao idempotente antes do ultimo finish_build()."""
    if START in code:
        if END not in code:
            raise ValueError('Marcador de integracao incompleto no build.py')
        return code
    if 'from apps_catalog import' in code:
        raise ValueError('build.py parece ser do site principal, e nao de um acervo')
    if 'config' not in code or 'ROOT' not in code or 'OUT' not in code:
        raise ValueError('build.py nao tem a estrutura esperada de um acervo Clave Sol')
    matches = list(re.finditer(r'(?m)^\s*finish_build\s*\(\s*OUT\s*,\s*BASE\s*\)\s*$', code))
    if len(matches) != 1:
        raise ValueError('Nao foi encontrada uma chamada unica de finish_build(OUT, BASE)')
    pos = matches[0].start()
    out = code[:pos].rstrip() + '\n' + INTEGRATION + '\n' + code[pos:].lstrip('\n')
    ast.parse(out)
    return out


def compile_check(path: Path, content: bytes) -> None:
    if path.suffix == '.py':
        compile(content.decode('utf-8'), str(path), 'exec')


def project_ok(dest: Path) -> bool:
    return dest.is_dir() and (dest / 'hinario.json').is_file() and (dest / 'build.py').is_file()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destinos', nargs='+', type=Path,
                        help='Raizes locais dos sites (um ou varios diretorios)')
    parser.add_argument('--template', type=Path, default=DEFAULT_TEMPLATE,
                        help='Pasta local templates/hinario-site')
    parser.add_argument('--dry-run', action='store_true', help='Mostra mudancas sem copiar nada')
    parser.add_argument('--template-build', action='store_true',
                        help='Substitui build.py pelo do template SOMENTE em projetos com .acervo-site.json')
    args = parser.parse_args(argv)
    template = args.template.expanduser().resolve()
    missing = [f for f in REQUIRED_TEMPLATE_FILES if not (template / f).is_file()]
    if missing:
        parser.error(f'Template incompleto: {", ".join(missing)}. Local: {template}')
    for dest_arg in args.destinos:
        dest = dest_arg.expanduser().resolve()
        if not project_ok(dest):
            print(f'ERRO: {dest} nao e um site de acervo reconhecido (faltam build.py/hinario.json)', file=sys.stderr)
            return 2
        if dest == template or dest == template.parent.parent:
            print(f'ERRO: nao altere o proprio template/site principal: {dest}', file=sys.stderr)
            return 2
        build_path = dest / 'build.py'
        original = build_path.read_text(encoding='utf-8')
        if args.template_build:
            if not (dest / '.acervo-site.json').is_file() or (dest / 'catalog_home.py').exists():
                print(f'ERRO: --template-build nao e seguro para {dest} (legado ou pagina personalizada).', file=sys.stderr)
                return 2
            proposed = (template / 'build.py').read_text(encoding='utf-8')
        elif (('.acervo-site.json' in original and not (dest / '.acervo-site.json').is_file())
              or 'from apps_catalog import' in original):
            recovered = get_legacy_from_git(dest)
            if recovered is None:
                print(f'ERRO: {dest}: build moderno sem .acervo-site.json e nao foi possivel recuperar build legado do Git.', file=sys.stderr)
                print('Restaure o build antigo via Git ou adicione o manifesto correto antes de executar.', file=sys.stderr)
                return 2
            proposed = recovered
            print(f'  {dest.name}: build legado recuperado do historico Git')
        else:
            proposed = original
        try:
            proposed = patch_build(proposed)
        except (ValueError, SyntaxError) as exc:
            print(f'ERRO: {dest}: {exc}', file=sys.stderr)
            return 2

        changes: dict[Path, bytes] = {build_path: proposed.encode('utf-8')}
        for rel in REQUIRED_TEMPLATE_FILES:
            src = template / rel
            target = dest / rel
            # Mantem slides proprios e padrao local ja existente.
            if rel == 'carrossel/padrao.svg' and target.is_file():
                continue
            changes[target] = src.read_bytes()
        for rel in OPTIONAL_MODULES:
            src = template / rel
            if 'from ' + Path(rel).stem + ' import' in proposed and not (dest / rel).is_file():
                if not src.is_file():
                    print(f'ERRO: falta dependencia no template: {src}', file=sys.stderr)
                    return 2
                changes[dest / rel] = src.read_bytes()

        real_changes = {p: data for p, data in changes.items() if not p.is_file() or p.read_bytes() != data}
        try:
            for p, data in real_changes.items():
                compile_check(p, data)
        except (SyntaxError, UnicodeError) as exc:
            print(f'ERRO: conteudo invalido: {exc}', file=sys.stderr)
            return 2

        print(f'\n{dest} - {len(real_changes)} arquivo(s) para atualizar')
        for p in real_changes:
            print('  ' + ('MODIFICAR' if p.exists() else 'CRIAR   ') + ': ' + str(p.relative_to(dest)))
        if args.dry_run or not real_changes:
            continue

        stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup = (dest / '.git' / 'backup-carrossel' / stamp
                  if (dest / '.git').is_dir()
                  else dest / '.backup-carrossel' / stamp)
        for p in real_changes:
            if p.is_file():
                backup_target = backup / p.relative_to(dest)
                backup_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, backup_target)
        for p, data in real_changes.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        print(f'  Backup das alteracoes anteriores: {backup}')
        print('  Rode: python3 build.py  (dentro do projeto)')
    return 0

if __name__ == '__main__':
    sys.exit(main())
