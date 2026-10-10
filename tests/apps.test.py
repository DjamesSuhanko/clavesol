"""Isolated CLI checks: no GitHub access or modification of the real catalog."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]


class AppsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('criar_app.py', 'apps_catalog.py', 'criar_site_app.py'):
            shutil.copy(ROOT / name, self.root / name)
        (self.root / 'assets').mkdir()
        shutil.copytree(ROOT / 'templates/app-site', self.root / 'templates/app-site')
        self.cover = self.root / 'cover.webp'
        shutil.copy(ROOT / 'assets/logo-clavesol.webp', self.cover)

    def run_cli(self, script, *args, ok=True):
        result = subprocess.run([sys.executable, str(self.root / script), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def test_card_creation_duplicate_and_update(self):
        args = ['--titulo', 'Aplicativo Novo', '--texto', 'Teste & música', '--imagem', self.cover, '--link', 'https://example.com/']
        self.run_cli('criar_app.py', *args)
        catalog = self.root / 'apps.json'
        original = catalog.read_bytes()
        self.run_cli('criar_app.py', *args, ok=False)
        self.assertEqual(catalog.read_bytes(), original)
        self.run_cli('criar_app.py', *args, '--atualizar')
        apps = json.loads(catalog.read_text())
        self.assertEqual(len(apps), 1)
        self.assertTrue((self.root / 'assets' / apps[0]['image']).is_file())
        self.run_cli('criar_app.py', *args[:-1], 'javascript:alert(1)', '--atualizar', ok=False)
        self.assertEqual(catalog.read_bytes(), original)

    def test_site_generation_preserves_policy_and_links(self):
        policy = self.root / 'policy.html'
        fragment = '<h1>Privacidade</h1><p>Texto fornecido &amp; preservado.</p>'
        policy.write_text('<html><body><main>' + fragment + '</main></body></html>')
        site = self.root / 'new-site'
        args = ['--repositorio', 'example/new-app', '--diretorio', site, '--dominio', 'app.example.com', '--titulo', 'App <&>', '--texto', 'Estudo & prática', '--email', 'dev@example.com', '--politica-html', policy]
        self.run_cli('criar_site_app.py', *args)
        self.assertEqual((site / 'content/privacy.html').read_text(), fragment)
        self.assertEqual((site / 'CNAME').read_text(), 'app.example.com\n')
        self.assertIn('App &lt;&amp;&gt;', (site / 'dist/index.html').read_text())
        self.assertFalse((site / 'dist/site.json').exists())
        dist = site / 'dist'
        testcase = self
        class Links(HTMLParser):
            def handle_starttag(self, tag, attrs):
                for key, value in attrs:
                    if key not in ('href', 'src') or not value or value.startswith('#') or urlsplit(value).scheme:
                        continue
                    target = dist / value.lstrip('/')
                    if target.is_dir():
                        target = target / 'index.html'
                    testcase.assertTrue(target.is_file(), value)
        for path in dist.rglob('*.html'):
            Links().feed(path.read_text())
        self.run_cli('criar_site_app.py', *args, ok=False)
        self.assertEqual((site / 'content/privacy.html').read_text(), fragment)

if __name__ == '__main__':
    unittest.main()
