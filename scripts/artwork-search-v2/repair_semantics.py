"""Merge checkpoints and refresh embeddings for corrected previews after cleanup."""
from pathlib import Path
import json,numpy as np
OUT=Path('work/processed');hashes=json.loads((OUT/'embedding-hashes.json').read_text());position={s:i for i,s in enumerate(hashes)}
valid=np.load(OUT/'image-embedding-valid.npy',mmap_mode='r+');vectors=np.load(OUT/'image-embeddings.npy',mmap_mode='r+')
tags={}
for p in [OUT/'visual-tags.jsonl']+sorted(OUT.glob('visual-tags-[0-9].jsonl')):
 if p.exists():
  for line in p.read_text().splitlines():
   try:r=json.loads(line);tags[r['sha256']]=r
   except json.JSONDecodeError:pass
active=set();reset=[]
for p in (OUT/'status').glob('*.json'):
 s=json.loads(p.read_text());i=position[p.stem]
 if s.get('active_library'):
  active.add(p.stem)
  if s.get('requires_reanalysis') or p.stem not in tags:
   valid[i]=0;tags.pop(p.stem,None);reset.append(p.stem);s.pop('requires_reanalysis',None);p.write_text(json.dumps(s))
 else:valid[i]=0;vectors[i]=0;tags.pop(p.stem,None)
valid.flush();vectors.flush()
with (OUT/'visual-tags.jsonl').open('w') as f:
 for s in sorted(tags):f.write(json.dumps(tags[s])+'\n')
print(json.dumps({'active_unique_images':len(active),'refresh_embeddings':len(reset),'removed_vector_rows':len(hashes)-len(active)}),flush=True)
