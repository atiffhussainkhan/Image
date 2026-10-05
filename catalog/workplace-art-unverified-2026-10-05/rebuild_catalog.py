from pathlib import Path
from PIL import Image
import hashlib,json,csv,re,collections,gzip,shutil
root=Path('work/extracted');out=Path('outputs/artwork-audit');out.mkdir(parents=True,exist_ok=True)
rows=[];seen={};packs=[]
raster={'.png','.jpg','.jpeg','.gif','.bmp','.tif','.tiff','.pcx','.rle'};vector={'.eps','.wmf','.emf','.svg'}
for folder in sorted(root.iterdir()):
 stats=collections.Counter();dims=collections.Counter();sample=[];lic=[];totalbytes=0
 for f in sorted(folder.rglob('*')):
  if not f.is_file():continue
  data=f.read_bytes();sha=hashlib.sha256(data).hexdigest();ext=f.suffix.lower();rel=f.relative_to(folder).as_posix();size=len(data);totalbytes+=size
  row={'pack':folder.name,'original_path':rel,'format':ext.lstrip('.'),'bytes':size,'sha256':sha,'category':' / '.join(f.relative_to(folder).parts[1:-1]),'tags':sorted(set(re.findall(r'[a-z]{3,}',rel.lower()))),'license_status':'unverified','readiness':'legacy-source','width':None,'height':None,'transparency':None,'duplicate_of':seen.get(sha)}
  seen.setdefault(sha,folder.name+'/'+rel)
  if row['duplicate_of']:stats['duplicate_files']+=1
  stats['files']+=1;stats[ext]+=1
  if ext in raster:
   try:
    with Image.open(f) as im:
     im.load();row.update(width=im.width,height=im.height,transparency=('A' in im.getbands() or 'transparency' in im.info),readiness='raster-ready' if ext in {'.png','.jpg','.jpeg'} else 'convert-raster');stats['decoded_rasters']+=1;dims[str(im.size)]+=1
     if row['transparency']:stats['alpha_capable']+=1
     if min(im.size)<128:stats['small_rasters']+=1
   except Exception as e:row.update(readiness='decode-failed',error=str(e));stats['decode_failures']+=1
  elif ext in vector:
   row['readiness']='convert-vector'
   if ext=='.eps':
    hdr=data[:16000];m=re.search(rb'%%BoundingBox:\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)',hdr)
    row['eps_header_valid']=b'%!PS-Adobe' in data[:512]
    if m:row['bounding_box_points']=[float(x) for x in m.groups()];stats['eps_with_bbox']+=1
    if row['eps_header_valid']:stats['eps_with_header']+=1
  elif ext in {'.db','.imf','.sbj'}:row['readiness']='metadata-only'
  if ext in {'.txt','.md','.pdf','.rtf','.html'} and any(x in f.name.lower() for x in ['license','licence','readme','copyright','eula','install']):lic.append({'path':rel,'text':data[:4000].decode('utf8','replace') if ext=='.txt' else ''})
  rows.append(row)
 print(folder.name,dict(stats),flush=True)
 packs.append({'pack':folder.name,'stats':dict(stats),'bytes':totalbytes,'common_dimensions':dict(dims.most_common(10)),'licence_documents':lic,'rendering_note':'EPS/WMF rendering not verified; no compatible renderer installed.'})
(out/'assets.json').write_text(json.dumps(rows,ensure_ascii=True,separators=(',',':')))
with gzip.open(out/'assets.json.gz','wb') as f:f.write((out/'assets.json').read_bytes())
with (out/'assets.csv').open('w',newline='') as f:
 fields=['pack','original_path','category','format','bytes','width','height','transparency','readiness','license_status','sha256','duplicate_of'];w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
(out/'pack-summary.json').write_text(json.dumps(packs,indent=2))
shutil.copy('work/build_catalog.py',out/'rebuild_catalog.py')
print('Catalogue complete:',len(rows),flush=True)
