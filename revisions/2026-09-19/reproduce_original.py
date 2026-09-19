"""Read-only verification of original seed-specific calibration and evaluation."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import empirical_study as e
lock=json.loads((ROOT/'results/empirical/calibration_lock.json').read_text());old=json.loads((ROOT/'results/empirical/evaluation.json').read_text())
errors=[]
for month in ['2026-07','2026-08']:
 x,p,d,_=e.month_episodes(month);mu=(x-lock['signal_center'])[:,None]*lock['slopes']
 for eta,risk in e.SCENARIOS:
  c=e.components(p,mu,eta,risk)
  if month=='2026-07':
   b=e.bootstrap_means(np.column_stack([c['R'],c['C']]),d,seed=20260918)
   q=np.quantile(b[:,0]/(2*b[:,1]),[.05,.95]);ref=next(v for v in lock['scenarios'] if v['eta']==eta and v['risk']==risk)
   errors.append(float(np.max(np.abs(q-ref['ratio_bootstrap_90_interval']))))
  else:
   for name,w in [('full',1),('half',.5)]:
    q=np.quantile(e.bootstrap_means(w*c['R']-w*w*c['C'],d,seed=20260919)[:,0],[.025,.975]);ref=next(v for v in old['results'] if v['eta']==eta and v['risk']==risk and v['strategy']==name)
    errors.append(float(np.max(np.abs(q-ref['objective_95_interval']))))
assert max(errors)<1e-12
out={'original_seed_calibration_and_full_half_intervals':'PASS','maximum_absolute_difference':max(errors),'original_files_rewritten':False}
Path(__file__).with_name('results').joinpath('original_seed_reproduction.json').write_text(json.dumps(out,indent=2)+'\n')
print(out)
