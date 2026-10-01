#!/usr/bin/env python3
"""Prepara uma lição independente para o Clave Sol a partir de um .mscz."""
import argparse
import importlib.util
import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent


def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', value).strip('-')


def one_line(value):
    return ' '.join(str(value).split())


def prepare(source, method, *, root=ROOT, slug=None, title=None, lesson=None,
            method_title=None, executable=None, update=False, pdf=False, tempo=None):
    from score_catalog import load_catalog, safe_key, validate_timing, read_markdown
    from musicxml_audio import parse_musicxml
    from scripts.score_timing import convert_media

    source = Path(source).expanduser().resolve()
    root = Path(root).resolve()
    if not source.is_file() or source.suffix.lower() != '.mscz':
        raise ValueError('Informe o caminho de um arquivo .mscz existente, contendo somente esta lição.')
    method = safe_key(method)
    slug = safe_key(slug or slugify(source.stem))
    if '/' in method or '/' in slug:
        raise ValueError('Método e lição devem ser nomes simples, sem barras.')
    key = f'metodos/{method}/{slug}'
    md = root / 'partituras' / f'{key}.md'
    assets = root / 'assets/music' / key
    for path in (md, assets):
        if not path.resolve().is_relative_to(root):
            raise ValueError('O destino não pode apontar para fora do projeto.')
    if (md.exists() or assets.exists()) and not update:
        raise ValueError(f'A lição {key} já existe. Use --atualizar para substituir os exports e preservar seu texto.')
    if assets.exists() and not assets.is_dir():
        raise ValueError(f'O destino não é uma pasta: {assets}')
    if md.exists() and not md.is_file():
        raise ValueError(f'O cadastro deve ser um arquivo Markdown, não uma pasta: {md}')
    if source.is_relative_to(assets.resolve()):
        raise ValueError('Use o original fora da pasta de assets; ela será substituída na atualização.')
    existing_meta = read_markdown(md)[0] if md.is_file() else {}
    tempo = tempo if tempo is not None else existing_meta.get('tempo')
    if any(existing_meta.get(k) for k in ('pages', 'measures')) and not update:
        raise ValueError('Use --atualizar para renovar o cadastro existente.')
    pdf = pdf or (assets / 'score.pdf').is_file()
    executable = executable or os.environ.get('MUSESCORE') or shutil.which('musescore') or shutil.which('mscore')
    if not executable:
        candidate = Path.home() / 'bin/musescore'
        if candidate.is_file():
            executable = str(candidate)
    if not executable:
        raise ValueError('MuseScore não encontrado. Informe --musescore /caminho/do/executavel.')

    # Stage everything before changing the working tree; no git command is executed.
    with tempfile.TemporaryDirectory(prefix='clavesol-') as directory:
        stage = Path(directory)
        output = stage / 'assets/music' / key
        output.mkdir(parents=True)
        env = dict(os.environ, QT_QPA_PLATFORM='offscreen')

        def export(arguments):
            try:
                result = subprocess.run([str(executable), *arguments, str(source)],
                                        capture_output=True, env=env, timeout=180, check=True)
            except subprocess.CalledProcessError as error:
                raise ValueError('MuseScore falhou: ' + error.stderr.decode(errors='replace')[-1500:]) from error
            except subprocess.TimeoutExpired as error:
                raise ValueError('MuseScore excedeu 180 segundos. Nenhum arquivo da lição foi alterado.') from error
            return result.stdout

        print('Exportando MusicXML…', flush=True)
        export(['-o', str(output / 'score.musicxml')])
        sequence = parse_musicxml(output / 'score.musicxml', tempo)
        print('Exportando páginas e cursor…', flush=True)
        media = json.loads(export(['--score-media']))
        # MuseScore rounds only metadata.duration. Use precise MusicXML duration
        # if rounding explains the difference, and verify all position timestamps.
        reported = float(media['metadata']['duration'])
        if abs(reported - sequence['duration']) > .500001:
            raise ValueError(f'Durações incompatíveis: MuseScore {reported:g}s; MusicXML {sequence["duration"]:g}s. Confira andamento e repetições.')
        normalized = copy.deepcopy(media)
        normalized['metadata']['duration'] = sequence['duration']
        svgs, timing = convert_media(normalized)
        validate_timing(timing, len(svgs))
        for i, svg in enumerate(svgs, 1):
            (output / f'score-{i}.svg').write_bytes(svg)
        (output / 'timing.json').write_text(json.dumps(timing, separators=(',', ':')), encoding='utf-8')
        shutil.copy2(source, output / 'score.mscz')
        if pdf:
            export(['-o', str(output / 'score.pdf')])
        xml = ET.parse(output / 'score.musicxml').getroot()
        composer = next((e.text for e in xml.iter('creator') if e.get('type') == 'composer' and e.text), '')
        instrument = next((e.text for e in xml.iter('part-name') if e.text), '')
        if md.exists():
            meta, _ = read_markdown(md)
            if meta.get('assets', f'music/{key}') != f'music/{key}':
                raise ValueError('O Markdown usa Assets personalizado. Ajuste-o antes de importar para este destino.')
            original = md.read_text(encoding='utf-8')
            header, separator, body = original, '\n\n', ''
            split = re.split(r'\r?\n[ \t]*\r?\n', original, maxsplit=1)
            if len(split) == 2:
                header, body = split
            updates = {'playback': 'generated', 'cursor': 'true', 'draft': 'false'}
            if 'pages' in meta: updates['pages'] = str(len(svgs))
            if 'measures' in meta: updates['measures'] = str(max(e['measure'] for e in timing['events']))
            if title: updates['title'] = one_line(title)
            if lesson: updates['lesson'] = str(lesson)
            if tempo: updates['tempo'] = str(tempo)
            lines = [line for line in header.splitlines() if line.split(':', 1)[0].lower() not in updates]
            lines += [f'{name.title()}: {value}' for name, value in updates.items()]
            markdown = '\n'.join(lines) + separator + body
        else:
            title = title or source.stem.replace('_', ' ')
            markdown = f'Title: {one_line(title)}\nAuthor: {one_line(composer)}\nInstrument: {one_line(instrument)}\n'
            if lesson: markdown += f'Lesson: {lesson}\n'
            if tempo: markdown += f'Tempo: {tempo}\n'
            markdown += 'Playback: generated\nCursor: true\nDraft: false\n\n'
        staged_md = stage / 'partituras' / f'{key}.md'
        staged_md.parent.mkdir(parents=True)
        staged_md.write_text(markdown, encoding='utf-8')
        load_catalog(stage)
        # Check the complete catalog with this replacement, without touching dist/.
        validation = stage / 'validation'
        for tree in ('partituras', 'assets'):
            if (root / tree).exists():
                shutil.copytree(root / tree, validation / tree)
        vassets = validation / 'assets/music' / key
        if vassets.exists(): shutil.rmtree(vassets)
        shutil.copytree(output, vassets)
        vmd = validation / 'partituras' / f'{key}.md'
        vmd.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged_md, vmd)
        load_catalog(validation)
        # Preserve unrelated files when replacing generated exports.
        if assets.exists():
            for file in assets.iterdir():
                if file.name not in {'score.musicxml','score.mscz','score.pdf','score.mp3','score.ogg','sequence.json','timing.json'} and not re.fullmatch(r'score-[0-9]+\.svg', file.name):
                    if file.is_dir(): shutil.copytree(file, output / file.name)
                    else: shutil.copy2(file, output / file.name)
        assets.parent.mkdir(parents=True, exist_ok=True)
        md.parent.mkdir(parents=True, exist_ok=True)
        backup = stage / 'previous-assets'
        old_md = md.read_bytes() if md.exists() else None
        try:
            if assets.exists(): shutil.move(str(assets), backup)
            shutil.copytree(output, assets)
            md.write_text(markdown, encoding='utf-8')
        except Exception:
            if assets.exists(): shutil.rmtree(assets)
            if backup.exists(): shutil.move(str(backup), assets)
            if old_md is not None: md.write_bytes(old_md)
            elif md.exists(): md.unlink()
            raise
        for path, heading in [(root/'partituras/metodos/_index.md', 'Métodos'),
                              (md.parent/'_index.md', method_title or method.replace('-', ' ').title())]:
            if not path.exists(): path.write_text(f'Title: {one_line(heading)}\n', encoding='utf-8')
        print(f'Pronto: {key}\n{len(svgs)} página(s), {sequence["duration"]:g}s, {sequence["marking"]}')
        if abs(reported - sequence['duration']) > .05:
            print(f'Duração arredondada do MuseScore normalizada: {reported:g}s → {sequence["duration"]:g}s; posições preservadas.')
        return key


def commit_lesson(root, paths, message):
    subprocess.run(['git', 'add', '--', *paths], cwd=root, check=True)
    changed = subprocess.run(['git', 'diff', '--cached', '--quiet', '--', *paths], cwd=root)
    if changed.returncode == 1:
        subprocess.run(['git', 'commit', '--only', '-m', message, '--', *paths], cwd=root, check=True)
    elif changed.returncode != 0:
        raise ValueError('Não foi possível verificar as alterações para o commit.')


def main():
    if importlib.util.find_spec('markdown') is None:
        interpreter = ROOT / '.venv/bin/python'
        if interpreter.is_file() and Path(sys.prefix).resolve() != (ROOT / '.venv').resolve():
            os.execv(str(interpreter), [str(interpreter), str(Path(__file__).resolve()), *sys.argv[1:]])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arquivo', type=Path, help='Caminho completo da lição.mscz')
    parser.add_argument('--metodo', help='Pasta do método, por exemplo domingos-pecci')
    parser.add_argument('--slug', help='Nome da lição no site; padrão: nome do .mscz normalizado')
    parser.add_argument('--titulo', help='Título da lição')
    parser.add_argument('--nome-metodo', help='Título de uma coleção nova')
    parser.add_argument('--licao', type=int, help='Número positivo para ordenar as lições')
    parser.add_argument('--musescore', help='Executável do MuseScore')
    parser.add_argument('--atualizar', action='store_true', help='Substitui exports existentes e preserva o texto do Markdown')
    parser.add_argument('--commit', action='store_true', help='Cria commit somente dos arquivos desta lição; depois basta git push')
    parser.add_argument('--pdf', action='store_true', help='Exporta também PDF para download')
    parser.add_argument('--tempo', type=float, help='Semínimas/minuto, somente se o MusicXML não informar andamento')
    args = parser.parse_args()
    method = args.metodo
    if not method:
        if not sys.stdin.isatty(): parser.error('Informe --metodo para execução sem perguntas.')
        available = sorted(p.name for p in (ROOT/'partituras/metodos').glob('*') if p.is_dir() and p.name != 'assets')
        if available: print('Métodos existentes: ' + ', '.join(available))
        method = input('Pasta do método (ex.: domingos-pecci): ').strip()
    if args.licao is not None and args.licao <= 0: parser.error('--licao deve ser positivo')
    try:
        key = prepare(args.arquivo, method, slug=args.slug, title=args.titulo,
                      method_title=args.nome_metodo, lesson=args.licao, executable=args.musescore,
                      update=args.atualizar, pdf=args.pdf, tempo=args.tempo)
    except ImportError:
        parser.exit(1, 'Ative o ambiente do projeto: source .venv/bin/activate\nDepois: pip install -r requirements.txt\n')
    except (ValueError, OSError, KeyError, ET.ParseError) as error:
        parser.exit(1, f'Não foi possível preparar a lição: {error}\n')
    if args.commit:
        paths = [f'partituras/{key}.md', f'assets/music/{key}'] + ['partituras/metodos/_index.md', f'partituras/{key.rsplit("/",1)[0]}/_index.md']
        try:
            commit_lesson(ROOT, paths, f'Prepara lição {key}')
        except (subprocess.CalledProcessError, ValueError) as error:
            parser.exit(1, f'Arquivos preparados, mas o commit não foi concluído: {error}\nConfira git status.\n')
        print('\nPreparado e commitado. Para publicar: git push origin main')
        return
    print('\nRevise e publique, na raiz do projeto:')
    print(f'git add partituras/metodos/_index.md partituras/{key.rsplit("/",1)[0]}/_index.md partituras/{key}.md assets/music/{key}/')
    print(f'git commit -m "Adiciona ou atualiza {key}"\ngit push origin main')


if __name__ == '__main__':
    main()
