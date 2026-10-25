#!/usr/bin/env python3
"""Build compact searchable index of actually stored bulk release archive members."""
import json,gzip,pathlib,sys
root=pathlib.Path(sys.argv[1]);dest=pathlib.Path(sys.argv[2]);dest.parent.mkdir(parents=True,exist_ok=True)
summaries=[];total=0
with gzip.open(dest,"wt",encoding="utf8",compresslevel=6) as out:
 for path in sorted(root.glob("*.json")):
  obj=json.loads(path.read_text())
  name=obj.get("stream",path.stem); count=0
  for a in obj.get("records",[]):
   record={"kind":"bulk_archive_member","asset_id":a.get("id"),"title":a.get("path"),"archive":name+".zip","release_tag":"mega-acquisition-2026-10-25","download_url":"https://github.com/atiffhussainkhan/Image/releases/download/mega-acquisition-2026-10-25/"+name+".zip","format":a.get("format"),"bytes":a.get("bytes"),"tags":a.get("tags"),"width":a.get("width"),"height":a.get("height"),"frames":a.get("frames"),"status":a.get("status"),"license_status":"per_pack_verification_required"}
   out.write(json.dumps(record,separators=(",",":"),ensure_ascii=False)+"\n");count+=1
  total+=count
  summaries.append({"stream":name,"files":count,"archive_bytes":obj.get("archive_bytes"),"errors":obj.get("error_count"),"download_url":"https://github.com/atiffhussainkhan/Image/releases/download/mega-acquisition-2026-10-25/"+name+".zip"})
(dest.parent/"bulk-acquisition-summary.json").write_text(json.dumps({"archive_count":len(summaries),"indexed_members":total,"streams":summaries,"quality_scope":"decode check on raster, not engine test; per-pack licence checks outstanding"},indent=2))
print("Indexed",total,"archive members from",len(summaries),"archives")
