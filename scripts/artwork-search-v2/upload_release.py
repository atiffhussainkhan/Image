"""Upload finished packs to a draft release, check GitHub digests, then publish."""
from pathlib import Path
import os,json,subprocess,hashlib,argparse
parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
DEST=Path('outputs/game-art-library');REPO='atiffhussainkhan/Image';TAG='game-art-search-v2-2026-10-05'
env={**os.environ,'GH_CONFIG_DIR':str(Path('work/gh-config').resolve())}
def gh(*args,capture=False):return subprocess.run(['gh',*args],check=True,env=env,capture_output=capture,text=True)
def get_release():
 releases=json.loads(gh('api',f'repos/{REPO}/releases',capture=True).stdout)
 return next((r for r in releases if r['tag_name']==TAG),None)
qa=json.loads((DEST/'quality-report.json').read_text());verification=json.loads((DEST/'verification-report.json').read_text());assert verification['passed']
notes=f"""Cleaned, searchable artwork from the four user-supplied archives.

- {qa['active_image_entries']:,} readable image entries with validated previews and engine PNG/JPEG paths.
- {qa['excluded_entries']:,} empty, unreadable, unconvertible or non-image entries excluded from the active library and cleaned packs. See quality-report.json for every exclusion.
- Gallery, JSON/JSONL, CSV, SQLite keyword search and offline CLIP visual search.
- ZIP membership/CRC, image hashes, preview atlas decoding, SQLite integrity and active image vectors verified.

Download game-art-gallery.zip to browse pictures. Use game-art-search-data.zip for engine/editor automation and game-art-semantic-search.zip for natural-language search. Each search result gives the exact cleaned ZIP part and engine file path.

Original archives remain in the historical workplace-art-unverified-2026-10-05 release as a source backup. Use this cleaned release for active searches and imports. Third-party artwork licences remain unverified; visual labels are model suggestions. Human preview review covered a stratified sample.
"""
(DEST/'RELEASE_NOTES.md').write_text(notes)
existing=get_release()
if not existing:gh('release','create',TAG,'--repo',REPO,'--draft','--latest=false','--title','Cleaned game artwork — search and engine files','--notes-file',str(DEST/'RELEASE_NOTES.md'))
else:assert existing['draft'],'Release already public; review before modifying.'
gh('release','edit',TAG,'--repo',REPO,'--title','Cleaned game artwork — search and engine files','--notes-file',str(DEST/'RELEASE_NOTES.md'))
files=sorted((DEST/'bundles').glob('*.zip'))+[DEST/n for n in ['README.md','quality-report.json','removed-entries.csv','bundle-manifest.json','search-bundle-manifest.json','verification-report.json','model-provenance.json']]
current=get_release();present={a['name']:a for a in current['assets']};pending=[]
for p in files:
 with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 a=present.get(p.name,{})
 if a.get('size')!=p.stat().st_size or a.get('digest')!='sha256:'+digest:pending.append(p)
if pending:gh('release','upload',TAG,'--repo',REPO,'--clobber',*[str(p) for p in pending])
release=json.loads(gh('api',f'repos/{REPO}/releases/{current['id']}',capture=True).stdout);remote={a['name']:a for a in release['assets']};verified=[]
for p in files:
 with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 a=remote[p.name];assert a['size']==p.stat().st_size and a.get('digest')=='sha256:'+digest,(p.name,a.get('digest'),digest)
 verified.append({'name':p.name,'bytes':p.stat().st_size,'sha256':digest,'download_url':a['browser_download_url']})
(DEST/'github-upload-verification.json').write_text(json.dumps({'release_tag':TAG,'assets':verified},indent=2))
if not args.prepare_only:gh('release','edit',TAG,'--repo',REPO,'--target','main','--draft=false','--latest=false')
print(('Draft verified: ' if args.prepare_only else 'Published: ')+TAG+'; all '+str(len(files))+' uploaded digests verified.',flush=True)
