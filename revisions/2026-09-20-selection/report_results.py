"""Report frozen results and predeclared monetary contrasts; no fitting or selection."""
import csv,gzip,json
import numpy as np
import selection_study as s
D=json.loads((s.HERE/'results/study.json').read_text())
with gzip.open(s.HERE/'results/daily.csv.gz','rt') as f:rows=list(csv.DictReader(f))
extra=[]
for cohort,syms in [('transfer',s.TRANSFER),('development',s.SYMBOLS[:2])]:
 part=[v for v in rows if v['symbol'] in syms and float(v['eta'])==2 and float(v['risk'])==1]
 days=sorted({int(v['day']) for v in part});assert np.array_equal(np.diff(days),np.ones(len(days)-1))
 lookup={(v['symbol'],int(v['day']),v['policy']):float(v['money']) for v in part}
 for base in ['endpoint','path','contrasts','zero']:
  daily=np.array([np.mean([lookup[(sym,d,'economic')]-lookup[(sym,d,base)] for sym in syms]) for d in days])
  ci=np.quantile(s.bootstrap(daily[:,None])[:,0],[.025,.975])
  extra.append({'cohort':cohort,'contrast':'economic_minus_'+base,'eta':2,'risk':1,'score':'monetary','mean':float(daily.mean()),'ci95':ci.tolist()})
(s.HERE/'monetary_contrasts.json').write_text(json.dumps(extra,indent=2)+'\n')
