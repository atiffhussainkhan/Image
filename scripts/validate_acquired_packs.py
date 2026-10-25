#!/usr/bin/env python3
"""Inspect downloaded ZIPs and create searchable records; rejects broken images and archives."""
import argparse,hashlib,json,pathlib,zipfile,io,sys
from PIL import Image
def main():
 ap=argparse.ArgumentParser();ap.add_argument("directory");ap.add_argument("--out",required=True);a=ap.parse_args()
 root=pathlib.Path(a.directory);records=[];packs=[]
 for p in sorted(root.glob("*.zip")):
  sha=hashlib.sha256(p.read_bytes()).hexdigest(); errors=[];images=0;animations=0;entries=0
  try:
   with zipfile.ZipFile(p) as z:
    for member in z.infolist():
     if member.is_dir():continue
     entries+=1
     if member.file_size==0:errors.append(member.filename+": empty");continue
     ext=pathlib.PurePosixPath(member.filename).suffix.lower()
     if ext in (".png",".jpg",".jpeg",".webp",".gif"):
      try:
       with Image.open(io.BytesIO(z.read(member))) as im:
        n=getattr(im,"n_frames",1);im.verify();images+=1;animations+=int(n>1)
      except Exception as e:errors.append(member.filename+": "+str(e)[:150])
     if ext in (".png",".jpg",".jpeg",".webp",".gif",".glb",".gltf",".fbx",".obj",".blend",".dae"):
      records.append({"asset_id":hashlib.sha256((p.name+"/"+member.filename).encode()).hexdigest()[:20],"pack":p.stem,"archive":p.name,"path":member.filename,"extension":ext,"bytes":member.file_size,"keywords":member.filename.replace("_"," ").replace("-"," ").replace("/"," "),"validation":"raster_decoded_or_binary_present_not_engine_tested"})
  except Exception as e:errors.append("archive failed: "+str(e))
  packs.append({"archive":p.name,"bytes":p.stat().st_size,"sha256":sha,"members":entries,"raster_decoded":images,"multi_frame_images":animations,"errors":errors[:100],"error_count":len(errors),"status":"integrity_pass_not_engine_tested" if not errors else "requires_review"})
 result={"schema_version":1,"warning":"Metadata and decoded raster validation, not gameplay/engine certification.","packs":packs,"assets":records}
 out=pathlib.Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2))
 print(json.dumps({"packs":len(packs),"assets":len(records),"bytes":sum(x["bytes"] for x in packs),"failures":sum(x["error_count"] for x in packs)}))
 return int(any(x["error_count"] for x in packs))
if __name__=="__main__":sys.exit(main())
