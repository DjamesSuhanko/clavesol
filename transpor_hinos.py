#!/usr/bin/env python3
"""Reescrita de tonalidade SATB preservando o som (MSCZ). Veja docs/TRANSPOR-HINOS.md."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
LETTERS = 'CDEFGAB'
NATURAL = [0, 2, 4, 5, 7, 9, 11]
TPC = [14, 16, 18, 13, 15, 17, 19]
KEYS = {'Cb': -7, 'Gb': -6, 'Db': -5, 'Ab': -4, 'Eb': -3, 'Bb': -2,
        'F': -1, 'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6, 'C#': 7}


def spelling(tpc):
    for i, base in enumerate(TPC):
        if (tpc-base) % 7 == 0:
            return i, (tpc-base)//7
    raise ValueError('TPC inválido')


def signature(fifths):
    if not -7 <= fifths <= 7:
        raise ValueError('Armadura não convencional não suportada')
    result = [0]*7
    for letter in ('FCGDAEB' if fifths >= 0 else 'BEADGCF')[:abs(fifths)]:
        result[LETTERS.index(letter)] = 1 if fifths >= 0 else -1
    return result


def put(parent, tag, value):
    node = parent.find(tag)
    if node is None:
        node = ET.SubElement(parent, tag)
    node.text = str(value)


def concert_tpc(written_midi, letter, chromatic, diatonic, accidental):
    octave = (written_midi-NATURAL[letter]-accidental)//12
    index = octave*7+letter+diatonic
    dest = index % 7
    alter = written_midi+chromatic-(index//7*12+NATURAL[dest])
    if abs(alter) > 2:
        raise ValueError('Transposição requer acidente maior que duplo')
    return TPC[dest]+alter*7


def transform(source, destination, voices, key):
    """Change written key; preserve concert pitches and concert key signatures."""
    with zipfile.ZipFile(source) as archive:
        entries = [(i, archive.read(i.filename)) for i in archive.infolist()]
    scores = [(i, data) for i, data in entries if i.filename.endswith('.mscx')]
    if len(scores) != 1:
        raise ValueError('Esperado um único MSCX dentro do MSCZ')
    info, data = scores[0]
    root = ET.fromstring(data)
    score = root.find('Score')
    staves, parts = score.findall('Staff'), score.findall('Part')
    if len(staves) != 2 or len(parts) != 2 or any(len(p.findall('Staff')) != 1 for p in parts):
        raise ValueError('Exige dois pentagramas SATB, um por Part')
    for pair in ({1, 2}, {3, 4}):
        if voices & pair and not pair <= voices:
            raise ValueError('Selecione o par 1,2 ou 3,4: a compensação vale para o instrumento inteiro')
    styles = [score]
    for entry, content in entries:
        if entry.filename.endswith('.mss'):
            styles.append(ET.fromstring(content))
    if any(e.text == '1' for style in styles for e in style.iter('concertPitch')):
        raise ValueError('Desative som de concerto antes de ajustar a escrita')
    if list(score.iter('InstrumentChange')) or any(h.findtext('harmonyInfo/name', h.findtext('name', '')).strip() != '*' for h in score.iter('Harmony')):
        raise ValueError('Mudanças de instrumento/cifras harmônicas exigem revisão manual')
    count = 0
    for si, (staff, part) in enumerate(zip(staves, parts)):
        if not voices & {si*2+1, si*2+2}:
            continue
        instr = part.find('Instrument')
        chrom = int(instr.findtext('transposeChromatic', '0'))
        dia = int(instr.findtext('transposeDiatonic', '0'))
        keys = staff.findall('.//KeySig')
        if not keys or staff.find('./Measure/voice/KeySig') is None:
            raise ValueError('Armadura inicial explícita necessária')
        old_key = int(keys[0].findtext('actualKey', keys[0].findtext('concertKey', '0')))
        old_name = next((k for k, v in KEYS.items() if v == old_key), None)
        if old_name is None:
            raise ValueError('Armadura inicial não suportada')
        def tonic(name):
            i = LETTERS.index(name[0])
            acc = 1 if '#' in name else -1 if 'b' in name else 0
            return i, NATURAL[i]+acc
        old_letter, old_pitch = tonic(old_name)
        new_letter, new_pitch = tonic(key)
        semitones, steps = new_pitch-old_pitch, new_letter-old_letter
        # Intervalo mais próximo; preserva o registro e evita oitavas gratuitas.
        while semitones > 6:
            semitones -= 12; steps -= 7
        while semitones < -6:
            semitones += 12; steps += 7
        new_chrom, new_dia = chrom-semitones, dia-steps
        fifth_delta = KEYS[key]-old_key
        for ks in keys:
            if ks.find('custom') is not None or ks.find('atonal') is not None:
                raise ValueError('Armadura customizada/atonal não suportada')
            old = int(ks.findtext('actualKey', ks.findtext('concertKey', '0')))
            target = old+fifth_delta
            if not -7 <= target <= 7:
                raise ValueError('Uma modulação excederia sete acidentes')
            put(ks, 'actualKey', target)
            # concertKey representa a tonalidade sonora e permanece intacta.
        for note in staff.iter('Note'):
            pitch = int(note.findtext('pitch'))
            written = pitch-chrom
            letter, acc = spelling(int(note.findtext('tpc2', note.findtext('tpc'))))
            if (written-NATURAL[letter]-acc) % 12:
                raise ValueError('Pitch/TPC escrito incompatíveis')
            index = (written-NATURAL[letter]-acc)//12*7+letter+steps
            dest = index % 7
            new_written = written+semitones
            new_acc = new_written-(index//7*12+NATURAL[dest])
            if abs(new_acc) > 2 or not 0 <= new_written <= 127:
                raise ValueError('Nota escrita fora da faixa suportada')
            put(note, 'tpc2', TPC[dest]+7*new_acc)
            # Não mudar pitch nem tpc: são o som e sua grafia de concerto.
            for accidental in note.findall('Accidental'):
                note.remove(accidental)
            count += 1
        put(instr, 'transposeChromatic', new_chrom)
        put(instr, 'transposeDiatonic', new_dia)
    payload = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as out:
        for entry, content in entries:
            if not entry.filename.startswith('Thumbnails/'):
                out.writestr(entry, payload if entry.filename == info.filename else content)
    return count


def verify_sound(source, changed, directory, executable):
    """Real MuseScore exports, then the same parser used by the website."""
    from musicxml_audio import parse_musicxml
    results = []
    xml_roots = []
    for name, path in [('antes', source), ('depois', changed)]:
        xml = directory/(name+'.musicxml')
        proc = subprocess.run([str(executable), '-o', str(xml), str(path)],
                              env=dict(os.environ, QT_QPA_PLATFORM='offscreen'),
                              capture_output=True, timeout=180)
        if proc.returncode or not xml.is_file():
            raise ValueError('Falha ao validar no MuseScore: '+proc.stderr.decode(errors='replace')[-1000:])
        results.append(parse_musicxml(xml, include_cursor=True))
        xml_roots.append(ET.parse(xml).getroot())
    for field in ('notes', 'duration', 'quarterBpm', 'fermatas', 'introEnd'):
        if results[0].get(field) != results[1].get(field):
            raise ValueError('Som não preservado na exportação: '+field+'; saída não será publicada')
    for tag in ('lyric', 'clef', 'time'):
        def values(root):
            return [[(e.tag, e.text.strip() if e.text else '', sorted((k,v) for k,v in e.attrib.items() if k not in ("default-x", "default-y", "relative-x", "relative-y"))) for e in node.iter()] for node in root.iter(tag)]
        if values(xml_roots[0]) != values(xml_roots[1]):
            raise ValueError('Exportação alterou '+tag)
    print(f"Som conferido: {len(results[0]['notes'])} notas idênticas, com os mesmos tempos e durações.", flush=True)


def site_destination(source):
    for repo in source.parents:
        if (repo/'hinario.json').is_file():
            import json
            collection = json.loads((repo/'hinario.json').read_text())['collection']
            expected = repo/'assets/music/hinos'/collection/source.parent.name
            if source.parent != expected or not (repo/'partituras/hinos'/collection/(source.parent.name+'.md')).is_file():
                break
            return repo, collection
    raise ValueError('--to-site exige arquivo na pasta cadastrada assets/music/hinos/<coleção>/hino-N')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('arquivo', type=Path)
    p.add_argument('--vozes', default='1,2,3,4', help='Pares completos: 1,2 ou 3,4; padrão todas')
    p.add_argument('--tonalidade', required=True, choices=KEYS, help='Nova tonalidade escrita inicial, preservando o som')
    p.add_argument('--to-site', action='store_true', help='Substitui assets cadastrados, exporta e gera dist; não faz commit/push')
    p.add_argument('--musescore', default=str(Path.home()/'bin/musescore'))
    args = p.parse_args(argv)
    try:
        voice_list = [int(v) for v in args.vozes.split(',')]
        voices = set(voice_list)
        if not voices or not voices <= {1, 2, 3, 4} or len(voice_list) != len(voices):
            raise ValueError('Use vozes únicas de 1 a 4')
        source = args.arquivo.expanduser().resolve(strict=True)
        if source.suffix.lower() != '.mscz':
            raise ValueError('Informe um arquivo .mscz')
        destination = source.with_name('FIX-'+source.name)
        if not args.to_site and destination.exists():
            raise ValueError(f'Destino já existe; não será sobrescrito: {destination}')
        site = site_destination(source) if args.to_site else None
        with tempfile.TemporaryDirectory(prefix='transpor-hinos-') as tmp:
            changed = Path(tmp)/'score.mscz'
            count = transform(source, changed, voices, args.tonalidade)
            verify_sound(source, changed, Path(tmp), args.musescore)
            if args.to_site:
                from criar_licao import prepare
                repo, collection = site
                # Backup durável antes da substituição; nunca executar Git.
                import datetime
                backup = Path.home()/'Documents/ClaveSol/backups-transposicao'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
                shutil.copytree(source.parent, backup/'assets')
                shutil.copy2(repo/'partituras/hinos'/collection/(source.parent.name+'.md'), backup/'metadata.md')
                print(f'Backup: {backup}', flush=True)
                prepare(changed, hinos=True, hinario=collection, root=repo, slug=source.parent.name,
                        executable=args.musescore, update=True)
                subprocess.run([sys.executable, str(repo/'build.py')], cwd=repo,
                               env=dict(os.environ, BASE_PATH=''), check=True)
                print(f'Site preparado em {repo / "dist"}. Nenhum commit/push executado.')
            else:
                # Criação exclusiva evita sobrescrita mesmo com duas execuções concorrentes.
                with destination.open('xb') as out:
                    out.write(changed.read_bytes())
                print(f'{count} notas reescritas, som preservado: {destination}')
    except (ValueError, OSError, ET.ParseError, zipfile.BadZipFile, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        p.exit(1, f'Erro: {error}\n')


if __name__ == '__main__':
    main()
