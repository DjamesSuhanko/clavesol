#!/usr/bin/env python3
"""Corrige a escrita de todos os MSCZ do hinário Dó, sem alterar o site."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from transpor_hinos import KEYS, ROOT, transform, verify_sound


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--origem',type=Path,default=ROOT.parent/'clavesol-hinos-do/assets/music/hinos/do')
    p.add_argument('--destino',type=Path,default=None)
    p.add_argument('--jobs',type=int,choices=range(1,5),default=3)
    p.add_argument('--musescore',default=str(Path.home()/'bin/musescore'))
    a=p.parse_args()
    source=a.origem.expanduser().resolve()
    output=(a.destino or ROOT.parent.parent/'correcoes-hinario-do'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')).expanduser().resolve()
    if output.is_relative_to(source) or output.exists():
        p.error('Use um destino novo e fora da árvore de assets')
    plans=[];missing=[]
    for folder in sorted(source.glob('hino-*'),key=lambda f:int(f.name.split('-')[-1])):
        if folder.name=='hino-52':continue
        original=folder/'score.mscz'
        if not original.exists():
            missing.append(folder.name);continue
        with zipfile.ZipFile(original) as z:
            root=ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith('.mscx'))))
        instruments=root.findall('./Score/Part/Instrument')
        if len(instruments)!=2 or any((i.findtext('transposeChromatic','0'),i.findtext('transposeDiatonic','0'))!=('-5','-3') for i in instruments):
            p.error(f'{folder.name}: configuração diferente; nenhuma saída criada')
        keys=[s.findtext('./Measure/voice/KeySig/concertKey') for s in root.findall('./Score/Staff')]
        if len(keys)!=2 or keys[0]!=keys[1] or keys[0] is None:
            p.error(f'{folder.name}: armaduras iniciais incompatíveis')
        target=next((k for k,v in KEYS.items() if v==int(keys[0])),None)
        if target is None:p.error(f'{folder.name}: tonalidade não suportada')
        plans.append((original,target))
    output.mkdir(parents=True)
    def correct(plan):
        original,key=plan;name=original.parent.name
        folder=output/name;folder.mkdir()
        original_bytes=original.read_bytes()
        backup=folder/'original.mscz';backup.write_bytes(original_bytes)
        try:
            with tempfile.TemporaryDirectory(prefix='validar-hino-') as tmp:
                temp=Path(tmp);changed=temp/'score.mscz'
                count=transform(backup,changed,{1,2,3,4},key)
                verify_sound(backup,changed,temp,a.musescore)
                with zipfile.ZipFile(changed) as z:r=ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith('.mscx'))))
                if any(int(i.findtext('transposeChromatic','0'))!=0 or int(i.findtext('transposeDiatonic','0'))!=0 for i in r.findall('./Score/Part/Instrument')):
                    raise ValueError('A compensação não foi zerada')
                if original.read_bytes()!=original_bytes:raise ValueError('Origem mudou durante a execução')
                shutil.copy2(changed,folder/'FIX-score.mscz')
            return {'hino':name,'tonalidade':key,'notas':count,'status':'validado','sha256_original':hashlib.sha256(original_bytes).hexdigest()}
        except Exception as e:
            return {'hino':name,'tonalidade':key,'status':'erro','erro':str(e)}
    results=[]
    report={'origem':str(source),'ignorado':['hino-52'],'sem_mscz':missing,'resultados':results}
    with ThreadPoolExecutor(max_workers=a.jobs) as executor:
        futures=[executor.submit(correct,plan) for plan in plans]
        for f in as_completed(futures):
            result=f.result();results.append(result)
            (output/'relatorio.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
            print(f'{len(results)}/{len(plans)} {result["hino"]}: {result["status"]}',flush=True)
    failures=sum(r['status']=='erro' for r in results)
    print(f'Destino: {output}\nValidados: {len(results)-failures}; erros: {failures}; sem MSCZ: {len(missing)}. Site intacto.',flush=True)
    return bool(failures)

if __name__=='__main__':raise SystemExit(main())
