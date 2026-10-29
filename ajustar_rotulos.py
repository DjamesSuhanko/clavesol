#!/usr/bin/env python3
"""Corrige rótulos de coleções externas e do botão de reprodução no Clave Sol.

Uso: python3 ajustar_rotulos.py /caminho/para/repo
Faz backups .bak-rotulos; não executa git, build nem publicação.
"""
from pathlib import Path
import argparse
import ast


def replace_once(text, old, new, description):
    if new in text:
        return text, False
    matches = text.count(old)
    if matches != 1:
        raise RuntimeError(f'{description}: esperava 1 ocorrência, encontrei {matches}; nenhum arquivo foi alterado.')
    return text.replace(old, new, 1), True


def changes_for_catalog(text):
    text, a = replace_once(text,
        "    link: str = ''\n",
        "    link: str = ''\n    tipo: str = 'hinario'\n",
        'campo de tipo na classe Group')
    text, b = replace_once(text,
        "groups[key] = Group(key, meta.get('title', key), meta.get('description', ''), body, meta.get('link', ''))",
        "groups[key] = Group(key, meta.get('title', key), meta.get('description', ''), body, meta.get('link', ''), meta.get('tipo', 'hinario').strip().lower())",
        'leitura de Tipo no Markdown')
    return text, a or b


def changes_for_pages(text):
    text, a = replace_once(text,
        "label = 'HINÁRIO' if link else quantity(count, 'partitura')",
        "label = ('HINÁRIO' if getattr(group, 'tipo', 'hinario') == 'hinario' else 'ACERVO MUSICAL') if link else quantity(count, 'partitura')",
        'rótulo dos cards externos')
    text, b = replace_once(text,
        "    player = ''\n",
        "    full_label = 'Hino completo' if score.category == 'hinos' else 'Música completa'\n    player = ''\n",
        'rótulo do botão de reprodução')
    text, c = replace_once(text,
        'disabled>Hino completo</button>',
        'disabled>{full_label}</button>',
        'texto do botão de reprodução')
    return text, a or b or c


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('raiz', type=Path, help='Raiz do repositório do site')
    args = ap.parse_args()
    raiz = args.raiz.expanduser().resolve()
    updates = []
    for filename, transform in [('score_catalog.py', changes_for_catalog), ('music_pages.py', changes_for_pages)]:
        path = raiz / filename
        if not path.is_file():
            raise SystemExit(f'Arquivo ausente: {path}')
        original = path.read_text(encoding='utf-8')
        altered, changed = transform(original)
        ast.parse(altered, filename=str(path))
        updates.append((path, original, altered, changed))
    for path, original, altered, changed in updates:
        if changed:
            backup = path.with_name(path.name + '.bak-rotulos')
            if not backup.exists():
                backup.write_text(original, encoding='utf-8')
            path.write_text(altered, encoding='utf-8')
        print(f'{"Corrigido" if changed else "Já atualizado"}: {path}')
    print('Use Tipo: musicas no _index.md de cada acervo musical externo.')


if __name__ == '__main__':
    main()
