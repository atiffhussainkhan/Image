from pathlib import Path
import json,gzip,collections
OUT=Path('outputs/repository-audit');path=OUT/'file-audit.jsonl.gz';supp=json.loads((OUT/'supplemental-format-audit.json').read_text());editor=json.loads((OUT/'editor-source-audit.json').read_text());overrides=json.loads((OUT/'format-overrides.json').read_text())
render={(r['collection'],r['path']):r for r in supp['results']};ed={(r['collection'],r['path']):r for r in editor['results']};corrected={(r['archive'],r['original_path']):r for r in overrides['overrides']}
counts=collections.Counter();temp=OUT/'resolved-file-audit.jsonl.gz'
with gzip.open(path,'rt')as src,gzip.open(temp,'wt')as dest:
 for line in src:
  r=json.loads(line);initial=r['status'];r['initial_status']=initial;r['native_gameplay_engine_import_tested']=False
  key=(r['collection'],r['path']);s=render.get(key);e=ed.get(key);base=Path(r['path']).name
  if '__MACOSX'in Path(r['path']).parts or base.startswith('._') or base in ('.DS_Store','Thumbs.db'):
   r['validation_status']='excluded-filesystem-metadata';r['standalone_image_selection']='exclude'
  elif initial=='empty-file':r['validation_status']='expected-empty-nonimage-marker';r['standalone_image_selection']='exclude'
  elif initial in ('image-uniform','image-fully-transparent'):
   r['validation_status']='decoded-contextual-review';r['standalone_image_selection']='review';r['context']='May be a deliberate texture, font space, animation timing or padding'
  elif s and s.get('passed'):
   r['validation_status']='alternate-renderer-pass';r['decoder']=s.get('decoder');r['render_has_visible_pixels']=s.get('render_has_visible_pixels');r['standalone_image_selection']='allow-if-appropriate-format'
   if s.get('svg_missing_explicit_viewport'):r['validation_status']='valid-vector-requires-viewport-review';r['standalone_image_selection']='review'
  elif e and e.get('passed'):
   r['validation_status']='editor-source-data-pass';r['editor_check']=e['check'];r['standalone_image_selection']='requires-editor-export'
  elif initial=='image-pass':r['validation_status']='image-decode-and-content-pass';r['standalone_image_selection']='allow'
  else:r['validation_status']=initial;r['standalone_image_selection']='not-a-verified-standalone-image'
  archive=Path(r['collection'].split('::')[0]).name;correction=corrected.get((archive,r['path']))
  if correction:r['validation_status']='use-corrected-override';r['corrected_file']=correction['corrected_file'];r['standalone_image_selection']='use-override'
  counts[r['validation_status']]+=1;dest.write(json.dumps(r,ensure_ascii=False)+'\n')
path.rename('work/full-audit/initial-file-audit.jsonl.gz');temp.rename(path)
summary=json.loads((OUT/'audit-summary.json').read_text());summary['resolved_validation_counts']=dict(counts);summary['file_ledger_includes_resolved_verdicts']=True;(OUT/'audit-summary.json').write_text(json.dumps(summary,indent=2))
policy=json.loads((OUT/'safe-import-policy.json').read_text());policy['file_status_field']='validation_status (initial_status preserves the first decoder result)';policy['supplemental_renderer_evidence']='supplemental-format-audit.json';(OUT/'safe-import-policy.json').write_text(json.dumps(policy,indent=2))
manifest=OUT/'format-overrides.json';o=json.loads(manifest.read_text());o['rule']='Use the corrected file or its engine PNG for these members. Original source archives remain unchanged.';manifest.write_text(json.dumps(o,indent=2))
print(json.dumps({'resolved_records':sum(counts.values()),'counts':dict(counts)}),flush=True)
