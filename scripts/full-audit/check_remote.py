from pathlib import Path
import subprocess,os,json,hashlib
OUT=Path('outputs/repository-audit');env={**os.environ,'GH_CONFIG_DIR':str(Path('work/gh-config').resolve())}
repos=[]
for repo in ('Image','animation'):
 base=Path('work')/repo;head=subprocess.check_output(['git','-C',str(base),'rev-parse','HEAD'],text=True).strip()
 remote=json.loads(subprocess.check_output(['gh','api',f'repos/atiffhussainkhan/{repo}/commits/HEAD'],env=env))['sha'];assert remote==head
 entries=subprocess.check_output(['git','-C',str(base),'ls-tree','-r','-z','HEAD']).split(b'\0');failed=[];n=0;total=0
 for entry in filter(None,entries):
  info,name=entry.split(b'\t',1);mode,kind,expected=info.split();p=base/name.decode();data=p.read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if actual!=expected.decode():failed.append(name.decode())
  n+=1;total+=len(data)
 assert not failed,failed;repos.append({'repository':f'atiffhussainkhan/{repo}','commit':head,'every_tracked_blob_matches_remote_commit':True,'tracked_files':n,'bytes':total})
r=json.load(open('work/image-release-inventory.json'));history=next(x for x in r if x['tag_name'].startswith('workplace'));verified=[]
for a in history['assets']:
 if a['name'].endswith(('.rar','.tar')):p=Path('/Users/mac/Documents/images from internet')/a['name']
 else:p=Path('work/full-audit/downloads')/history['tag_name']/a['name']
 if not p.exists():continue
 with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 assert p.stat().st_size==a['size'] and a['digest']=='sha256:'+digest,p
 verified.append({'release':history['tag_name'],'file':a['name'],'bytes':a['size'],'sha256':digest})
report={'repositories':repos,'historical_release_assets_verified':verified,'cleaned_release':json.loads(Path('outputs/game-art-library/github-upload-verification.json').read_text()),'catalog_only_missing_packs':json.loads(Path('work/Image/catalog/storage_status.json').read_text()).get('unresolved_catalogued',[])}
(OUT/'remote-completeness-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({'git_files_verified':sum(x['tracked_files']for x in repos),'historical_assets_verified':len(verified)}),flush=True)
