"""Locked train/calibrate/evaluate study; see empirical_protocol.md.

Stages are separated to persist the calibration decisions before evaluation.
"""
import argparse
import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT=Path('results/empirical')
SCENARIOS=[(.5,0.),(.5,1.),(2.,0.),(2.,1.),(5.,0.),(5.,1.)]
SEED=20260918


def filehash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def month_episodes(month):
    path=Path('data/raw')/f'BTCUSDT-1m-{month}.zip'
    expected=next(row['sha256'] for row in json.loads(Path('data/manifest.json').read_text()) if row['month']==month)
    if filehash(path)!=expected:
        raise ValueError('archive hash changed')
    with zipfile.ZipFile(path) as z:
        rows=np.loadtxt(io.BytesIO(z.read(z.namelist()[0])),delimiter=',')
    index=np.concatenate([day+np.arange(5,1425,30) for day in range(0,len(rows),1440)])
    x=[]
    for i in index:
        vol=rows[i-5:i,5].sum()
        x.append((2*rows[i-5:i,9].sum()-vol)/vol if vol>0 else 0.)
    prices=10000*(rows[index[:,None]+np.arange(1,16),1]/rows[index,None,1]-1)
    days=(rows[index,0].astype(np.int64)//86_400_000_000).astype(int)
    return np.array(x),prices,days,index


def simplex(v):
    s=np.sort(v)[::-1]
    c=np.cumsum(s)-1
    good=s-c/np.arange(1,len(s)+1)>0
    rho=np.flatnonzero(good)[-1]
    return np.maximum(v-c[rho]/(rho+1),0)


def qp(H,b,start=None):
    u=np.ones(len(b))/len(b) if start is None else start.copy()
    step=1/np.linalg.eigvalsh(H)[-1]
    for _ in range(2000):
        new=simplex(u-step*(H@u-b))
        if np.max(np.abs(new-u))<1e-13:
            u=new;break
        u=new
    else:
        raise RuntimeError('QP failed to converge')
    g=H@u-b
    positive=u>1e-10
    level=g[positive].mean()
    residual=max(np.max(np.abs(g[positive]-level)),max(0.,level-g.min()),abs(u.sum()-1),max(0.,-u.min()))
    if residual>1e-8:
        raise RuntimeError(f'QP KKT residual {residual}')
    return u,float(residual)


def components(prices,forecast,eta,risk):
    n=prices.shape[1]; L=np.tril(np.ones((n,n)))
    H=2*eta*n*np.eye(n)+2*risk/n*L.T@L
    b=2*risk/n*L.T@np.ones(n)
    u0,res=qp(H,b)
    q0=1-L@u0
    d=[]
    for mu in forecast:
        u,e=qp(H,b+mu,u0);d.append(u-u0);res=max(res,e)
    d=np.array(d);Ld=d@L.T
    C=eta*n*np.sum(d*d,axis=1)+risk/n*np.sum(Ld*Ld,axis=1)
    monetary_R=np.sum(d*prices,axis=1)-2*eta*n*(d@u0)
    R=monetary_R+2*risk/n*(Ld@q0)
    monetary_C=eta*n*np.sum(d*d,axis=1)
    u_t=np.ones(n)/n;q_t=1-L@u_t
    twap_gain=(prices@(u_t-u0)+eta*n*(u0@u0-u_t@u_t)
               +risk/n*(q0@q0-q_t@q_t))
    twap_money=prices@(u_t-u0)+eta*n*(u0@u0-u_t@u_t)
    return dict(R=R,C=C,monetary_R=monetary_R,monetary_C=monetary_C,
                twap_gain=twap_gain,twap_money=twap_money,kkt=res,u0=u0,d=d)


def bootstrap_means(values,days,seed=SEED,reps=2000):
    values=np.asarray(values)
    if values.ndim==1: values=values[:,None]
    unique=np.unique(days)
    sums=np.array([values[days==d].sum(axis=0) for d in unique])
    counts=np.array([(days==d).sum() for d in unique])
    draws=np.random.default_rng(seed).integers(0,len(unique),(reps,len(unique)))
    return sums[draws].sum(axis=1)/counts[draws].sum(axis=1)[:,None]


def fit():
    ROOT.mkdir(parents=True,exist_ok=True)
    x,prices,days,_=month_episodes('2026-06')
    coef=np.linalg.lstsq(np.column_stack([np.ones(len(x)),x]),prices,rcond=None)[0]
    xc,pv,dv,_=month_episodes('2026-07')
    forecast=(xc-x.mean())[:,None]*coef[1]
    records=[]
    for eta,risk in SCENARIOS:
        c=components(pv,forecast,eta,risk)
        if c['C'].mean()<=1e-14: raise ValueError('degenerate nominal direction')
        ratio=c['R'].mean()/(2*c['C'].mean())
        bs=bootstrap_means(np.column_stack([c['R'],c['C']]),dv)
        ratios=bs[:,0]/(2*bs[:,1])
        low,high=np.quantile(ratios,[.05,.95])
        records.append({'eta':eta,'risk':risk,'ratio':float(ratio),
                        'ratio_bootstrap_90_interval':[float(low),float(high)],
                        'plugin_weight':float(np.clip(ratio,0,1)),
                        'conservative_weight':float(np.clip(low,0,1)),
                        'mean_C':float(c['C'].mean()),'max_kkt_residual':c['kkt']})
    lock={'created_utc':datetime.now(timezone.utc).isoformat(),
          'protocol_sha256':filehash('empirical_protocol.md'),'code_sha256':filehash(__file__),
          'training_month':'2026-06','calibration_month':'2026-07','evaluation_month':'2026-08',
          'training_episodes':len(x),'calibration_episodes':len(xc),
          'signal_center':float(x.mean()),'intercepts':coef[0].tolist(),'slopes':coef[1].tolist(),
          'scenarios':records,'outcome':'risk-adjusted objective gain, bps',
          'primary_scenario':{'eta':2.,'risk':1.},'seed':SEED}
    (ROOT/'calibration_lock.json').write_text(json.dumps(lock,indent=2)+'\n')
    (ROOT/'calibration_lock.sha256').write_text(filehash(ROOT/'calibration_lock.json')+'\n')
    print(json.dumps(lock,indent=2))


def evaluate():
    lock=json.loads((ROOT/'calibration_lock.json').read_text())
    if filehash(ROOT/'calibration_lock.json')!=(ROOT/'calibration_lock.sha256').read_text().strip():
        raise ValueError('calibration lock changed')
    if lock['protocol_sha256']!=filehash('empirical_protocol.md') or lock['code_sha256']!=filehash(__file__):
        raise ValueError('code/protocol changed after calibration')
    x,prices,days,index=month_episodes('2026-08')
    forecast=(x-lock['signal_center'])[:,None]*np.array(lock['slopes'])
    results=[];episode_rows=[]
    for s in lock['scenarios']:
        c=components(prices,forecast,s['eta'],s['risk'])
        weights={'baseline':0.,'full':1.,'half':.5,'plugin':s['plugin_weight'],
                 'conservative':s['conservative_weight']}
        gains={name:w*c['R']-w*w*c['C'] for name,w in weights.items()}
        monetary={name:w*c['monetary_R']-w*w*c['monetary_C'] for name,w in weights.items()}
        gains['twap']=c['twap_gain'];monetary['twap']=c['twap_money']
        for name,gain in gains.items():
            bs=bootstrap_means(np.column_stack([gain,monetary[name]]),days,seed=SEED+1)
            results.append({'eta':s['eta'],'risk':s['risk'],'strategy':name,'weight':weights.get(name),
                            'episodes':len(x),'days':len(np.unique(days)),
                            'mean_objective_gain_bps':float(gain.mean()),
                            'objective_95_interval':np.quantile(bs[:,0],[.025,.975]).tolist(),
                            'mean_monetary_gain_bps':float(monetary[name].mean()),
                            'monetary_95_interval':np.quantile(bs[:,1],[.025,.975]).tolist(),
                            'episode_objective_gain_p05_bps':float(np.quantile(gain,.05)),
                            'max_kkt_residual':c['kkt']})
            for j in range(len(x)):
                episode_rows.append({'eta':s['eta'],'risk':s['risk'],'strategy':name,
                                     'minute_index':int(index[j]),'utc_day':int(days[j]),
                                     'objective_gain_bps':float(gain[j]),
                                     'monetary_gain_bps':float(monetary[name][j])})
        for comparator in ('half','plugin'):
            delta=gains['conservative']-gains[comparator]
            bs=bootstrap_means(delta,days,seed=SEED+1)
            results.append({'eta':s['eta'],'risk':s['risk'],
                            'strategy':'conservative_minus_'+comparator,
                            'mean_objective_gain_bps':float(delta.mean()),
                            'objective_95_interval':np.quantile(bs[:,0],[.025,.975]).tolist()})
    report={'status':'locked evaluation under hypothetical execution costs',
            'evaluated_utc':datetime.now(timezone.utc).isoformat(),
            'lock_sha256':filehash(ROOT/'calibration_lock.json'),
            'results':results}
    (ROOT/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
    with (ROOT/'episodes.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=episode_rows[0].keys());w.writeheader();w.writerows(episode_rows)
    print(json.dumps([r for r in results if r['eta']==2 and r['risk']==1],indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['fit','evaluate'])
    args=p.parse_args()
    fit() if args.stage=='fit' else evaluate()
