"""Keep already compatible JPEGs when byte-for-byte originals decode identically."""
from pathlib import Path
from PIL import Image,ImageChops
import json,shutil,hashlib
OUT=Path('work/processed');rows=json.loads((OUT/'source-rows.json').read_text());seen=set();kept=0;saved=0
for r in rows:
 sha=r['sha256']
 if sha in seen or r['format'] not in {'jpg','jpeg'}:continue
 seen.add(sha);p=OUT/'status'/(sha+'.json');s=json.loads(p.read_text())
 if not s.get('active_library'):continue
 src=Path(r['source_path']);png=OUT/'images'/(sha+'.png')
 with Image.open(src) as a,Image.open(png) as b:
  a.load();b.load()
  if a.mode not in {'RGB','L'} or a.info.get('icc_profile') or a.getexif().get(274,1)!=1:continue
  if a.size!=b.size or ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox():continue
 dest=OUT/'images'/(sha+'.jpg');shutil.copyfile(src,dest)
 with Image.open(dest) as check:check.load()
 saved+=png.stat().st_size-dest.stat().st_size;png.unlink()
 s.update(normalized_file='images/'+sha+'.jpg',normalized_bytes=dest.stat().st_size,normalized_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),conversion_method='Original game-compatible JPEG retained; decoded pixels verified identical to normalized PNG')
 p.write_text(json.dumps(s));kept+=1
print(json.dumps({'compatible_jpegs_retained':kept,'bytes_saved':saved}),flush=True)
