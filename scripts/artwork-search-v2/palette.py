"""Index visible palette colours as pixel estimates, not claims about object identity."""
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import colorsys,json,collections,time
OUT=Path('work/processed')
def colour(rgb):
 h,s,v=colorsys.rgb_to_hsv(*(c/255 for c in rgb));h*=360
 if v<.16:return 'black'
 if s<.14:return 'white' if v>.91 else 'gray'
 if h<20 or h>=345:return 'pink' if v>.75 and s<.45 else 'red'
 if h<48:return 'brown' if v<.72 or s<.42 else 'orange'
 if h<72:return 'yellow'
 if h<168:return 'green'
 if h<205:return 'cyan'
 if h<258:return 'blue'
 if h<300:return 'purple'
 return 'pink'
def analyse(path):
 s=json.loads(path.read_text())
 if not s.get('active_library'):return False
 with Image.open(OUT/'thumbs'/(path.stem+'.webp')) as im:
  im=im.convert('RGB').resize((64,64));q=im.quantize(colors=12);palette=q.getpalette();counts=collections.Counter()
  for n,index in q.getcolors():counts[colour(palette[index*3:index*3+3])]+=n
 if s.get('white_alpha_artwork'):counts=collections.Counter({'white':4096})
 # White matte is not a foreground colour. Other colours come from visible pixels.
 values=[(c,n) for c,n in counts.most_common() if c!='white' and n>=24]
 if not values:values=counts.most_common(1)
 total=sum(n for c,n in values)
 s['palette_colors']=[c for c,n in values[:4]]
 s['palette_estimates']=[{'color':c,'pixel_share':round(n/max(1,total),3)} for c,n in values[:4]]
 s['palette_method']='12-colour quantized 64px preview; white matte excluded; visible-pixel estimate'
 path.write_text(json.dumps(s));return True
if __name__=='__main__':
 files=list((OUT/'status').glob('*.json'));n=0;started=time.time()
 with ThreadPoolExecutor(max_workers=6) as pool:
  for start in range(0,len(files),1000):
   n+=sum(pool.map(analyse,files[start:start+1000]))
   if start%10000==0:print(json.dumps({'palettes_indexed':n,'elapsed_seconds':round(time.time()-started)}),flush=True)
 print('Palette analysis complete:',n,flush=True)
