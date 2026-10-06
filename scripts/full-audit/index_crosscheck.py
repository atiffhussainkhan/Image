from pathlib import Path
import json,gzip,hashlib,time,collections
OUT=Path('outputs/repository-audit');ART=Path('outputs/game-art-library')
while not (OUT/'content-audit.json').exists():time.sleep(3)
with gzip.open(ART/'assets.json.gz','rt') as f:rows=json.load(f)
files={};formats=[]
with gzip.open(OUT/'file-audit.jsonl.gz','rt') as f:
 for line in f:
  r=json.loads(line)
  if '-cleaned-' in r['collection'] and r['collection'].startswith('outputs/game-art-library/bundles/'):
   files[(Path(r['collection']).name,r['path'])]=r
  if r['status']=='image-pass':
   fmt=r.get('format');ext=Path(r['path']).suffix.lower()
   expected={'PNG':{'.png'},'JPEG':{'.jpg','.jpeg'},'WEBP':{'.webp'},'GIF':{'.gif'},'TIFF':{'.tif','.tiff'},'BMP':{'.bmp'},'DDS':{'.dds'},'PSD':{'.psd'},'ICO':{'.ico'},'TGA':{'.tga'},'PCX':{'.pcx'},'ICNS':{'.icns'}}.get(fmt)
   if expected and ext not in expected:formats.append({'collection':r['collection'],'path':r['path'],'actual_format':fmt})
masters={};frames=set();mismatches=[]
for r in rows:
 key=(r['normalized_bundle']['name'],r['normalized_file']);f=files.get(key)
 if not f or f['sha256']!=r['normalized_sha256'] or f['bytes']!=r['normalized_bytes']:mismatches.append(r['asset_id'])
 assert r['normalized_dimensions']==[f['width'],f['height']]
 assert f['format']=={'png':'PNG','jpg':'JPEG','jpeg':'JPEG'}[r['engine_format']]
 masters[key]=f
 for p in r.get('animation_frames') or []:frames.add((r['normalized_bundle']['name'],p))
for key in frames:
 f=files.get(key);p=Path('work/processed')/key[1]
 if not f or f['sha256']!=hashlib.sha256(p.read_bytes()).hexdigest():mismatches.append(str(key))
assert not mismatches,mismatches[:10]
manifest=json.loads((ART/'search-manifest.json').read_text());print('Search manifest keys',list(manifest),flush=True)
# Discovery shards must collectively contain exactly the same asset IDs.
ids=[]
for p in sorted(ART.glob('search-*.json.gz')):
 with gzip.open(p,'rt') as f:data=json.load(f)
 if isinstance(data,dict):data=data.get('assets',data.get('items',data.get('rows',[])))
 ids.extend(r.get('asset_id',r.get('id')) for r in data)
assert len(ids)==len(rows) and len(set(ids))==len(rows) and set(ids)=={r['asset_id']for r in rows}
blank_frames=[key for key in frames if files[key]['status']=='image-fully-transparent']
report={'index_records_checked':len(rows),'master_images_checked_against_actual_zip_bytes':len(masters),'animation_frame_files_checked_against_actual_zip_bytes':len(frames),'all_indexed_hashes_and_sizes_match_zip_contents':True,'every_indexed_dimension_matches_decoded_zip_image':True,'every_engine_format_matches_actual_header':True,'all_discovery_shard_ids_match':True,'fully_transparent_animation_timing_frame_files':len(blank_frames),'other_image_extension_mismatches':formats}
(OUT/'index-content-crosscheck.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='other_image_extension_mismatches'}),flush=True)
