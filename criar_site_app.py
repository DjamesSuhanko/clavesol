#!/usr/bin/env python3
"""Prepara um site Clave Sol independente; opcionalmente cria o repositório e configura Pages."""
import argparse
from html import escape
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
ROOT = Path(__file__).resolve().parent


def run(*command, cwd=None, capture=False):
    return subprocess.run(command, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE if capture else None).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repositorio', 'dominio', 'titulo', 'texto', 'email'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--autor', default='Djames Suhanko')
    parser.add_argument('--diretorio', type=Path, required=True, help='Pasta nova para o repositório')
    parser.add_argument('--imagem', type=Path, help='Logo/capa PNG, JPEG ou WebP; padrão: logo Clave Sol')
    parser.add_argument('--conteudo-html', type=Path, help='Fragmento HTML adicional para a página inicial')
    parser.add_argument('--politica-html', type=Path, help='Política HTML; documento com main ou fragmento contendo um h1')
    parser.add_argument('--github', action='store_true', help='Criar repositório público, enviar e configurar Pages; não aciona deploy')
    parser.add_argument('--retomar-github', action='store_true', help='Retomar apenas criação/envio/configuração da pasta já gerada')
    args = parser.parse_args()
    try:
        if not re.fullmatch(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', args.repositorio):
            raise ValueError('--repositorio deve ser DONO/NOME.')
        if not re.fullmatch(r'(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}', args.dominio):
            raise ValueError('Domínio inválido: use somente o hostname, sem https ou barras.')
        if not re.fullmatch(r'[^\s<>"@]+@[^\s<>"@]+\.[^\s<>"@]+', args.email):
            raise ValueError('Email inválido.')
        if not args.titulo.strip() or not args.texto.strip():
            raise ValueError('Título e texto obrigatórios.')
        destination = args.diretorio.expanduser().resolve()
        if args.retomar_github:
            config = json.loads((destination / 'site.json').read_text())
            if config['repository'] != args.repositorio or config['domain'] != args.dominio:
                raise ValueError('Repositório/domínio não correspondem à pasta existente.')
        else:
            if destination.exists():
                raise ValueError('O diretório já existe; escolha uma pasta nova. Para retomar envio use --retomar-github.')
            image = args.imagem.expanduser().resolve(strict=True) if args.imagem else ROOT / 'templates/app-site/assets/logo-clavesol.webp'
            if image.suffix.lower() not in ('.webp', '.png', '.jpg', '.jpeg'):
                raise ValueError('Imagem deve ser WebP, PNG ou JPEG.')
            home = args.conteudo_html.expanduser().read_text() if args.conteudo_html else '<p>Mais informações sobre o aplicativo serão disponibilizadas aqui.</p>'
            privacy = '<h1>Política de privacidade</h1><p>A política de privacidade deste aplicativo será disponibilizada em breve.</p>'
            if args.politica_html:
                privacy = args.politica_html.expanduser().read_text()
                main_content = re.search(r'<main\b[^>]*>(.*?)</main>', privacy, re.S | re.I)
                if main_content:
                    privacy = main_content[1]
                if re.search(r'<(?:html|body)\b', privacy, re.I) or len(re.findall(r'<h1\b', privacy, re.I)) != 1:
                    raise ValueError('Forneça um fragmento HTML com um h1 ou documento com esse conteúdo dentro de main.')
            shutil.copytree(ROOT / 'templates/app-site', destination, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            logo = 'app-logo' + image.suffix.lower()
            shutil.copyfile(image, destination / 'assets' / logo)
            config = dict(repository=args.repositorio, domain=args.dominio, title=args.titulo, description=args.texto, author=args.autor, email=args.email, logo=logo, privacy_ready=bool(args.politica_html))
            (destination / 'site.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n')
            (destination / 'CNAME').write_text(args.dominio + '\n')
            (destination / '.gitignore').write_text('dist/\n__pycache__/\n*.pyc\n')
            (destination / 'content').mkdir()
            (destination / 'content/home.html').write_text(home)
            (destination / 'content/privacy.html').write_text(privacy)
            (destination / 'README.md').write_text(f'# {args.titulo}\n\nSite público Clave Sol: https://{args.dominio}/\n\nEdite `site.json`, `content/home.html` e `content/privacy.html`. Ao fornecer a política definitiva, marque `privacy_ready` como `true` em `site.json`.\n\nGerar: `python3 build.py`\n\nVisualizar: `python3 -m http.server 8000 --directory dist`\n\nPublicação: Actions → Publicar aplicativo → Run workflow. O primeiro commit usa `[skip ci]`; pushes posteriores em main publicam automaticamente.\n\nDNS: CNAME do subdomínio apontando para `{args.repositorio.split("/")[0].lower()}.github.io` (somente DNS). Em Settings → Pages, habilite Enforce HTTPS quando o certificado estiver pronto.\n\nPublique apenas conteúdo público. Nunca inclua chaves de assinatura, credenciais ou dados de usuários.\n')
            run(sys.executable, 'build.py', cwd=destination)
            run('git', 'init', '-b', 'main', cwd=destination)
        if args.github or args.retomar_github:
            run('gh', 'auth', 'status')
            # Check only this exact repository. Never adopt an unrelated existing repository.
            lookup = subprocess.run(['gh', 'repo', 'view', args.repositorio, '--json', 'nameWithOwner'], capture_output=True, text=True)
            if lookup.returncode == 0 and not args.retomar_github:
                raise ValueError('O repositório remoto já existe; a pasta local foi preservada, mas nada foi enviado.')
            expected = 'https://github.com/' + args.repositorio + '.git'
            remote = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=destination, capture_output=True, text=True)
            if remote.returncode == 0 and remote.stdout.strip() != expected:
                raise ValueError('Origin não corresponde ao repositório solicitado.')
            # Explicit identity local to generated repo, if the user has no configured git identity.
            for key, value in [('user.name', args.autor), ('user.email', args.email)]:
                check = subprocess.run(['git', 'config', '--get', key], cwd=destination, capture_output=True)
                if check.returncode:
                    run('git', 'config', key, value, cwd=destination)
            head = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], cwd=destination, capture_output=True)
            if head.returncode:
                run('git', 'add', '.', cwd=destination)
                run('git', 'commit', '-m', 'Preparar site público Clave Sol [skip ci]', cwd=destination)
            if lookup.returncode:
                run('gh', 'repo', 'create', args.repositorio, '--public', '--description', args.titulo, cwd=destination)
            if remote.returncode:
                run('git', 'remote', 'add', 'origin', expected, cwd=destination)
            run('git', 'push', '-u', 'origin', 'main', cwd=destination)
            endpoint = 'repos/' + args.repositorio + '/pages'
            pages = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True)
            run('gh', 'api', '--method', 'PUT' if pages.returncode == 0 else 'POST', endpoint, '-f', 'build_type=workflow')
            run('gh', 'api', '--method', 'PUT', endpoint, '-f', 'cname=' + args.dominio)
            print('GitHub Pages configurado. Execute Actions → Publicar aplicativo → Run workflow.')
        print('Pronto:', destination)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Erro: {error}\nArquivos já gerados são preservados. Se a falha foi no GitHub, use --retomar-github com os mesmos parâmetros.\n')

if __name__ == '__main__':
    main()
