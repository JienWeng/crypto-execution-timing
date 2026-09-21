"""Post-pilot oracle diagnostic. Hindsight schedules are not feasible policies."""
import csv,datetime as dt,hashlib,json,sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
PILOT=HERE.parent/'2026-09-21-research-direction'
sys.path.insert(0,str(PILOT))
from book_execution import Book,allocate,forecast_books,replay
from pilot_study import ASSETS,H,SIZES,epoch,features,fit_ridge,predict_ridge,seasonal_design,state,targets,valid_indices

def oracle_price_bps(mids,arrival_mid):
    return 1e4*(np.asarray(mids)/arrival_mid-1)

def realized_liquidity_books(bids,asks,sizes,arrival_mid,reference_mids):
    asks=np.asarray(asks)
    if asks.ndim==2:asks=asks[:,0]
    mids=(np.asarray(bids)[:,0]+asks)/2
    return np.asarray(bids)-mids[:,None]+np.asarray(reference_mids)[:,None],np.asarray(sizes).copy()

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main(data_dir,output):
    output=Path(output)
    if output.exists() and any(output.iterdir()):raise ValueError('refuse overwrite')
    lock=json.loads((HERE/'protocol_lock.json').read_text())
    if sha(HERE/'PROTOCOL.md')!=lock['sha256']:raise ValueError('protocol changed after lock')
    output.mkdir(parents=True,exist_ok=True)
    rows=[];audit={}
    for asset in ASSETS:
        path=Path(data_dir)/f'martinsn_{asset}_causal_minutes.npz'
        with np.load(path,allow_pickle=False) as f:d={k:f[k] for k in f.files}
        times=d['boundary_us'];x=features(d);mid,sp,dep=state(d)
        train=valid_indices(times,epoch('2021-04-08'),epoch('2021-04-14'))
        evaluation=valid_indices(times,epoch('2021-04-14'),epoch('2021-04-19'))
        train=train[np.isfinite(x[train]).all(axis=1)]
        evaluation=evaluation[np.isfinite(x[evaluation]).all(axis=1)]
        evaluation=evaluation[((times[evaluation]//60_000_000)%30)==5]
        season=np.linalg.lstsq(seasonal_design(times[train]),np.column_stack([np.log(sp[train]),np.log(dep[train])]),rcond=None)[0]
        failures=0
        for i in evaluation:
            current=Book(int(times[i]//1e6),d['bids_price'][i],d['bids_amount'][i],d['asks_price'][i,0])
            future=[Book(int(times[j]//1e6),d['bids_price'][j],d['bids_amount'][j],d['asks_price'][j,0]) for j in range(i+1,i+H+1)]
            future_mid=np.array([b.mid for b in future])
            seasonal=(seasonal_design(times[i+1:i+H+1])-seasonal_design(times[i:i+1]))@season
            reference_mid=np.full(H,current.mid)
            for fraction in SIZES:
                quantity=float(dep[i]*fraction);cap=quantity/3
                # Identical reference schedule to the frozen pilot.
                rp,rs=forecast_books(current,np.zeros(H),seasonal[:,0],seasonal[:,1],False,True)
                schedules={}
                try:
                    schedules['reference']=allocate(rp,rs,quantity,cap)
                    pp,ps=forecast_books(current,oracle_price_bps(future_mid,current.mid),seasonal[:,0],seasonal[:,1],True,True)
                    schedules['oracle_price']=allocate(pp,ps,quantity,cap)
                    lp,ls=realized_liquidity_books(d['bids_price'][i+1:i+H+1],d['asks_price'][i+1:i+H+1,0],d['bids_amount'][i+1:i+H+1],current.mid,reference_mid)
                    schedules['oracle_liquidity']=allocate(lp,ls,quantity,cap)
                    schedules['full_oracle']=allocate(d['bids_price'][i+1:i+H+1],d['bids_amount'][i+1:i+H+1],quantity,cap)
                except ValueError:
                    failures+=1;continue
                date=dt.datetime.fromtimestamp(current.timestamp,dt.timezone.utc).date().isoformat()
                for arm,schedule in schedules.items():
                    for depletion in (True,False):
                        result=replay(current.mid,future,schedule,0.,depletion,child_cap=cap)
                        result.pop('child_fills')
                        rows.append(dict(asset=asset,date=date,arrival_us=int(times[i]),fraction=fraction,arm=arm,depletion=int(depletion),arrival_notional=quantity*current.mid,**result))
        audit[asset]={'evaluation_arrivals':len(evaluation),'failed_arrival_size_cases':failures,'input_sha256':sha(path)}
    with (output/'episodes.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (output/'audit.json').write_text(json.dumps(audit,indent=2))
    (output/'manifest.json').write_text(json.dumps({'protocol_sha256':lock['sha256'],'code_sha256':sha(HERE/'oracle_study.py'),'rows':len(rows)},indent=2))
    print(json.dumps(audit,indent=2));print('rows',len(rows))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--data-dir',required=True);p.add_argument('--output',required=True);a=p.parse_args();main(a.data_dir,a.output)
