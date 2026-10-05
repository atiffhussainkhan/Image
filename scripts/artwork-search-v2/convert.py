"""Lossless PNG conversion, individual preview validation, resumable checkpoints."""
from pathlib import Path
from PIL import Image,ImageOps,ImageChops,ImageStat,ImageCms
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,os,re,time,collections,hashlib,io
OUT=Path('work/processed');GS=Path('work/tooling/render/bin/gs').resolve();MAGICK=Path('work/tooling/render/bin/magick').resolve()
RASTER={'png','jpg','jpeg','gif','tif','tiff','bmp','rle','pcx','webp'}
rows=json.loads((OUT/'source-rows.json').read_text());unique={}
for r in rows:unique.setdefault(r['sha256'],r)
env={**os.environ,'XDG_CACHE_HOME':str(Path('work/tooling/cache').resolve()),'OMP_NUM_THREADS':'1'}
def convert(row):
 sha=row['sha256'];status=OUT/'status'/(sha+'.json');status.parent.mkdir(exist_ok=True)
 if status.exists():return json.loads(status.read_text())
 dest=OUT/'images'/(sha+'.png');thumb=OUT/'thumbs'/(sha+'.webp');src=Path(row['source_path']);ext=row['format']
 r={'sha256':sha,'conversion_status':'unsupported','preview_status':'unavailable','original_format':ext}
 try:
  if ext in RASTER:
   with Image.open(src) as source:
    source.load();r['original_dimensions']=list(source.size);r['frame_count']=getattr(source,'n_frames',1)
    im=ImageOps.exif_transpose(source).convert('RGBA')
    if source.info.get('icc_profile'):
     try:im=ImageCms.profileToProfile(im,ImageCms.ImageCmsProfile(io.BytesIO(source.info['icc_profile'])),ImageCms.createProfile('sRGB'),outputMode='RGBA');r['colour_profile']='converted-to-sRGB'
     except Exception:r['colour_profile']='profile-conversion-unverified'
    r['conversion_method']='Pillow lossless PNG, EXIF orientation applied'
  elif ext=='eps':
   data=src.read_bytes()[:32768];m=re.search(rb'%%(?:HiRes)?BoundingBox:\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)',data)
   if not m:raise ValueError('No numeric EPS bounding box')
   b=list(map(float,m.groups()));w=b[2]-b[0];h=b[3]-b[1]
   if not(0<w<100000 and 0<h<100000):raise ValueError('Invalid EPS bounding box')
   dpi=72*1024/max(w,h)
   if not row.get('_rendered'):
    p=subprocess.run([str(GS),'-q','-dSAFER','-dBATCH','-dNOPAUSE','-dEPSCrop','-sDEVICE=pngalpha','-dGraphicsAlphaBits=4','-dTextAlphaBits=4','-r'+str(dpi),'-sOutputFile='+str(dest),str(src)],capture_output=True,timeout=20,env=env)
    if p.returncode:raise ValueError('Ghostscript exit '+str(p.returncode)+': '+(p.stderr+p.stdout).decode(errors='replace')[-500:])
   im=Image.open(dest);im.load();im=im.convert('RGBA');r['conversion_method']='Ghostscript 10.08.0; EPS bounding box; 1024px longest side';r['vector_bounding_box']=b
  elif ext=='wmf':
   p=OUT/'wmf-render'/(sha+'.png')
   if not p.exists():return {**r,'conversion_status':'awaiting-wmf-render'}
   im=Image.open(p);im.load();im=im.convert('RGBA')
   # Only trim outside visible drawing bounds; retain all interior white pixels.
   bg=Image.new('RGB',im.size,'white');diff=ImageChops.difference(im.convert('RGB'),bg);box=diff.getbbox()
   if box:
    box=(max(0,box[0]-4),max(0,box[1]-4),min(im.width,box[2]+4),min(im.height,box[3]+4))
    r['removed_page_margins']=list(box);im=im.crop(box)
   im.thumbnail((1024,1024),Image.Resampling.LANCZOS);r['conversion_method']='LibreOffice Draw PNG; external page margins cropped, white artwork retained'
  elif ext=='wpg':
   p=subprocess.run([str(MAGICK),str(src),str(dest)],capture_output=True,timeout=30,env=env)
   if p.returncode:raise ValueError('WPG conversion failed')
   im=Image.open(dest);im.load();im=im.convert('RGBA');r['conversion_method']='ImageMagick WPG decoder'
  else:
   r['reason']='Legacy drawing format requires a compatible importer' if ext in {'drw','drt','mgx'} else 'Container or non-image metadata; preserved in original archive'
   status.write_text(json.dumps(r));return r
  if im.width<1 or im.height<1:raise ValueError('Zero image dimensions')
  a=im.getchannel('A');r['has_transparent_pixels']=a.getextrema()[0]<255;r['fully_transparent']=a.getextrema()[1]==0
  rgb=Image.new('RGBA',im.size,'white');rgb.alpha_composite(im)
  sample=rgb.convert('RGB');sample.thumbnail((128,128))
  extrema=sample.getextrema();r['near_blank']=all(high-low<4 for low,high in extrema)
  r['normalized_dimensions']=list(im.size);r['aspect_ratio']=round(im.width/im.height,4)
  r['needs_visual_review']=r['near_blank'] or r['fully_transparent']
  r['original_transparency_preserved']=ext in RASTER or ext=='eps'
  if ext!='eps':im.save(dest,format='PNG',compress_level=6)
  with Image.open(dest) as verify:verify.load();assert verify.size==im.size
  r['normalized_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();r['normalized_bytes']=dest.stat().st_size
  im.thumbnail((224,224),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(224,224),'white');canvas.alpha_composite(im,((224-im.width)//2,(224-im.height)//2));canvas.convert('RGB').save(thumb,'WEBP',quality=90)
  with Image.open(thumb) as verify:verify.load();assert verify.size==(224,224)
  r.update(conversion_status='converted',preview_status='decode-verified',normalized_file='images/'+sha+'.png',thumbnail_file='thumbs/'+sha+'.webp')
  r['dominant_rgb']=[round(x) for x in ImageStat.Stat(sample.resize((1,1))).mean]
 except Exception as e:
  r.update(conversion_status='failed',preview_status='unavailable',reason=str(e)[:700]);dest.unlink(missing_ok=True);thumb.unlink(missing_ok=True)
 status.write_text(json.dumps(r));return r
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--kind',choices=['eps','wmf','other','all'],default='all');p.add_argument('--workers',type=int,default=10);a=p.parse_args()
 selected=[r for r in unique.values() if a.kind=='all' or (a.kind=='eps' and r['format']=='eps') or (a.kind=='wmf' and r['format']=='wmf') or (a.kind=='other' and r['format'] not in {'eps','wmf'})]
 counts=collections.Counter();started=time.time()
 with ThreadPoolExecutor(max_workers=a.workers) as pool:
  for chunk in range(0,len(selected),1000):
   for s in pool.map(convert,selected[chunk:chunk+1000]):counts[s['conversion_status']]+=1
   print(json.dumps({'kind':a.kind,'processed':min(chunk+1000,len(selected)),'total':len(selected),'states':dict(counts),'elapsed_seconds':round(time.time()-started)}),flush=True)
