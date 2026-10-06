from pathlib import Path
import json,gzip,collections,csv,zipfile,io,hashlib,urllib.parse
OUT=Path('outputs/repository-audit');content=json.loads((OUT/'content-audit.json').read_text());supp=json.loads((OUT/'supplemental-format-audit.json').read_text());editor=json.loads((OUT/'editor-source-audit.json').read_text());remote=json.loads((OUT/'remote-completeness-audit.json').read_text());cross=json.loads((OUT/'index-content-crosscheck.json').read_text());previews=json.loads((OUT/'preview-tile-audit.json').read_text());masters=json.loads((OUT/'clean-master-image-audit.json').read_text());animation=json.loads((OUT/'animation-frame-audit.json').read_text());qa=json.loads(Path('outputs/game-art-library/quality-report.json').read_text())
rows=[]
with gzip.open(OUT/'file-audit.jsonl.gz','rt')as f:
 for l in f:rows.append(json.loads(l))
by_key={(r['collection'],r['path']):r for r in rows};sidecars=[r for r in rows if '__MACOSX' in Path(r['path']).parts or Path(r['path']).name.startswith('._') or Path(r['path']).name in ('.DS_Store','Thumbs.db')]
resolved=[]
for r in supp['results']:
 if r.get('classification'):
  resolved.append({'collection':r['collection'],'path':r['path'],'status':'exclude-filesystem-metadata','reason':'Valid AppleDouble resource-fork data; not a game image','sha256':r['sha256']})
for r in editor['results']:
 if not r['passed']:
  assert '/__MACOSX/._' in r['path'],r
  with zipfile.ZipFile(r['collection'])as z:data=z.read(r['path'])
  assert data[:4]==b'\x00\x05\x16\x07',r
  resolved.append({'collection':r['collection'],'path':r['path'],'status':'exclude-filesystem-metadata','reason':'AppleDouble resource fork; not Illustrator artwork','sha256':hashlib.sha256(data).hexdigest()})
assert len(resolved)==78
# Every remaining decoder exception has a successful secondary result.
results={(r['collection'],r['path']):r for r in supp['results']}
for r in content['issues']:
 if r['status']=='failed':assert results[(r['collection'],r['path'])]['passed'] or '/__MACOSX/._' in r['path']
real_retry=sum(r['previous_status']=='failed' and r['passed'] and not r.get('classification')for r in supp['results'])
missing=remote['catalog_only_missing_packs'];no_viewport=[r for r in supp['results']if r.get('svg_missing_explicit_viewport')];empty_svg=[r for r in supp['results']if r.get('render_has_visible_pixels')==False]
assert len(empty_svg)==1
summary={'date':'2026-10-06','repositories':remote['repositories'],'file_occurrences_inspected':len(rows),'zip_archives_inspected_including_nested':len(content['packs']),'github_release_files_integrity_verified':54,'cleaned_library':{**masters,**cross,'preview_tiles_checked':previews['occupied_tiles_checked'],'uniform_preview_tiles':len(previews['uniform_tiles']),'very_low_contrast_preview_tiles':len(previews['low_contrast_tiles']),'exclusions':qa['excluded_entries'],'unique_unreadable_or_empty_master_images':0,'intentional_blank_timing_frames':6},'animation_repository':{'sprite_sheets':animation['sheets'],'frames_checked':animation['declared_frames'],'passed':animation['passed']},'secondary_decoder_recoveries':real_retry,'editor_sources_checked':editor['files_checked'],'aseprite_sources_checked':sum(r['format']=='.aseprite'for r in editor['results']),'illustrator_artwork_rendered':sum(r['format']=='.ai' and r['passed']for r in editor['results']),'macos_sidecar_file_occurrences':len(sidecars),'png_named_sidecars_are_metadata':4,'sidecar_headers_verified':78,'all_secondary_renderer_inputs_sha256_verified':True,'empty_nonimage_marker_files':2,'uniform_raster_file_occurrences':content['counts']['image-uniform'],'fully_transparent_raster_file_occurrences':content['counts']['image-fully-transparent'],'svg_files_without_explicit_viewport':len(no_viewport),'default_empty_svg_repaired':1,'preview_extension_mismatches_corrected':4,'catalog_size_mismatch_corrected':1,'unavailable_catalogued_packs':missing,'verdict':'Cleaned master images and animation repository pass exhaustive technical checks. The complete repositories are not image-only or universally engine-ready: source backups, non-image game data, sidecars, blank timing/font/texture files, conditional vectors and unstored catalogue entries remain explicitly distinguished.','human_review':'Representative previews and corrected artwork inspected; no claim of manually viewing all 408,439 file occurrences.','limitations':['Original archives retain excluded/unconvertible sources as backups.','Models/audio/editor files passed byte/hash/ZIP integrity; universal gameplay-engine import was not certified.','Uniform/transparent files may be intentional material textures, font spaces, spritesheet padding or animation timing frames; contextual flags do not declare corruption.','SVGs lacking explicit viewport geometry require an appropriate importer or canvas repair.','Third-party licences for user-supplied artwork remain unverified.']}
assert summary['cleaned_library']['unique_master_images']==110490 and not previews['uniform_tiles'] and not previews['low_contrast_tiles']
(OUT/'audit-summary.json').write_text(json.dumps(summary,indent=2))
policy={'preferred_active_index':'catalog/game-art-search-v2-2026-10-05/assets.jsonl.gz','rule':'Select standalone art from the verified active index. Availability of an older archive does not certify every member as a direct engine image.','ignore_metadata_patterns':['**/__MACOSX/**','**/._*','**/.DS_Store','**/Thumbs.db','.nojekyll','.gitkeep'],'require_contextual_review':['fully-transparent standalone images','uniform images unless deliberate material/texture/timing data','SVG without width/height or viewBox','non-image binary and editor formats requiring their importer'],'format_overrides':'format-overrides.json','file_audit':'file-audit.jsonl.gz','unavailable_catalogued_packs':[r['id']for r in missing]}
(OUT/'safe-import-policy.json').write_text(json.dumps(policy,indent=2));(OUT/'resolved-sidecar-exclusions.json').write_text(json.dumps(resolved,indent=2))
with (OUT/'issues.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=['collection','path','status','reason','sha256']);w.writeheader()
 for r in content['issues']:
  status=r['status'];reason=r.get('error','')
  if status=='failed':
   s=results[(r['collection'],r['path'])]
   if s.get('classification') or '/__MACOSX/._'in r['path']:status='exclude-sidecar';reason='Filesystem sidecar; not game artwork'
   else:status='secondary-decoder-pass';reason='Decoded with ImageMagick instead of Pillow'
  elif status=='empty-file':status='expected-empty-marker';reason='Website/package marker, not an image'
  else:reason='Context review: possible texture/font-space/timing/padding; not automatically corruption'
  w.writerow({'collection':r['collection'],'path':r['path'],'status':status,'reason':reason,'sha256':r.get('sha256','')})
with (OUT/'conditional-vectors.csv').open('w',newline='')as f:
 w=csv.writer(f);w.writerow(['collection','path','sha256','issue'])
 for r in no_viewport:w.writerow([r['collection'],r['path'],r['sha256'],'No explicit SVG canvas/viewBox; verify importer bounds. One gameCharacter.svg has a corrected override.'])
with (OUT/'archives.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=['collection','files','uncompressed_bytes','failures']);w.writeheader()
 for r in content['packs']:w.writerow({k:r.get(k,0)for k in w.fieldnames})
release_rows=[]
for release in json.loads(Path('work/image-release-inventory.json').read_text()):
 for a in release['assets']:release_rows.append({'release':release['tag_name'],'file':a['name'],'bytes':a['size'],'sha256':a['digest'].removeprefix('sha256:'),'integrity_verified':True,'download_url':'https://github.com/atiffhussainkhan/Image/releases/download/'+release['tag_name']+'/'+urllib.parse.quote(a['name'])})
assert len(release_rows)==54
(OUT/'release-files-audit.json').write_text(json.dumps(release_rows,indent=2))
repository_lines='\n'.join(f"| [{r['repository']}](https://github.com/{r['repository']}) | {r['tracked_files']:,} | `{r['commit']}` | Every tracked blob matched GitHub |"for r in remote['repositories'])
missing_lines='\n'.join('- `'+r['id']+'`: '+r['reason']for r in missing)
notes=f'''# Complete repository image audit — 6 October 2026

**The cleaned image library and the animation repository pass exhaustive technical checks. I cannot label the entire repositories “100% usable images”: they also contain original source backups, models, audio, editor files, filesystem metadata, deliberate blank/solid files and catalogue entries without stored downloads.** Binary data is normal for PNG, JPEG, WebP and game models; decoding and content checks establish whether an image is valid.

## Scope and evidence

| Repository | Tracked files checked | Audited commit | Result |
|---|---:|---|---|
{repository_lines}

- **54 GitHub release files** verified for size and SHA-256, covering every file in all five Image releases. Four original archive hashes and their earlier complete source audit were reused; original unusable sources remain documented in the exclusion ledger.
- **104 ZIP archives**, including every nested ZIP, completely read. Every member was checked by the ZIP CRC decoder; **408,439 file occurrences** inspected, including repeated packs, metadata and previews. No archive-member CRC failure was found.
- Raster headers, dimensions, full pixel decoding and animation frames checked. SVG XML plus actual rendering checked. PSD/HDR warnings retried with the appropriate renderer. Aseprite header/frame/chunk/cel data checked against the [official format specification](https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md).
- All 1,954 tracked Git blobs matched the audited GitHub commits. Metadata corrections and new override files described below were subsequently prepared separately and verified.

## Cleaned artwork — pass

| Check | Full coverage | Result |
|---|---:|---|
| Unique PNG/JPEG master images | **110,490** | Every image decoded; none empty, fully transparent or uniform |
| Search records | **114,852** | Every record matched the actual ZIP bytes, size and member path |
| Additional animation frame files | **4,312** | Every frame matched its stored bytes; six blank/solid timing frames intentionally preserved |
| Occupied preview tiles | **110,490** | Every tile inspected; zero uniform or extremely low-contrast tiles |
| Preview atlases | **1,760** | All decoded and dimensions checked |
| Search shards | All | IDs exactly cover the active index |
| SQLite / semantic vectors | All active entries | Database integrity, vector coverage/norms and extraction checks passed |

**2,195 unusable, unconvertible or non-image entries are excluded** from the active searchable library and cleaned packs. The original archives remain historical backups; their presence does not mean every original member is a usable image. See the [existing removal report](https://github.com/atiffhussainkhan/Image/blob/main/catalog/game-art-search-v2-2026-10-05/quality-report.json).

## Animation repository — pass

All **12 WebP sheets and 132 declared animation frames** decoded and contained visible artwork. Manifest dimensions, byte counts, frame counts, frame rates and grid positions matched. Unused grid cells are expected padding, not missing declared frames.

## Findings and corrections

1. **Four `.png` previews contained JPEG data.** Proper PNG replacements were created; decoded pixels are identical. Use [format-overrides.json](format-overrides.json).
2. **One SVG rendered empty because it lacked a canvas.** All six drawing shapes were measured in the browser; explicit bounds with a 5% margin were added. The [corrected SVG](corrected-previews/gameCharacter.svg) and [engine PNG](corrected-previews/gameCharacter.png) render nonempty, complete artwork without changing the drawing geometry.
3. **109 filesystem sidecar occurrences** are excluded from image selection. The four PNG-named sidecars and four apparent Illustrator failures are valid AppleDouble resource-fork data, not artwork. All 78 image/editor-named sidecars were identified by their metadata headers.
4. **{real_retry} raster warnings** were decoder limitations and passed secondary decoding. All **715 Aseprite sources** passed structural/cel checks; all **28 actual Illustrator sources** rendered. Metadata sidecars are excluded from those artwork counts.
5. **One catalogue size was wrong by one byte.** `opengameart-modular-vector-characters.zip` is 71,527,593 bytes. The storage record and both master indexes were corrected.
6. **{len(no_viewport):,} SVG occurrences lack explicit canvas dimensions or `viewBox`.** Their vector data is present, but reliable direct import depends on the importer or repaired bounds. One empty default render was corrected; the other entries remain flagged in [conditional-vectors.csv](conditional-vectors.csv).
7. **392 fully transparent and 858 uniform raster occurrences** were found in source/older packs, including four transparent and two solid cleaned-animation timing frames. These files decoded; some are font spaces, neutral textures or padding. They require context and must not be selected automatically as standalone artwork. No such file is a cleaned master-image entry.
8. The two zero-byte files are `.nojekyll` and `.gitkeep`, expected package/website markers—not images.

## Catalogue entries with no stored archive

These eight records are explicitly unavailable; a source link is not a repository-owned asset:

{missing_lines}

No replacement asset or invented file was inserted to conceal a missing download. The original Dungeon entry is separate from the stored Dungeon Remastered pack.

## What this verifies—and its limits

Use the [cleaned active library](https://github.com/atiffhussainkhan/Image/releases/tag/game-art-search-v2-2026-10-05), the animation pack, the corrected overrides and [safe-import-policy.json](safe-import-policy.json) for future asset selection. Original/older packs remain source archives; metadata, blank contextual files and conditional vectors are not certified standalone engine art.

The audit checked every stored file in scope automatically. Representative previews and the repaired character were inspected visually; this is **not** a claim of manually viewing 408,439 files. Model/audio/editor binaries passed byte/hash/archive integrity, but every gameplay-engine importer was not executed. User-supplied artwork licences remain unverified; technical readability does not establish redistribution rights.

## Downloadable detailed evidence

- [Machine-readable final summary](audit-summary.json)
- [Every inspected file, status, dimensions and SHA-256 — compressed JSONL](file-audit.jsonl.gz)
- [Every archive and member count](archives.csv)
- [Every release file and verified checksum](release-files-audit.json)
- [Contextual issues and resolved decoder warnings](issues.csv)
- [Cleaned master-image checks](clean-master-image-audit.json), [index/ZIP crosschecks](index-content-crosscheck.json), [all preview tiles](preview-tile-audit.json)
- [All animation frames](animation-frame-audit.json), [secondary render checks](supplemental-format-audit.json), [editor-source checks](editor-source-audit.json)
- [Format corrections](format-overrides.json), [excluded sidecars](resolved-sidecar-exclusions.json), [conditional vectors](conditional-vectors.csv)
'''
(OUT/'REPORT.md').write_text(notes)
print(json.dumps({'file_occurrences':len(rows),'archives':len(content['packs']),'real_retry':real_retry,'sidecars':len(sidecars),'summary':'written','report':'written'}),flush=True)
