#!/usr/bin/env python3
"""Local integration: all input formats, resume, backup and Pages commands without network."""
import importlib.util,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import criar_hinario as app

class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='acervo-test-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.source=self.root/'source';self.source.mkdir()
        self.dest=self.root/'site'
        self.fixture=ROOT/'tests/fixtures/hino-6-introduction.musicxml'
        self.muse=str(Path.home()/'bin/musescore')
    def cli(self,kind='musicxml',*extra):
        result=subprocess.run([sys.executable,str(ROOT/'criar_hinario.py'),'--origem',str(self.source),'--destino',str(self.dest),'--arquivos',kind,'--dominio','teste','--titulo','Teste','--repositorio','Exemplo/acervo','--somente-local',*extra],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        return json.loads((self.dest/'.importacao/resumo.json').read_text())
    def test_musicxml_resume_backup_carousel_and_github(self):
        source=self.source/'01.musicxml';shutil.copyfile(self.fixture,source)
        self.dest.mkdir();(self.dest/'pessoal.txt').write_text('não enviar')
        (self.dest/'assets').mkdir();(self.dest/'assets/privado.txt').write_text('não publicar')
        result=self.cli();self.assertEqual(len(result['preparados']),1)
        target=self.dest/'assets/music/hinos/acervo/01/score.musicxml'
        self.assertEqual(target.read_bytes(),source.read_bytes())
        home=(self.dest/'dist/index.html').read_text()
        self.assertLess(home.index('class="collection-carousel"'),home.index('class="list-search"'))
        self.assertIn('padrao.svg',home)
        player=(self.dest/'dist/partituras/hinos/acervo/01/index.html').read_text()
        self.assertNotIn('collection-carousel',player)
        self.assertIn('score.musicxml',player)
        self.assertNotIn('Baixar MuseScore',player)
        self.assertFalse((self.dest/'dist/pessoal.txt').exists())
        self.assertFalse((self.dest/'dist/assets/privado.txt').exists())
        self.assertEqual(len(self.cli()['ignorados']),1)
        source.write_bytes(source.read_bytes()+b'\n')
        self.cli('musicxml','--atualizar')
        backups=list((self.dest/'.importacao/backups').rglob('score.musicxml'));self.assertEqual(len(backups),1)
        self.assertEqual(backups[0].read_bytes(),self.fixture.read_bytes())
        for n in ('10','02'):
            shutil.copyfile(self.dest/'carrossel/padrao.svg',self.dest/f'carrossel/{n}.svg')
        spec=importlib.util.spec_from_file_location('carousel',self.dest/'carousel.py');carousel=importlib.util.module_from_spec(spec);spec.loader.exec_module(carousel)
        self.assertEqual(carousel.images(self.dest),['02.svg','10.svg'])
        subprocess.run([sys.executable,'build.py'],cwd=self.dest,check=True,capture_output=True)
        home=(self.dest/'dist/index.html').read_text();self.assertLess(home.index('02.svg'),home.index('10.svg'));self.assertNotIn('padrao.svg',home)
        # Simulate gh, keep real local Git. Never create a remote or push during tests.
        calls=[];real_run=subprocess.run
        def simulated(command,**kwargs):
            args=list(map(str,command));calls.append(args)
            if args[0]=='gh':
                code=1 if args[1:3]==['repo','view'] or (args[1]=='api' and '--method' not in args) else 0
                return subprocess.CompletedProcess(args,code,stdout='',stderr='')
            if args[:2]==['git','push']:return subprocess.CompletedProcess(args,0,stdout='',stderr='')
            return real_run(command,**kwargs)
        state=json.loads((self.dest/'.acervo-site.json').read_text())
        args=SimpleNamespace(titulo='Teste',autor='Teste',email='teste@example.com')
        with patch('subprocess.run',side_effect=simulated):app.configure_github(self.dest,state,args)
        tracked=subprocess.check_output(['git','ls-files'],cwd=self.dest,text=True)
        self.assertNotIn('pessoal.txt',tracked)
        self.assertTrue(any(c[:3]==['gh','repo','create'] and '--public' in c for c in calls))
        self.assertTrue(any('build_type=workflow' in c for c in calls))
        self.assertTrue(any('cname=teste.clavesol.com.br' in c for c in calls))
        self.assertFalse(any('workflow' in c for c in calls))
        subjects=subprocess.check_output(['git','log','--format=%s'],cwd=self.dest,text=True).splitlines()
        self.assertTrue(all('[skip ci]' in s for s in subjects))
    def test_mid_and_mscz(self):
        for kind in ('mid','mscz'):
            with self.subTest(kind=kind):
                self.dest=self.root/('site-'+kind)
                for p in self.source.iterdir():p.unlink()
                source=self.source/('teste.'+kind)
                subprocess.run([self.muse,'-o',str(source),str(self.fixture)],env=dict(os.environ,QT_QPA_PLATFORM='offscreen'),check=True,capture_output=True)
                result=self.cli(kind);self.assertEqual(len(result['preparados']),1)
                self.assertTrue((self.dest/'assets/music/hinos/acervo/teste/score.musicxml').is_file())
                self.assertFalse(any(p.suffix in ('.mscz','.mid','.midi') for p in self.dest.rglob('*')))
    def test_composer_folders_and_flat_files(self):
        import xml.etree.ElementTree as ET
        xml=ET.parse(self.fixture)
        for parent in xml.iter():
            for child in list(parent):
                if child.tag=='creator':parent.remove(child)
        for name in (' Bach ', 'Beethoven'):
            folder=self.source/name;folder.mkdir()
            xml.write(folder/'mesma-musica.musicxml',encoding='utf-8',xml_declaration=True)
        # Embedded composer overrides the folder only for the Author metadata.
        root=xml.getroot();identity=root.find('identification')
        if identity is None:identity=ET.SubElement(root,'identification')
        ET.SubElement(identity,'creator',type='composer').text='Ludwig van Beethoven'
        xml.write(self.source/'Beethoven/mesma-musica.musicxml',encoding='utf-8',xml_declaration=True)
        report=self.cli();self.assertEqual(len(report['preparados']),2)
        mapping=json.loads((self.dest/'compositores.json').read_text())
        self.assertEqual(mapping['groups'],{'bach':'Bach','beethoven':'Beethoven'})
        for slug,author in [('bach','Bach'),('beethoven','Ludwig van Beethoven')]:
            metadata=(self.dest/f'partituras/hinos/acervo/{slug}-mesma-musica.md').read_text()
            self.assertIn('Author: '+author,metadata)
            page=(self.dest/f'dist/compositores/{slug}/index.html').read_text()
            self.assertIn('class="list-search"',page)
            self.assertNotIn('collection-carousel',page)
            self.assertIn(f'acervo/{slug}-mesma-musica/',page)
            player=(self.dest/f'dist/partituras/hinos/acervo/{slug}-mesma-musica/index.html').read_text()
            self.assertIn(f'/compositores/{slug}/',player)
            self.assertNotIn('collection-carousel',player)
        home=(self.dest/'dist/index.html').read_text()
        self.assertIn('/compositores/bach/',home)
        self.assertIn('/compositores/beethoven/',home)
        self.assertLess(home.index('collection-carousel'),home.index('class="list-search"'))
        self.assertEqual(len(self.cli()['ignorados']),2)
        # Root-level files coexist under a separate card when there are composer folders.
        xml.write(self.source/'avulsa.musicxml',encoding='utf-8',xml_declaration=True)
        self.cli()
        self.assertTrue((self.dest/'dist/compositores/sem-compositor/index.html').exists())
        self.assertIn('Outras partituras',(self.dest/'dist/index.html').read_text())

    def test_upgrade_previous_template_and_preserve_manual_changes(self):
        self.dest.mkdir()
        template=(ROOT/'templates/hinario-site/build.py').read_text()
        old=template.replace('from composer_pages import build_composers\n','').replace('html=build_composers(ROOT,OUT,BASE,catalog,page) or entry.read_text()','html=entry.read_text()')
        (self.dest/'build.py').write_text(old)
        state={'domain':'teste.clavesol.com.br','repository':'Exemplo/acervo','managed':['build.py','.acervo-site.json']}
        app.upgrade_composers(self.dest,state)
        self.assertEqual(state['schema'],2)
        self.assertTrue((self.dest/'composer_pages.py').exists())
        saved=list((self.dest/'.importacao/backups').rglob('build.py'))
        self.assertEqual(saved[0].read_text(),old)
        state['schema']=1
        (self.dest/'build.py').write_text('# alteração manual')
        with self.assertRaises(ValueError):app.upgrade_composers(self.dest,state)
        self.assertEqual((self.dest/'build.py').read_text(),'# alteração manual')

    def test_existing_conflict_is_not_overwritten(self):
        self.dest.mkdir();(self.dest/'build.py').write_text('preservar')
        with self.assertRaises(ValueError):app.initialize(self.dest,'teste.clavesol.com.br','Teste','Texto','Exemplo/acervo')
        self.assertEqual((self.dest/'build.py').read_text(),'preservar')
        self.assertFalse((self.dest/'assets').exists())

if __name__=='__main__':unittest.main()
