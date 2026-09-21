"""Stream CC0 one-second files to causal UTC minute snapshots (<=5s old)."""
import csv,io,zipfile,json,hashlib,importlib.util
from datetime import datetime
from pathlib import Path
import numpy as np

def run(symbol):
 folder=Path('data/orderbook/open_pilots');source=folder/f'martinsn_{symbol}_1sec.csv.download'
 chosen=[];boundary=None;previous=None;last=None;count=0;stale=0;maxgap=0
 with zipfile.ZipFile(source) as z,io.TextIOWrapper(z.open(f'{symbol}_1sec.csv')) as f:
  for row in csv.DictReader(f):
   parsed=datetime.fromisoformat(row['system_time'])
   if parsed.tzinfo is None:raise ValueError('Timezone missing from source timestamp')
   t=int(parsed.timestamp()*1e6);count+=1
   if last is not None:
    if t<=last:raise ValueError('Nonincreasing time')
    maxgap=max(maxgap,t-last)
   if boundary is None:boundary=((t+59_999_999)//60_000_000)*60_000_000
   while t>boundary:
    if previous is not None and boundary-last<=5_000_000:chosen.append((boundary,last,previous))
    else:stale+=1
    boundary+=60_000_000
   previous=row;last=t
 mid=np.array([float(r['midpoint']) for b,t,r in chosen]);spread=np.array([float(r['spread']) for b,t,r in chosen])
 a={'boundary_us':np.array([b for b,t,r in chosen],dtype=np.int64),'source_timestamp_us':np.array([t for b,t,r in chosen],dtype=np.int64),'midpoint':mid,'spread':spread}
 for side in ['bids','asks']:
  d=np.array([[float(r[f'{side}_distance_{i}']) for i in range(15)] for b,t,r in chosen]);n=np.array([[float(r[f'{side}_notional_{i}']) for i in range(15)] for b,t,r in chosen]);a[side+'_price']=mid[:,None]*(1+d);a[side+'_amount']=n/a[side+'_price']
 valid=np.ones(len(mid),bool)
 for v in a.values():valid &= np.isfinite(v).all(axis=1) if v.ndim==2 else np.isfinite(v)
 valid &= (a['bids_price']>0).all(axis=1) & (a['asks_price']>0).all(axis=1) & (a['bids_amount'][:,0]>0) & (a['asks_amount'][:,0]>0) & (a['bids_price'][:,0]<a['asks_price'][:,0]) & (a['bids_amount']>=0).all(axis=1) & (a['asks_amount']>=0).all(axis=1) & (np.diff(a['bids_price'],axis=1)<0).all(axis=1) & (np.diff(a['asks_price'],axis=1)>0).all(axis=1)
 invalid=int((~valid).sum());a={k:v[valid] for k,v in a.items()};output=folder/f'martinsn_{symbol}_causal_minutes.npz';np.savez_compressed(output,**a)
 h=hashlib.sha256()
 with source.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 audit={'symbol':symbol,'source':str(source),'sha256':h.hexdigest(),'compressed_bytes':source.stat().st_size,'raw_rows':count,'sampled_minutes':int(valid.sum()),'stale_minutes':stale,'invalid_books':invalid,'first_boundary_utc':datetime.fromtimestamp(int(a['boundary_us'][0])/1e6,__import__('datetime').timezone.utc).isoformat(),'last_boundary_utc':datetime.fromtimestamp(int(a['boundary_us'][-1])/1e6,__import__('datetime').timezone.utc).isoformat(),'max_raw_gap_seconds':maxgap/1e6,'max_age_seconds':float((a['boundary_us']-a['source_timestamp_us']).max()/1e6),'timestamp_semantics':'source_timestamp_us is dataset system_time with explicit +00:00 offset; independent receipt and exchange times unavailable','outcomes_evaluated':False}
 output.with_suffix('.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit),flush=True)
if __name__=='__main__':
 import sys
 for symbol in sys.argv[1:] or ['BTC','ETH','ADA']:run(symbol)
