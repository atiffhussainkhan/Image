#!/usr/bin/env python3
"""Strict CC0 ZIP acquisition. Run in an ephemeral GitHub Actions runner.
CSV: id,url,source_url,license,license_evidence_url,redistribution_approved
Manifest fields are assertions by curator, not independent proof of rights.
"""
import argparse,csv,hashlib,json,pathlib,re,shutil,stat,urllib.request,zipfile
from urllib.parse import urlsplit
MAX_ARCHIVE=2*1024**3
MAX_EXPANDED=4*1024**3
def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def https(value):
    u=urlsplit(value)
    return u.scheme=="https" and bool(u.hostname) and not u.username and not u.password
def run(manifest,output):
    output.mkdir(parents=True,exist_ok=True)
    approved=output/"approved";approved.mkdir(exist_ok=True)
    audit=[]; hashes={}
    with open(manifest,newline="",encoding="utf8") as f:
        for row in csv.DictReader(f):
            ident=row.get("id",""); url=row.get("url","")
            rec={"id":ident,"url":url,"source_url":row.get("source_url",""),"license":row.get("license",""),"files":[]}
            audit.append(rec)
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}",ident) or ".." in ident or not https(url):
                rec["status"]="invalid_input";continue
            if row.get("license","").strip().upper()!="CC0" or row.get("redistribution_approved","").strip().lower()!="yes" or not https(row.get("license_evidence_url","")) or not https(row.get("source_url","")):
                rec["status"]="excluded_pending_license";continue
            target=approved/ident
            archive=output/(ident+".zip")
            try:
                if target.exists():raise ValueError("duplicate pack id")
                req=urllib.request.Request(url,headers={"User-Agent":"GameAssetAudit/2.0"})
                with urllib.request.urlopen(req,timeout=120) as response,open(archive,"wb") as out:
                    if not https(response.geturl()):raise ValueError("non-HTTPS redirect")
                    size=0
                    while True:
                        block=response.read(1024*1024)
                        if not block:break
                        size+=len(block)
                        if size>MAX_ARCHIVE:raise ValueError("archive size limit")
                        out.write(block)
                if not zipfile.is_zipfile(archive):raise ValueError("not a ZIP")
                rec["archive_sha256"]=digest(archive)
                with zipfile.ZipFile(archive) as z:
                    members=z.infolist()
                    if len(members)>100000:raise ValueError("member count limit")
                    if sum(x.file_size for x in members)>MAX_EXPANDED:raise ValueError("expansion size limit")
                    seen=set()
                    for info in members:
                        name=info.filename
                        parts=pathlib.PurePosixPath(name).parts
                        mode=info.external_attr>>16
                        kind=stat.S_IFMT(mode)
                        if not parts or name.startswith("/") or "\\" in name or any(p in (".","..") for p in parts) or ":" in parts[0] or kind not in (0,stat.S_IFREG,stat.S_IFDIR):
                            raise ValueError("unsafe ZIP member")
                        if not info.is_dir():
                            normalized="/".join(parts)
                            if normalized in seen:raise ValueError("duplicate member name")
                            seen.add(normalized)
                target.mkdir()
                with zipfile.ZipFile(archive) as z:
                    for info in z.infolist():
                        if info.is_dir():continue
                        rel=pathlib.PurePosixPath(info.filename)
                        dest=target.joinpath(*rel.parts)
                        dest.parent.mkdir(parents=True,exist_ok=True)
                        with z.open(info) as src,open(dest,"wb") as dst:
                            remaining=info.file_size
                            while remaining:
                                block=src.read(min(1024*1024,remaining))
                                if not block:raise ValueError("truncated ZIP member")
                                dst.write(block);remaining-=len(block)
                        sha=digest(dest)
                        if sha in hashes:
                            dest.unlink()
                            rec["files"].append({"path":str(rel),"sha256":sha,"duplicate_of":hashes[sha]})
                        else:
                            hashes[sha]=ident+"/"+str(rel)
                            rec["files"].append({"path":str(rel),"sha256":sha,"bytes":dest.stat().st_size})
                rec["status"]="extracted_deduplicated"
            except Exception as exc:
                rec["status"]="failed";rec["error"]=str(exc)
                if target.exists():shutil.rmtree(target)
            finally:
                archive.unlink(missing_ok=True)
    (output/"audit.json").write_text(json.dumps(audit,indent=2),encoding="utf8")
    print(json.dumps({"total":len(audit),"approved":sum(x["status"]=="extracted_deduplicated" for x in audit),"failed":sum(x["status"]=="failed" for x in audit)}))
    return int(any(x["status"]=="failed" for x in audit))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("manifest");p.add_argument("--output",default="/tmp/game-asset-acquisition")
    a=p.parse_args();raise SystemExit(run(pathlib.Path(a.manifest),pathlib.Path(a.output)))
