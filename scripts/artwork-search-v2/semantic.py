"""Create CLIP vectors and suggested visual tags for every decodable unique image."""
from pathlib import Path
import json,os,time,re,collections,argparse
import numpy as np,onnxruntime as ort
from PIL import Image
from tokenizers import Tokenizer
parser=argparse.ArgumentParser();parser.add_argument('--shard-index',type=int,default=0);parser.add_argument('--shard-count',type=int,default=1);args=parser.parse_args()
OUT=Path('work/processed');MODEL=Path('work/model')
rows=json.loads((OUT/'source-rows.json').read_text());hashes=sorted(set(r['sha256'] for r in rows));positions={s:i for i,s in enumerate(hashes)}
words='''cat,dog,horse,sheep,cow,pig,chicken,duck,bird,eagle,owl,fish,shark,whale,dolphin,turtle,frog,snake,lizard,crocodile,dragon,dinosaur,tiger,lion,bear,wolf,fox,deer,rabbit,mouse,rat,squirrel,monkey,gorilla,elephant,giraffe,zebra,penguin,seal,octopus,crab,lobster,shrimp,butterfly,bee,ant,spider,beetle,fly,snail,bat,camel,goat,kangaroo,rhinoceros,hippopotamus
man,woman,boy,girl,baby,child,family,person,face,eye,hand,foot,skull,skeleton,ghost,zombie,vampire,witch,wizard,knight,pirate,robot,alien,monster,angel,devil,fairy,mermaid,superhero,clown,snowman,Santa Claus,elf,princess,king,queen,warrior,soldier,police officer,firefighter,doctor,nurse,teacher,chef,farmer,construction worker,scientist,athlete,dancer,musician,artist,office worker,cartoon character
tree,flower,rose,sunflower,tulip,leaf,grass,bush,vine,cactus,mushroom,fruit,apple,banana,orange,grape,pear,peach,cherry,strawberry,pineapple,watermelon,lemon,coconut,pumpkin,carrot,tomato,corn,onion,potato,broccoli,pepper,lettuce
mountain,hill,rock,stone,sand,beach,desert,forest,jungle,river,lake,waterfall,ocean,island,cloud,sun,moon,star,rain,snow,lightning,fire,smoke,ice,water,rainbow,sky,landscape,cityscape,space,planet,galaxy
house,castle,tower,bridge,fence,gate,door,window,roof,stairs,ladder,church,school,hospital,factory,skyscraper,shop,barn,lighthouse,windmill,well,tent,igloo,statue,fountain,road,path,railway,airport,harbour,park,garden,playground
car,truck,bus,taxi,motorcycle,bicycle,scooter,train,tram,airplane,helicopter,rocket,spaceship,boat,ship,sailboat,submarine,tractor,tank,wheel,anchor,traffic light,traffic sign
sword,shield,bow and arrow,axe,spear,gun,bomb,helmet,armour,tool,hammer,wrench,screwdriver,saw,drill,scissors,needle,brush,pencil,pen,ruler,paint palette,paint bucket,watering can,shovel,rake,hoe,broom,magnet,chain,rope,key,lock,gear,compass,map,chest,coin,gem,diamond,crown,trophy,medal,flag,banner,scroll,book,document,envelope,calendar,clock,hourglass
computer,laptop,monitor,keyboard,mouse device,printer,scanner,camera,video camera,telephone,mobile phone,television,radio,speaker,headphones,microphone,CD,DVD,hard drive,USB drive,network globe,folder,file,application icon,web browser,email icon,settings icon,power button,play button,pause button,stop button,volume icon,search icon,information icon,warning icon,question mark,check mark,cross mark,plus sign,minus sign,arrow,cursor,home icon,download icon,upload icon,trash can,shopping cart,floppy disk
chair,table,desk,sofa,bed,cupboard,shelf,lamp,light bulb,candle,mirror,bathtub,toilet,shower,sink,fridge,oven,stove,washing machine,vacuum cleaner,fan,air conditioner,umbrella,bag,backpack,suitcase,box,basket,bottle,jar,cup,mug,glass,plate,bowl,fork,spoon,knife,teapot,kettle,pot,pan
hat,cap,shoe,boot,shirt,trousers,coat,dress,skirt,glove,sock,scarf,tie,belt,glasses,sunglasses,watch,ring,necklace,earring,button,ribbon
bread,cake,cookie,pizza,hamburger,sandwich,hot dog,egg,cheese,meat,fish dish,ice cream,candy,chocolate,coffee,tea,milk,juice,wine,beer,food,meal
football,basketball,baseball,tennis ball,golf ball,bowling ball,sports ball,tennis racket,golf club,baseball bat,skateboard,ski,snowboard,ice skate,roller skate,swimming pool,boxing glove,dumbbell,bicycle rider,football player,baseball player,guitar,piano,violin,drum,trumpet,saxophone,flute,music note,music instrument
heart,peace sign,religious cross,Star of David,yin yang,zodiac symbol,national flag,Christmas tree,Christmas decoration,Easter egg,Halloween pumpkin,birthday cake,balloon,gift,party decoration,wedding,celebration
frame,border,corner ornament,floral pattern,geometric pattern,abstract pattern,texture,background,decorative design,swirl,triangle,square,circle,polygon,spiral,checkerboard,stripe,dot,line,alphabet letter,number,word,text logo,symbol,icon,photo,illustration,line drawing,silhouette,pixel art,cartoon,watercolour painting,oil painting,3D rendered object'''
base=[s.strip() for line in words.splitlines() for s in line.split(',') if s.strip()]
counts=collections.Counter()
for r in rows:
 if r['format']=='eps':
  stem=re.sub(r'\s+',' ',re.sub(r'\b\d+\b','',Path(r['original_path']).stem)).strip()
  if 3<len(stem)<55:counts[stem]+=1
labels=list(dict.fromkeys(base+[s for s,n in counts.most_common(1700) if n>=4]))
(OUT/'visual-vocabulary.json').write_text(json.dumps(labels,ensure_ascii=False))
opt=ort.SessionOptions();opt.intra_op_num_threads=2;opt.inter_op_num_threads=1
vision=ort.InferenceSession(str(MODEL/'vision_model_quantized.onnx'),opt,providers=['CPUExecutionProvider'])
text=ort.InferenceSession(str(MODEL/'text_model_quantized.onnx'),opt,providers=['CPUExecutionProvider'])
tok=Tokenizer.from_file(str(MODEL/'tokenizer.json'));tok.enable_padding(pad_id=49407,length=77);tok.enable_truncation(77)
if (OUT/'visual-label-vectors.npy').exists():text_vectors=np.load(OUT/'visual-label-vectors.npy')
else:
 text_vectors=[]
 for start in range(0,len(labels),64):
  batch=labels[start:start+64];ids=np.asarray([x.ids for x in tok.encode_batch(['an image of '+s for s in batch])],dtype=np.int64)
  e=text.run(None,{'input_ids':ids})[0];e/=np.linalg.norm(e,axis=1,keepdims=True);text_vectors.append(e)
 text_vectors=np.concatenate(text_vectors);np.save(OUT/'visual-label-vectors.npy',text_vectors)
shape=(len(hashes),512);dest=OUT/'image-embeddings.npy';valid_dest=OUT/'image-embedding-valid.npy'
vectors=np.lib.format.open_memmap(dest,mode='r+' if dest.exists() else 'w+',dtype=np.float16,shape=shape)
valid=np.lib.format.open_memmap(valid_dest,mode='r+' if valid_dest.exists() else 'w+',dtype=np.uint8,shape=(len(hashes),))
(OUT/'embedding-hashes.json').write_text(json.dumps(hashes))
mean=np.asarray([.48145466,.4578275,.40821073],dtype=np.float32);std=np.asarray([.26862954,.26130258,.27577711],dtype=np.float32)
done=set(hashes[i] for i in np.flatnonzero(valid));tags_path=OUT/('visual-tags-'+str(args.shard_index)+'.jsonl' if args.shard_count>1 else 'visual-tags.jsonl');started=time.time();run_count=0
with tags_path.open('a') as result:
 while True:
  available=[p for p in (OUT/'thumbs').glob('*.webp') if p.stem not in done and positions[p.stem]%args.shard_count==args.shard_index]
  if not available:
   if (OUT/'conversion-complete').exists():break
   time.sleep(3);continue
  for start in range(0,len(available),16):
   batch=[];names=[]
   for p in available[start:start+16]:
    try:
     with Image.open(p) as im:arr=np.asarray(im.convert('RGB'),dtype=np.float32)/255
     batch.append(((arr-mean)/std).transpose(2,0,1));names.append(p.stem)
    except (OSError,ValueError):continue
   if not batch:continue
   e=vision.run(None,{'pixel_values':np.asarray(batch,dtype=np.float32)})[0];e/=np.linalg.norm(e,axis=1,keepdims=True)
   score=e@text_vectors.T
   for sha,vec,scores in zip(names,e,score):
    i=positions[sha];vectors[i]=vec;valid[i]=1;done.add(sha)
    top=np.argsort(scores)[-5:][::-1];best=float(scores[top[0]])
    suggested=[{'label':labels[j],'similarity':round(float(scores[j]),4)} for j in top if scores[j]>=max(.23,best-.035)]
    result.write(json.dumps({'sha256':sha,'embedding_index':i,'visual_tags':suggested,'visual_tag_method':'CLIP ViT-B/32 ONNX int8; suggestions, cosine similarity is not confidence'})+'\n')
   result.flush();run_count+=len(names)
   if run_count%512<16:
    vectors.flush();valid.flush();print(json.dumps({'shard':args.shard_index,'visually_analysed_total':int(np.count_nonzero(valid)),'unique_files':len(hashes),'elapsed_seconds':round(time.time()-started)}),flush=True)
vectors.flush();valid.flush()
print(json.dumps({'visually_analysed':len(done),'finished':True}),flush=True)
