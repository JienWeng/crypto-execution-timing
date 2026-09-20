"""Post-run numerical audit of mathematical identity; does not alter experiment."""
import json
import numpy as np
import selection_study as s
fits=json.loads((s.HERE/'results/fits.json').read_text());rows=[];max_error=0.
for sym in s.SYMBOLS:
    cache={m:s.load(sym,m)[0] for m in s.MONTHS}
    for fit in [f for f in fits if f['symbol']==sym]:
      model={k:np.array(fit[k]) for k in ['center','scale','coeff']}
      for stage in ['calibration','evaluation']:
        X,P,days,idx=cache[fit[stage]];mu=s.predict(model,X)
        for eta,r in s.SCENARIOS:
          n=15;L=np.tril(np.ones((n,n)));H=2*eta*n*np.eye(n)+2*r/n*L.T@L;b=2*r/n*L.T@np.ones(n);inv=np.linalg.inv(H);z=inv@np.ones(n);Q=inv-np.outer(z,z)/z.sum()
          V=(mu+b)@inv.T;V-=(V.sum(2)-1)[:,:,None]*z[None,None,:]/z.sum();eligible=np.min(V,2)>=0
          u0=V[0];d=V-u0
          gain=(d*P).sum(2)-eta*n*((V*V).sum(2)-(u0*u0).sum(1))-r/n*(((1-np.cumsum(V,2))**2).sum(2)-((1-np.cumsum(u0,1))**2).sum(1))
          expected=np.einsum('mni,ij,nj->mn',mu,Q,P)-.5*np.einsum('mni,ij,mnj->mn',mu,Q,mu)
          max_error=max(max_error,float(np.max(np.abs(gain-expected))))
          qerrors=np.einsum('mni,ij,mnj->mn',mu-P,Q,mu-P).mean(1)
          empirical=s.solve(mu,eta,r)[0];actual=s.score(empirical,P,eta,r)['gain'].mean(1)
          rows.append({'symbol':sym,'evaluation':fit['evaluation'],'stage':stage,'eta':eta,'risk':r,'episodes_per_candidate':len(P),'candidate_equality_infeasible_counts':{name:int((~eligible[j]).sum()) for j,name in enumerate(s.NAMES)},'all_candidates_equality_feasible':bool(eligible.all()),'weighted_error_choice':s.NAMES[s.first_min(qerrors)],'utility_choice':s.NAMES[s.first_min(-actual)]})
print('max identity error',max_error)
(s.HERE/'geometry_audit.json').write_text(json.dumps({'scope':'post-run verification, no model or selector changes','max_equality_solution_identity_error':max_error,'rows':rows},indent=2)+'\n')
