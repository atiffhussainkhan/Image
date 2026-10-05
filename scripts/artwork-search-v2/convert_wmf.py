"""Batch Draw import prevents treating unsupported binary drawings as text."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,os,time
OUT=Path('work/processed');rows=json.loads((OUT/'source-rows.json').read_text());u={}
for r in rows:
 if r['format']=='wmf':u.setdefault(r['sha256'],r)
items=[]
for sha,r in u.items():
 target=(OUT/'wmf-input'/(sha+'.wmf')).resolve()
 if not target.exists():target.symlink_to(Path(r['source_path']).resolve())
 if not (OUT/'wmf-render'/(sha+'.png')).exists():items.append(target)
groups=[items[i:i+160] for i in range(0,len(items),160)]
def batch(item):
 i,files=item;profile=(Path('work/tooling')/('lo-'+str(i%4))).resolve()
 # Matching worker profile groups are executed sequentially below.
 cmd=['soffice','-env:UserInstallation='+profile.as_uri(),'--headless','--convert-to','png:draw_png_Export:{"PixelWidth":{"type":"long","value":"1536"}}','--outdir',str((OUT/'wmf-render').resolve())]+list(map(str,files))
 env={**os.environ,'XDG_CACHE_HOME':str(Path('work/tooling/cache').resolve())}
 try:
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=max(120,len(files)*5),env=env)
  (OUT/('wmf-batch-'+str(i)+'.log')).write_text(r.stdout+'\n'+r.stderr)
 except subprocess.TimeoutExpired:(OUT/('wmf-batch-'+str(i)+'.log')).write_text('Import timeout')
 print(json.dumps({'wmf_batch':i,'requested':len(files),'rendered':sum((OUT/'wmf-render'/(f.stem+'.png')).exists() for f in files)}),flush=True)
def lane(k):
 for i in range(k,len(groups),4):batch((i,groups[i]))
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lane,range(4)))
