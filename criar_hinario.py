#!/usr/bin/env python3
"""Cria um acervo Clave Sol com player, carrossel e GitHub Pages. Veja docs/CRIAR-HINARIO.md."""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from criar_licao import slugify, one_line, synchronize_media
from musicxml_audio import parse_musicxml
from scripts.score_timing import convert_media
from score_catalog import load_catalog
ROOT=Path(__file__).resolve().parent
MODULES=('score_catalog.py','music_pages.py','musicxml_audio.py','musicxml_repeats.py','cache_assets.py','seo.py','list_search.py','requirements.txt')
ASSETS=('style.css','icon.svg','logo-clavesol.webp','clarinet.jpg','music.js','music-synth.mjs','music-timing.mjs','list-search.css','list-search.mjs','updates.js')
SUFFIXES={'musicxml':{'.musicxml','.xml'},'mid':{'.mid','.midi'},'mscz':{'.mscz'}}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()
def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temp.replace(path)
def run(args,**kwargs):
    return subprocess.run([str(a) for a in args],check=True,text=True,**kwargs)
def output(args,**kwargs):return run(args,capture_output=True,**kwargs).stdout.strip()


def initialize(destination,domain,title,description,repository,tipo):
    """Preserve arbitrary preexisting files. Adopt only nonconflicting template paths."""
    marker=destination/'.acervo-site.json'
    if marker.exists():
        state=json.loads(marker.read_text())
        if state['domain']!=domain or state['repository']!=repository:
            raise ValueError('Domínio/repositório diferem do cadastro existente neste destino.')
        original_type = state.get('tipo', 'hinos')
        if original_type != tipo:
            raise ValueError(f'O destino existente foi criado como {original_type}; não é seguro transformá-lo em {tipo} sem migração dos arquivos e URLs. Escolha um novo destino.')
        if tipo == 'hinos':
            upgrade_composers(destination,state)
        return state
    files={}
    for path in (ROOT/'templates/hinario-site').rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:files[str(path.relative_to(ROOT/'templates/hinario-site'))]=path.read_bytes()
    for name in MODULES:files[name]=(ROOT/name).read_bytes()
    for name in ASSETS:files['assets/'+name]=(ROOT/'assets'/name).read_bytes()
    files['scripts/check_links.py']=(ROOT/'scripts/check_links.py').read_bytes()
    config={'collection':'musicas' if tipo == 'musicas' else 'acervo','label':title,'repository':repository.split('/')[-1]}
    files['hinario.json']=(json.dumps(config,ensure_ascii=False,indent=2)+'\n').encode()
    files['seo.json']=(json.dumps({'site_url':'https://'+domain,'site_name':'Clave Sol','description':description,'default_image':'clarinet.jpg','default_image_alt':'Detalhe de um clarinete','social_profiles':['https://www.youtube.com/@ClaveSolMusic']},ensure_ascii=False,indent=2)+'\n').encode()
    files['CNAME']=(domain+'\n').encode()
    if tipo == 'musicas':
        for key in list(files):
            if key.startswith('partituras/hinos/'):
                del files[key]
        files['partituras/musicas/_index.md'] = f'Title: Músicas\nDescription: {description}\n'.encode()
        if 'music_pages.py' in files:
            files['music_pages.py'] = files['music_pages.py'].replace(b'Hino completo', 'Música completa'.encode('utf-8'))
    else:
        files['partituras/hinos/_index.md']=b'Title: Hinos\n'
        files['partituras/hinos/acervo/_index.md']=f'Title: {title}\nDescription: {description}\n'.encode()
    files['GUIA-ACERVO.md']=(ROOT/'docs/CRIAR-HINARIO.md').read_bytes()
    files['README.md']=f'''# {title}

{description}

Domínio: https://{domain}/

## Editar

Título/descrição: `partituras/musicas/_index.md` (músicas) ou `partituras/hinos/acervo/_index.md` (hinário). Partituras: arquivos Markdown agrupados por compositor ou coleção. Banners: `carrossel/01.webp`, `02.webp`, etc.; sem imagens numeradas, usa `padrao.svg`. Veja `GUIA-ACERVO.md`.

## Prévia

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python build.py
python scripts/check_links.py
python -m http.server 8000 --directory dist
```

## Publicar

Actions → **Publicar acervo** → Run workflow. O script não dispara o primeiro deploy. Configure o CNAME na Cloudflare para `{repository.split('/')[0].lower()}.github.io` (somente DNS), e habilite Enforce HTTPS em Pages quando o certificado estiver pronto. Pushes futuros sem `[skip ci]` publicam normalmente.

Arquivos MIDI/MSCZ e credenciais não pertencem a este repositório. Apenas MusicXML é oferecido para download. Os SVGs, sequência e cursor são usados pelo player.
'''.encode()
    # Detect conflicts before writing any template file. Existing unrelated content stays untouched.
    for name,data in files.items():
        target=destination/name
        if target.exists() and (not target.is_file() or target.read_bytes()!=data):
            raise ValueError(f'Destino contém arquivo conflitante: {target}. Use uma pasta livre ou reorganize esse arquivo.')
        if any(p.is_symlink() for p in [target,*target.parents] if p!=destination.parent):
            raise ValueError(f'Caminho simbólico não permitido: {target}')
    destination.mkdir(parents=True,exist_ok=True)
    for name,data in files.items():
        p=destination/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    ignore=destination/'.gitignore'
    previous=ignore.read_text() if ignore.exists() else ''
    ignore.write_text(previous+'\n# Acervo Clave Sol\ndist/\n.venv/\n__pycache__/\n.importacao/\n*.mid\n*.midi\n*.mscz\n*.mscx\n.env\n*.jks\n*.keystore\n')
    state={'schema':3,'tipo':tipo,'domain':domain,'repository':repository,'managed':sorted([*files,'.gitignore','.acervo-site.json'])}
    write_json(marker,state)
    return state


def upgrade_composers(destination,state):
    if state.get('schema',1)>=2:return
    previous='f73b48560fd0d52d849c76dc75f5136b050763f1b71908591275a6709ad672e9'
    new_build=ROOT/'templates/hinario-site/build.py'
    if digest(destination/'build.py') not in (previous,digest(new_build)):
        raise ValueError('build.py foi editado no destino. Preserve suas alterações e incorpore o novo modelo antes de retomar.')
    module=destination/'composer_pages.py';template=ROOT/'templates/hinario-site/composer_pages.py'
    if module.exists() and module.read_bytes()!=template.read_bytes():
        raise ValueError('composer_pages.py conflitante no destino.')
    backup=destination/'.importacao/backups'/('estrutura-compositores-'+time.strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True,exist_ok=True)
    shutil.copy2(destination/'build.py',backup/'build.py')
    shutil.copyfile(new_build,destination/'build.py');shutil.copyfile(template,module)
    state['schema']=2;state['managed']=sorted(set(state['managed'])|{'composer_pages.py'})
    write_json(destination/'.acervo-site.json',state)


def author_fallback(metadata,composer):
    if composer:
        metadata=re.sub(r'^Author:[ \t]*$',lambda _: 'Author: '+composer,metadata,flags=re.M)
    return metadata


def prepare_score(source,folder,kind,executable):
    """Export in isolated staging; keep original MusicXML bytes unchanged."""
    env=dict(os.environ,QT_QPA_PLATFORM='offscreen')
    def export(args):
        proc=subprocess.run([str(executable),*map(str,args),str(source)],env=env,capture_output=True,timeout=180)
        if proc.returncode:
            raise ValueError('MuseScore: '+proc.stderr.decode(errors='replace')[-1500:])
        return proc.stdout
    folder.mkdir(parents=True)
    xml=folder/'score.musicxml'
    if kind=='musicxml':shutil.copyfile(source,xml)
    else:export(['-o',xml])
    if not xml.exists():raise ValueError('MuseScore não produziu MusicXML.')
    sequence=parse_musicxml(xml,include_cursor=True)
    media=json.loads(export(['--score-media']))
    normalized,_,_=synchronize_media(media,sequence)
    pages,timing=convert_media(normalized)
    for i,svg in enumerate(pages,1):(folder/f'score-{i}.svg').write_bytes(svg)
    (folder/'timing.json').write_text(json.dumps(timing,separators=(',',':')))
    root=ET.parse(xml).getroot()
    title=root.findtext('work/work-title') or root.findtext('movement-title') or source.stem
    composer=next((e.text for e in root.iter('creator') if e.get('type')=='composer' and e.text),'')
    instrument=next((e.text for e in root.iter('part-name') if e.text),'')
    return f'Title: {one_line(title)}\nAuthor: {one_line(composer)}\nInstrument: {one_line(instrument)}\nPlayback: generated\nCursor: true\nDraft: false\n\n'


def import_scores(args, destination, state, report):
    """Converte em paralelo e instala em série, preservando arquivos já preparados."""
    inputs = sorted(p for p in args.origem.rglob('*')
                    if p.is_file() and p.suffix.lower() in SUFFIXES[args.arquivos])
    if not inputs:
        raise ValueError('Nenhum arquivo do tipo selecionado foi encontrado na origem.')
    total = len(inputs)
    thematic = {slugify(value) for value in args.pastas_tematicas.split(',') if value.strip()}
    jobs = []
    composers = {}
    seen_keys = set()
    for source in inputs:
        rel = source.relative_to(args.origem)
        group_name = one_line(rel.parts[0]) if len(rel.parts) > 1 else 'Sem autor'
        group = slugify(group_name)
        if not group:
            raise ValueError(f'Pasta de compositor inválida: {rel}')
        title_slug = '-'.join(slugify(part) for part in rel.parts[1:-1] + (rel.stem,)) if len(rel.parts) > 1 else slugify(rel.stem)
        if not title_slug:
            raise ValueError(f'Nome de música inválido: {rel}')
        if args.tipo == 'musicas':
            key = f'musicas/{group}/{title_slug}'
        else:
            key = 'hinos/acervo/' + '-'.join(slugify(part) for part in rel.with_suffix('').parts)
        if key in seen_keys:
            raise ValueError('Arquivos distintos geram o mesmo identificador: ' + key)
        seen_keys.add(key)
        if group in composers and composers[group] != group_name:
            raise ValueError('Pastas diferentes geram o mesmo nome normalizado: ' + group)
        composers[group] = group_name
        jobs.append({'source': source, 'key': key, 'group': group,
                     'author': '' if group in thematic or group == 'sem-autor' else group_name})

    data_dir = destination / '.importacao'
    old_manifest = data_dir / 'manifest.json'
    legacy = json.loads(old_manifest.read_text()) if old_manifest.exists() else {}
    items_dir = data_dir / 'itens'
    groups_file = destination / 'compositores.json'
    groups_data = json.loads(groups_file.read_text()) if groups_file.exists() else {'groups': {}, 'scores': {}}
    managed = set(state.get('managed', []))
    pending = []
    start_total = time.monotonic()

    def manifest_file(key):
        return items_dir / (hashlib.sha256(key.encode()).hexdigest() + '.json')

    def register(job):
        key, group = job['key'], job['group']
        if group != 'sem-autor':
            groups_data['groups'][group] = composers[group]
            groups_data['scores'][key] = group
            managed.add('compositores.json')
        if args.tipo == 'musicas':
            index = destination / 'partituras/musicas' / group / '_index.md'
            if not index.exists():
                index.parent.mkdir(parents=True, exist_ok=True)
                label = 'Coleção: ' + composers[group] if group in thematic else composers[group]
                index.write_text('Title: ' + label + '\n', encoding='utf-8')
            managed.add(str(index.relative_to(destination)))

    for job in jobs:
        source, key = job['source'], job['key']
        md = destination / 'partituras' / (key + '.md')
        assets = destination / 'assets/music' / key
        record = manifest_file(key)
        previous = json.loads(record.read_text()) if record.exists() else legacy.get(key, legacy.get(key.split('/')[-1]) if args.tipo == 'hinos' else None)
        # Hash only input on resumption; recorded output sizes/mtimes allow a quick check.
        stamp = (source.stat().st_size, source.stat().st_mtime_ns)
        if previous and previous.get('kind') == args.arquivos:
            same_source = previous.get('stamp') == list(stamp) if previous.get('stamp') else previous.get('source') == digest(source)
            same_outputs = all((destination / p).is_file() and
                               ((destination / p).stat().st_size == details[0] and
                                (destination / p).stat().st_mtime_ns == details[1])
                               for p, details in previous.get('output_stamps', {}).items()) if previous.get('output_stamps') else all(
                                   (destination / p).is_file() and digest(destination / p) == h
                                   for p, h in previous.get('outputs', {}).items())
            if same_source and same_outputs and md.is_file() and assets.is_dir():
                before = md.read_text(encoding='utf-8')
                after = author_fallback(before, job['author'])
                if before != after:
                    md.write_text(after, encoding='utf-8')
                    # The old manifest is now invalid; save fresh stamps.
                    previous['output_stamps'] = {str(p.relative_to(destination)):
                         [p.stat().st_size, p.stat().st_mtime_ns] for p in [md, *assets.iterdir()] if p.is_file()}
                    previous.pop('outputs', None)
                    write_json(record, previous)
                managed.update([str(md.relative_to(destination)), *[
                    str(p.relative_to(destination)) for p in assets.iterdir() if p.is_file()]])
                register(job)
                report['ignorados'].append(str(source))
                continue
        if (md.exists() or assets.exists()) and not args.atualizar:
            report['erros'].append({'arquivo': str(source), 'erro': 'Destino já existe; use --atualizar.'})
            continue
        job.update(md=md, assets=assets, record=record, stamp=stamp)
        pending.append(job)

    print(f'Origem: {args.origem} | {total} arquivos | {len(pending)} para converter | '
          f'{len(report["ignorados"])} reaproveitados | workers={args.workers}', flush=True)
    def convert(job):
        temp = tempfile.TemporaryDirectory(prefix='acervo-converter-')
        try:
            stage = Path(temp.name)
            key = job['key']
            folder = stage / 'assets/music' / key
            folder.parent.mkdir(parents=True, exist_ok=True)
            metadata = author_fallback(prepare_score(job['source'], folder, args.arquivos, executable), job['author'])
            staged_md = stage / 'partituras' / (key + '.md')
            staged_md.parent.mkdir(parents=True, exist_ok=True)
            staged_md.write_text(metadata, encoding='utf-8')
            load_catalog(stage)
            return temp, folder, metadata
        except Exception:
            temp.cleanup()
            raise

    executable = shutil.which(args.musescore) or args.musescore
    def install(job, result):
        temp, folder, metadata = result
        try:
            md, target = job['md'], job['assets']
            md.parent.mkdir(parents=True, exist_ok=True)
            target.parent.mkdir(parents=True, exist_ok=True)
            backup = destination / '.importacao/backups' / time.strftime('%Y%m%d-%H%M%S') / hashlib.sha256(job['key'].encode()).hexdigest()[:16]
            old_md = md.read_bytes() if md.exists() else None
            if target.exists() or old_md is not None:
                backup.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    shutil.move(str(target), str(backup / 'assets'))
                if old_md is not None: (backup / 'metadata.md').write_bytes(old_md)
            try:
                shutil.copytree(folder, target)
                md.write_text(metadata, encoding='utf-8')
            except Exception:
                if target.exists(): shutil.rmtree(target)
                if (backup / 'assets').exists(): shutil.move(str(backup / 'assets'), str(target))
                if old_md is not None: md.write_bytes(old_md)
                elif md.exists(): md.unlink()
                raise
            outputs = [md, *target.iterdir()]
            record_data = {'stamp': list(job['stamp']), 'kind': args.arquivos,
                           'output_stamps': {str(p.relative_to(destination)):
                               [p.stat().st_size, p.stat().st_mtime_ns] for p in outputs if p.is_file()}}
            write_json(job['record'], record_data)
            managed.update(record_data['output_stamps'])
            register(job)
        finally:
            temp.cleanup()

    processed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        iterator = iter(pending)
        running = {}
        def submit_one():
            try: j = next(iterator)
            except StopIteration: return False
            running[pool.submit(convert, j)] = (j, time.monotonic())
            return True
        for _ in range(min(len(pending), args.workers * 2)):
            submit_one()
        while running:
            ready, _ = wait(running, return_when=FIRST_COMPLETED)
            for future in ready:
                job, started = running.pop(future)
                processed += 1
                try:
                    install(job, future.result())
                    report['preparados'].append(str(job['source']))
                    status = 'OK'
                except Exception as error:
                    report['erros'].append({'arquivo': str(job['source']), 'erro': str(error)})
                    status = 'ERRO: ' + str(error)
                elapsed = time.monotonic() - started
                print(f'[{processed}/{len(pending)}] {status} | {elapsed:.1f}s | '
                      f'{job["source"].relative_to(args.origem)}', flush=True)
                if processed % 10 == 0:
                    write_json(data_dir / 'resumo.json', report)
                    write_json(groups_file, groups_data)
                    state['managed'] = sorted(managed)
                    write_json(destination / '.acervo-site.json', state)
                submit_one()
    write_json(groups_file, groups_data)
    state['managed'] = sorted(managed)
    write_json(destination / '.acervo-site.json', state)
    write_json(data_dir / 'resumo.json', report)
    print(f'Importação concluída: {len(report["preparados"])} preparados; '
          f'{len(report["ignorados"])} reaproveitados; {len(report["erros"])} erros; '
          f'{time.monotonic()-start_total:.1f}s', flush=True)
    return report


def configure_github(destination,state,args):
    repo=state['repository'];expected='https://github.com/'+repo+'.git'
    if not (destination/'.git').exists():run(['git','init','-b','main'],cwd=destination)
    top=Path(output(['git','rev-parse','--show-toplevel'],cwd=destination)).resolve()
    if top!=destination:raise ValueError('O destino não é a raiz do repositório Git.')
    if output(['git','branch','--show-current'],cwd=destination)!='main':raise ValueError('Use a branch main no destino.')
    staged=output(['git','diff','--cached','--name-only'],cwd=destination)
    if staged:raise ValueError('Existem arquivos já staged no destino; resolva-os antes de criar o commit.')
    run(['gh','auth','status'],capture_output=True)
    remote=subprocess.run(['git','remote','get-url','origin'],cwd=destination,capture_output=True,text=True)
    if remote.returncode==0 and remote.stdout.strip()!=expected:raise ValueError('Origin diferente do repositório solicitado.')
    lookup=subprocess.run(['gh','repo','view',repo,'--json','nameWithOwner'],capture_output=True,text=True)
    if lookup.returncode==0 and not state.get('github_created'):
        raise ValueError('Repositório remoto já existe e não foi criado por este script. Nada será enviado.')
    if lookup.returncode:
        run(['gh','repo','create',repo,'--public','--description',one_line(args.titulo)])
        state['github_created']=True;write_json(destination/'.acervo-site.json',state)
    if remote.returncode:run(['git','remote','add','origin',expected],cwd=destination)
    # Only managed files and explicitly numbered carousel images, never arbitrary preexisting files.
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('collection_carousel',destination/'carousel.py');module=module_from_spec(spec);spec.loader.exec_module(module)
    carousel_files=['carrossel/'+name for name in module.images(destination)]
    for name in list(carousel_files):
        alt=Path(name).with_suffix('.txt')
        if (destination/alt).exists():carousel_files.append(str(alt))
    files=sorted(set(state['managed']+carousel_files))
    state['managed']=files
    write_json(destination/'.acervo-site.json',state)
    # Do not allow a preexisting repository's unrelated tracked files into a new public remote.
    tracked=set(output(['git','ls-files'],cwd=destination).splitlines())
    if tracked-set(files):raise ValueError('Repositório local contém arquivos rastreados alheios ao acervo; envio bloqueado.')
    for key,value in [('user.name',args.autor),('user.email',args.email)]:
        exists=subprocess.run(['git','config','--get',key],cwd=destination,capture_output=True)
        if exists.returncode:run(['git','config',key,value],cwd=destination)
    for name in files:
        p=destination/name
        if p.is_symlink():raise ValueError('Link simbólico entre os arquivos públicos: '+name)
        if p.is_file() and p.stat().st_size>=95*1024*1024:raise ValueError('Arquivo muito grande para GitHub: '+name)
    # Git-add in chunks to avoid command line limits, commit only once.
    for start in range(0, len(files), 300):
        batch = [n for n in files[start:start + 300] if (destination/n).exists() or n in tracked]
        if batch:
            run(['git', 'add', '--all', '--', *batch], cwd=destination)
    changed = subprocess.run(['git','diff','--cached','--quiet'], cwd=destination).returncode
    if changed == 1:
        run(['git','commit','-m','Preparar acervo Clave Sol [skip ci]'],cwd=destination)
    elif changed != 0:
        raise ValueError('Falha ao verificar alterações staged.')
    run(['git','push','-u','origin','main'],cwd=destination)
    endpoint='repos/'+repo+'/pages'
    status=subprocess.run(['gh','api',endpoint],capture_output=True,text=True)
    run(['gh','api','--method','PUT' if status.returncode==0 else 'POST',endpoint,'-f','build_type=workflow'],capture_output=True)
    run(['gh','api','--method','PUT',endpoint,'-f','cname='+state['domain']],capture_output=True)
    print('Pages configurado. Execute Actions → Publicar acervo → Run workflow. HTTPS: habilite quando o certificado estiver pronto.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destino',type=Path,required=True)
    parser.add_argument('--tipo',choices=('musicas','hinos'),default='musicas',help='Músicas por compositor ou hinário legado.')
    parser.add_argument('--workers',type=int,default=3,help='Conversões simultâneas do MuseScore (padrão 3).')
    parser.add_argument('--pastas-tematicas',default='Christmas',help='Pastas separadas por vírgula que não representam compositores.')
    parser.add_argument('--pular-build',action='store_true',help='Pular build e verificação de links; exige --somente-local.')
    parser.add_argument('--simular',action='store_true',help='Mostra os destinos dos arquivos sem alterar nada nem chamar MuseScore/GitHub.')
    parser.add_argument('--origem',type=Path,required=True)
    parser.add_argument('--arquivos',choices=SUFFIXES,required=True)
    parser.add_argument('--dominio',required=True,help='Subdomínio, ex.: exemplo → exemplo.clavesol.com.br')
    parser.add_argument('--titulo',default=None)
    parser.add_argument('--descricao',default='Partituras para ler, ouvir e praticar com o player Clave Sol.')
    parser.add_argument('--repositorio',help='DONO/NOME; padrão: usuário gh/nome da pasta de destino')
    parser.add_argument('--musescore',default=str(Path.home()/'bin/musescore'))
    parser.add_argument('--somente-local',action='store_true',help='Preparar/testar sem criar repositório remoto')
    parser.add_argument('--atualizar',action='store_true',help='Reimportar arquivos alterados, com backup no destino')
    parser.add_argument('--ignorar-incompativeis',action='store_true',help='Permitir envio somente dos funcionais quando houver falhas de importação')
    parser.add_argument('--autor',default='Djames Suhanko')
    parser.add_argument('--email',default='djames.suhanko@gmail.com')
    args=parser.parse_args()
    try:
        destination=args.destino.expanduser().resolve();args.origem=args.origem.expanduser().resolve(strict=True)
        if args.workers < 1 or args.workers > 16: raise ValueError('--workers deve ficar entre 1 e 16.')
        if args.pular_build and not args.somente_local: raise ValueError('--pular-build exige --somente-local.')
        if not args.origem.is_dir():raise ValueError('--origem precisa ser um diretório.')
        if destination==args.origem or destination.is_relative_to(args.origem) or args.origem.is_relative_to(destination):raise ValueError('Origem e destino devem ser diretórios separados, sem conter um ao outro.')
        if not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',args.dominio):raise ValueError('--dominio deve conter só o subdomínio, sem pontos/barras.')
        if destination.exists() and not destination.is_dir():raise ValueError('--destino precisa ser um diretório.')
        args.titulo=one_line(args.titulo or args.dominio.replace('-',' ').title());args.descricao=one_line(args.descricao)
        if args.simular:
            sources = sorted(p for p in args.origem.rglob('*')
                             if p.is_file() and p.suffix.lower() in SUFFIXES[args.arquivos])
            if not sources: raise ValueError('Nenhum arquivo encontrado.')
            seen = set()
            print(f'SIMULAÇÃO: {len(sources)} arquivos encontrados; nenhum será alterado.', flush=True)
            for i, source in enumerate(sources):
                rel = source.relative_to(args.origem)
                group = slugify(rel.parts[0]) if len(rel.parts) > 1 else 'sem-autor'
                name = '-'.join(slugify(part) for part in rel.parts[1:-1] + (rel.stem,)) if len(rel.parts) > 1 else slugify(rel.stem)
                key = f'musicas/{group}/{name}' if args.tipo == 'musicas' else 'hinos/acervo/' + '-'.join(slugify(part) for part in rel.with_suffix('').parts)
                if key in seen:raise ValueError('Colisão de nome: ' + key)
                seen.add(key)
                if i < 30:print(f'  {rel}  =>  partituras/{key}.md', flush=True)
            if len(sources) > 30:print(f'  ... e outros {len(sources)-30} arquivos.', flush=True)
            return

        marker=destination/'.acervo-site.json'
        repository=args.repositorio or (json.loads(marker.read_text())['repository'] if marker.exists() else None)
        if not repository:
            owner=output(['gh','api','user','--jq','.login']) if not args.somente_local else 'DjamesSuhanko'
            repository=owner+'/'+destination.name
        if not re.fullmatch(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+',repository):raise ValueError('--repositorio precisa ser DONO/NOME válido.')
        if (destination/'.git').exists() and not marker.exists():raise ValueError('Destino já é repositório não gerenciado; use outra pasta.')
        state=initialize(destination,args.dominio+'.clavesol.com.br',args.titulo,args.descricao,repository,args.tipo)
        report={'status':'importando','preparados':[],'ignorados':[],'erros':[]}
        write_json(destination/'.importacao/resumo.json',report)
        import_scores(args,destination,state,report)
        env=dict(os.environ,BASE_PATH='')
        if not args.pular_build:
            started=time.monotonic();print('Gerando site...',flush=True)
            run([sys.executable,'build.py'],cwd=destination,env=env)
            print(f'Build: {time.monotonic()-started:.1f}s',flush=True)
            started=time.monotonic();print('Verificando links...',flush=True)
            run([sys.executable,'scripts/check_links.py'],cwd=destination,env=env)
            print(f'Verificação de links: {time.monotonic()-started:.1f}s',flush=True)
        if report['erros'] and not args.ignorar_incompativeis:
            report['status']='erros_importacao';write_json(destination/'.importacao/resumo.json',report)
            raise ValueError('Há arquivos incompatíveis. Veja .importacao/resumo.json; nada enviado. Use --ignorar-incompativeis se quiser publicar apenas os funcionais.')
        if not args.somente_local:configure_github(destination,state,args)
        report['status']='pronto_local' if args.somente_local else 'pronto_pages';write_json(destination/'.importacao/resumo.json',report)
        print('Pronto:',destination,'\nResumo:',destination/'.importacao/resumo.json')
    except (ValueError,OSError,subprocess.SubprocessError,ET.ParseError) as error:
        parser.exit(1,f'Erro: {error}\nArquivos já preparados foram preservados; execute o mesmo comando para retomar.\n')
if __name__=='__main__':main()
