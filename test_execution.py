"""Numerical mathematical checks, not evidence of empirical effectiveness."""
import unittest
import numpy as np
from execution_model import ExecutionModel


class ModelChecks(unittest.TestCase):
    def setUp(self):
        self.m = ExecutionModel(0.1*np.exp(-2*np.arange(30)/30))

    def test_zero_risk_baseline_is_twap(self):
        m = ExecutionModel(np.ones(20), risk=0)
        np.testing.assert_allclose(m.u0, np.ones(20)/20, atol=1e-13)

    def test_kkt_independent_oracle(self):
        m = self.m
        kkt = np.block([[m.H, np.ones((m.n, 1))],
                        [np.ones((1, m.n)), np.zeros((1, 1))]])
        for a in (0, .2, .7):
            oracle = np.linalg.solve(kkt, np.r_[m.b+a*m.h, m.quantity])[:-1]
            np.testing.assert_allclose(m.schedule(a), oracle, atol=1e-12)

    def test_identity_random_forecasts_and_true_amplitudes(self):
        rng = np.random.default_rng(42)
        for _ in range(30):
            m = ExecutionModel(rng.normal(0, .3, 20))
            a = .8*m.exposure_limit()
            beta = rng.uniform(-2, 2)
            observed = m.objective(m.u0, beta)-m.objective(m.schedule(a), beta)
            self.assertAlmostEqual(observed, m.K*(a*beta-a*a/2), places=12)

    def test_sell_only_and_completion_at_boundary(self):
        m = ExecutionModel(10*np.exp(-np.arange(30)/10))
        a = m.exposure_limit()
        self.assertLess(a, 1)
        u = m.schedule(a)
        self.assertGreaterEqual(u.min(), -1e-12)
        self.assertAlmostEqual(u.sum(), 1, places=12)
        with self.assertRaises(ValueError):
            m.schedule(a+.01)

    def test_maximin_against_grid(self):
        m = self.m
        for lower, upper in [(-.5, .5), (.2, .8), (1.2, 1.5)]:
            a = m.safe_amplitude(lower, upper)
            grid = np.linspace(0, m.exposure_limit(), 10001)
            gains = m.K*(grid*lower-grid**2/2)
            gain = m.K*(a*lower-a*a/2)
            self.assertGreaterEqual(gain+1e-14, gains.max())
            self.assertGreaterEqual(gain, 0)

    def test_switch_off_and_zero_signal(self):
        self.assertEqual(self.m.safe_amplitude(-.1, .5), 0)
        m = ExecutionModel(np.zeros(10))
        self.assertEqual(m.K, 0)
        np.testing.assert_array_equal(m.direction, np.zeros(10))

    def test_break_even_and_false_interval_failure(self):
        m = self.m
        self.assertAlmostEqual(m.objective(m.u0, .5), m.objective(m.schedule(1), .5))
        a = m.safe_amplitude(.4, .8)
        self.assertLess(m.objective(m.u0, -.2)-m.objective(m.schedule(a), -.2), 0)

    def test_shape_error_generalization(self):
        m = self.m
        actual_drift = np.linspace(-.2, .4, m.n)
        h_actual = -m.dt*m.L.T@actual_drift
        a = .4
        u = m.schedule(a)
        q0, q = m.quantity-m.L@m.u0, m.quantity-m.L@u
        gain = (m.objective(m.u0, 0)-m.objective(u, 0)
                -m.dt*actual_drift@(q0-q))
        self.assertAlmostEqual(gain, a*m.direction@h_actual-a*a*m.K/2, places=12)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            ExecutionModel(np.ones(3), impact=0)
        with self.assertRaises(ValueError):
            self.m.safe_amplitude(1, -1)


if __name__ == '__main__':
    unittest.main()
