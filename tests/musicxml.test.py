from pathlib import Path
from tempfile import TemporaryDirectory
import sys, unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from musicxml_audio import parse_musicxml

def note(step='C', duration=1, extra=''):
    return f'<note>{extra}<pitch><step>{step}</step><octave>4</octave></pitch><duration>{duration}</duration></note>'

class MusicXMLTests(unittest.TestCase):
    def parse(self, body, tempo=None, **kwargs):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'score.musicxml'
            path.write_text(f'<score-partwise><part id="P1">{body}</part></score-partwise>')
            return parse_musicxml(path,tempo,**kwargs)

    def test_dotted_tempo_transposition_chords_rest_ties_and_backup(self):
        attributes='<attributes><divisions>2</divisions><transpose><chromatic>-2</chromatic></transpose></attributes>'
        tempo='<direction><direction-type><metronome><beat-unit>quarter</beat-unit><beat-unit-dot/><per-minute>30</per-minute></metronome></direction-type></direction>'
        first=attributes+tempo+note('C',2,'<tie type="start"/>')+note('E',2,'<chord/>')+'<note><rest/><duration>2</duration></note>'
        second=note('C',2,'<tie type="stop"/>')+'<backup><duration>2</duration></backup>'+note('G',4)
        seq=self.parse(f'<measure>{first}</measure><measure>{second}</measure>')
        self.assertEqual(seq['quarterBpm'],45)
        self.assertAlmostEqual(seq['duration'],16/3,places=5)
        self.assertEqual([n['midi'] for n in seq['notes']],[58,62,65])
        self.assertAlmostEqual(seq['notes'][0]['duration'],4)
        self.assertAlmostEqual(seq['notes'][2]['time'],8/3,places=5)

    def test_tempo_change_forward_and_override(self):
        body='<measure><sound tempo="60"/>'+note()+'<sound tempo="120"/>'+note('D')+'<forward><duration>2</duration></forward></measure>'
        seq=self.parse(body)
        self.assertEqual(seq['duration'],2.5)
        self.assertEqual(seq['notes'][1]['duration'],.5)
        self.assertEqual(self.parse(body,60)['duration'],4)

    def test_cursor_includes_rests_chords_tie_continuations_and_tempo_changes(self):
        body='<measure><sound tempo="60"/>'+note('C',1,'<tie type="start"/>')+note('E',1,'<chord/>')+'<note><rest/><duration>1</duration></note></measure>'
        body+='<measure><sound tempo="120"/>'+note('C',1,'<tie type="stop"/>')+note('D',1)+'</measure>'
        seq=self.parse(body,include_cursor=True)
        self.assertEqual(seq['cursorEvents'],[dict(time=0,measure=1),dict(time=1,measure=1),dict(time=2,measure=2),dict(time=2.5,measure=2)])
        self.assertEqual(seq['measureStarts'],[dict(time=0,measure=1),dict(time=2,measure=2)])

    def test_explicit_errors(self):
        with self.assertRaisesRegex(ValueError,'andamento ausente'):
            self.parse('<measure>'+note()+'</measure>')
        with self.assertRaisesRegex(ValueError,'recorded'):
            self.parse('<measure>'+note()+'<barline><repeat direction="backward"/></barline></measure>',60)

    def test_msa109_no_cumulative_drift_after_final_fermata(self):
        import json
        folder=Path(__file__).resolve().parents[1]/'assets/music/msa/msa-109'
        seq=parse_musicxml(folder/'score.musicxml',include_cursor=True)
        timing=json.loads((folder/'timing.json').read_text())
        self.assertEqual(len(seq['cursorEvents']),250)
        self.assertEqual(len(timing['events']),250)
        self.assertEqual(len(seq['measureStarts']),41)
        for event, expected in zip(timing['events'],seq['cursorEvents']):
            self.assertEqual(event['measure'],expected['measure'])
            self.assertAlmostEqual(event['time'],expected['time'],places=6)
        self.assertAlmostEqual(timing['events'][84]['time'],57.777778,places=6)
        self.assertAlmostEqual(timing['events'][-1]['time'],180,places=6)
        self.assertEqual(timing['duration'],seq['duration'])

    def test_actual_lesson_matches_cursor(self):
        import json
        folder=Path(__file__).resolve().parents[1]/'assets/music/107-msa-bb'
        seq=parse_musicxml(folder/'score.musicxml')
        self.assertEqual(seq['quarterBpm'],45)
        self.assertEqual(seq['duration'],104)
        self.assertEqual(seq['duration'],json.loads((folder/'timing.json').read_text())['duration'])

if __name__=='__main__':unittest.main()
