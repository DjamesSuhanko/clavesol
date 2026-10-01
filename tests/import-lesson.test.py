import base64
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from criar_licao import prepare, commit_lesson, lesson_paths, main
import subprocess
from score_catalog import load_catalog

class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.root=self.base/'project';self.root.mkdir()
        self.source=self.base/'Lição 20.mscz';self.source.write_bytes(b'original')
        enc=lambda value:base64.b64encode(value.encode()).decode()
        positions='<score><elements><element id="0" page="0" x="120" y="120" sx="60" sy="120"/></elements><events><event elid="0" position="0"/></events></score>'
        self.media=dict(metadata={'duration':1},svgs=[enc('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 200"/>')],sposXML=enc(positions),mposXML=enc(positions))
        self.xml='<score-partwise><part><measure><sound tempo="50"/><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part></score-partwise>'
        self.mock=patch('criar_licao.subprocess.run',side_effect=self.export).start()
        self.addCleanup(patch.stopall)

    def export(self,command,**kwargs):
        if '-o' in command:
            p=Path(command[command.index('-o')+1]);p.write_text(self.xml if p.suffix=='.musicxml' else 'pdf')
            return SimpleNamespace(stdout=b'')
        return SimpleNamespace(stdout=json.dumps(self.media).encode())

    def run_import(self,**kwargs):
        return prepare(self.source,'pecci',root=self.root,executable='musescore',**kwargs)

    def test_two_lessons_independent_and_rounding(self):
        self.run_import(slug='licao-20',lesson=20,pdf=True)
        self.run_import(slug='licao-21',lesson=21)
        catalog=load_catalog(self.root)
        self.assertEqual([s.lesson for s in catalog.scores],[20,21])
        for s in catalog.scores:
            a=self.root/'assets'/s.assets
            self.assertEqual(json.loads((a/'timing.json').read_text())['duration'],1.2)
            self.assertEqual((a/'score.mscz').read_bytes(),b'original')
        self.assertEqual(self.source.read_bytes(),b'original')

    def test_msa_assets_index_and_independent_method(self):
        key = prepare(self.source, msa=True, root=self.root, slug='licao-20', lesson=20, pdf=True, executable='musescore')
        self.assertEqual(key, 'msa/licao-20')
        self.assertEqual((self.root/'partituras/msa/_index.md').read_text(), 'Title: MSA\n')
        self.assertFalse((self.root/'partituras/metodos').exists())
        assets = self.root/'assets/music/msa/licao-20'
        self.assertTrue(all((assets/name).is_file() for name in ['score.musicxml','score-1.svg','timing.json','score.mscz','score.pdf']))
        self.assertEqual(lesson_paths(self.root, key), ['partituras/msa/licao-20.md','assets/music/msa/licao-20','partituras/msa/_index.md'])
        self.run_import(slug='licao-20')
        catalog = load_catalog(self.root)
        self.assertEqual({s.key for s in catalog.scores}, {'msa/licao-20','metodos/pecci/licao-20'})

    def test_update_existing_msa_preserves_legacy_assets_and_text(self):
        md = self.root/'partituras/msa/107-msa-bb.md'
        md.parent.mkdir(parents=True)
        md.write_text('Title: Meu estudo\nAssets: music/107-msa-bb\nLegacy: musica/msa/107-msa-bb\n\nMeu texto.\n')
        index = md.parent/'_index.md'
        index.write_text('Title: MSA\nDescription: Minha descrição.\n')
        original_index = index.read_bytes()
        key = prepare(self.source, msa=True, root=self.root, slug='107-msa-bb', update=True, executable='musescore')
        self.assertIn('Meu texto.', md.read_text())
        self.assertIn('Legacy: musica/msa/107-msa-bb', md.read_text())
        self.assertEqual(index.read_bytes(), original_index)
        self.assertTrue((self.root/'assets/music/107-msa-bb/score.mscz').is_file())
        self.assertFalse((self.root/'assets/music/msa/107-msa-bb').exists())
        self.assertIn('assets/music/107-msa-bb', lesson_paths(self.root, key))
        self.assertEqual(load_catalog(self.root).scores[0].legacy, 'musica/msa/107-msa-bb')

    def test_msa_and_method_are_mutually_exclusive(self):
        with self.assertRaisesRegex(ValueError, 'não ambos'):
            self.run_import(msa=True)
        self.assertEqual(self.mock.call_count, 0)

    def test_update_preserves_text_and_cleans_old_pages(self):
        self.run_import(slug='licao-20')
        md=self.root/'partituras/metodos/pecci/licao-20.md'
        md.write_text(md.read_text()+'## Meu texto\nOrientações que devem ficar.\n')
        a=self.root/'assets/music/metodos/pecci/licao-20'
        (a/'score-2.svg').write_text('old')
        (a/'foto.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError,'já existe'):
            self.run_import(slug='licao-20')
        self.run_import(slug='licao-20',update=True)
        self.assertIn('Orientações que devem ficar.',md.read_text())
        self.assertFalse((a/'score-2.svg').exists())
        self.assertEqual((a/'foto.txt').read_text(),'keep')

    def test_export_failure_and_bad_duration_do_not_install(self):
        self.media['metadata']['duration']=4
        with self.assertRaisesRegex(ValueError,'incompatíveis'):
            self.run_import()
        self.assertEqual(list(self.root.iterdir()),[])
        self.mock.side_effect=OSError('export failed')
        with self.assertRaises(OSError): self.run_import()
        self.assertEqual(list(self.root.iterdir()),[])

    def test_refuses_path_escape_and_other_invalid_lesson(self):
        with self.assertRaises(ValueError): self.run_import(slug='../escape')
        md=self.root/'partituras/metodos/pecci/incomplete.md';md.parent.mkdir(parents=True)
        md.write_text('Title: Incompleta\n')
        with self.assertRaisesRegex(ValueError,'incomplete'):
            self.run_import()
        self.assertFalse((self.root/'assets').exists())

class CliTests(unittest.TestCase):
    def test_msa_does_not_prompt_and_reports_msa_paths(self):
        from io import StringIO
        with patch('sys.argv', ['criar_licao.py', '/tmp/licao.mscz', '--msa']), patch('builtins.input') as prompt, patch('criar_licao.prepare', return_value='msa/licao') as importer, patch('criar_licao.lesson_paths', return_value=['partituras/msa/licao.md','assets/music/msa/licao','partituras/msa/_index.md']), patch('sys.stdout', new_callable=StringIO) as output:
            main()
            prompt.assert_not_called()
            self.assertTrue(importer.call_args.kwargs['msa'])
            self.assertIn('git add partituras/msa/licao.md', output.getvalue())
            self.assertNotIn('metodos/', output.getvalue())

    def test_cli_rejects_mixed_destinations_before_export(self):
        with patch('sys.argv', ['criar_licao.py', '/tmp/licao.mscz', '--msa', '--metodo', 'pecci']), patch('sys.stderr'), patch('criar_licao.prepare') as importer:
            with self.assertRaises(SystemExit) as error: main()
            self.assertEqual(error.exception.code, 2)
            importer.assert_not_called()

class CommitTests(unittest.TestCase):
    def test_commits_only_lesson_and_preserves_other_staged_changes(self):
        with TemporaryDirectory() as directory:
            root=Path(directory)
            def git(*args):
                return subprocess.run(['git',*args],cwd=root,check=True,capture_output=True,text=True).stdout
            git('init','-q');git('config','user.name','Test');git('config','user.email','test@example.com')
            (root/'unrelated').write_text('original');git('add','unrelated');git('commit','-qm','initial')
            (root/'unrelated').write_text('user work');git('add','unrelated')
            (root/'lesson').write_text('new lesson')
            commit_lesson(root,['lesson'],'lesson import')
            self.assertEqual(git('show','--format=','--name-only','HEAD').strip(),'lesson')
            self.assertEqual(git('diff','--cached','--name-only').strip(),'unrelated')

if __name__=='__main__': unittest.main()
