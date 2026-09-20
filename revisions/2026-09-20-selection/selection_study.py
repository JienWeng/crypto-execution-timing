"""Frozen, retrospective selection experiment. See protocol.md; never edits old results."""
import csv,gzip,hashlib,io,json,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'revisions/2026-09-19'))
from download_extended import validate_rows
NAMES=['zero','mean','flow1','flow5','momentum5','ridge_01','ridge_1']
SELECTORS=['endpoint','path','contrasts','economic']
POLICIES=NAMES+SELECTORS
SYMBOLS=['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT']
TRANSFER=SYMBOLS[2:]
MONTHS=[f'2026-{m:02d}' for m in range(1,9)]
SCENARIOS=[(.5,0),(.5,1),(2.,0),(2.,1),(5.,0),(5.,1)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def features(a):
    idx=np.concatenate([d+np.arange(5,1425,30) for d in range(0,len(a),1440)])
    v1=a[idx-1,5]; b1=a[idx-1,9]
    v5=np.array([a[i-5:i,5].sum() for i in idx]);b5=np.array([a[i-5:i,9].sum() for i in idx])
    flow1=np.divide(2*b1-v1,v1,out=np.zeros_like(v1),where=v1>0)
    flow5=np.divide(2*b5-v5,v5,out=np.zeros_like(v5),where=v5>0)
    X=np.column_stack([flow1,flow5,1e4*np.log(a[idx,1]/a[idx-1,1]),1e4*np.log(a[idx,1]/a[idx-5,1]),np.log1p(v5)])
    P=1e4*(a[idx[:,None]+np.arange(1,16),1]/a[idx,None,1]-1)
    days=(a[idx,0].astype(np.int64)//86400000000).astype(int)
    return X,P,days,idx

def load(symbol,month):
    p=ROOT/'data/raw'/f'{symbol}-1m-{month}.zip';checksum=Path(str(p)+'.CHECKSUM').read_text().split()[0]
    if sha(p)!=checksum:raise ValueError('Checksum mismatch')
    with zipfile.ZipFile(p) as z:rows=list(csv.reader(io.StringIO(z.read(z.namelist()[0]).decode())))
    meta=validate_rows(rows,month)
    return features(np.asarray(rows,dtype=float)),{'symbol':symbol,'month':month,'sha256':checksum,'rows':meta['rows']}

def fit(X,Y):
    center=X.mean(0);scale=X.std(0);scale=np.where(scale>1e-12,scale,1.);Z=(X-center)/scale
    coeff=[]
    zero=np.zeros((6,15));coeff.append(zero);mean=zero.copy();mean[0]=Y.mean(0);coeff.append(mean)
    for col in [0,1,3]:
        c=zero.copy();ols=np.linalg.lstsq(np.column_stack([np.ones(len(X)),Z[:,col]]),Y,rcond=None)[0];c[0]=ols[0];c[col+1]=ols[1];coeff.append(c)
    for penalty in [.1,1.]:
        c=zero.copy();c[0]=Y.mean(0);c[1:]=np.linalg.solve(Z.T@Z/len(X)+penalty*np.eye(5),Z.T@(Y-Y.mean(0))/len(X));coeff.append(c)
    return {'center':center,'scale':scale,'coeff':np.stack(coeff)}
def predict(model,X):
    Z=np.column_stack([np.ones(len(X)),(X-model['center'])/model['scale']])
    return np.einsum('nf,mfj->mnj',Z,model['coeff'])
def project(V):
    s=np.sort(V,axis=1)[:,::-1];css=np.cumsum(s,axis=1)-1
    rho=(s-css/np.arange(1,V.shape[1]+1)>0).sum(1)-1
    theta=css[np.arange(len(V)),rho]/(rho+1)
    return np.maximum(V-theta[:,None],0)
def solve(mu,eta,r):
    shape=mu.shape;M=mu.reshape(-1,15);n=15;L=np.tril(np.ones((n,n)))
    H=2*eta*n*np.eye(n)+2*r/n*L.T@L;b=2*r/n*L.T@np.ones(n)
    inv=np.linalg.inv(H);z=inv@np.ones(n);U=(M+b)@inv.T
    U-=(U.sum(1)-1)[:,None]*z[None,:]/z.sum();bad=np.any(U<0,axis=1)
    if bad.any():
        V=project(U[bad]);target=M[bad]+b;step=1/np.linalg.eigvalsh(H)[-1]
        for it in range(20000):
            W=project(V-step*(V@H-target))
            if np.max(np.abs(W-V))<1e-12:V=W;break
            V=W
        else:raise RuntimeError('batch QP did not converge')
        U[bad]=V
    g=U@H-(M+b);active=U>1e-9;level=(g*active).sum(1)/active.sum(1)
    residual=max(float(np.max(np.where(active,np.abs(g-level[:,None]),0))),float(np.maximum(level[:,None]-g,0).max()),float(np.abs(U.sum(1)-1).max()),float(np.maximum(-U,0).max()))
    if residual>1e-7:raise ValueError(f'KKT {residual}')
    return U.reshape(shape),residual

def score(U,P,eta,r):
    # zero forecast included as index0; its schedule is the exact cost baseline.
    u0=U[0];d=U-u0[None,:,:];q=1-np.cumsum(U,axis=-1);q0=1-np.cumsum(u0,axis=-1)
    alignment=np.sum(d*P[None,:,:],axis=-1)
    impact=eta*15*(np.sum(U*U,axis=-1)-np.sum(u0*u0,axis=-1)[None,:])
    inventory=r/15*(np.sum(q*q,axis=-1)-np.sum(q0*q0,axis=-1)[None,:])
    return {'gain':alignment-impact-inventory,'money':alignment-impact,'alignment':alignment,'cost':impact+inventory,'shifted':np.sum(np.abs(d),axis=-1)/2}

def first_min(v):return int(np.flatnonzero(v<=v.min()+1e-12)[0])
def selection(pred,truth,gain):
    endpoint=np.mean((pred[:,:,-1]-truth[None,:,-1])**2,axis=1)
    path=np.mean((pred-truth[None,:,:])**2,axis=(1,2))
    contrasts=np.mean(((pred-pred.mean(2,keepdims=True))-(truth-truth.mean(1,keepdims=True))[None,:,:])**2,axis=(1,2))
    scores={'endpoint':endpoint,'path':path,'contrasts':contrasts,'economic':-gain.mean(1)}
    return {n:first_min(v) for n,v in scores.items()},scores

def bootstrap(daily,block=7,reps=4000,seed=20260920):
    rng=np.random.default_rng(seed);n=len(daily);starts=rng.integers(n,size=(reps,(n+block-1)//block))
    idx=((starts[:,:,None]+np.arange(block))%n).reshape(reps,-1)[:,:n]
    return daily[idx].mean(1)

def summarize(rows):
    output=[]
    for cohort,syms in [('transfer',TRANSFER),('development',SYMBOLS[:2])]:
      for eta,r in SCENARIOS:
        part=[v for v in rows if v['symbol'] in syms and v['eta']==eta and v['risk']==r]
        days=sorted(set(v['day'] for v in part));lookup={(v['symbol'],v['day'],v['policy']):v for v in part}
        assert len(part)==len(days)*len(syms)*len(POLICIES)
        daily=np.array([[np.mean([lookup[(sym,d,p)]['gain'] for sym in syms]) for p in POLICIES] for d in days])
        money=np.array([[np.mean([lookup[(sym,d,p)]['money'] for sym in syms]) for p in POLICIES] for d in days])
        names=POLICIES+['economic_minus_'+p for p in ['endpoint','path','contrasts','zero']]
        contrast=np.column_stack([daily[:,POLICIES.index('economic')]-daily[:,POLICIES.index(p)] for p in ['endpoint','path','contrasts','zero']])
        data=np.column_stack([daily,contrast]);bs=bootstrap(data)
        moneybs=bootstrap(money)
        for i,name in enumerate(names):
          row={'cohort':cohort,'eta':eta,'risk':r,'policy':name,'mean_gain':float(data[:,i].mean()),'ci95':np.quantile(bs[:,i],[.025,.975]).tolist(),'dates':len(days),'episodes':len(days)*len(syms)*48}
          if i<len(POLICIES):row.update(mean_money=float(money[:,i].mean()),money_ci95=np.quantile(moneybs[:,i],[.025,.975]).tolist())
          if eta==2 and r==1:
            row['block_sensitivity']={str(k):np.quantile(bootstrap(data[:,i,None],k)[:,0],[.025,.975]).tolist() for k in [1,14]}
            row['leave_month_out']={str(m):float(data[np.array([datetime.fromtimestamp(d*86400,timezone.utc).month!=m for d in days]),i].mean()) for m in range(3,9)}
          output.append(row)
    return output

def run():
    out=HERE/'results'
    if out.exists() and any(out.iterdir()):raise FileExistsError('Preserve all prior/partial results; use an explicitly named new run directory')
    out.mkdir(exist_ok=True)
    lock=json.loads((HERE/'protocol_lock.json').read_text());assert sha(HERE/'protocol.md')==lock['sha256']
    manifest={'started_utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':sha(HERE/'protocol.md'),'code_sha256':sha(__file__),'validator_sha256':sha(ROOT/'revisions/2026-09-19/download_extended.py'),'seed':20260920,'bootstrap':'4000 circular moving block draws, seven calendar days, paired assets; policies fixed'}
    (out/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    daily=[];windows=[];fits=[];inputs=[];maxkkt=0.;audit=[]
    f=gzip.open(out/'primary_episodes.csv.gz','wt',newline='');writer=None
    for sym in SYMBOLS:
      cache={}
      for m in MONTHS:cache[m],meta=load(sym,m);inputs.append(meta)
      for end in range(2,8):
        tr,ca,ev=MONTHS[end-2:end+1];xt,yt,dt,it=cache[tr];xc,yc,dc,ic=cache[ca];xe,ye,de,ie=cache[ev]
        model=fit(xt,yt);pc=predict(model,xc);pe=predict(model,xe)
        fits.append({'symbol':sym,'training':tr,'calibration':ca,'evaluation':ev,**{k:v.tolist() for k,v in model.items()}})
        for eta,r in SCENARIOS:
          uc,resc=solve(pc,eta,r);cc=score(uc,yc,eta,r);chosen,metrics=selection(pc,yc,cc['gain'])
          # All selection IDs fixed before scoring evaluation prices.
          ue,rese=solve(pe,eta,r);ce=score(ue,ye,eta,r);maxkkt=max(maxkkt,resc,rese)
          selected=np.array(list(range(len(NAMES)))+[chosen[n] for n in SELECTORS])
          values={k:v[selected] for k,v in ce.items()}
          windows.append({'symbol':sym,'training':tr,'calibration':ca,'evaluation':ev,'eta':eta,'risk':r,'episodes':len(ye),'chosen':{k:NAMES[v] for k,v in chosen.items()},'calibration_scores':{k:v.tolist() for k,v in metrics.items()},'gains':{p:float(values['gain'][j].mean()) for j,p in enumerate(POLICIES)},'money':{p:float(values['money'][j].mean()) for j,p in enumerate(POLICIES)}})
          for day in np.unique(de):
            mask=de==day
            for j,name in enumerate(POLICIES):daily.append({'symbol':sym,'day':int(day),'month':ev,'eta':eta,'risk':r,'policy':name,**{k:float(v[j,mask].mean()) for k,v in values.items()}})
          if eta==2 and r==1:
            for k,day in enumerate(de):
              row={'symbol':sym,'day':int(day),'month':ev,'minute_index':int(ie[k])};row.update({name:float(values['gain'][j,k]) for j,name in enumerate(POLICIES)})
              if writer is None:writer=csv.DictWriter(f,fieldnames=list(row));writer.writeheader()
              writer.writerow(row)
            # Full forecast errors and fixed candidates retained as diagnostics.
            audit.append({'symbol':sym,'month':ev,'endpoint_mse':np.mean((pe[:,:,-1]-ye[None,:,-1])**2,axis=1).tolist(),'path_mse':np.mean((pe-ye[None,:,:])**2,axis=(1,2)).tolist()})
        print(f'{sym} {ev} completed',flush=True)
    f.close()
    with gzip.open(out/'daily.csv.gz','wt',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(daily[0]));w.writeheader();w.writerows(daily)
    report={'status':'retrospective historical asset transfer, not prospective confirmation','completed_utc':datetime.now(timezone.utc).isoformat(),'candidate_names':NAMES,'policies':POLICIES,'inputs':inputs,'max_kkt_residual':maxkkt,'windows':windows,'summary':summarize(daily),'evaluation_forecast_errors':audit}
    (out/'fits.json').write_text(json.dumps(fits,indent=2)+'\n')
    (out/'study.json').write_text(json.dumps(report,indent=2)+'\n')
    assert manifest['code_sha256']==sha(__file__) and manifest['protocol_sha256']==sha(HERE/'protocol.md')
    print('COMPLETE',flush=True)
    print(json.dumps([v for v in report['summary'] if v['cohort']=='transfer' and v['eta']==2 and v['risk']==1 and v['policy'].startswith('economic')],indent=2))
if __name__=='__main__':run()
