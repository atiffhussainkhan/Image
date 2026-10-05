"""Install the verified cleaned catalog and mark historical search as superseded."""
from pathlib import Path
import json,shutil
ROOT=Path('work/Image');DEST=Path('outputs/game-art-library');TAG='game-art-search-v2-2026-10-05';CAT=ROOT/'catalog'/TAG;CAT.mkdir(parents=True,exist_ok=True)
assert json.loads((DEST/'verification-report.json').read_text())['passed']
names=['README.md','index.html','assets.json.gz','assets.jsonl.gz','search.py','search-manifest.json','quality-report.json','removed-entries.csv','bundle-manifest.json','search-bundle-manifest.json','model-provenance.json','verification-report.json','preview-review.jpg','LICENSE-CLIP.txt']
for name in names:shutil.copy2(DEST/name,CAT/name)
for p in DEST.glob('search-*.json.gz'):shutil.copy2(p,CAT/p.name)
shutil.copytree(DEST/'previews',CAT/'previews',dirs_exist_ok=True)
(CAT/'.gitattributes').write_text('*.jpg -filter -diff -merge -text\n')
active={'schema_version':2,'release_tag':TAG,'release_url':'https://github.com/atiffhussainkhan/Image/releases/tag/'+TAG,'index':'catalog/'+TAG+'/assets.jsonl.gz','gallery':'catalog/'+TAG+'/index.html','status':'cleaned-active-library','license_status':'unverified','historical_release':'workplace-art-unverified-2026-10-05','removed_entries_report':'catalog/'+TAG+'/quality-report.json','engine_formats':['png','jpg']}
(ROOT/'catalog/user-artwork-active-library.json').write_text(json.dumps(active,indent=2))
manifest_path=ROOT/'catalog/repository_manifest.json';repository_manifest=json.loads(manifest_path.read_text());repository_manifest['user_artwork_active_library']=active;manifest_path.write_text(json.dumps(repository_manifest,indent=2))
for name in ['README.md','AI_ASSET_INDEX.md','STORAGE_STATUS.md','CRAWLER_ENTRYPOINT.md']:
 p=ROOT/name;s=p.read_text();s+='\n## Active cleaned artwork library\n\nThe [cleaned search gallery](catalog/'+TAG+'/README.md) is the active index for the four user-supplied archives. Unreadable, empty and unconvertible sources are excluded from its searchable records and cleaned PNG/JPEG packs. Use `catalog/user-artwork-active-library.json` for machine discovery. JSON/JSONL, SQLite, CSV and natural-language search are available in the [cleaned release]('+active['release_url']+'). Original archives remain historical backups; licences remain unverified.\n';p.write_text(s)
old=ROOT/'catalog/workplace-art-unverified-2026-10-05'
p=old/'README.md';p.write_text('> **Superseded for active image search:** use [the cleaned library](../'+TAG+'/README.md). This folder remains the historical source audit, including entries removed from the active library.\n\n'+p.read_text())
(old/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=../'+TAG+'/index.html"><title>Cleaned artwork library</title><p>The historical inventory has been superseded. <a href="../'+TAG+'/index.html">Open the cleaned image search gallery.</a></p></html>\n')
print('Installed verified cleaned catalogue; historical viewer points to active library.',flush=True)
