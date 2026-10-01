import base64
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from score_catalog import load_catalog, validate_timing
from music_pages import build_music
from scripts.score_timing import convert_media

SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 200"></svg>'


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, path, text):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def score(self, name='licao-27', extra='', files=None):
        self.write(f'partituras/metodos/pecci/{name}.md', f'Title: {name}\n{extra}\n\n## Estudo\nTexto **musical**.')
        for filename, text in (files if files is not None else {'score-1.svg': SVG}).items():
            self.write(f'assets/music/metodos/pecci/{name}/{filename}', text)

    def test_categories_collections_numeric_order_and_both_bases(self):
        self.write('partituras/metodos/_index.md', 'Title: Métodos\n')
        self.write('partituras/metodos/pecci/_index.md', 'Title: Método Pecci\n')
        self.score('licao-10', 'Lesson: 10')
        self.score('licao-2', 'Lesson: 2')
        catalog = load_catalog(self.root)
        self.assertEqual([s.lesson for s in catalog.scores], [2, 10])
        for base in ['', '/clavesol']:
            out = self.root / ('out' if not base else 'subpath')
            build_music(out, base, lambda title, body: body, catalog)
            index = (out / 'partituras/metodos/index.html').read_text()
            lesson = (out / 'partituras/metodos/pecci/licao-2/index.html').read_text()
            self.assertIn(f'href="{base}/partituras/metodos/pecci/"', index)
            self.assertIn('<strong>musical</strong>', lesson)
            self.assertIn(f'src="{base}/assets/music/metodos/pecci/licao-2/score-1.svg"', lesson)
            self.assertNotIn('<audio', lesson)

    def test_draft_needs_no_assets(self):
        self.score(extra='Draft: true', files={})
        self.assertEqual(load_catalog(self.root).scores, [])

    def test_download_only_and_audio_without_cursor(self):
        self.score(extra='Playback: recorded', files={'score.musicxml': '<score-partwise/>', 'score.mp3': 'audio fixture'})
        catalog = load_catalog(self.root)
        out = self.root / 'out'
        build_music(out, '', lambda title, body: body, catalog)
        body = (out / 'partituras/metodos/pecci/licao-27/index.html').read_text()
        self.assertIn('Baixar MusicXML', body)
        self.assertIn('<audio', body)
        self.assertNotIn('score-zoom', body)
        self.assertNotIn('data-timing', body)

    def test_generated_player_without_recording_and_duration_validation(self):
        xml = '<score-partwise><part><measure><sound tempo="60"/><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note></measure></part></score-partwise>'
        self.score(files={'score.musicxml': xml, 'score-1.svg': SVG})
        catalog = load_catalog(self.root)
        score = catalog.scores[0]
        self.assertEqual(score.playback, 'generated')
        self.assertEqual(score.audio, [])
        self.assertEqual(score.sequence['duration'], 1)
        out = self.root / 'out'
        build_music(out, '/clavesol', lambda title, body: body, catalog)
        body = (out / 'partituras/metodos/pecci/licao-27/index.html').read_text()
        self.assertIn('data-sequence="/clavesol/assets/', body)
        self.assertIn('Mudo para solfejo', body)
        self.assertNotIn('<audio', body)
        timing = dict(duration=1.4, events=[dict(time=0, page=1, measure=1, x=1, y=1, width=2, height=2)])
        self.write('assets/music/metodos/pecci/licao-27/timing.json', json.dumps(timing))
        self.assertTrue(load_catalog(self.root).scores[0].timing)
        timing['duration'] = 2
        self.write('assets/music/metodos/pecci/licao-27/timing.json', json.dumps(timing))
        with self.assertRaisesRegex(ValueError, 'durações diferentes'):
            load_catalog(self.root)

    def test_multi_page_cursor(self):
        event = dict(time=0, page=1, measure=1, x=10, y=10, width=3, height=5)
        data = dict(duration=10, events=[event, dict(event, time=5, page=2, measure=2)])
        self.score(files={'score-1.svg': SVG, 'score-2.svg': SVG,
                          'score.ogg': 'audio fixture', 'timing.json': json.dumps(data)})
        catalog = load_catalog(self.root)
        self.assertEqual(catalog.scores[0].measures, 2)
        out = self.root / 'out'
        build_music(out, '', lambda title, body: body, catalog)
        body = (out / 'partituras/metodos/pecci/licao-27/index.html').read_text()
        self.assertIn('data-page="2"', body)
        self.assertEqual(body.count('id="score-cursor"'), 1)
        self.assertIn('data-measures="2"', body)
        data['events'][1].pop('page')
        with self.assertRaisesRegex(ValueError, 'page'):
            validate_timing(data, 2)

    def test_missing_assets_and_page_gaps_fail(self):
        self.score(files={})
        with self.assertRaisesRegex(ValueError, 'licao-27.md.*Pasta'):
            load_catalog(self.root)
        self.score(files={'score-2.svg': SVG})
        with self.assertRaisesRegex(ValueError, 'consecutivamente'):
            load_catalog(self.root)

    def test_required_audio_and_cursor_fail(self):
        self.score(extra='Audio: true')
        with self.assertRaisesRegex(ValueError, 'Audio'):
            load_catalog(self.root)
        self.score(extra='Cursor: true')
        with self.assertRaisesRegex(ValueError, 'Cursor'):
            load_catalog(self.root)

    def test_reject_asset_escape_and_group_collision(self):
        self.score(extra='Assets: ../outside')
        with self.assertRaisesRegex(ValueError, 'Caminho inválido'):
            load_catalog(self.root)
        self.score()
        self.write('partituras/metodos/pecci.md', 'Title: Outra lição\nAssets: music/metodos/pecci/licao-27\n')
        with self.assertRaisesRegex(ValueError, 'endereço|coincide'):
            load_catalog(self.root)

    def test_original_msa_and_legacy(self):
        catalog = load_catalog(ROOT)
        score = next(s for s in catalog.scores if s.key == 'msa/107-msa-bb')
        self.assertEqual(score.measures, 13)
        self.assertTrue(score.timing)
        out = self.root / 'out'
        build_music(out, '', lambda title, body: body, catalog)
        self.assertEqual((out / 'partituras/msa/107-msa-bb/index.html').read_text(),
                         (out / 'musica/msa/107-msa-bb/index.html').read_text())

    def test_exporter_multi_page_and_repeat_measure_numbers(self):
        def encode(s):
            return base64.b64encode(s.encode()).decode()
        positions = '<score><elements><element id="0" page="0" x="120" y="240" sx="60" sy="120"/><element id="1" page="1" x="240" y="480" sx="60" sy="120"/></elements><events><event elid="0" position="0"/><event elid="1" position="5000"/><event elid="0" position="10000"/></events></score>'
        media = dict(svgs=[encode(SVG), encode(SVG)], sposXML=encode(positions),
                     mposXML=encode(positions), metadata={'duration': 15})
        svgs, timing = convert_media(media)
        self.assertEqual(len(svgs), 2)
        self.assertEqual([e['page'] for e in timing['events']], [1, 2, 1])
        self.assertEqual([e['measure'] for e in timing['events']], [1, 2, 1])
        self.assertEqual(timing['events'][0]['x'], 10)
        self.assertEqual(timing['events'][1]['y'], 20)


if __name__ == '__main__':
    unittest.main()
