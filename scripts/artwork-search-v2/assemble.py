"""Publish a cross-engine index, SQLite FTS search, previews and integrity report."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,gzip,hashlib,collections,csv,sqlite3,re,shutil,random
OUT=Path('work/processed');DEST=Path('outputs/game-art-library');DEST.mkdir(exist_ok=True,parents=True)
rows=json.loads((OUT/'source-rows.json').read_text());hashes=json.loads((OUT/'embedding-hashes.json').read_text());position={s:i for i,s in enumerate(hashes)}
aliases=collections.defaultdict(list)
for r in rows:aliases[r['sha256']].append(r)
states={p.stem:json.loads(p.read_text()) for p in (OUT/'status').glob('*.json')}
visual={}
bundles=json.loads((OUT/'bundle-map.json').read_text())
for line in (OUT/'visual-tags.jsonl').read_text().splitlines():
 r=json.loads(line);visual[r['sha256']]=r
counts=collections.Counter();records=[];slim=[];excluded=[]
synonyms={'dog':['canine','puppy','hound'],'cat':['feline','kitten'],'horse':['equine','pony'],'bird':['avian'],'car':['automobile','vehicle'],'truck':['lorry','vehicle'],'airplane':['aeroplane','aircraft','vehicle'],'boat':['watercraft','ship'],'flower':['floral','plant'],'tree':['plant','vegetation'],'leaf':['leaves','foliage','plant'],'arrow':['pointer','direction','navigation'],'gear':['cog','settings'],'sword':['weapon','blade'],'shield':['armour','armor'],'coin':['money','currency','gold'],'computer':['pc','desktop','technology'],'folder':['directory','files'],'basketball':['sport','ball'],'football':['sport','ball'],'skull':['skeleton','bone'],'star':['shape','space'],'frame':['border','decoration'],'border':['frame','decoration'],'castle':['building','architecture'],'house':['building','architecture'],'landscape':['environment','scenery'],'Christmas':['holiday','winter'],'pumpkin':['Halloween','vegetable'],'dragon':['creature','fantasy'],'wizard':['mage','magic','fantasy'],'chair':['furniture'],'table':['furniture'],'map':['navigation'],'photo':['photograph','reference']}
for original in rows:
 r={k:v for k,v in original.items() if k!='source_path'};s=states.get(r['sha256'],{'conversion_status':'failed','preview_status':'unavailable','reason':'WMF importer produced no image'})
 r.update(s);v=visual.get(r['sha256'],{});r.update({k:val for k,val in v.items() if k!='sha256'})
 for field in ['reason','initial_failure']:
  if r.get(field):r[field]=r[field].replace(original['source_path'],original['original_path']).replace(str(Path.cwd())+'/', '{workspace}/')
 r.pop('requires_reanalysis',None)
 r.pop('thumbnail_file',None)
 r['source_readiness']=r.get('readiness');r['readiness']='engine-readable-rights-unverified' if s.get('active_library') else 'excluded'
 stem=Path(r['original_path']).stem;meaningful=re.sub(r'[_-]+',' ',stem).strip()
 numeric=not re.search('[a-zA-Z]{3}',meaningful) or bool(re.fullmatch(r'[a-z]{0,2}\d+',meaningful,re.I))
 candidates=[x['label'] for x in v.get('visual_tags',[])]
 r['display_title']=((candidates[0].capitalize()+' · '+stem) if numeric and candidates else meaningful) or r['asset_id']
 r['title_source']='visual-suggestion-plus-original-name' if numeric and candidates else 'original-filename'
 r['engine_format']=Path(s['normalized_file']).suffix.lstrip('.') if s['conversion_status']=='converted' else None
 r['technical_ready']=s['conversion_status']=='converted' and not s.get('needs_visual_review',False)
 r['visual_review_status']='needs-review' if s.get('needs_visual_review') else ('automated-checks-passed' if r['technical_ready'] else 'unavailable')
 alias_text=' '.join(a['original_path']+' '+a.get('category','')+' '+' '.join(a.get('source_keywords',[])) for a in aliases[r['sha256']])
 words=set(re.findall(r'[^\W_]{2,}',(' '.join([r['display_title'],alias_text]+r.get('source_keywords',[])+r.get('tags',[])+candidates+r.get('palette_colors',[]))).lower(),flags=re.UNICODE))
 words-=set(['png','jpg','jpeg','eps','wmf','gif','tif','clipart','part','samples'])
 for term,expansion in synonyms.items():
  if term.lower() in words:words.update(s.lower() for s in expansion)
 if s.get('has_transparent_pixels'):words.add('transparent')
 if 'Icon.Pack' in r['pack']:words.update(['ui','icon','interface'])
 if r['format'] in {'wmf','eps'}:words.update(['vector','illustration'])
 r['search_terms']=sorted(words)
 if s['preview_status']=='decode-verified':
  i=position[r['sha256']];r['preview']={'atlas':'previews/atlas-'+str(i//64).zfill(4)+'.webp','x':(i%8)*128,'y':((i%64)//8)*128,'width':128,'height':128,'atlas_size':1024}
 else:r['preview']=None
 if s['conversion_status']=='converted':
  r['normalized_bundle']=bundles[r['sha256']];r.update(availability='stored',stored_copy=True,release_asset=r['normalized_bundle']['name'],bundle_name=r['normalized_bundle']['name'],bundle_download_url=r['normalized_bundle']['download_url'])
 counts[s['conversion_status']]+=1;counts['preview_'+s['preview_status']]+=1
 if s.get('needs_visual_review'):counts['needs_visual_review']+=1
 if v:counts['visually_analysed_entries']+=1
 if not s.get('active_library',False):
  excluded.append({'asset_id':r['asset_id'],'original_path':r['original_path'],'pack':r['pack'],'format':r['format'],'reason':r.get('reason','Not a usable image')});continue
 records.append(r)
 slim.append({k:r.get(k) for k in ['asset_id','display_title','original_path','pack','category','format','engine_format','normalized_file','normalized_dimensions','has_transparent_pixels','frame_count','animation_frames','animation_durations_ms','animation_loop','poster_frame_index','conversion_status','preview_status','visual_review_status','visual_tags','search_terms','palette_colors','preview','source_archive','license_status','duplicate_asset_id','normalized_bundle']})
with gzip.open(DEST/'assets.json.gz','wt',encoding='utf8',compresslevel=6) as f:json.dump(records,f,ensure_ascii=False,separators=(',',':'))
with gzip.open(DEST/'assets.jsonl.gz','wt',encoding='utf8',compresslevel=6) as f:
 for r in records:f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
fields=['asset_id','display_title','pack','category','original_path','source_archive','source_container','entry_kind','format','engine_format','normalized_file','normalized_dimensions','bundle_name','bundle_download_url','conversion_status','preview_status','visual_review_status','search_terms','visual_tags','palette_colors','sha256','normalized_sha256','duplicate_asset_id','license_status']
with (DEST/'assets.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
 for r in records:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
db=DEST/'search.sqlite';db.unlink(missing_ok=True);con=sqlite3.connect(db)
con.execute('CREATE TABLE assets(id TEXT PRIMARY KEY, record_json TEXT NOT NULL)')
con.execute("CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,title,category,keywords,tokenize='porter unicode61')")
con.executemany('INSERT INTO assets VALUES (?,?)',[(r['asset_id'],json.dumps(r,ensure_ascii=False)) for r in records])
con.executemany('INSERT INTO search VALUES (?,?,?,?)',[(r['asset_id'],r['display_title'],r['category'],' '.join(r['search_terms'])) for r in records]);con.commit();con.close()
previews=DEST/'previews';previews.mkdir(exist_ok=True)
total=(len(hashes)+63)//64;atlas_count=0;verified=0
for n in range(total):
 canvas=Image.new('RGB',(1024,1024),(239,242,246));used=False
 for j,sha in enumerate(hashes[n*64:(n+1)*64]):
  p=OUT/'thumbs'/(sha+'.webp')
  if not p.exists():continue
  with Image.open(p) as im:
   im.load();assert im.size==(224,224);tile=im.convert('RGB').resize((128,128),Image.Resampling.LANCZOS)
  canvas.paste(tile,((j%8)*128,(j//8)*128));verified+=1;used=True
 if used:
  dest=previews/('atlas-'+str(n).zfill(4)+'.webp');canvas.save(dest,'WEBP',quality=86,method=4)
  with Image.open(dest) as check:check.load();assert check.size==(1024,1024)
  atlas_count+=1
 if n%200==0:print('Validated preview atlases',n,'of',total,flush=True)
shards=[]
for n,start in enumerate(range(0,len(slim),2500)):
 name='search-'+str(n).zfill(3)+'.json.gz';shards.append(name)
 with gzip.open(DEST/name,'wt',encoding='utf8',compresslevel=6) as f:json.dump(slim[start:start+2500],f,ensure_ascii=False,separators=(',',':'))
(DEST/'search-manifest.json').write_text(json.dumps({'schema_version':2,'entry_count':len(records),'shards':shards,'preview_tile_size':128,'atlas_size':1024,'license_status':'unverified'}))
# Human review sheet is a reproducible stratified sample; it is not a claim to have viewed every image.
sample=[];rng=random.Random(20261005)
for fmt in ['eps','wmf','png','jpg','gif','tif','wpg']:
 group=[r for r in records if r['format']==fmt and r['preview']]
 sample.extend(rng.sample(group,min(12,len(group))))
sheet=Image.new('RGB',(1200,((len(sample)+7)//8)*174),'#edf1f6');draw=ImageDraw.Draw(sheet)
for i,r in enumerate(sample):
 with Image.open(OUT/'thumbs'/(r['sha256']+'.webp')) as im:im=im.copy();im.thumbnail((140,140))
 x=(i%8)*150;y=(i//8)*174;sheet.paste(im,(x+(150-im.width)//2,y));draw.text((x+5,y+143),r['format']+' '+r['asset_id'][:8],fill='#23324b');draw.text((x+5,y+157),r['display_title'][:19].encode('latin1','replace').decode('latin1'),fill='#23324b')
sheet.save(DEST/'preview-review.jpg',quality=90)
qa={'schema_version':2,'source_files':102393,'inspected_source_entries':len(rows),'active_image_entries':len(records),'excluded_entries':len(excluded),'unique_source_blobs':len(hashes),'embedded_images_in_library':sum(r['entry_kind']=='embedded-image' for r in records),'entry_statuses':dict(counts),'unique_verified_previews':verified,'verified_atlases':atlas_count,'unique_visual_embeddings':len(visual),'machine_suggested_tags':True,'quality_limits':['All generated PNGs and individual thumbnails were fully decoded. All preview atlases were decoded and their dimensions checked.','Empty, uniform, fully transparent, unreadable and unconvertible sources are excluded from the active library and converted bundles.','Human visual review covers a stratified sample, not every image. CLIP labels are suggestions, not verified descriptions.','Legacy DRW/DRT/MGX drawings need an original compatible importer. Empty JPEG files have no recoverable pixels.','Original archival release is a source backup. Its historical inventory is superseded by this cleaned active library. Licence status remains unverified.'],'excluded_sources':excluded}
(DEST/'quality-report.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False))
with (DEST/'removed-entries.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=['asset_id','original_path','pack','format','reason']);w.writeheader();w.writerows(excluded)
(OUT/'assembled-rows.json').write_text(json.dumps(records,ensure_ascii=False,separators=(',',':')))
print(json.dumps({k:v for k,v in qa.items() if k!='excluded_sources'},ensure_ascii=False),flush=True)
