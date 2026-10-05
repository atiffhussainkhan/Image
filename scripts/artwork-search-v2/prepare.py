"""Preserve source identities and extract embedded Microsoft Clip Gallery artwork."""
from pathlib import Path
import gzip,json,hashlib,base64,xml.etree.ElementTree as ET,collections,os
ROOT=Path(os.environ.get('ARTWORK_SOURCE_ROOT','work/extracted'))
OUT=Path('work/processed')
with gzip.open('work/Image/catalog/workplace-art-unverified-2026-10-05/assets.json.gz','rt') as f:rows=json.load(f)
C='{urn:schemas-microsoft-com:office:clipgallery}'
for row in rows:
 row['source_path']=str(ROOT/row['pack']/row['original_path'])
 row['source_archive']={'10000.HighDefinition.PNG.Icon.Pack':'10000.HighDefinition.PNG.Icon.Pack.rar','Clipart':'Clipart.tar','EPS_Clipart':'EPS_Clipart.rar','Samples':'Samples.rar'}[row['pack']]
 row['asset_id']=hashlib.sha256((row['pack']+'\0'+row['original_path']).encode()).hexdigest()[:20]
 row['entry_kind']='source-file'
 row['source_keywords']=[]
extra=[]
for row in rows:
 if row['format']!='mpf':continue
 try:
  tree=ET.parse(row['source_path'])
  for i,response in enumerate(tree.findall('.//{DAV:}response')):
   resource=response.find('.//'+C+'resource')
   if resource is None:continue
   contents=resource.find(C+'contents');name=resource.findtext(C+'filepath','unnamed')
   if contents is None or not contents.text:continue
   data=base64.b64decode(contents.text);sha=hashlib.sha256(data).hexdigest();ext=Path(name).suffix.lower().lstrip('.')
   dest=OUT/'embedded'/(sha+'.'+ext)
   if not dest.exists():dest.write_bytes(data)
   keywords=response.findtext('.//'+C+'subject','')
   path=row['original_path']+'::'+str(i)+'/'+name
   extra.append({'pack':row['pack'],'original_path':path,'source_container':row['original_path'],'format':ext,'bytes':len(data),'sha256':sha,'category':row['category'],'tags':row['tags'],'source_keywords':[s.strip() for s in keywords.split(',') if s.strip()],'license_status':'unverified','readiness':'extracted-embedded','source_path':str(dest.resolve()),'source_archive':row['source_archive'],'asset_id':hashlib.sha256((row['pack']+'\0'+path).encode()).hexdigest()[:20],'entry_kind':'embedded-image'})
 except Exception as e:row['container_error']=str(e)
rows.extend(extra)
seen={}
for row in rows:
 row['duplicate_asset_id']=seen.get(row['sha256'])
 seen.setdefault(row['sha256'],row['asset_id'])
missing=[r['original_path'] for r in rows if not Path(r['source_path']).is_file()]
assert not missing,missing[:10]
(OUT/'source-rows.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
print(json.dumps({'original_files':len(rows)-len(extra),'embedded_images':len(extra),'unique_blobs':len(seen),'embedded_formats':dict(collections.Counter(r['format'] for r in extra))}),flush=True)
