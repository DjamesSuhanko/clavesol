#!/usr/bin/env python3
"""Prepara Bb, Eb e C pelo importador padrão; exclui falhas, sem PDF ou publicação."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import contextlib
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from criar_licao import prepare, slugify, one_line
from score_catalog import load_catalog

LABELS = {'bb': 'Bb', 'eb': 'Eb', 'do': 'C'}
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path.home()/'Documents/ClaveSol/lab/Musescore4'
DEFAULT_STAGE = Path.home()/'Documents/ClaveSol/lab/hinarios-para-publicar'


def source_title(source):
    """Use the printed title without rewriting the source score."""
    with zipfile.ZipFile(source) as archive:
        name = next(n for n in archive.namelist() if n.endswith('.mscx'))
        xml = ET.fromstring(archive.read(name))
    titles = [e.find('text') for e in xml.findall('.//VBox/Text') if e.findtext('style') == 'title']
    title = next((one_line(''.join(e.itertext())) for e in titles if e is not None), '')
    number = re.search(r'\d+', source.stem)
    is_chorus = source.stem.lower().startswith('coro')
    prefix = f'{"Coro" if is_chorus else "Hino"} {int(number.group())}' if number else source.stem
    return prefix + (' — ' + title if title else ''), (int(number.group()) + (1000 if is_chorus else 0)) if number else None


def export_one(job):
    source, collection, stage, executable, retry = job
    slug = slugify(source.stem)
    key = f'hinos/{collection}/{slug}'
    marker = stage/'_progresso'/collection/f'{slug}.json'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    md = stage/'partituras'/f'{key}.md'
    assets = stage/'assets/music'/key
    if marker.exists():
        saved = json.loads(marker.read_text())
        if saved['sha256'] == digest:
            if saved['status'] == 'excluido' and not retry:
                return saved
            if saved['status'] == 'pronto' and md.is_file() and all((assets/f).is_file() for f in saved['files']):
                return saved
    # A modified score must not leave an obsolete successful version in the result.
    md.unlink(missing_ok=True)
    if assets.exists(): shutil.rmtree(assets)
    log = stage/'logs'/collection/f'{slug}.log'
    log.parent.mkdir(parents=True, exist_ok=True)
    record = {'source':str(source), 'key':key, 'sha256':digest}
    try:
        title, number = source_title(source)
        with tempfile.TemporaryDirectory(prefix='clavesol-hino-') as directory, log.open('w') as stream, contextlib.redirect_stdout(stream):
            work = Path(directory)
            prepare(source, hinos=True, hinario=collection, root=work, slug=slug,
                    title=title, lesson=number, executable=executable, pdf=False)
            # Keep the exact generated player/cursor validation used for individual lessons.
            score = load_catalog(work).scores[0]
            if score.playback != 'generated' or not score.timing:
                raise ValueError('A partitura precisa ter player gerado e cursor válidos.')
            original_assets = work/'assets/music'/key
            if (original_assets/'score.pdf').exists(): raise ValueError('PDF inesperado no resultado.')
            md.parent.mkdir(parents=True, exist_ok=True)
            assets.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(original_assets, assets)
            shutil.copy2(work/'partituras'/f'{key}.md', md)
        record.update(status='pronto', files=sorted(p.name for p in assets.iterdir()), reason='')
    except (ValueError, OSError, KeyError, ET.ParseError, zipfile.BadZipFile) as error:
        md.unlink(missing_ok=True)
        if assets.exists(): shutil.rmtree(assets)
        record.update(status='excluido', files=[], reason=str(error))
    marker.parent.mkdir(parents=True, exist_ok=True)
    temporary=marker.with_suffix('.tmp');temporary.write_text(json.dumps(record,ensure_ascii=False,indent=2));temporary.replace(marker)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=DEFAULT_SOURCE)
    parser.add_argument('--stage',type=Path,default=DEFAULT_STAGE)
    parser.add_argument('--musescore',default=os.environ.get('MUSESCORE',str(Path.home()/'bin/musescore')))
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--tentar-excluidos',action='store_true')
    args = parser.parse_args()
    source=args.source.expanduser().resolve();stage=args.stage.expanduser().resolve()
    if stage == ROOT or stage.is_relative_to(ROOT) or stage.is_relative_to(source) or source.is_relative_to(stage):
        parser.error('A pasta de resultados deve ficar separada do projeto e dos originais.')
    if args.workers < 1: parser.error('--workers deve ser positivo')
    if not shutil.which(args.musescore): parser.error('MuseScore não encontrado. Informe --musescore.')
    jobs=[]
    for collection in LABELS:
        files=sorted((source/collection).glob('*.mscz'))
        if not files: parser.error(f'Nenhum .mscz em {source/collection}')
        slugs=[slugify(p.stem) for p in files]
        if len(set(slugs)) != len(slugs): parser.error(f'Nomes normalizados repetidos em {collection}')
        jobs.extend((p,collection,stage,args.musescore,args.tentar_excluidos) for p in files)
    stage.mkdir(parents=True,exist_ok=True)
    (stage/'CONCLUIDO.json').unlink(missing_ok=True)
    for collection,title in LABELS.items():
        index=stage/'partituras/hinos'/collection/'_index.md';index.parent.mkdir(parents=True,exist_ok=True)
        index.write_text(f'Title: {title}\nDescription: Hinário para instrumentos em {title}.\n')
    (stage/'partituras/hinos/_index.md').write_text('Title: Hinos\n')
    print(f'{len(jobs)} arquivos. Sem PDF. Somente player e cursor funcionais. Resultados: {stage}',flush=True)
    results=[];start=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        tasks=[pool.submit(export_one,job) for job in jobs]
        for i,task in enumerate(as_completed(tasks),1):
            result=task.result();results.append(result)
            ready=sum(r['status']=='pronto' for r in results)
            print(f'[{i}/{len(jobs)}] {result["status"]}: {result["key"]} | funcionais={ready}, excluídos={i-ready}',flush=True)
    # Drop records for source files removed since an earlier run.
    keys={r['key'] for r in results if r['status']=='pronto'}
    for md in (stage/'partituras/hinos').rglob('*.md'):
        if md.name!='_index.md' and md.relative_to(stage/'partituras').with_suffix('').as_posix() not in keys:
            old_key=md.relative_to(stage/'partituras').with_suffix('').as_posix()
            md.unlink();shutil.rmtree(stage/'assets/music'/old_key,ignore_errors=True)
    catalog=load_catalog(stage)
    if len(catalog.scores)!=len(keys): raise SystemExit('Quantidade de partituras funcionais divergente.')
    results.sort(key=lambda r:r['key'])
    (stage/'relatorio.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    with (stage/'relatorio-excluidos.csv').open('w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.writer(stream);writer.writerow(['arquivo_original','destino','motivo'])
        for record in results:
            if record['status']=='excluido':writer.writerow([record['source'],record['key'],record['reason']])
    summary={'total':len(jobs),'funcionais':len(keys),'excluidos':len(jobs)-len(keys),'segundos':round(time.monotonic()-start),'source':str(source),'stage':str(stage)}
    (stage/'CONCLUIDO.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(f'CONCLUÍDO: {len(keys)} funcionais, {len(jobs)-len(keys)} excluídos. Avise ao Codex que terminou para revisar e publicar.',flush=True)


if __name__=='__main__':
    try: main()
    except KeyboardInterrupt: raise SystemExit('Interrompido. Execute o mesmo comando para retomar.')
