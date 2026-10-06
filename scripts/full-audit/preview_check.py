from pathlib import Path
import json,gzip,collections
from PIL import Image
base=Path('outputs/game-art-library');groups=collections.defaultdict(dict)
with gzip.open(base/'assets.json.gz','rt') as f:rows=json.load(f)
for r in rows:groups[r['preview']['atlas']][(r['preview']['x'],r['preview']['y'])]=r
uniform=[];low=[];checked=0
for name,tiles in groups.items():
 with Image.open(base/name) as im:
  im.load()
  for (x,y),r in tiles.items():
   p=r['preview'];ex=im.crop((x,y,x+p['width'],y+p['height'])).convert('RGB').getextrema();variation=max(hi-lo for lo,hi in ex);checked+=1
   info={'asset_id':r['asset_id'],'sha256':r['sha256'],'original_path':r['original_path'],'normalized_file':r['normalized_file'],'atlas':name,'preview':p,'range':variation}
   if variation==0:uniform.append(info)
   elif variation<=3:low.append(info)
report={'occupied_tiles_checked':checked,'uniform_tiles':uniform,'low_contrast_tiles':low}
Path('outputs/repository-audit/preview-tile-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({'tiles_checked':checked,'uniform':len(uniform),'very_low_contrast':len(low)}),flush=True)
