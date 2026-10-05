"""Create cleaned, engine-readable ZIP parts with exact membership and checksums."""
from pathlib import Path
import json,zipfile,hashlib,collections
OUT=Path('work/processed');DEST=Path('outputs/game-art-library');BUNDLES=DEST/'bundles';BUNDLES.mkdir(parents=True,exist_ok=True)
TAG='game-art-search-v2-2026-10-05';BASE='https://github.com/atiffhussainkhan/Image/releases/download/'+TAG+'/'
rows=json.loads((OUT/'source-rows.json').read_text());owners={}
for r in rows:owners.setdefault(r['sha256'],r['pack'])
groups=collections.defaultdict(list)
for p in sorted((OUT/'status').glob('*.json')):
 s=json.loads(p.read_text())
 if s.get('active_library'):groups[owners[p.stem]].append(s)
manifest=[];mapping={}
for pack,entries in sorted(groups.items()):
 parts=[];part=[];size=0
 for s in entries:
  files=[s['normalized_file']]+s.get('animation_frames',[]);amount=sum((OUT/name).stat().st_size for name in files)
  if part and size+amount>900_000_000:parts.append(part);part=[];size=0
  part.append((s,files));size+=amount
 if part:parts.append(part)
 for i,part in enumerate(parts,1):
  name=pack+'-cleaned-'+str(i).zfill(2)+'.zip';path=BUNDLES/name;count=0
  with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
   for s,files in part:
    for f in files:z.write(OUT/f,f);count+=1
    mapping[s['sha256']]={'name':name,'download_url':BASE+name,'file':s['normalized_file']}
  with zipfile.ZipFile(path) as z:
   assert z.testzip() is None
   assert len(z.namelist())==count
  with path.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
  manifest.append({'name':name,'bytes':path.stat().st_size,'sha256':digest,'image_sources':len(part),'files':count,'download_url':BASE+name})
  print(json.dumps(manifest[-1]),flush=True)
(OUT/'bundle-map.json').write_text(json.dumps(mapping,separators=(',',':')))
(DEST/'bundle-manifest.json').write_text(json.dumps({'release_tag':TAG,'bundles':manifest},indent=2))
