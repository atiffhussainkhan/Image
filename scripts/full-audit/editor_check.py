from pathlib import Path
import json,gzip,io,zipfile,struct,zlib,time,subprocess,os
OUT=Path('outputs/repository-audit')
while not (OUT/'content-audit.json').exists():time.sleep(3)
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

results=[]
with gzip.open(OUT/'file-audit.jsonl.gz','rt') as f:
 for l in f:
  r=json.loads(l);ext=Path(r['path']).suffix.lower()
  if ext not in ('.aseprite','.ai'):continue
  result={'collection':r['collection'],'path':r['path'],'format':ext,'passed':False}
  try:
   data=retrieve(r)
   if ext=='.ai':
    p=subprocess.run([str(Path('work/tooling/render/bin/magick').resolve()),'-limit','memory','256MiB','ai:-','-resize','512x512>','png:-'],input=data,capture_output=True,timeout=30,env={**os.environ,'OMP_NUM_THREADS':'1','PATH':str(Path('work/tooling/render/bin').resolve())+os.pathsep+os.environ['PATH']})
    assert p.returncode==0,p.stderr.decode(errors='replace')[-300:];assert p.stdout.startswith(b'\x89PNG');result['check']='Rendered with ImageMagick/Ghostscript'
   else:
    size,magic,frames,w,h,depth=struct.unpack_from('<IHHHHH',data);assert size==len(data) and magic==0xa5e0 and w and h and frames and depth in (8,16,32)
    pos=128;cels=0
    for frame in range(frames):
     length,fmagic,old,duration=struct.unpack_from('<IHHH',data,pos);new=struct.unpack_from('<I',data,pos+12)[0];assert fmagic==0xf1fa and length>=16 and pos+length<=len(data)
     end=pos+length;p=pos+16
     for chunk in range(new or old):
      length2,typ=struct.unpack_from('<IH',data,p);assert length2>=6 and p+length2<=end;payload=data[p+6:p+length2]
      if typ==0x2005:
       cels+=1;celtype=struct.unpack_from('<H',payload,7)[0]
       if celtype in (0,2):
        cw,ch=struct.unpack_from('<HH',payload,16);raw=payload[20:] if celtype==0 else zlib.decompress(payload[20:]);assert len(raw)==cw*ch*(depth//8)
       elif celtype==1:assert struct.unpack_from('<H',payload,16)[0]<frames
       elif celtype==3:
        cw,ch,bits=struct.unpack_from('<HHH',payload,16);assert len(zlib.decompress(payload[48:]))==cw*ch*(bits//8)
       else:raise ValueError('Unknown cel type '+str(celtype))
      p+=length2
     assert p==end;pos=end
    assert pos==len(data) and cels>0;result.update(check='Header, every frame/chunk, linked frame bounds and all cel zlib payloads validated',frames=frames,width=w,height=h,cels=cels)
   result['passed']=True
  except Exception as e:result['error']=str(e)[:400]
  results.append(result)
report={'files_checked':len(results),'passed':sum(r['passed']for r in results),'results':results,'specification':'https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md','limitation':'Aseprite structure/cel pixels checked; editor layer compositing and gameplay engine import not certified.'}
(OUT/'editor-source-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k]for k in ('files_checked','passed')}),flush=True)
