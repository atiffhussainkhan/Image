"""Detect real image content behind unsupported extensions before excluding files."""
from PIL import Image
from pathlib import Path
import json,subprocess
from convert import OUT,unique,convert
formats={'PNG':'png','JPEG':'jpg','GIF':'gif','TIFF':'tif','BMP':'bmp','PCX':'pcx','WEBP':'webp','EPS':'eps','WMF':'wmf'}
detected=[]
for sha,row in unique.items():
 p=OUT/'status'/(sha+'.json');s=json.loads(p.read_text())
 if s['conversion_status']!='unsupported':continue
 try:
  with Image.open(row['source_path']) as im:fmt=formats.get(im.format)
 except Exception:continue
 if not fmt:continue
 if fmt=='wmf':
  src=OUT/'wmf-input'/(sha+'.wmf')
  if not src.exists():src.symlink_to(Path(row['source_path']).resolve())
  profile=Path('work/recover-wmf-profile').resolve()
  try:subprocess.run(['soffice','-env:UserInstallation='+profile.as_uri(),'--headless','--convert-to','png:draw_png_Export','--outdir',str((OUT/'wmf-render').resolve()),str(src.absolute())],capture_output=True,timeout=60)
  except subprocess.TimeoutExpired:pass
  if not (OUT/'wmf-render'/(sha+'.png')).exists():
   s.update(conversion_status='failed',reason='WMF content detected behind a mislabeled extension, but the importer produced no readable image',detected_source_format=fmt);p.write_text(json.dumps(s));continue
 p.unlink();result=convert({**row,'format':fmt});result.update(original_format=row['format'],detected_source_format=fmt);p.write_text(json.dumps(result));detected.append({'original_path':row['original_path'],'actual_format':fmt,'result':result['conversion_status']})
print(json.dumps({'mislabeled_images':detected}),flush=True)
