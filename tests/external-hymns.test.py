"""Verify the migration contract in the built site, including old deep links."""
from pathlib import Path
from html.parser import HTMLParser
import json
from urllib.parse import urlsplit
root=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
 def __init__(self,text):
  super().__init__(); self.links=[]; self.feed(text)
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='a':self.links.append(attrs)
page=(root/'dist/partituras/hinos/index.html').read_text()
links=Links(page).links
config=json.loads((root/'external_hymns.json').read_text())
for key,value in config.items():
 assert any(a.get('class')=='text-link' and a.get('href')==value['url'] for a in links)
 assert any(urlsplit(a.get('href','')).path==f'/partituras/{key}/' for a in links)
 for slug in value['scores']:
  redirect=(root/f'dist/partituras/{key}/{slug}/index.html').read_text()
  assert f'content="0;url={value["url"]}partituras/{key}/{slug}/"' in redirect
  assert not (root/f'dist/assets/music/{key}/{slug}').exists()
from collections import Counter
for count, occurrences in Counter(len(c['scores']) for c in config.values()).items():
 assert page.count(f'{count} partituras') == occurrences
assert 'Outros' in page
assert (root/'dist/partituras/hinos/outros/144-a-vida-eterna/index.html').is_file()
print('External cards, counts, all deep-link redirects and local Outros: OK')
