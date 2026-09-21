"""Frozen small-sample development study; see PILOT_PROTOCOL.md.

Run only on verified CC0 minute extracts, not restricted vendor samples.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import numpy as np
from book_execution import Book, allocate, forecast_books, replay

HERE=Path(__file__).resolve().parent
H=15
ASSETS=('BTC','ETH','ADA')
SIZES=(.01,.05,.20)
ARMS=('reference','price','liquidity','both','twap')


def epoch(date):
    return int(dt.datetime.fromisoformat(date).replace(tzinfo=dt.timezone.utc).timestamp()*1e6)


def state(d):
    mid=(d['bids_price'][:,0]+d['asks_price'][:,0])/2
    spread=(d['asks_price'][:,0]-d['bids_price'][:,0])/2
    depth=d['bids_amount'].sum(axis=1)
    return mid,spread,depth


def features(d):
    mid,sp,depth=state(d)
    askdepth=d['asks_amount'].sum(axis=1)
    angle=(d['boundary_us']%86_400_000_000)/86_400_000_000*2*np.pi
    with np.errstate(divide='ignore',invalid='ignore'):
        x=np.column_stack([1e4*np.log(mid/np.roll(mid,1)),1e4*np.log(mid/np.roll(mid,5)),
                           np.log(1e4*sp/mid),np.log(depth),(depth-askdepth)/(depth+askdepth),
                           np.log(sp/np.roll(sp,1)),np.log(depth/np.roll(depth,1)),
                           np.sin(angle),np.cos(angle)])
    x[:5]=np.nan
    return x


def valid_indices(times,start,end):
    """All feature/target minute slots exist; target's last timestamp < end."""
    times=np.asarray(times,np.int64)
    good=[]
    for i in range(5,len(times)-H):
        if start<=times[i] and times[i+H]<end and np.all(np.diff(times[i-5:i+H+1])==60_000_000):
            good.append(i)
    return np.array(good,dtype=int)


def targets(d,ix):
    mid,sp,dep=state(d)
    future=ix[:,None]+np.arange(1,H+1)[None,:]
    return np.concatenate([1e4*(mid[future]/mid[ix,None]-1),
                           np.log(sp[future]/sp[ix,None]),np.log(dep[future]/dep[ix,None])],axis=1)


def fit_ridge(x,y):
    mean=x.mean(axis=0);scale=x.std(axis=0);scale=np.where(scale<1e-12,1.,scale)
    z=(x-mean)/scale;ym=y.mean(axis=0)
    coef=np.linalg.solve(z.T@z/len(z)+np.eye(z.shape[1]),z.T@(y-ym)/len(z))
    return dict(mean=mean,scale=scale,coef=coef,intercept=ym,
                lower=np.quantile(y,.01,axis=0),upper=np.quantile(y,.99,axis=0))


def predict_ridge(model,x):
    z=np.clip((x-model['mean'])/model['scale'],-5,5)
    return np.clip(z@model['coef']+model['intercept'],model['lower'],model['upper'])


def seasonal_design(times):
    angle=(times%86_400_000_000)/86_400_000_000*2*np.pi
    return np.column_stack([np.ones(len(times)),np.sin(angle),np.cos(angle)])


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(data_dir,output):
    output=Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('refuse to overwrite existing results')
    lock=json.loads((HERE/'pilot_protocol_lock.json').read_text())
    if file_hash(HERE/'PILOT_PROTOCOL.md')!=lock['sha256']:
        raise ValueError('protocol changed after lock')
    output.mkdir(parents=True,exist_ok=True)
    manifest={'protocol_sha256':lock['sha256'],'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
              'code_sha256':{p.name:file_hash(p) for p in [HERE/'pilot_study.py',HERE/'book_execution.py']},
              'inputs':{}}
    (output/'run_manifest.json').write_text(json.dumps(manifest,indent=2))
    rows=[];audits={};fits={};errors={}
    for asset in ASSETS:
        path=Path(data_dir)/f'martinsn_{asset}_causal_minutes.npz'
        with np.load(path,allow_pickle=False) as f:d={k:f[k] for k in f.files}
        manifest['inputs'][asset]={'path':str(path),'sha256':file_hash(path)}
        times=d['boundary_us'];x=features(d);mid,sp,dep=state(d)
        train=valid_indices(times,epoch('2021-04-08'),epoch('2021-04-14'))
        evaluation=valid_indices(times,epoch('2021-04-14'),epoch('2021-04-19'))
        train=train[np.isfinite(x[train]).all(axis=1)]
        evaluation=evaluation[np.isfinite(x[evaluation]).all(axis=1)]
        evaluation=evaluation[((times[evaluation]//60_000_000)%30)==5]
        if len(train)<100 or len(evaluation)==0:raise ValueError('insufficient valid rows')
        y=targets(d,train);model=fit_ridge(x[train],y)
        predictions=predict_ridge(model,x[evaluation])
        sy=np.column_stack([np.log(sp[train]),np.log(dep[train])])
        season=np.linalg.lstsq(seasonal_design(times[train]),sy,rcond=None)[0]
        fits[asset]={k:v.tolist() for k,v in model.items()};fits[asset]['season']=season.tolist()
        audits[asset]={'training_rows':len(train),'evaluation_orders':len(evaluation),
                       'potential_orders':5*48,'sizes':{}}
        truth=targets(d,evaluation)
        errors[asset]={'learned_mse_by_target_horizon':np.mean((predictions-truth)**2,axis=0).tolist()}
        reference_predictions=[]
        for i,pred in zip(evaluation,predictions):
            current=Book(int(times[i]//1_000_000),d['bids_price'][i],d['bids_amount'][i],d['asks_price'][i,0])
            future=[Book(int(times[j]//1_000_000),d['bids_price'][j],d['bids_amount'][j],d['asks_price'][j,0]) for j in range(i+1,i+H+1)]
            seasonal=(seasonal_design(times[i+1:i+H+1])-seasonal_design(times[i:i+1]))@season
            reference_predictions.append(np.r_[np.zeros(H),seasonal[:,0],seasonal[:,1]])
            date=dt.datetime.fromtimestamp(current.timestamp,dt.timezone.utc).date().isoformat()
            for fraction in SIZES:
                quantity=float(dep[i]*fraction);cap=quantity/3
                for arm in ARMS:
                    fallback=False
                    if arm=='twap':schedule=np.full(H,quantity/H)
                    else:
                        liquidity=pred[H:] if arm in ('liquidity','both') else np.r_[seasonal[:,0],seasonal[:,1]]
                        prices,sizes=forecast_books(current,pred[:H],liquidity[:H],liquidity[H:],arm in ('price','both'),True)
                        try:schedule=allocate(prices,sizes,quantity,cap)
                        except ValueError:
                            schedule=np.full(H,quantity/H);fallback=True
                    for depletion in (True,False):
                        result=replay(current.mid,future,schedule,0.,depletion,child_cap=cap)
                        # The fee sensitivity changes accounting, not the optimal schedule,
                        # since a constant percentage scales all gross proceeds equally.
                        result['shortfall_bps_fee10']=(result['shortfall_bps']+10*result['proceeds']/(quantity*current.mid)
                                                     if result['shortfall_bps'] is not None else None)
                        result.pop('child_fills')
                        rows.append(dict(asset=asset,date=date,arrival_us=int(times[i]),fraction=fraction,arm=arm,
                                         depletion=int(depletion),fallback=int(fallback),arrival_notional=quantity*current.mid,**result))
        errors[asset]['reference_mse_by_target_horizon']=np.mean((np.array(reference_predictions)-truth)**2,axis=0).tolist()
        print(asset,audits[asset],flush=True)
    with (output/'episodes.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (output/'fits.json').write_text(json.dumps(fits,indent=2))
    (output/'forecast_errors.json').write_text(json.dumps(errors,indent=2))
    (output/'data_audit.json').write_text(json.dumps(audits,indent=2))
    manifest['completed_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    (output/'run_manifest.json').write_text(json.dumps(manifest,indent=2))
    print('completed',len(rows),'policy-size-replay rows',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.data_dir,a.output)
