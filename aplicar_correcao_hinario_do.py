#!/usr/bin/env python3
"""Prepara, valida e aplica o lote corrigido ao site, sem executar Git."""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from criar_licao import synchronize_media
from musicxml_audio import parse_musicxml
from score_catalog import read_markdown
from scripts.score_timing import convert_media
from transpor_hinos import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(folder):
    return {str(p.relative_to(folder)):digest(p) for p in folder.rglob('*') if p.is_file()}


def unpack_xml(media):
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(media['mxml']))) as z:
        c=ET.fromstring(z.read('META-INF/container.xml'))
        name=next(e.get('full-path') for e in c.iter() if e.tag.rsplit('}',1)[-1]=='rootfile')
        return z.read(name)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lote',type=Path,required=True)
    p.add_argument('--trabalho',type=Path,required=True)
    p.add_argument('--repositorio',type=Path,default=ROOT.parent/'clavesol-hinos-do')
    p.add_argument('--musescore',default=str(Path.home()/'bin/musescore'))
    p.add_argument('--jobs',type=int,choices=range(1,5),default=3)
    a=p.parse_args();repo=a.repositorio.resolve();work=a.trabalho.resolve();batch=a.lote.resolve()
    if work.exists() or work.is_relative_to(repo):p.error('Diretório de trabalho deve ser novo e externo ao repositório')
    work.mkdir(parents=True)
    state={'status':'preparando','inicio':datetime.datetime.now().isoformat(),'repositorio':str(repo),'erros':[]}
    def save():
        temp=work/'status.tmp';temp.write_text(json.dumps(state,ensure_ascii=False,indent=2));temp.replace(work/'status.json')
    save()
    try:
        report=json.loads((batch/'relatorio.json').read_text())
        entries=report['resultados']
        if len(entries)!=479 or any(e['status']!='validado' for e in entries) or any(e['hino']=='hino-52' for e in entries):
            raise ValueError('Lote não corresponde aos 479 hinos validados, sem o 52')
        if len({e['hino'] for e in entries})!=479:raise ValueError('Hinos duplicados')
        assets=Path('assets/music/hinos/do');metadata=Path('partituras/hinos/do')
        originals={}
        for e in entries:
            name=e['hino'];folder=repo/assets/name
            if digest(folder/'score.mscz')!=e['sha256_original']:raise ValueError(f'{name}: original mudou após validação')
            originals[name]=(snapshot(folder),digest(repo/metadata/(name+'.md')))
        preserved52=snapshot(repo/assets/'hino-52')
        # Cópia isolada de todo o site: build/validação não alteram o repositório.
        staged=work/'site-preparado'
        shutil.copytree(repo,staged,ignore=shutil.ignore_patterns('.git','dist','__pycache__','.venv','work'))
        def export(entry):
            name=entry['hino'];dest=staged/assets/name;source=batch/name/'FIX-score.mscz'
            command=[a.musescore,'-r','72','--score-media',str(source)]
            proc=subprocess.run(command,env=dict(os.environ,QT_QPA_PLATFORM='offscreen'),capture_output=True,timeout=180)
            if proc.returncode:raise ValueError(proc.stderr.decode(errors='replace')[-1200:])
            media=json.loads(proc.stdout)
            xml=unpack_xml(media)
            xml_path=dest/'score.musicxml';xml_path.write_bytes(xml)
            meta,_=read_markdown(staged/metadata/(name+'.md'))
            before=parse_musicxml(repo/assets/name/'score.musicxml',meta.get('tempo'),include_cursor=True)
            after=parse_musicxml(xml_path,meta.get('tempo'),include_cursor=True)
            for field in ('notes','duration','quarterBpm','fermatas','introEnd'):
                if before.get(field)!=after.get(field):raise ValueError('Diferença sonora em relação ao site atual: '+field)
            normalized,_,_=synchronize_media(media,after)
            svgs,timing=convert_media(normalized,scale=.72)
            for old in dest.glob('score-*.svg'):old.unlink()
            for i,svg in enumerate(svgs,1):(dest/f'score-{i}.svg').write_bytes(svg)
            (dest/'timing.json').write_text(json.dumps(timing,separators=(',',':')))
            shutil.copy2(source,dest/'score.mscz')
            if (dest/'score.pdf').exists():
                subprocess.run([a.musescore,'-o',str(dest/'score.pdf'),str(source)],env=dict(os.environ,QT_QPA_PLATFORM='offscreen'),check=True,capture_output=True,timeout=180)
            # Áudio gravado antigo não deve substituir a sequência regenerada.
            for n in ('score.mp3','score.ogg','sequence.json'):
                (dest/n).unlink(missing_ok=True)
            md=staged/metadata/(name+'.md');text=md.read_text()
            text=re.sub(r'^([Pp]ages:\s*)\d+',lambda m:m[1]+str(len(svgs)),text,flags=re.M)
            text=re.sub(r'^([Mm]easures:\s*)\d+',lambda m:m[1]+str(max(e['measure'] for e in timing['events'])),text,flags=re.M)
            md.write_text(text)
            return {'hino':name,'paginas':len(svgs),'notas':len(after['notes'])}
        done=[]
        with ThreadPoolExecutor(max_workers=a.jobs) as pool:
            tasks={pool.submit(export,e):e['hino'] for e in entries}
            for future in as_completed(tasks):
                name=tasks[future]
                try:done.append(future.result())
                except Exception as error:state['erros'].append({'hino':name,'erro':str(error)})
                state['exportados']=len(done);save()
                print(f'{len(done)+len(state["erros"])}/479 {name}; erros: {len(state["erros"])}',flush=True)
        if state['erros']:raise ValueError('Falhas na exportação; repositório intacto. Veja status.json')
        state['status']='validando-build';save()
        with (work/'build.log').open('w') as log:
            subprocess.run([sys.executable,str(staged/'build.py')],cwd=staged,env=dict(os.environ,BASE_PATH=''),stdout=log,stderr=subprocess.STDOUT,check=True)
        for e in entries:
            name=e['hino']
            if originals[name]!=(snapshot(repo/assets/name),digest(repo/metadata/(name+'.md'))):raise ValueError(f'{name}: alteração concorrente; aplicação cancelada')
        if snapshot(repo/assets/'hino-52')!=preserved52:raise ValueError('Hino 52 mudou durante a preparação')
        backup=work/'backup';backup.mkdir()
        for e in entries:
            name=e['hino'];shutil.copytree(repo/assets/name,backup/assets/name)
            md=backup/metadata/(name+'.md');md.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/metadata/(name+'.md'),md)
        state['status']='aplicando';save();applied=[];old_dist=False;new_dist=False
        try:
            for e in entries:
                name=e['hino'];applied.append(name)
                shutil.rmtree(repo/assets/name);shutil.copytree(staged/assets/name,repo/assets/name)
                shutil.copy2(staged/metadata/(name+'.md'),repo/metadata/(name+'.md'))
            if (repo/'dist').exists():shutil.move(repo/'dist',backup/'dist');old_dist=True
            shutil.move(staged/'dist',repo/'dist');new_dist=True
            if snapshot(repo/assets/'hino-52')!=preserved52:raise ValueError('Hino 52 alterado')
        except Exception:
            for name in applied:
                if (repo/assets/name).exists():shutil.rmtree(repo/assets/name)
                shutil.copytree(backup/assets/name,repo/assets/name)
                shutil.copy2(backup/metadata/(name+'.md'),repo/metadata/(name+'.md'))
            if new_dist:shutil.rmtree(repo/'dist')
            if old_dist:shutil.move(backup/'dist',repo/'dist')
            raise
        state.update(status='concluido',fim=datetime.datetime.now().isoformat(),aplicados=len(applied),backup=str(backup),hino52='preservado');save()
        print('CONCLUÍDO: 479 hinos aplicados, build validado; pronto para commit. Nenhum commit/push executado.',flush=True)
    except Exception as error:
        state.update(status='erro',erro_final=str(error));save();raise

if __name__=='__main__':main()
