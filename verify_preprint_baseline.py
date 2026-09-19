"""Reproducible numerical evidence for the separate preprint comparison note."""
import json
from pathlib import Path
import numpy as np
from ou_execution import signal_kernel, inventory_rate, DiscreteOUExecution


def clipping_counterexample():
    """Deterministic OU, risk-neutral buy program; even stopping at x=0 fails.

    phi>0, nu=0, eta=Q=T=1, f0=16. The true buy-only optimum has a
    free completion time z and rate integral_t^z f(s)/(2*eta) ds.
    """
    eta,Q,T,phi,f0=1.,1.,1.,.1,16.
    scale=f0/(2*eta*phi)
    def integral_drift(t):
        return -np.expm1(-phi*t)/phi
    def bisection(function,lo,hi):
        flo=function(lo)
        if flo*function(hi)>0:
            raise ValueError('root not bracketed')
        for _ in range(80):
            mid=(lo+hi)/2
            if function(mid)*flo>0:
                lo,flo=mid,function(mid)
            else:
                hi=mid
        return (lo+hi)/2
    # Inventory equals integral of a nonnegative, decreasing execution rate.
    end=bisection(lambda z:scale*(integral_drift(z)-z*np.exp(-phi*z))-Q,1e-5,T)
    c0=Q/T+scale*(1-integral_drift(T)/T)
    def q_unconstrained(t):
        return Q-c0*t+scale*(t-integral_drift(t))
    # Unconstrained policy crosses x=0 before half the original horizon here.
    clipped_end=bisection(q_unconstrained,0,T/2)
    def cost(t,v,q):
        return float(np.trapezoid(eta*v*v+f0*np.exp(-phi*t)*q,t))
    t=np.linspace(0,end,20001)
    v=scale*(np.exp(-phi*t)-np.exp(-phi*end))
    q=Q-scale*(integral_drift(t)-t*np.exp(-phi*end))
    optimum=cost(t,v,q)
    tc=np.linspace(0,clipped_end,20001)
    vc=c0-scale*(1-np.exp(-phi*tc))
    qc=q_unconstrained(tc)
    clipped=cost(tc,vc,qc)
    return {'parameters':{'Q':Q,'T':T,'eta':eta,'phi':phi,'f0':f0,'nu':0,'risk_weight':0},
            'optimal_completion_time':end,'clipped_completion_time':clipped_end,
            'optimal_buy_only_cost':optimum,'clipped_with_inventory_stop_cost':clipped,
            'excess_cost':clipped-optimum,
            'relative_excess_percent':100*(clipped/optimum-1),
            'note':'Corrected unconstrained kernel used; original divergent kernel is never evaluated as a policy.'}


def main():
    tau,kappa,phi=1.,1.,1.
    wrong=[]
    for epsilon in (1e-2,1e-4,1e-6,1e-8):
        # Endpoint-distance r=tau-u on a log grid resolves the logarithmic pole.
        z=np.linspace(np.log(epsilon),np.log(tau),20000)
        r=np.exp(z)
        integrand=np.exp(-phi*(tau-r))*np.sinh(kappa*tau)/np.sinh(kappa*r)*r
        wrong.append({'endpoint_cutoff':epsilon,
                      'printed_integral_truncated':float(np.trapezoid(integrand,z))})
    eps=1e-5
    b=signal_kernel(tau,kappa,phi)
    residual=(signal_kernel(tau+eps,kappa,phi)-signal_kernel(tau-eps,kappa,phi))/(2*eps)
    residual+=(inventory_rate(tau,kappa)+phi)*b-1
    m=DiscreteOUExecution()
    gains=[]
    for a,beta in [(1.,.3),(.5,.3),(0.,.3),(1.,1.)]:
        actual=m.expected_cost(0,beta)-m.expected_cost(a,beta)
        gains.append({'assumed_amplitude':a,'true_amplitude':beta,
                      'expected_objective_gain':actual,
                      'identity_error':abs(actual-m.gain_scale()*(a*beta-a*a/2))})
    results={'status':'baseline verification, synthetic parameters; no novelty or crypto-profit claim',
             'corrected_B_at_tau1_kappa1_phi1':b,'corrected_ode_residual':residual,
             'printed_kernel_divergence':wrong,
             'clipping_counterexample':clipping_counterexample(),
             'discrete_feedback_gain_scale':m.gain_scale(),
             'feedback_gain_checks':gains}
    Path('results/preprint_baseline_checks.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':
    main()
