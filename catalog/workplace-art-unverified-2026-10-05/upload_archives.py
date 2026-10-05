#!/usr/bin/env python3
"""Upload original workplace archives without claiming a licence for them."""
import argparse,base64,hashlib,json,subprocess,tempfile
from pathlib import Path
REPO='atiffhussainkhan/Image';TAG='workplace-art-unverified-2026-10-05';DEST='catalog/'+TAG+'/archive-manifest.json'
def gh(*args):
 p=subprocess.run(['gh',*args],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr.strip())
 return p.stdout
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--audit',type=Path,default=Path(__file__).resolve().parent);a=p.parse_args()
gh('api','user')
manifest=json.loads((a.audit/'archive-manifest.json').read_text());files=[]
for item in manifest:
 f=a.source/item['filename'];h=hashlib.sha256()
 with f.open('rb') as s:
  for b in iter(lambda:s.read(1048576),b''):h.update(b)
 if h.hexdigest()!=item['sha256']:raise RuntimeError('Checksum mismatch: '+f.name)
 files.append(f)
files.extend(a.audit/n for n in ['assets.json.gz','assets.csv','README.md'])
for f in files:
 if not f.is_file():raise RuntimeError('Missing upload file: '+str(f))
try:release=json.loads(gh('api','repos/'+REPO+'/releases/tags/'+TAG))
except RuntimeError as e:
 if '404' not in str(e):raise
 gh('release','create',TAG,'--repo',REPO,'--draft','--title','Workplace artwork — unverified licences — 2026-10-05','--notes-file',str(a.audit/'README.md'))
for f in files:
 print('Uploading',f.name,flush=True);gh('release','upload',TAG,str(f),'--repo',REPO,'--clobber')
release=next(x for x in json.loads(gh('api','repos/'+REPO+'/releases')) if x['tag_name']==TAG);remote={x['name']:x for x in release['assets']}
for f in files:
 if f.name not in remote or remote[f.name]['size']!=f.stat().st_size:raise RuntimeError('Remote size verification failed: '+f.name)
for item in manifest:
 item['storage_status']='stored-unverified-release';item['download_url']=remote[item['filename']]['browser_download_url']
gh('release','edit',TAG,'--repo',REPO,'--draft=false')
old=json.loads(gh('api','repos/'+REPO+'/contents/'+DEST));content=json.dumps(manifest,indent=2)
with tempfile.TemporaryDirectory() as d:
 body=Path(d)/'update.json';body.write_text(json.dumps({'message':'Record uploaded unverified workplace artwork archives','sha':old['sha'],'content':base64.b64encode(content.encode()).decode()}));gh('api','repos/'+REPO+'/contents/'+DEST,'--method','PUT','--input',str(body))
(a.audit/'archive-manifest.json').write_text(content)
print('Uploaded and size-verified:',release['html_url'])
