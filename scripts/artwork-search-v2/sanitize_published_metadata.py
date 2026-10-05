"""Remove working-only thumbnail paths; published previews use verified atlases."""
from pathlib import Path
import gzip,json,sqlite3
DEST=Path('outputs/game-art-library')
with gzip.open(DEST/'assets.json.gz','rt') as f:rows=json.load(f)
for r in rows:r.pop('thumbnail_file',None)
with gzip.open(DEST/'assets.json.gz','wt',encoding='utf8',compresslevel=6) as f:json.dump(rows,f,ensure_ascii=False,separators=(',',':'))
with gzip.open(DEST/'assets.jsonl.gz','wt',encoding='utf8',compresslevel=6) as f:
 for r in rows:f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
con=sqlite3.connect(DEST/'search.sqlite');con.execute("UPDATE assets SET record_json=json_remove(record_json,'$.thumbnail_file')");con.commit();con.close()
print('Published preview paths now refer only to atlas files.',flush=True)
