"""Create a downloadable source archive without runtime data or host credentials."""
from pathlib import Path
import zipfile,json,re
root=Path(__file__).resolve().parents[1];dist=root/'dist';output=dist/'english-footpath-source.zip'
allowed=[]
for folder in ['dist','server','tests','scripts','qa','.github']:
 for p in (root/folder).rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or 'data' in p.relative_to(root).parts or p==output:continue
  if p.suffix in ['.sqlite3','.pyc'] or p.name.startswith('.env'):continue
  allowed.append(p)
for name in ['README.md','CURRICULUM.md','.gitignore']:allowed.append(root/name)
for p in dist.iterdir():
 if p.is_file() and p.suffix=='.js':
  assert 'art_v2_' not in p.read_text(), 'Credential-like value in public script'
manifest=json.loads((dist/'manifest.webmanifest').read_text())
for icon in manifest['icons']:assert (dist/icon['src']).is_file()
html=(dist/'index.html').read_text()
for src in re.findall(r'<script src="([^"]+)"',html):assert (dist/src).is_file(),src
sw=(dist/'sw.js').read_text();names=re.search(r'const FILES=\[(.*?)\]',sw).group(1)
for name in re.findall(r"'([^']+)'",names):assert (dist/name).exists(),name
assert '/api/' in sw,'Account requests must bypass offline caching'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(allowed):z.write(p,p.relative_to(root))
with zipfile.ZipFile(output) as z:
 assert z.testzip() is None
 assert 'server/server.py' in z.namelist()
 assert not any('/data/' in n or '.sqlite3' in n for n in z.namelist())
print(f'Validated {len(allowed)} source files and package: {output}')
