#!/usr/bin/env python3
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from transpor_hinos import transform, verify_sound, transpose_harmonies, sounding_harmonies
SOURCE=ROOT.parent/'clavesol-hinos-do/assets/music/hinos/do/hino-52/score.mscz'

def read(p):
    with zipfile.ZipFile(p) as z:return ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith('.mscx'))))

class HarmonyTransposition(unittest.TestCase):
    def test_roots_basses_and_quality(self):
        for wrapped in (True, False):
            content='<root>15</root><base>19</base><name>7</name><extension>77</extension>'
            if wrapped: content='<harmonyInfo>'+content+'</harmonyInfo>'
            staff=ET.fromstring('<Staff><Harmony>'+content+'</Harmony><Harmony><name>*</name></Harmony></Staff>')
            transpose_harmonies(staff,-2)
            harmony=staff.find('Harmony')
            info=harmony.find('harmonyInfo') if wrapped else harmony
            self.assertEqual(info.findtext('root'),'13')  # G -> F
            self.assertEqual(info.findtext('base'),'17')  # B -> A
            self.assertEqual(info.findtext('name'),'7')
            self.assertEqual(info.findtext('extension'),'77')
            self.assertEqual(staff.findall('Harmony')[1].findtext('name'),'*')
            transpose_harmonies(staff,2)
            self.assertEqual(info.findtext('root'),'15')
            self.assertEqual(info.findtext('base'),'19')

    def test_accidentals_and_unstructured_chords(self):
        staff=ET.fromstring('<Staff><Harmony><harmonyInfo><root>21</root><base>-2</base><name>m7</name></harmonyInfo></Harmony></Staff>')
        transpose_harmonies(staff,-2)  # C# -> B; invalid bass means no bass.
        self.assertEqual(staff.findtext('.//root'),'19')
        self.assertEqual(staff.findtext('.//base'),'-2')
        with self.assertRaises(ValueError):
            transpose_harmonies(ET.fromstring('<Staff><Harmony><name>G7/B</name></Harmony></Staff>'),-2)
        with self.assertRaises(ValueError):
            transpose_harmonies(ET.fromstring('<Staff><Harmony><root>33</root></Harmony></Staff>'),7)

class PreserveSound(unittest.TestCase):
    def test_real_exports_and_pitches(self):
        digest=hashlib.sha256(SOURCE.read_bytes()).digest()
        before=read(SOURCE)
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory)
            for key in ['C','Bb','Eb']:
                output=d/(key+'.mscz')
                transform(SOURCE,output,{1,2,3,4},key)
                after=read(output)
                for tag in ['pitch','tpc','concertKey','defaultClef','durationType','Lyrics','Harmony']:
                    self.assertEqual([ET.tostring(e) for e in before.iter(tag)],[ET.tostring(e) for e in after.iter(tag)])
                verify_sound(SOURCE,output,d,str(Path.home()/'bin/musescore'))
            c=read(d/'C.mscz')
            self.assertTrue(all(n.text=='0' for n in c.iter('transposeChromatic')))
            self.assertTrue(all(n.text=='0' for n in c.iter('actualKey')))
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).digest(),digest)

    def test_pairs_and_idempotence(self):
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory); a=d/'a.mscz'; b=d/'b.mscz'; c=d/'c.mscz'
            transform(SOURCE,a,{1,2},'C')
            self.assertEqual(ET.tostring(read(SOURCE).findall('./Score/Staff')[1]),ET.tostring(read(a).findall('./Score/Staff')[1]))
            transform(a,b,{3,4},'C')
            transform(b,c,{1,2,3,4},'C')
            self.assertEqual(ET.tostring(read(b)),ET.tostring(read(c)))
            for voices in [{1},{2},{3},{4},{1,3}]:
                with self.assertRaises(ValueError):transform(SOURCE,c,voices,'C')

    def test_cli_rejections(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'score.mscz';source.write_bytes(SOURCE.read_bytes())
            base=[sys.executable,str(ROOT/'transpor_hinos.py'),str(source)]
            for flags in [['--down','4','--tonalidade','C'],['--up','1','--tonalidade','C'],['--tonalidade','Am'],['--tonalidade','C','--vozes','1'],['--tonalidade','C','--vozes','5']]:
                self.assertNotEqual(subprocess.run(base+flags,capture_output=True).returncode,0)
            output=source.with_name('FIX-score.mscz');output.write_bytes(b'preservar')
            self.assertNotEqual(subprocess.run(base+['--tonalidade','C'],capture_output=True).returncode,0)
            self.assertEqual(output.read_bytes(),b'preservar')

if __name__=='__main__':unittest.main()
