#!/usr/bin/env python3
"""Validate a downloaded source folder and produce a genuinely searchable member index.
Never claims game-engine playback or licence clearance solely from decoding.
"""
import argparse, pathlib, hashlib, json, zipfile, io, collections, os, sys
from PIL import Image
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--root",required=True);p.add_argument("--stream",required=True);p.add_argument("--source",required=True);p.add_argument("--out",required=True);p.add_argument("--zip",required=True)
 a=p.parse_args();root=pathlib.Path(a.root);output=pathlib.Path(a.out);output.parent.mkdir(parents=True,exist_ok=True)
 entries=[];errors=[];kinds=collections.Counter();bytes_read=0
 with zipfile.ZipFile(a.zip,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for f in sorted(root.rglob("*")):
   if not f.is_file() or ".git" in f.parts:continue
   rel=f.relative_to(root).as_posix()
   if rel.startswith(".git/"):continue
   size=f.stat().st_size
   if size==0:continue
   if size>300*1024*1024:
    errors.append({"path":rel,"reason":"over 300MB individual file; skipped"});continue
   data=f.read_bytes();digest=hashlib.sha256(data).hexdigest();ext=f.suffix.lower()
   if ext in (".png",".jpg",".jpeg",".webp",".gif",".bmp"):
    try:
     with Image.open(io.BytesIO(data)) as im:
      frames=getattr(im,"n_frames",1);w,h=im.size;im.verify()
     if w<1 or h<1:raise ValueError("zero dimensions")
    except Exception as e:
     errors.append({"path":rel,"reason":"image decode "+str(e)[:160]});continue
   else:frames=0;w=h=0
   z.writestr(rel,data)
   bytes_read+=size;kinds[ext or "(none)"]+=1
   entries.append({"id":digest[:20],"source":a.source,"stream":a.stream,"path":rel,"bytes":size,"sha256":digest,"format":ext,"width":w,"height":h,"frames":frames,"tags":rel.replace("_"," ").replace("-"," ").replace("/"," "),"status":"archive_published_raster_decoded_engine_not_tested"})
 report={"stream":a.stream,"source":a.source,"member_count":len(entries),"uncompressed_member_bytes":bytes_read,"archive_bytes":pathlib.Path(a.zip).stat().st_size,"sha256":hashlib.sha256(pathlib.Path(a.zip).read_bytes()).hexdigest(),"errors":errors[:300],"error_count":len(errors),"formats":kinds,"records":entries,"engine_tested":False,"copyright_and_license_require_per_pack_review":True}
 output.write_text(json.dumps(report,indent=1),encoding="utf8")
 print(json.dumps({k:report[k] for k in ("stream","member_count","archive_bytes","error_count")}))
if __name__=="__main__":main()
