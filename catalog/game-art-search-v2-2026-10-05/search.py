#!/usr/bin/env python3
"""Search cleaned image records from any engine or tool using ordinary JSON output."""
import argparse,sqlite3,json,re,zipfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('query',nargs='?',default='');p.add_argument('--index',type=Path,default=Path(__file__).resolve().parent/'search.sqlite');p.add_argument('--limit',type=int,default=20);p.add_argument('--pack');p.add_argument('--id');p.add_argument('--semantic',action='store_true');p.add_argument('--models',type=Path);p.add_argument('--vectors',type=Path);p.add_argument('--bundles',type=Path);p.add_argument('--extract-to',type=Path);a=p.parse_args()
con=sqlite3.connect(a.index)
if a.id:
 row=con.execute('SELECT record_json FROM assets WHERE id=?',(a.id,)).fetchone()
 if row and a.extract_to:
  if not a.bundles:p.error('--extract-to requires --bundles and --id')
  record=json.loads(row[0]);bundle=record['normalized_bundle']['name'];names=[record['normalized_file']]+record.get('animation_frames',[])
  if Path(bundle).name!=bundle or Path(bundle).is_absolute():raise ValueError('Unsafe bundle name')
  with zipfile.ZipFile(a.bundles/bundle) as z:
   for name in names:
    target=(a.extract_to/name).resolve()
    if not target.is_relative_to(a.extract_to.resolve()):raise ValueError('Unsafe image path')
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(name))
 print(row[0] if row else 'null');raise SystemExit(0 if row else 1)
if a.semantic:
 import numpy as np,onnxruntime as ort
 from tokenizers import Tokenizer
 if not a.models or not a.vectors:p.error('--semantic requires --models and --vectors')
 tok=Tokenizer.from_file(str(a.models/'tokenizer.json'));tok.enable_padding(pad_id=49407,length=77);tok.enable_truncation(77)
 ids=np.asarray([tok.encode(a.query).ids],dtype=np.int64)
 opt=ort.SessionOptions();opt.intra_op_num_threads=2
 model=ort.InferenceSession(str(a.models/'text_model_quantized.onnx'),opt,providers=['CPUExecutionProvider']);q=model.run(None,{'input_ids':ids})[0][0];q/=np.linalg.norm(q)
 vectors=np.load(a.vectors/'image-embeddings.npy',mmap_mode='r');hashes=json.loads((a.vectors/'embedding-hashes.json').read_text());active={}
 for (record,) in con.execute('SELECT record_json FROM assets'):
  r=json.loads(record)
  if not a.pack or r['pack']==a.pack:active.setdefault(r['sha256'],r)
 indexes=np.asarray([i for i,s in enumerate(hashes) if s in active]);scores=vectors[indexes].astype(np.float32)@q;top=np.argsort(scores)[-a.limit:][::-1]
 results=[{**active[hashes[int(indexes[i])]],'semantic_similarity':round(float(scores[i]),4)} for i in top]
else:
 terms=re.findall(r'[^\W_]+',a.query,flags=re.UNICODE)
 if not terms:p.error('Provide search words or --id')
 query=' AND '.join('"'+word.replace('"','""')+'"*' for word in terms)
 results=[]
 for (record,) in con.execute('SELECT a.record_json FROM search s JOIN assets a ON a.id=s.id WHERE search MATCH ? ORDER BY bm25(search,0,5,2,1)',(query,)):
  r=json.loads(record)
  if a.pack and r['pack']!=a.pack:continue
  results.append(r)
  if len(results)>=a.limit:break
print(json.dumps(results,ensure_ascii=False,indent=2))
