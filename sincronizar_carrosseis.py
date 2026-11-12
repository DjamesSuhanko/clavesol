#!/usr/bin/env python3
"""Espelha CARROSSEL-HUB nos sites ClaveSol e publica os repositórios Git.

Uso (na pasta que contém CARROSSEL-HUB e os projetos):
    python3 sincronizar_carrosseis.py             # simula, sem alterar nada
    python3 sincronizar_carrosseis.py --aplicar   # copia, faz commit e push

Não executa force-push, não adiciona dist/ ignorado pelo Git e não mexe nos
outros arquivos dos repositórios. Exige Git, Python 3.9+ e autenticação Git.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys

# Diretórios pedidos. Os marcados com dist são apenas cópias locais geradas.
SITES = {
    "clavesol-hinos-bb": False,
    "clavesol-choro": True,
    "clavesol-harpa-crista": False,
    "clavesol-hinos-do": False,
    "clavesol-classicos": True,
    "clavesol-hinos-eb": False,
    "clavesol-cantor-cristao": True,
}
COMMIT_MESSAGE = "Atualiza carrossel compartilhado"


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout.strip()


def sha256(path: Path) -> bytes:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.digest()


def inventory(folder: Path) -> tuple[dict[Path, Path], set[Path]]:
    files, directories = {}, set()
    if not folder.exists():
        return files, directories
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError(f"Pasta inexistente, inválida ou simbólica: {folder}")
    for item in folder.rglob("*"):
        relative = item.relative_to(folder)
        if ".git" in relative.parts:
            raise ValueError(f"Encontrado diretório Git dentro do carrossel: {item}")
        if item.is_symlink():
            raise ValueError(f"Link simbólico não permitido: {item}")
        if item.is_dir():
            directories.add(relative)
        elif item.is_file():
            files[relative] = item
        else:
            raise ValueError(f"Tipo de arquivo não suportado: {item}")
    return files, directories


def plan(source: Path, target: Path) -> tuple[list[Path], list[Path], list[Path], list[Path]]:
    src_files, src_dirs = inventory(source)
    dst_files, dst_dirs = inventory(target)
    # Abortar se um arquivo estiver no lugar de uma pasta (ou vice-versa).
    if src_dirs & dst_files.keys() or dst_dirs & src_files.keys():
        raise ValueError(f"Conflito entre arquivo e diretório em {target}")
    put = [rel for rel, file in src_files.items()
           if rel not in dst_files or sha256(file) != sha256(dst_files[rel])]
    remove_files = [rel for rel in dst_files if rel not in src_files]
    remove_dirs = sorted(dst_dirs - src_dirs, key=lambda p: len(p.parts), reverse=True)
    create_dirs = sorted(src_dirs - dst_dirs, key=lambda p: len(p.parts))
    return put, remove_files, create_dirs, remove_dirs


def apply_plan(source: Path, target: Path, actions: tuple[list[Path], list[Path], list[Path], list[Path]]) -> None:
    put, remove_files, create_dirs, remove_dirs = actions
    target.mkdir(parents=True, exist_ok=True)
    for rel in remove_files:
        (target / rel).unlink()
    for rel in remove_dirs:
        (target / rel).rmdir()
    for rel in create_dirs:
        (target / rel).mkdir(parents=True, exist_ok=True)
    for rel in put:
        item = target / rel
        item.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / rel, item)


def check_repo(repo: Path, allow_dirty: bool) -> None:
    if not repo.is_dir() or repo.is_symlink():
        raise ValueError(f"Repositório não encontrado ou inválido: {repo}")
    root = Path(git(repo, "rev-parse", "--show-toplevel")).resolve()
    if root != repo.resolve():
        raise ValueError("A pasta não é a raiz do seu próprio repositório Git")
    if git(repo, "branch", "--show-current") != "main":
        raise ValueError("Branch atual não é main; não vou publicar em outra branch")
    if not git(repo, "remote") or "origin" not in git(repo, "remote").splitlines():
        raise ValueError("Remote origin não configurado")
    staged = git(repo, "diff", "--cached", "--name-only")
    if staged:
        raise ValueError("Há alterações já staged; faça commit ou unstaging antes de executar")
    if not allow_dirty:
        dirty = git(repo, "status", "--porcelain", "--untracked-files=all", "--",
                    "carrossel", "dist/carrossel")
        if dirty:
            raise ValueError("Alterações locais em carrossel; revise-as ou use --sobrescrever-locais")


def summary(name: str, actions: tuple[list[Path], list[Path], list[Path], list[Path]]) -> None:
    put, remove_files, create_dirs, remove_dirs = actions
    print(f"  {name}: {len(put)} arquivos novos/alterados; "
          f"{len(remove_files)} arquivos antigos a excluir; "
          f"{len(create_dirs)} novas pastas")
    for rel in put:
        print(f"    + {rel}")
    for rel in remove_files:
        print(f"    - {rel}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parent,
                        help="Pasta que contém CARROSSEL-HUB e os projetos (padrão: pasta do script)")
    parser.add_argument("--hub", type=Path, default=Path("CARROSSEL-HUB"),
                        help="Origem do carrossel (relativa a --raiz, salvo caminho absoluto)")
    parser.add_argument("--aplicar", action="store_true",
                        help="Efetivamente sincronizar, fazer commit e git push origin main")
    parser.add_argument("--sobrescrever-locais", action="store_true",
                        help="Permite substituir alterações locais ainda não commitadas em carrossel")
    args = parser.parse_args()
    base = args.raiz.expanduser().resolve()
    hub = args.hub.expanduser()
    if not hub.is_absolute():
        hub = base / hub
    hub = hub.resolve()
    if not hub.is_dir():
        parser.error(f"Não encontrei o diretório CARROSSEL-HUB: {hub}")
    try:
        files, _ = inventory(hub)
    except ValueError as e:
        parser.error(str(e))
    if not files:
        parser.error("O CARROSSEL-HUB está vazio; cancelado para não apagar carrosséis")

    print(f"Origem: {hub} ({len(files)} arquivos)")
    print("Modo:", "APLICAR E PUBLICAR" if args.aplicar else "SIMULAÇÃO — nenhum arquivo será modificado")
    failures = []
    successes = []
    for name, with_dist in SITES.items():
        repo = base / name
        print(f"\n[{name}]")
        try:
            check_repo(repo, args.sobrescrever_locais)
            if (repo / "carrossel").is_symlink():
                raise ValueError("carrossel é um link simbólico")
            destinations = [Path("carrossel")]
            if with_dist and (repo / "dist").is_dir():
                destinations.append(Path("dist/carrossel"))
            elif with_dist:
                print("  dist/ não existe: será criado no próximo build; ignorando cópia local")
            plans = {}
            for relative in destinations:
                actions = plan(hub, repo / relative)
                plans[relative] = actions
                summary(str(relative), actions)
            if not args.aplicar:
                successes.append(name)
                continue
            for relative, actions in plans.items():
                apply_plan(hub, repo / relative, actions)

            # Adicionar apenas o carrossel-fonte, e dist se já tiver arquivos rastreados.
            paths = ["carrossel"]
            if "dist/carrossel" in [p.as_posix() for p in plans]:
                if git(repo, "ls-files", "--", "dist/carrossel"):
                    paths.append("dist/carrossel")
            git(repo, "add", "-A", "--", *paths)
            changed = git(repo, "diff", "--cached", "--name-only", "--", *paths)
            if changed:
                git(repo, "commit", "-m", COMMIT_MESSAGE)
                print("  Commit realizado.")
            else:
                print("  Sem alterações versionadas; nenhum novo commit necessário.")
            # Também retoma um push que tenha falhado numa execução anterior.
            response = git(repo, "push", "origin", "main")
            print("  Push concluído.", response)
            successes.append(name)
        except (ValueError, RuntimeError, OSError) as e:
            print(f"  ERRO: {e}", file=sys.stderr)
            failures.append(name)

    print(f"\nResumo: {len(successes)} projeto(s) OK; {len(failures)} falha(s).")
    if failures:
        print("Falharam:", ", ".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
