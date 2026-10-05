"""Enlarge small artwork for legible previews without modifying engine files."""
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import gzip,json,time
from palette import analyse
OUT=Path('work/processed')
with gzip.open('outputs/game-art-library/assets.json.gz','rt') as f:rows=json.load(f)
unique={r['sha256']:r for r in rows};small=[r for r in unique.values() if max(r['normalized_dimensions'])<224]
def repair(r):
 p=OUT/'status'/(r['sha256']+'.json');s=json.loads(p.read_text())
 with Image.open(OUT/s['normalized_file']) as source:
  im=source.convert('RGBA');factor=224/max(im.size);size=(max(1,round(im.width*factor)),max(1,round(im.height*factor)))
  pixel=max(im.size)<=64 and r['format'] not in {'wmf','eps','jpg','jpeg','tif','tiff'}
  im=im.resize(size,Image.Resampling.NEAREST if pixel else Image.Resampling.LANCZOS)
  colour=(195,205,220,255) if s.get('white_alpha_artwork') else (255,255,255,255)
  canvas=Image.new('RGBA',(224,224),colour);canvas.alpha_composite(im,((224-im.width)//2,(224-im.height)//2));canvas.convert('RGB').save(OUT/'thumbs'/(r['sha256']+'.webp'),'WEBP',quality=90)
 with Image.open(OUT/'thumbs'/(r['sha256']+'.webp')) as check:check.load();assert check.size==(224,224)
 s.update(preview_upscaled=True,preview_art_dimensions=list(size),preview_resize_method='nearest pixels' if pixel else 'Lanczos',requires_reanalysis=True);p.write_text(json.dumps(s));analyse(p)
started=time.time()
with ThreadPoolExecutor(max_workers=8) as pool:
 for start in range(0,len(small),1000):
  list(pool.map(repair,small[start:start+1000]));print(json.dumps({'small_previews_enlarged':min(start+1000,len(small)),'total':len(small),'elapsed_seconds':round(time.time()-started)}),flush=True)
(OUT/'small-preview-repair.json').write_text(json.dumps({'enlarged_previews':len(small),'master_images_unchanged':True}))
