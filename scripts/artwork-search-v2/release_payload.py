"""Package portable viewers, search data and offline semantic search resources."""
from pathlib import Path
import zipfile,json,hashlib,shutil
DEST=Path('outputs/game-art-library');B=DEST/'bundles';MODEL=Path('work/model');OUT=Path('work/processed')
files={}
for name in ['text_model_quantized.onnx','vision_model_quantized.onnx','tokenizer.json','preprocessor_config.json','LICENSE-CLIP.txt']:
 p=MODEL/name;files[name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
provenance={'model':'Xenova/clip-vit-base-patch32','revision':'d15189d7028b43f1d3e65039190477f6af591c2a','source':'https://huggingface.co/Xenova/clip-vit-base-patch32/tree/d15189d7028b43f1d3e65039190477f6af591c2a','upstream':'https://github.com/openai/CLIP','licence_source':'https://github.com/openai/CLIP/blob/main/LICENSE','files':files,'processing':'ONNX quantized image/text encoders; 224px image padded on matte; normalized cosine vectors; suggested labels, not verified descriptions'}
(DEST/'model-provenance.json').write_text(json.dumps(provenance,indent=2));shutil.copy2(MODEL/'LICENSE-CLIP.txt',DEST/'LICENSE-CLIP.txt')
def make(name,pairs):
 p=B/name
 with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=4,allowZip64=True) as z:
  for source,target in pairs:z.write(source,target)
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 return {'name':name,'bytes':p.stat().st_size,'sha256':digest,'download_url':'https://github.com/atiffhussainkhan/Image/releases/download/game-art-search-v2-2026-10-05/'+name}
common=[(DEST/n,n) for n in ['README.md','quality-report.json','removed-entries.csv','verification-report.json','bundle-manifest.json','model-provenance.json']]
gallery=common+[(DEST/'index.html','index.html'),(DEST/'search-manifest.json','search-manifest.json')]+[(p,p.name) for p in sorted(DEST.glob('search-*.json.gz'))]+[(p,'previews/'+p.name) for p in sorted((DEST/'previews').glob('*.webp'))]
search=common+[(DEST/n,n) for n in ['assets.json.gz','assets.jsonl.gz','assets.csv','search.sqlite','search.py']]
semantic=[(DEST/n,n) for n in ['README.md','model-provenance.json','LICENSE-CLIP.txt']]+[(OUT/n,'vectors/'+n) for n in ['image-embeddings.npy','embedding-hashes.json']]+[(MODEL/n,'models/'+n) for n in ['text_model_quantized.onnx','tokenizer.json']]
metadata=[make('game-art-gallery.zip',gallery),make('game-art-search-data.zip',search),make('game-art-semantic-search.zip',semantic)]
(DEST/'search-bundle-manifest.json').write_text(json.dumps({'bundles':metadata},indent=2))
print(json.dumps(metadata),flush=True)
