from pathlib import Path
import json,zipfile,io,gzip,subprocess,time,hashlib,os
from PIL import Image
OUT=Path('outputs/repository-audit')
while not (OUT/'content-audit.json').exists():time.sleep(3)
report=json.loads((OUT/'content-audit.json').read_text());targets=[]
with gzip.open(OUT/'file-audit.jsonl.gz','rt') as f:
 for line in f:
  r=json.loads(line)
  if r['status']=='vector-parse-pass' or (r['status']=='failed' and Path(r['path']).suffix.lower() in {'.hdr','.exr','.dds','.psd','.tga','.icns','.png','.jpg','.jpeg','.gif','.webp','.bmp','.tif','.tiff','.ico','.pcx','.svg'}):targets.append(r)
zip_handles={}
def retrieve(r):
 origin=r['collection']
 if origin.endswith(' Git tree'):return (Path('work')/origin.split()[0]/r['path']).read_bytes()
 if origin not in zip_handles:
  parts=origin.split('::');key=parts[0]
  if key not in zip_handles:zip_handles[key]=zipfile.ZipFile(Path(key))
  for nested in parts[1:]:
   parent=key;key+='::'+nested
   if key not in zip_handles:zip_handles[key]=zipfile.ZipFile(io.BytesIO(zip_handles[parent].read(nested)))
 return zip_handles[origin].read(r['path'])

import concurrent.futures,collections,xml.etree.ElementTree as ET,threading
magick=str(Path('work/tooling/render/bin/magick').resolve());env={**os.environ,'OMP_NUM_THREADS':'1','PATH':str(Path('work/tooling/render/bin').resolve())+os.pathsep+os.environ['PATH'],'XDG_CACHE_HOME':str(Path('work/tooling/cache').resolve())}
read_lock=threading.Lock()
unique={r['sha256']:r for r in targets}
# Initialise shared ZIP central directories once, before renderer threads start.
origins={r['collection']:r for r in targets}
for r in origins.values():retrieve(r)
def render(r):
 sha=r['sha256'];ext=Path(r['path']).suffix.lower()[1:]
 try:
  with read_lock:data=retrieve(r)
  assert hashlib.sha256(data).hexdigest()==sha,'Archive member hash mismatch'
  if data[:4] in (b'\x00\x05\x16\x07',b'\x00\x05\x16\x00'):
   return sha,{'passed':True,'classification':'AppleDouble filesystem metadata; not an image','source_sha256_confirmed':True}
  viewport={}
  if ext=='svg':
   root=ET.fromstring(data);viewport={'svg_missing_explicit_viewport':not root.get('viewBox') and not (root.get('width') and root.get('height'))}
  p=subprocess.run([magick,'-background','none','-limit','memory','256MiB','-limit','map','512MiB','-define','svg:render-width=512','-define','svg:render-height=512',ext+':-','-resize','512x512>','png:-'],input=data,capture_output=True,timeout=30,env=env)
  assert p.returncode==0,p.stderr.decode(errors='replace')[-300:]
  with Image.open(io.BytesIO(p.stdout)) as im:
   im.load();assert im.width>0 and im.height>0
   rgba=im.convert('RGBA');alpha=rgba.getchannel('A');box=alpha.getbbox();visible=bool(box);uniform=not any(hi>lo for lo,hi in rgba.getextrema())
  return sha,{'passed':True,'source_sha256_confirmed':True,'render_has_visible_pixels':visible,'render_is_uniform':uniform,'decoder':'ImageMagick 7 / librsvg or format decoder; transparent backdrop',**viewport}
 except Exception as e:return sha,{'passed':False,'error':str(e)[:400]}
cache={}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 futures=[pool.submit(render,r)for r in unique.values()]
 for n,f in enumerate(concurrent.futures.as_completed(futures),1):
  sha,result=f.result();cache[sha]=result
  if n%100==0:print(json.dumps({'unique_formats_checked':n,'unique_targets':len(unique)}),flush=True)
results=[{'collection':r['collection'],'path':r['path'],'sha256':r['sha256'],'previous_status':r['status'],**cache[r['sha256']]}for r in targets]
(OUT/'supplemental-format-audit.json').write_text(json.dumps({'files_checked':len(results),'unique_content_checked':len(cache),'passed':sum(x['passed']for x in results),'results':results},indent=2));print('Supplement complete',flush=True)
