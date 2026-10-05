"""Retry failed EPS exports sequentially after bulk jobs finish before removing them."""
import json
from convert import OUT,unique,convert
retried=0;recovered=0
for p in (OUT/'status').glob('*.json'):
 s=json.loads(p.read_text())
 if s['conversion_status']=='failed' and s['original_format']=='eps':
  p.unlink();r=convert(unique[p.stem]);r['sequential_retry']=True;r['initial_failure']=s.get('reason');p.write_text(json.dumps(r));retried+=1;recovered+=r['conversion_status']=='converted'
print(json.dumps({'retried':retried,'recovered':recovered}),flush=True)
