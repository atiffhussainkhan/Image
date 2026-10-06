import json,hashlib
from pathlib import Path
from PIL import Image
base=Path('work/animation/packs/opengameart-knight-princess-dragon');m=json.loads((base/'manifest.json').read_text());results=[]
for char,anims in m['characters'].items():
 for anim,a in anims.items():
  p=base/char/a['file'];r={'character':char,'animation':anim,'path':str(p),'frames':a['frames'],'issues':[]}
  with Image.open(p) as im:
   im.load();assert im.size==(a['cols']*a['frameW'],a['rows']*a['frameH']),(p,im.size)
   assert p.stat().st_size==a['bytes'];assert a['fps']>0 and a['frames']<=a['cols']*a['rows']
   for n in range(a['frames']):
    x=n%a['cols']*a['frameW'];y=n//a['cols']*a['frameH'];cell=im.crop((x,y,x+a['frameW'],y+a['frameH'])).convert('RGBA')
    if not cell.getchannel('A').getbbox():r['issues'].append({'frame':n,'problem':'Empty declared frame'})
  r['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();results.append(r)
report={'sheets':len(results),'declared_frames':sum(r['frames']for r in results),'passed':all(not r['issues']for r in results),'results':results,'blank_unused_grid_cells':'Expected padding; excluded from declared animation frames'}
Path('outputs/repository-audit/animation-frame-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k]for k in ('sheets','declared_frames','passed')}))
