"""Drain newly imported WMFs and signal semantic analysis only after all conversions finish."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,time
from convert import convert,OUT
rows=json.loads((OUT/'source-rows.json').read_text());u={}
for r in rows:u.setdefault(r['sha256'],r)
wmf=[r for r in u.values() if r['format']=='wmf'];expected_batches=(len(wmf)+159)//160
done=set(p.stem for p in (OUT/'status').glob('*.json'))
with ThreadPoolExecutor(max_workers=3) as pool:
 while True:
  imported=[r for r in wmf if r['sha256'] not in done and (OUT/'wmf-render'/(r['sha256']+'.png')).exists()]
  for r,s in zip(imported,pool.map(convert,imported)):
   if s['conversion_status']!='awaiting-wmf-render':done.add(r['sha256'])
  logs=list(OUT.glob('wmf-batch-*.log'))
  if len(logs)>=expected_batches:
   for r in wmf:
    if r['sha256'] not in done:
     s={'sha256':r['sha256'],'conversion_status':'failed','preview_status':'unavailable','original_format':'wmf','reason':'LibreOffice Draw importer produced no readable PNG'}
     (OUT/'status'/(r['sha256']+'.json')).write_text(json.dumps(s));done.add(r['sha256'])
  count=sum(1 for _ in (OUT/'status').glob('*.json'))
  print(json.dumps({'finished_source_blobs':count,'total_source_blobs':len(u),'wmf_import_batches':len(logs),'expected_wmf_batches':expected_batches}),flush=True)
  if count==len(u):
   (OUT/'conversion-complete').touch();break
  time.sleep(15)
