from pathlib import Path
import importlib.util
import subprocess
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('sync',Path(__file__).resolve().parents[1]/'scripts/sincronizar_player.py')
sync=importlib.util.module_from_spec(spec);spec.loader.exec_module(sync)
class SyncTest(unittest.TestCase):
 def test_preflight_and_idempotence(self):
  with tempfile.TemporaryDirectory() as tmp:
   source=Path(tmp)/'source'; target=Path(tmp)/'target'
   source.mkdir();target.mkdir()
   subprocess.run(['git','init','-q',str(target)],check=True)
   for name in sync.SHARED:
    p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('new')
   self.assertEqual(len(sync.plan(source,[target])),len(sync.SHARED))
   # A single dirty destination blocks the whole plan before any copy.
   p=target/sync.SHARED[-1];p.parent.mkdir(parents=True,exist_ok=True);p.write_text('local edit')
   with self.assertRaisesRegex(ValueError,'Alteração local'):
    sync.plan(source,[target])
   self.assertFalse((target/sync.SHARED[0]).exists())
   for name in sync.SHARED:
    p=target/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((source/name).read_bytes())
   self.assertEqual(sync.plan(source,[target]),[])
if __name__=='__main__':unittest.main()
