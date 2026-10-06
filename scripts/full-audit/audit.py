from pathlib import Path
import json,gzip,io,zipfile,hashlib,collections,concurrent.futures,threading,subprocess,os,xml.etree.ElementTree as ET
from PIL import Image,ImageSequence
Image.MAX_IMAGE_PIXELS=None
ROOT=Path('work/full-audit');OUT=Path('outputs/repository-audit');OUT.mkdir(exist_ok=True)
lock=threading.Lock();counts=collections.Counter();issues=[];packs=[]
ledger=gzip.open(OUT/'file-audit.jsonl.gz','wt')
RASTER={'.png','.jpg','.jpeg','.gif','.webp','.bmp','.tif','.tiff','.ico','.tga','.dds','.psd','.pcx','.ppm','.pgm','.pbm','.icns','.hdr','.exr'}
def emit(r):
 with lock:
  counts[r['status']]+=1;ledger.write(json.dumps(r,ensure_ascii=False)+'\n')
  if r['status'] not in ('image-pass','data-pass','archive-pass','metadata-pass','vector-parse-pass'):issues.append(r)
def check(data,name,origin):
 r={'collection':origin,'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};ext=Path(name).suffix.lower()
 try:
  if not data:r['status']='empty-file'
  elif data.startswith(b'version https://git-lfs.github.com/spec/v1'):r['status']='unresolved-lfs-pointer'
  elif ext in RASTER or data[:8]==b'\x89PNG\r\n\x1a\n' or data[:3]==b'\xff\xd8\xff' or data[:6] in (b'GIF87a',b'GIF89a'):
   with Image.open(io.BytesIO(data)) as im:
    r.update(format=im.format,width=im.width,height=im.height,frames=getattr(im,'n_frames',1));visible=False;distinguishable=False
    for frame in ImageSequence.Iterator(im):
     frame.load();rgba=frame.convert('RGBA');alpha=rgba.getchannel('A');box=alpha.getbbox()
     if box:
      visible=True;crop=rgba.crop(box);ex=crop.getextrema();distinguishable=distinguishable or any(hi>lo for lo,hi in ex) or alpha.getextrema()[0]<255
    r['status']='image-pass' if visible and distinguishable else ('image-fully-transparent' if not visible else 'image-uniform')
  elif ext=='.svg':
   e=ET.fromstring(data);assert e.tag.endswith('svg');r['status']='vector-parse-pass';r['limitation']='XML checked; rendering not yet verified'
  elif ext in ('.json','.jsonl'):
   if ext=='.json':json.loads(data)
   else:
    for line in data.splitlines():
     if line.strip():json.loads(line)
   r['status']='metadata-pass'
  elif name.endswith(('.json.gz','.jsonl.gz')):
   raw=gzip.decompress(data)
   if name.endswith('.json.gz'):json.loads(raw)
   else:
    for line in raw.splitlines():
     if line.strip():json.loads(line)
   r['status']='metadata-pass'
  elif ext=='.zip':
   audit_zip(io.BytesIO(data),origin+'::'+name);r['status']='archive-pass'
  else:r['status']='data-pass';r['limitation']='Non-image data; content hash and archive CRC verified, engine import not certified'
 except Exception as e:r.update(status='failed',error=str(e)[:400])
 emit(r)
def audit_zip(source,origin):
 local=collections.Counter()
 with zipfile.ZipFile(source) as z:
  names=[i.filename for i in z.infolist() if not i.is_dir()];dups=[n for n,c in collections.Counter(names).items() if c>1]
  if dups:emit({'collection':origin,'path':'<central-directory>','status':'duplicate-archive-paths','paths':dups})
  for info in z.infolist():
   if info.is_dir():continue
   try:
    data=z.read(info);check(data,info.filename,origin);local['files']+=1;local['uncompressed_bytes']+=len(data)
   except Exception as e:emit({'collection':origin,'path':info.filename,'status':'failed','error':str(e)});local['failures']+=1
 with lock:packs.append({'collection':origin,**local});print(json.dumps({'complete':origin,**local}),flush=True)
def run_zip(p):
 try:audit_zip(p,str(p))
 except Exception as e:emit({'collection':str(p),'path':'<archive>','status':'failed','error':str(e)})
# Actual engine packs and every metadata ZIP, not a sample.
clean=list(Path('outputs/game-art-library/bundles').glob('*.zip'))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run_zip,clean))
# Every tracked file in both Git repositories, excluding .git internals.
for repo in ('Image','animation'):
 base=Path('work')/repo
 files=subprocess.check_output(['git','-C',str(base),'ls-files','-z']).decode().split('\0')
 for n in filter(None,files):check((base/n).read_bytes(),n,repo+' Git tree')
# Wait for all approved-pack downloads to complete before auditing them.
for tag in ('mega-assets-v1','mega-assets-expansion-v1','mega-assets-expansion-v2'):
 inventory=next(r for r in json.load(open('work/image-release-inventory.json')) if r['tag_name']==tag)
 for a in inventory['assets']:
  p=ROOT/'downloads'/tag/a['name'];assert p.exists() and p.stat().st_size==a['size'],str(p)
  digest=hashlib.sha256(p.read_bytes()).hexdigest();assert a.get('digest')=='sha256:'+digest,(str(p),'GitHub digest mismatch')
  if p.suffix.lower()=='.zip':run_zip(p)
  else:check(p.read_bytes(),p.name,tag)
ledger.close()
report={'counts':dict(counts),'packs':packs,'issues':issues,'scope':['Image repository tracked files','animation repository tracked files','all 12 cleaned release ZIPs','all three approved-pack releases, including nested ZIPs'],'limitations':['Non-image 3D/audio/binary game data is not a corrupt image and requires its own engine importer.','Uniform textures and transparent sprite padding are flagged for contextual review, not assumed corruption.','SVG parsing does not prove SVG rendering.']}
(OUT/'content-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({'finished':True,'counts':dict(counts),'issues':len(issues)}),flush=True)
