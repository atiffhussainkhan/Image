"""Keep only readable, nonempty PNGs in the active game library; emit a removal ledger."""
from pathlib import Path
from PIL import Image,ImageSequence,ImageChops
import json,shutil,csv
OUT=Path('work/processed');rows=json.loads((OUT/'source-rows.json').read_text());u={}
for r in rows:u.setdefault(r['sha256'],r)
removed=[];animations=0
for sha,r in u.items():
 p=OUT/'status'/(sha+'.json');s=json.loads(p.read_text())
 if s['conversion_status']=='converted' and s.get('detected_source_format',r['format'])=='gif' and s.get('frame_count',1)>1:
  try:
   frames=[];durations=[];folder=OUT/'images'/sha;folder.mkdir(exist_ok=True);poster=None;poster_index=None
   with Image.open(r['source_path']) as gif:
    loop=gif.info.get('loop',None)
    for i,frame in enumerate(ImageSequence.Iterator(gif)):
     dest=folder/('frame-'+str(i).zfill(4)+'.png');rgba=frame.convert('RGBA');rgba.save(dest,'PNG',compress_level=6)
     with Image.open(dest) as check:check.load()
     frames.append('images/'+sha+'/'+dest.name);durations.append(frame.info.get('duration',100))
     alpha=rgba.getchannel('A').getextrema();sample=Image.new('RGBA',rgba.size,'white');sample.alpha_composite(rgba);sample=sample.convert('RGB');sample.thumbnail((64,64))
     varying=any(hi-lo>=4 for lo,hi in sample.getextrema()) or alpha[1]-alpha[0]>=4
     if poster is None and alpha[1]>0 and varying:poster=rgba.copy();poster_index=i
   s.update(animation_frames=frames,animation_durations_ms=durations,animation_loop=loop);animations+=1
   if poster is not None:
    s.update(fully_transparent=False,near_blank=False,needs_visual_review=False,poster_frame_index=poster_index,has_transparent_pixels=poster.getchannel('A').getextrema()[0]<255)
    if poster_index!=0:
     poster.save(OUT/'images'/(sha+'.png'),'PNG',compress_level=6);s['requires_reanalysis']=True
     poster.thumbnail((224,224));canvas=Image.new('RGBA',(224,224),'white');canvas.alpha_composite(poster,((224-poster.width)//2,(224-poster.height)//2));canvas.convert('RGB').save(OUT/'thumbs'/(sha+'.webp'),'WEBP',quality=90)
     import hashlib
     s['normalized_sha256']=hashlib.sha256((OUT/'images'/(sha+'.png')).read_bytes()).hexdigest();s['normalized_bytes']=(OUT/'images'/(sha+'.png')).stat().st_size
  except Exception as e:s.update(conversion_status='failed',preview_status='unavailable',reason='Animation frame decoding failed: '+str(e))
 # Uniform or wholly transparent images contain no distinguishable picture to index.
 # A white silhouette with a nonuniform alpha mask is real artwork, not an empty white image.
 meaningful_alpha=False
 if s['conversion_status']=='converted' and s.get('near_blank') and not s.get('fully_transparent'):
  with Image.open(OUT/'images'/(sha+'.png')) as im:
   rgba=im.convert('RGBA');lo,hi=rgba.getchannel('A').getextrema();meaningful_alpha=hi>lo
   if meaningful_alpha:
    rgba.thumbnail((224,224));canvas=Image.new('RGBA',(224,224),(195,205,220,255));canvas.alpha_composite(rgba,((224-rgba.width)//2,(224-rgba.height)//2));canvas.convert('RGB').save(OUT/'thumbs'/(sha+'.webp'),'WEBP',quality=90)
    s.update(near_blank=False,needs_visual_review=False,requires_reanalysis=True,white_alpha_artwork=True)
 # Low contrast alone is not emptiness. Check full-resolution pixels before deletion.
 uniform=False
 if s['conversion_status']=='converted' and s.get('near_blank',False) and not meaningful_alpha:
  with Image.open(OUT/'images'/(sha+'.png')) as im:
   rgba=im.convert('RGBA');matte=Image.new('RGBA',rgba.size,'white');matte.alpha_composite(rgba)
   uniform=all(lo==hi for lo,hi in matte.convert('RGB').getextrema())
  if not uniform:s.update(near_blank=False,needs_visual_review=False)
 empty=s.get('fully_transparent',False) or uniform
 if s['conversion_status']!='converted' or empty:
  reason='Empty or uniform image; no distinguishable artwork' if empty else s.get('reason','Unreadable or unsupported source')
  if r.get('bytes')==0:reason='Empty file (0 bytes); no recoverable image data'
  s['reason']=reason
  if s['conversion_status']=='converted':s.update(conversion_status='removed-empty',preview_status='unavailable',reason=reason)
  (OUT/'images'/(sha+'.png')).unlink(missing_ok=True);(OUT/'thumbs'/(sha+'.webp')).unlink(missing_ok=True)
  if (OUT/'images'/sha).is_dir():shutil.rmtree(OUT/'images'/sha)
  s['active_library']=False;removed.append({'sha256':sha,'format':r['format'],'original_path':r['original_path'],'reason':reason})
 else:
  s['active_library']=True
 p.write_text(json.dumps(s))
(OUT/'removal-report.json').write_text(json.dumps(removed,ensure_ascii=False,indent=2))
print(json.dumps({'removed_unique_sources':len(removed),'animation_sequences_exported':animations}),flush=True)
