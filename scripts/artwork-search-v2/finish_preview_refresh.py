"""Refresh changed visual features in parallel and rebuild verified gallery metadata."""
from pathlib import Path
import subprocess,os,time,shutil,sys
OUT=Path('work/processed');S=Path('work/Image/scripts/artwork-search-v2');DEST=Path('outputs/game-art-library');PY=sys.executable
env={**os.environ,'PYTHONPATH':str(Path('work/tooling/python-libs').resolve()),'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'2'}
(OUT/'local-library-complete').unlink(missing_ok=True)
while not (OUT/'small-preview-repair.json').exists():time.sleep(2)
subprocess.run([PY,str(S/'repair_semantics.py')],check=True,env=env)
jobs=[]
for i in range(4):
 log=(OUT/('semantic-preview-'+str(i)+'-progress.log')).open('w')
 jobs.append((subprocess.Popen([PY,str(S/'semantic.py'),'--shard-index',str(i),'--shard-count','4'],stdout=log,stderr=subprocess.STDOUT,env=env),log))
for job,log in jobs:
 code=job.wait();log.close();assert code==0,code
subprocess.run([PY,str(S/'repair_semantics.py')],check=True,env=env)
subprocess.run([PY,str(S/'assemble.py')],check=True,env=env)
for name in ['index.html','search.py']:shutil.copy2(S/name,DEST/name)
(OUT/'local-library-complete').write_text('Cleaned library completed with enlarged small-image previews.\n')
print('Local preview refresh complete',flush=True)
