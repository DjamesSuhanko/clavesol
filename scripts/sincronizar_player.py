#!/usr/bin/env python3
"""Replica o player do blog nos três hinários, valida e opcionalmente publica."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('clavesol', 'clavesol-hinos-bb', 'clavesol-hinos-eb', 'clavesol-hinos-do')
SHARED = ('tests/introduction.test.py', 'tests/fixtures/hino-6-introduction.musicxml', 'list_search.py', 'assets/list-search.css', 'assets/list-search.mjs',
          'tests/list-search.test.mjs', 'assets/music.js', 'assets/music-synth.mjs', 'assets/music-timing.mjs',
          'assets/style.css', 'music_pages.py', 'tests/music-player.test.mjs',
          'tests/music-synth.test.mjs', 'musicxml_audio.py', 'tests/fermatas.test.py', 'criar_licao.py', 'tests/import-sync.test.py', 'musicxml_repeats.py', 'tests/repeats.test.py')
SOURCE_ONLY = ('scripts/sincronizar_player.py', 'docs/SINCRONIZAR-PLAYER.md',
               'tests/sync-player.test.py', 'tests/musicxml.test.py', 'docs/IMPORTAR-LICAO.md')


def run(args, cwd, capture=False):
    return subprocess.run(args, cwd=cwd, check=True, text=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def plan(source, targets):
    """Preflight every destination before changing any file."""
    changes = []
    for name in SHARED:
        if not (source/name).is_file():
            raise ValueError(f'Arquivo de origem ausente: {source/name}')
    for target in targets:
        if not (target/'.git').exists():
            raise ValueError(f'Repositório ausente: {target}')
        for name in SHARED:
            destination = target/name
            if destination.exists() and destination.read_bytes() == (source/name).read_bytes():
                continue
            if run(['git', 'status', '--porcelain', '--', name], target, True).strip():
                raise ValueError(f'Alteração local em {destination}. Faça commit ou concilie esse arquivo antes de sincronizar.')
            changes.append((source/name, destination))
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Somente lista diferenças; não altera arquivos nem executa builds.')
    parser.add_argument('--publicar', action='store_true', help='Após validar todos, faz commit dos arquivos do player e push nos quatro repositórios.')
    parser.add_argument('--node', help='Executável Node.js (padrão: detecção automática).')
    args = parser.parse_args()
    if args.check and args.publicar:
        parser.error('--check não pode ser usado com --publicar')
    repos = [ROOT.parent/name for name in NAMES]
    if repos[0].resolve() != ROOT.resolve():
        raise ValueError('Execute a cópia do script que fica no repositório principal clavesol.')
    changes = plan(ROOT, repos[1:])
    for source, destination in changes:
        print(f'{source.relative_to(ROOT)} → {destination.parent}', flush=True)
    if args.check:
        print(f'{len(changes)} arquivo(s) a sincronizar.')
        return
    node = shutil.which(args.node or 'node')
    if not node and not args.node:
        bundled = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
        if bundled.is_file():
            node = str(bundled)
    if not node:
        raise ValueError('Node.js não encontrado. Instale-o ou informe --node /caminho/para/node.')
    # Validate publishing prerequisites before copying or committing anything.
    if args.publicar:
        for repo in repos:
            if run(['git', 'branch', '--show-current'], repo, True).strip() != 'main':
                raise ValueError(f'{repo}: a publicação exige a branch main.')
            if run(['git', 'diff', '--cached', '--name-only'], repo, True).strip():
                raise ValueError(f'{repo}: há arquivos já staged; conclua esse commit primeiro.')
            origin = run(['git', 'remote', 'get-url', 'origin'], repo, True).strip()
            if origin.removesuffix('.git') not in (f'https://github.com/DjamesSuhanko/{repo.name}', f'git@github.com:DjamesSuhanko/{repo.name}'):
                raise ValueError(f'Origin inesperado em {repo}.')
    for source, destination in changes:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    import os
    for repo in repos:
        print(f'Validando {repo.name}…', flush=True)
        for test in ('music.test.mjs', 'music-player.test.mjs', 'music-synth.test.mjs'):
            run([node, 'tests/'+test], repo)
        run([sys.executable, 'tests/fermatas.test.py'], repo)
        run([sys.executable, 'tests/import-sync.test.py'], repo)
        run([sys.executable, 'tests/repeats.test.py'], repo)
        env = os.environ.copy()
        # Explicit local root build, independent of shell/domain configuration.
        env['BASE_PATH'] = ''
        subprocess.run([sys.executable, 'build.py'], cwd=repo, env=env, check=True)
        subprocess.run([sys.executable, 'scripts/check_links.py'], cwd=repo, env=env, check=True)
    if args.publicar:
        for repo in repos:
            paths = list(SHARED) + (list(SOURCE_ONLY) if repo == ROOT else [])
            paths = [p for p in paths if (repo/p).exists()]
            run(['git', 'add', '--', *paths], repo)
            if run(['git', 'diff', '--cached', '--name-only'], repo, True).strip():
                run(['git', 'commit', '-m', 'Atualiza player compartilhado'], repo)
            run(['git', 'push', 'origin', 'main'], repo)
        print('Push concluído nos quatro repositórios. Acompanhe os deploys na aba Actions de cada um.')
    else:
        print('Player sincronizado e validado nos quatro repositórios. Nenhum commit ou push foi feito.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f'Falha: {error}')
