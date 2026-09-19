"""Corrected OU baseline and exact discrete Bellman verification model.

New follow-up research code. Does not modify or reproduce the printed, divergent
Equation (10). Controls are unrestricted signed trades: no clipping or assertion
of buy-only/sell-only optimality. risk_weight means lambda*sigma**2.
"""
import numpy as np


def signal_kernel(tau, kappa, phi, order=96):
    """Correct B(t), evaluated by stable Gauss-Legendre quadrature in tau=T-t."""
    if not np.isfinite([tau, kappa, phi]).all() or min(tau, kappa, phi) < 0:
        raise ValueError('finite, nonnegative tau/kappa/phi required')
    if tau == 0:
        return 0.0
    nodes, weights = np.polynomial.legendre.leggauss(order)
    z = (nodes+1)/2
    if kappa*tau < 1e-8:
        ratio = 1-z
    else:
        # sinh(kappa*tau*(1-z))/sinh(kappa*tau), without overflow.
        ratio = (np.exp(-kappa*tau*z)*(-np.expm1(-2*kappa*tau*(1-z)))
                 /(-np.expm1(-2*kappa*tau)))
    return float(tau/2*np.sum(weights*np.exp(-phi*tau*z)*ratio))


def inventory_rate(tau, kappa):
    if tau <= 0 or kappa < 0 or not np.isfinite([tau,kappa]).all():
        raise ValueError('tau must be positive; kappa nonnegative')
    return 1/tau if kappa == 0 else kappa/np.tanh(kappa*tau)


class DiscreteOUExecution:
    """Exact discrete-time LQ controller with compulsory terminal execution.

    State x is remaining quantity. u executes at interval start. q=x-u is
    exposed to drift side*beta*f*dt and risk_weight*q**2*dt. Signal follows
    exact sampled OU dynamics. side=+1 denotes purchase cost, -1 liquidation.
    """
    def __init__(self, steps=100, horizon=1., impact=.05, risk_weight=.1,
                 phi=1.2, signal_vol=.2, side=1):
        if not isinstance(steps,int) or steps<2:
            raise ValueError('steps must be an integer >=2')
        params = [horizon, impact, risk_weight, phi, signal_vol]
        if not np.isfinite(params).all() or min(params[:2]) <= 0 or min(params[2:]) < 0:
            raise ValueError('invalid model parameters')
        if side not in (-1,1):
            raise ValueError('side must be +1 for buy, -1 for sell')
        self.steps, self.dt = steps, horizon/steps
        self.impact, self.risk_weight, self.side = impact, risk_weight, side
        self.phi, self.signal_vol = phi, signal_vol
        self.rho = np.exp(-phi*self.dt)
        self.noise_var = (signal_vol**2*self.dt if phi==0 else
                          signal_vol**2*(-np.expm1(-2*phi*self.dt))/(2*phi))
        self.A, self.B, self.C, self.D = (np.zeros(steps) for _ in range(4))
        self.k, self.l = np.zeros(steps), np.zeros(steps)
        m = impact/self.dt
        # Final trade clears all remaining inventory before any further drift.
        self.A[-1], self.k[-1] = m, 1.
        for i in range(steps-2,-1,-1):
            aa = self.A[i+1]+risk_weight*self.dt
            bb = self.rho*self.B[i+1]+side*self.dt
            denom = m+aa
            self.k[i], self.l[i] = aa/denom, bb/(2*denom)
            self.A[i] = m*aa/denom
            self.B[i] = m*bb/denom
            self.C[i] = self.rho**2*self.C[i+1]-bb**2/(4*denom)
            self.D[i] = self.D[i+1]+self.C[i+1]*self.noise_var

    def expected_cost(self, assumed_amplitude, true_amplitude, quantity=1., initial_signal=.1):
        """Exact second-moment evaluation, independent of value recursion."""
        if not np.isfinite([assumed_amplitude,true_amplitude,quantity,initial_signal]).all():
            raise ValueError('finite inputs required')
        initial = np.array([quantity,initial_signal])
        moment = np.outer(initial,initial)
        total = 0.
        e_signal = np.array([0.,1.])
        for k,l in zip(self.k,self.l):
            u = np.array([k,assumed_amplitude*l])
            q = np.array([1-k,-assumed_amplitude*l])
            total += (self.impact/self.dt*(u@moment@u)
                      +self.risk_weight*self.dt*(q@moment@q)
                      +self.side*true_amplitude*self.dt*(e_signal@moment@q))
            transition = np.array([q,[0.,self.rho]])
            moment = transition@moment@transition.T
            moment[1,1] += self.noise_var
        return float(total)

    def gain_scale(self, initial_signal=.1):
        # Improvement = K*(a*beta-a**2/2).
        return float(-2*(self.C[0]*initial_signal**2+self.D[0]))

    def optimal_value(self, amplitude, quantity=1., initial_signal=.1):
        return float(self.A[0]*quantity**2+amplitude*self.B[0]*quantity*initial_signal
                     +amplitude**2*(self.C[0]*initial_signal**2+self.D[0]))
