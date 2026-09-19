"""Exploratory matched-terminal execution study. Frozen design: protocol.md.
Original production files and locks are imported/read, never rewritten.
"""
import csv
import gzip
import hashlib
import io
import json
import sys
import zipfile
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
import empirical_study as original
from download_extended import validate_rows

SCENARIOS=original.SCENARIOS
SYMBOLS=['BTCUSDT','ETHUSDT']
MONTHS=[f'2026-{m:02d}' for m in range(1,9)]

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def episodes(symbol,month,manifest):
    record=next(v for v in manifest['records'] if v['symbol']==symbol and v['month']==month)
    path=ROOT/'data/raw'/f'{symbol}-1m-{month}.zip'
    if record['status']!='verified' or digest(path)!=record['sha256']:raise ValueError('input digest/status mismatch')
    with zipfile.ZipFile(path) as z:
        raw=list(csv.reader(io.StringIO(z.read(z.namelist()[0]).decode())))
    validate_rows(raw,month)  # Reject malformed grids BEFORE positional indexing.
    a=np.asarray(raw,dtype=float)
    index=np.concatenate([d+np.arange(5,1425,30) for d in range(0,len(a),1440)])
    vol=np.array([a[i-5:i,5].sum() for i in index]);buy=np.array([a[i-5:i,9].sum() for i in index])
    x=np.divide(2*buy-vol,vol,out=np.zeros_like(vol),where=vol>0)
    p=10000*(a[index[:,None]+np.arange(1,16),1]/a[index,None,1]-1)
    days=(a[index,0].astype(np.int64)//86_400_000_000).astype(int)
    return x,p,days,index

def profiles(mu):
    terminal=mu[:,-1,None]
    return {'learned':mu,'parallel':np.broadcast_to(terminal,mu.shape).copy(),
            'ramp':terminal*np.arange(1,mu.shape[1]+1)/mu.shape[1],
            'mirror':2*terminal-mu}

def components(prices,forecast,eta,risk):
    """Fast equality solution if feasible, original simplex QP otherwise."""
    p=np.asarray(prices);mu=np.asarray(forecast);n=p.shape[1]
    L=np.tril(np.ones((n,n)));H=2*eta*n*np.eye(n)+2*risk/n*L.T@L
    b=2*risk/n*L.T@np.ones(n);u0,res=original.qp(H,b)
    inv=np.linalg.inv(H);z=inv@np.ones(n)
    U=(mu+b)@inv.T;U-=(U.sum(axis=1)-1)[:,None]*z[None,:]/z.sum()
    for k in np.flatnonzero(np.any(U<0,axis=1)):
        U[k],rr=original.qp(H,b+mu[k],u0);res=max(res,rr)
    g=U@H-(b+mu);active=U>1e-10
    level=np.sum(g*active,axis=1)/active.sum(axis=1)
    station=np.max(np.where(active,np.abs(g-level[:,None]),0))
    res=max(res,float(station),float(np.maximum(level[:,None]-g,0).max()),float(np.abs(U.sum(axis=1)-1).max()),float(np.maximum(-U,0).max()))
    if res>1e-8:raise ValueError(f'KKT failure {res}')
    d=U-u0;q0=1-L@u0;Ld=d@L.T
    alignment=np.sum(d*p,axis=1)
    gradient=2*eta*n*(d@u0)-2*risk/n*(Ld@q0)
    C=eta*n*np.sum(d*d,axis=1)+risk/n*np.sum(Ld*Ld,axis=1)
    return {'R':alignment-gradient,'C':C,'alignment':alignment,'gradient':gradient,
            'monetary_R':alignment-2*eta*n*(d@u0),'monetary_C':eta*n*np.sum(d*d,axis=1),
            'u0':u0,'d':d,'kkt':res,'active':np.any(U<1e-10,axis=1),
            'shifted':np.abs(d).sum(axis=1)/2}

def bootstrap(values,days,seed,reps=2000):
    return original.bootstrap_means(values,days,seed=seed,reps=reps)

def estimate(c,days):
    if c['C'].mean()<1e-14:return {'theta':None,'interval90':[None,None],'plugin':0.,'conservative':0.}
    b=bootstrap(np.column_stack([c['R'],c['C']]),days,20260919)
    ratio=c['R'].mean()/(2*c['C'].mean());lo,hi=np.quantile(b[:,0]/(2*b[:,1]),[.05,.95])
    return {'theta':float(ratio),'interval90':[float(lo),float(hi)],'plugin':float(np.clip(ratio,0,1)),'conservative':float(np.clip(lo,0,1))}

def numeric_metrics(mu,p):
    terminal=mu[:,-1];y=p[:,-1]
    corr=float(np.corrcoef(terminal,y)[0,1]) if terminal.std()>0 and y.std()>0 else None
    return {'terminal_rmse_bps':float(np.sqrt(np.mean((terminal-y)**2))),
            'terminal_r2_vs_zero':float(1-np.sum((terminal-y)**2)/np.sum(y*y)),
            'terminal_directional_accuracy':float(np.mean(np.sign(terminal)==np.sign(y))),
            'terminal_correlation':corr,
            'mean_terminal_forecast_bps':float(terminal.mean()),'mean_terminal_outcome_bps':float(y.mean())}

def main():
    out=HERE/'results';out.mkdir(exist_ok=True)
    manifest=json.loads((HERE/'data_manifest.json').read_text())
    if manifest['verified_archives']!=16:raise ValueError('incomplete fixed sample')
    provenance={'started_utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':digest(HERE/'protocol.md'),
                'code_sha256':digest(__file__),'data_manifest_sha256':digest(HERE/'data_manifest.json'),
                'original_code_sha256':digest(ROOT/'empirical_study.py'),
                'status':'review-driven retrospective exploratory extension; not preregistered'}
    (out/'run_manifest.json').write_text(json.dumps(provenance,indent=2)+'\n')
    cache={(s,m):episodes(s,m,manifest) for s in SYMBOLS for m in MONTHS}
    fits=[];rows=[];forecast_metrics=[];allterms=[];pooled={};primary=[];maxres=0
    for symbol in SYMBOLS:
      for end in range(2,8):
        train,cal,test=MONTHS[end-2:end+1]
        xt,pt,_,_=cache[symbol,train];xc,pc,dc,_=cache[symbol,cal];xe,pe,de,indices=cache[symbol,test]
        coef=np.linalg.lstsq(np.column_stack([np.ones(len(xt)),xt]),pt,rcond=None)[0]
        muc=(xc-xt.mean())[:,None]*coef[1];mue=(xe-xt.mean())[:,None]*coef[1]
        variants=profiles(mue)
        metrics=numeric_metrics(mue,pe)
        forecast_metrics.append({'symbol':symbol,'train':train,'calibration':cal,'evaluation':test,'episodes':len(xe),**metrics})
        fits.append({'symbol':symbol,'train':train,'calibration':cal,'evaluation':test,'signal_center':float(xt.mean()),'slopes':coef[1].tolist(),'intercepts':coef[0].tolist()})
        for eta,risk in SCENARIOS:
            cc=components(pc,muc,eta,risk);weights=estimate(cc,dc)
            comps={name:components(pe,mu,eta,risk) for name,mu in variants.items()}
            maxres=max(maxres,cc['kkt'],max(c['kkt'] for c in comps.values()))
            c=comps['learned'];gain={};money={};shift={};wmap={}
            for name,k in comps.items():
                gain[name]=k['R']-k['C'];money[name]=k['monetary_R']-k['monetary_C'];shift[name]=k['shifted'];wmap[name]=1.
                allterms.append({'symbol':symbol,'month':test,'eta':eta,'risk':risk,'profile':name,
                    'price_alignment':float(k['alignment'].mean()),'baseline_cost_gradient':float(k['gradient'].mean()),
                    'curvature':float(k['C'].mean()),'active_episodes':int(k['active'].sum()),
                    'mean_shifted_quantity':float(k['shifted'].mean()),'episodes':len(xe)})
            for name,w in [('half',.5),('plugin',weights['plugin']),('conservative',weights['conservative'])]:
                gain[name]=w*c['R']-w*w*c['C'];money[name]=w*c['monetary_R']-w*w*c['monetary_C'];shift[name]=w*c['shifted'];wmap[name]=w
            # Paired contrasts retain the same realized market outcomes.
            gain['learned_minus_ramp']=gain['learned']-gain['ramp'];gain['learned_minus_mirror']=gain['learned']-gain['mirror']
            money['learned_minus_ramp']=money['learned']-money['ramp'];money['learned_minus_mirror']=money['learned']-money['mirror']
            names=list(gain);G=np.column_stack([gain[k] for k in names]);M=np.column_stack([money[k] for k in names])
            bs=bootstrap(np.column_stack([G,M]),de,20260920)
            for j,name in enumerate(names):
                rows.append({'symbol':symbol,'train':train,'calibration':cal,'month':test,'eta':eta,'risk':risk,'policy':name,
                    'episodes':len(xe),'weight':wmap.get(name),'calibration_theta':weights['theta'],
                    'calibration_theta_interval90':weights['interval90'],'mean_gain':float(G[:,j].mean()),
                    'gain_ci95':np.quantile(bs[:,j],[.025,.975]).tolist(),
                    'mean_monetary_gain':float(M[:,j].mean()),'monetary_ci95':np.quantile(bs[:,len(names)+j],[.025,.975]).tolist()})
            pooled.setdefault((eta,risk),[]).append((G,M,de,names,symbol,test))
            if eta==2 and risk==1:
                for j,day in enumerate(de):
                    item={'symbol':symbol,'month':test,'utc_day':int(day),'minute_index':int(indices[j]),'terminal_forecast':float(mue[j,-1]),'terminal_outcome':float(pe[j,-1])}
                    item.update({name+'_gain':float(gain[name][j]) for name in names})
                    item.update({name:float(c[name][j]) for name in ['alignment','gradient','C','shifted']})
                    primary.append(item)
        print(f'{symbol} {test} done',flush=True)
    pooledrows=[]
    for (eta,risk),parts in pooled.items():
        G=np.concatenate([a[0] for a in parts]);M=np.concatenate([a[1] for a in parts]);days=np.concatenate([a[2] for a in parts]);names=parts[0][3]
        bs=bootstrap(np.column_stack([G,M]),days,20260920)
        for j,name in enumerate(names):
            pooledrows.append({'eta':eta,'risk':risk,'policy':name,'episodes':len(G),'calendar_days':len(np.unique(days)),
                'mean_gain':float(G[:,j].mean()),'gain_ci95':np.quantile(bs[:,j],[.025,.975]).tolist(),
                'equal_asset_month_mean_gain':float(np.mean([a[0][:,j].mean() for a in parts])),
                'mean_monetary_gain':float(M[:,j].mean()),'monetary_ci95':np.quantile(bs[:,len(names)+j],[.025,.975]).tolist()})
    report={'status':provenance['status'],'completed_utc':datetime.now(timezone.utc).isoformat(),'max_kkt_residual':maxres,
            'input_rows':sum(x['rows'] for x in manifest['records']),'asset_months':12,'window_results':rows,
            'pooled_results':pooledrows,'forecast_diagnostics':forecast_metrics,'decompositions':allterms,'fits':fits}
    (out/'study.json').write_text(json.dumps(report,indent=2)+'\n')
    with gzip.open(out/'primary_episodes.csv.gz','wt',newline='') as f:
        w=csv.DictWriter(f,fieldnames=primary[0]);w.writeheader();w.writerows(primary)
    # Check original July fit and August means, allowing the explicitly changed bootstrap seed.
    old=json.loads((ROOT/'results/empirical/evaluation.json').read_text())
    checks=[]
    for row in rows:
        if row['symbol']=='BTCUSDT' and row['month']=='2026-08' and row['policy'] in ['learned','half']:
            oldname='full' if row['policy']=='learned' else 'half'
            ref=next(v for v in old['results'] if v['eta']==row['eta'] and v['risk']==row['risk'] and v['strategy']==oldname)
            error=abs(row['mean_gain']-ref['mean_objective_gain_bps'])
            if error>1e-10:raise ValueError('original reproduction mismatch')
            checks.append(error)
    (out/'verification.json').write_text(json.dumps({'original_full_half_mean_max_abs_error':max(checks),
        'parallel_max_abs_mean_gain':max(abs(v['mean_gain']) for v in rows if v['policy']=='parallel'),
        'max_kkt_residual':maxres,'code_unchanged_during_run':digest(__file__)==provenance['code_sha256'],
        'protocol_unchanged_during_run':digest(HERE/'protocol.md')==provenance['protocol_sha256']},indent=2)+'\n')
    print(json.dumps([r for r in pooledrows if r['eta']==2 and r['risk']==1],indent=2))

if __name__=='__main__':main()
