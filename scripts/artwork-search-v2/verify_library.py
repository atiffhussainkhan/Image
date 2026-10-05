"""Verify cleaned index coverage, duplicates, bundle membership, vectors and search."""
from pathlib import Path
import json,gzip,sqlite3,zipfile,hashlib,subprocess,sys
import numpy as np
OUT=Path('work/processed');DEST=Path('outputs/game-art-library')
with gzip.open(DEST/'assets.json.gz','rt') as f:rows=json.load(f)
qa=json.loads((DEST/'quality-report.json').read_text());manifest=json.loads((DEST/'bundle-manifest.json').read_text())
assert len(rows)==qa['active_image_entries']
assert len(rows)+qa['excluded_entries']==qa['inspected_source_entries']
ids={r['asset_id'] for r in rows};unique={r['sha256']:r for r in rows}
sources={}
for r in json.loads((OUT/'source-rows.json').read_text()):sources.setdefault(r['sha256'],r['source_path'])
assert len(ids)==len(rows)
assert len(unique)==qa['unique_verified_previews']
hashes=json.loads((OUT/'embedding-hashes.json').read_text());positions={s:i for i,s in enumerate(hashes)}
vectors=np.load(OUT/'image-embeddings.npy',mmap_mode='r');valid=np.load(OUT/'image-embedding-valid.npy',mmap_mode='r')
tags={json.loads(line)['sha256'] for line in (OUT/'visual-tags.jsonl').read_text().splitlines()}
indexes=np.asarray([positions[s] for s in unique]);norms=np.linalg.norm(vectors[indexes].astype(np.float32),axis=1)
assert np.all(valid[indexes]==1) and np.all(np.abs(norms-1)<.01)
assert set(unique)==tags
members={}
for b in manifest['bundles']:
 with zipfile.ZipFile(DEST/'bundles'/b['name']) as z:members[b['name']]=set(z.namelist())
for r in rows:
 assert r['conversion_status']=='converted' and r['preview_status']=='decode-verified' and r['active_library']
 assert r['duplicate_asset_id'] is None or r['duplicate_asset_id'] in ids
 assert r['normalized_file'] in members[r['normalized_bundle']['name']]
 if r.get('animation_frames'):
  assert len(r['animation_frames'])==r['frame_count']==len(r['animation_durations_ms'])
  assert set(r['animation_frames']).issubset(members[r['normalized_bundle']['name']])
 assert (DEST/r['preview']['atlas']).is_file()
for r in unique.values():
 assert hashlib.sha256(Path(sources[r['sha256']]).read_bytes()).hexdigest()==r['sha256']
 p=OUT/r['normalized_file']
 assert p.stat().st_size==r['normalized_bytes']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['normalized_sha256']
db=sqlite3.connect(DEST/'search.sqlite');assert db.execute('SELECT count(*) FROM assets').fetchone()[0]==len(rows);assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';db.close()
for query in ['sheep','arrow','flower']:
 result=subprocess.run([sys.executable,str(DEST/'search.py'),query,'--index',str(DEST/'search.sqlite'),'--limit','3'],capture_output=True,text=True,check=True)
 assert json.loads(result.stdout),query
sample=next(iter(unique.values()))
subprocess.run([sys.executable,str(DEST/'search.py'),'--index',str(DEST/'search.sqlite'),'--id',sample['asset_id'],'--bundles',str(DEST/'bundles'),'--extract-to','work/import-check'],check=True,stdout=subprocess.DEVNULL)
assert hashlib.sha256((Path('work/import-check')/sample['normalized_file']).read_bytes()).hexdigest()==sample['normalized_sha256']
report={'passed':True,'active_entries':len(rows),'unique_readable_images':len(unique),'removed_entries':qa['excluded_entries'],'all_active_vectors_verified':True,'all_source_hashes_verified':True,'all_normalized_hashes_verified':True,'all_bundle_membership_verified':True,'sqlite_integrity':'ok','keyword_queries':['sheep','arrow','flower'],'asset_extraction_verified':True}
(DEST/'verification-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
