"""Reuse Ghostscript initialization while retaining file-specific crop and resolution."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,re,time,subprocess,collections
from convert import convert,OUT,GS,env
rows=json.loads((OUT/'source-rows.json').read_text());unique={}
for r in rows:
 if r['format']=='eps':unique.setdefault(r['sha256'],r)
todo=[r for sha,r in unique.items() if not (OUT/'status'/(sha+'.json')).exists()]
groups=[todo[i:i+24] for i in range(0,len(todo),24)]
def ps_string(s):return '('+s.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')+')'
def batch(group):
 cmd=[str(GS),'-q','-dSAFER','-dBATCH','-dNOPAUSE','--permit-file-write='+str((OUT/'images').resolve())+'/*','-dEPSCrop','-sDEVICE=pngalpha','-dGraphicsAlphaBits=4','-dTextAlphaBits=4']
 included=[]
 for r in group:
  src=Path(r['source_path']);m=re.search(rb'%%(?:HiRes)?BoundingBox:\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)',src.read_bytes()[:32768])
  if not m:continue
  b=list(map(float,m.groups()));length=max(b[2]-b[0],b[3]-b[1])
  if not(0<length<100000):continue
  dpi=72*1024/length;dest=(OUT/'images'/(r['sha256']+'.png')).resolve();dest.unlink(missing_ok=True)
  cmd+=['-c','<< /OutputFile '+ps_string(str(dest))+' /HWResolution ['+str(dpi)+' '+str(dpi)+'] >> setpagedevice','-f',str(src)]
  included.append(r)
 if included:
  try:subprocess.run(cmd,capture_output=True,timeout=90,env=env)
  except subprocess.TimeoutExpired:pass
 results=[]
 for r in group:
  p=OUT/'images'/(r['sha256']+'.png')
  if p.exists():r={**r,'_rendered':True}
  results.append(convert(r))
 return results
counts=collections.Counter();done=len(unique)-len(todo);started=time.time()
print(json.dumps({'eps_already_finished':done,'eps_remaining':len(todo)}),flush=True)
with ThreadPoolExecutor(max_workers=8) as pool:
 for start in range(0,len(groups),40):
  for results in pool.map(batch,groups[start:start+40]):
   for s in results:counts[s['conversion_status']]+=1;done+=1
  print(json.dumps({'eps_processed':done,'eps_total':len(unique),'states':dict(counts),'elapsed_seconds':round(time.time()-started)}),flush=True)
