import unittest
import numpy as np
from ou_execution import DiscreteOUExecution, inventory_rate, signal_kernel


class CorrectedKernelTests(unittest.TestCase):
    def test_ode_residual(self):
        for tau,kappa,phi in [(1.,.8,1.2),(.1,2.,.3),(.5,1.,1.)]:
            eps=1e-5*tau
            derivative=(signal_kernel(tau+eps,kappa,phi)-signal_kernel(tau-eps,kappa,phi))/(2*eps)
            residual=derivative+(inventory_rate(tau,kappa)+phi)*signal_kernel(tau,kappa,phi)-1
            self.assertLess(abs(residual),1e-8)

    def test_terminal_asymptotic(self):
        self.assertEqual(signal_kernel(0,1,1),0)
        self.assertAlmostEqual(signal_kernel(1e-6,1,1)/1e-6,.5,places=6)

    def test_zero_parameters_and_removable_singularity(self):
        self.assertAlmostEqual(signal_kernel(.8,0,0),.4,places=12)
        self.assertAlmostEqual(signal_kernel(.8,1.4,0),np.tanh(1.4*.8/2)/1.4,places=12)
        k,tau=1.3,.8
        self.assertAlmostEqual(signal_kernel(tau,k,k),1/(2*k)-tau/np.expm1(2*k*tau),places=12)

    def test_independent_bellman_convergence(self):
        eta,r,phi=.05,.1,1.2
        expected=signal_kernel(1,np.sqrt(r/eta),phi)
        errors=[]
        for n in (100,400,1600):
            m=DiscreteOUExecution(steps=n,impact=eta,risk_weight=r,phi=phi)
            errors.append(abs(m.B[0]-expected))
        self.assertLess(errors[-1],errors[0]/10)
        self.assertLess(errors[-1],.001)


class FeedbackTests(unittest.TestCase):
    def test_clipping_is_not_constrained_optimality(self):
        from verify_preprint_baseline import clipping_counterexample
        result=clipping_counterexample()
        self.assertGreater(result['excess_cost'],.4)
        self.assertLess(result['clipped_completion_time'],result['optimal_completion_time'])

    def test_value_recursion_against_moment_accounting(self):
        for side in (-1,1):
            m=DiscreteOUExecution(side=side)
            for a in (-.5,0,.4,1):
                self.assertAlmostEqual(m.expected_cost(a,a),m.optimal_value(a),places=12)

    def test_stochastic_feedback_gain_identity(self):
        for nu in (0.,.2,.7):
            for side in (-1,1):
                m=DiscreteOUExecution(signal_vol=nu,side=side)
                for a,beta in [(1,.3),(.5,.3),(.2,-.4),(1,1)]:
                    actual=m.expected_cost(0,beta)-m.expected_cost(a,beta)
                    target=m.gain_scale()*(a*beta-a*a/2)
                    self.assertAlmostEqual(actual,target,places=12)

    def test_buy_sell_symmetry(self):
        buy,sell=DiscreteOUExecution(side=1),DiscreteOUExecution(side=-1)
        self.assertAlmostEqual(buy.expected_cost(.6,.4,initial_signal=.1),
                               sell.expected_cost(.6,.4,initial_signal=-.1),places=12)

    def test_final_trade_clears_inventory(self):
        m=DiscreteOUExecution()
        self.assertEqual(m.k[-1],1)
        self.assertEqual(m.l[-1],0)

    def test_signed_controls_are_not_claimed_one_sided(self):
        m=DiscreteOUExecution()
        self.assertLess(m.k[0]*1+m.l[0]*(-100),0)


if __name__=='__main__':
    unittest.main()
