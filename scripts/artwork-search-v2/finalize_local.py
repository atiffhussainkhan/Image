"""Wait for running conversions, then clean, package and validate the published index."""
from pathlib import Path
import subprocess,time,os,json,shutil,sys
OUT=Path('work/processed');SCRIPTS=Path('work/Image/scripts/artwork-search-v2');PYTHON=Path(os.environ.get('ARTWORK_PYTHON',sys.executable))
env={**os.environ,'PYTHONPATH':str(Path('work/tooling/python-libs').resolve()),'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'2'}
while not (OUT/'conversion-complete').exists():time.sleep(10)
while not all('"finished": true' in (OUT/('semantic-'+str(i)+'-progress.log')).read_text() for i in range(4)):time.sleep(10)
for name in ['retry_failed.py','recover_mislabeled.py','clean.py','retain_jpegs.py','palette.py','repair_semantics.py','semantic.py','package.py','assemble.py']:
 print('Starting '+name,flush=True)
 subprocess.run([str(PYTHON),str(SCRIPTS/name)],check=True,env=env)
DEST=Path('outputs/game-art-library')
for name in ['index.html','search.py']:shutil.copy2(SCRIPTS/name,DEST/name)
(OUT/'local-library-complete').write_text('All cleanup, search and packaging stages completed.\n')
print('Local library complete',flush=True)
