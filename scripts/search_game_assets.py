#!/usr/bin/env python3
"""Search known cleaned images, candidate links and GitHub Release metadata. Requires Python standard library only."""
import argparse,gzip,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
def norm(s):return ' '.join(re.findall(r'[a-z0-9]+',str(s).lower()))
def records(scope):
 if scope in ('all','candidate'):
  path=ROOT/'catalog/new-asset-candidates-2026-10-25.json'
  if path.exists():
   for d in json.loads(path.read_text(encoding='utf8'))['items']:
    yield {'kind':'discovery_only','title':d['title'],'asset_id':d['id'],'url':d['source_url'],'status':'not_downloaded_not_tested','keywords':d['tags']}
 if scope in ('all','releases'):
  path=ROOT/'catalog/ALL_RELEASE_ASSETS.json'
  if path.exists():
   for rel in json.loads(path.read_text(encoding='utf8'))['releases']:
    for d in rel['assets']:
     yield {'kind':'github_release_file','title':d['name'],'asset_id':rel['tag']+'/'+d['name'],'url':d['url'],'bytes':d['bytes'],'status':'stored_archive_not_necessarily_game_ready'}
 if scope in ('all','images'):
  path=ROOT/'catalog/game-art-search-v2-2026-10-05/assets.jsonl.gz'
  if path.exists():
   with gzip.open(path,'rt',encoding='utf8') as f:
    for line in f:
     try:d=json.loads(line)
     except ValueError:continue
     if isinstance(d,dict):
      yield {'kind':'cleaned_image_index','title':str(d.get('original_path') or d.get('path') or d.get('name') or ''),'asset_id':d.get('asset_id') or d.get('id'),'record':d,'status':'technically_indexed_license_unverified'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('query',nargs='+');ap.add_argument('--limit',type=int,default=20);ap.add_argument('--scope',choices=['all','candidate','releases','images'],default='all');a=ap.parse_args()
 terms=norm(' '.join(a.query)).split();found=[]
 for d in records(a.scope):
  s=norm(json.dumps(d,ensure_ascii=False))
  if all(t in s for t in terms):
   score=sum(3 if t in norm(d.get('title','')) else 1 for t in terms)
   found.append((score,d))
 found.sort(key=lambda item:-item[0])
 print(json.dumps({'query':' '.join(terms),'total_matches':len(found),'results':[d for _,d in found[:max(0,a.limit)]]},indent=2,ensure_ascii=False))
if __name__=='__main__':main()
