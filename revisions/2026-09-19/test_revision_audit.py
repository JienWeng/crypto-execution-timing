"""Independent synthetic audit; never reads empirical extension outputs."""
import unittest
import numpy as np
import revision_study as m

class IndependentRevisionAudit(unittest.TestCase):
    def test_all_cost_scenarios_against_original_solver(self):
        rng=np.random.default_rng(1919)
        prices=rng.normal(size=(18,15))*8
        forecast=np.vstack([rng.normal(size=(6,15))*.01,rng.normal(size=(6,15))*4,rng.normal(size=(6,15))*50])
        for eta,risk in m.SCENARIOS:
            c=m.components(prices,forecast,eta,risk)
            old=m.original.components(prices,forecast,eta,risk)
            for key in ['d','R','C','monetary_R','monetary_C']:
                np.testing.assert_allclose(c[key],old[key],atol=5e-10,rtol=1e-10)
            self.assertTrue(np.any(c['active']))
            self.assertTrue(np.any(~c['active']))
            np.testing.assert_allclose(c['R'],c['alignment']-c['gradient'],atol=1e-14)
            self.assertGreaterEqual(c['gradient'].min(),-1e-10)

    def test_episode_specific_price_and_forecast_level_invariance(self):
        rng=np.random.default_rng(1920)
        p=rng.normal(size=(12,15));mu=rng.normal(size=(12,15))*20
        shifts=rng.normal(size=(12,1))*100
        c=m.components(p,mu,.5,1)
        f=m.components(p,mu+shifts,.5,1)
        r=m.components(p+shifts,mu,.5,1)
        np.testing.assert_allclose(c['d'],f['d'],atol=1e-10)
        np.testing.assert_allclose(c['R']-c['C'],r['R']-r['C'],atol=1e-10)

    def test_matched_terminal_diagnostics(self):
        rng=np.random.default_rng(1921)
        mu=rng.normal(size=(100,15));p=rng.normal(size=(100,15))
        expected=m.numeric_metrics(mu,p)
        for profile in m.profiles(mu).values():
            metrics=m.numeric_metrics(profile,p)
            for key in expected:
                self.assertAlmostEqual(metrics[key],expected[key],places=13)

    def test_parallel_no_timing_gain_all_scenarios(self):
        rng=np.random.default_rng(1922)
        p=rng.normal(size=(20,15))*20
        mu=np.repeat(rng.normal(size=(20,1))*10,15,axis=1)
        for eta,risk in m.SCENARIOS:
            c=m.components(p,mu,eta,risk)
            self.assertLess(np.max(np.abs(c['d'])),1e-11)
            self.assertLess(np.max(np.abs(c['R']-c['C'])),1e-9)
            self.assertLess(np.max(c['shifted']),1e-10)
            self.assertEqual(m.estimate(c,np.arange(20))['plugin'],0)
            self.assertEqual(m.estimate(c,np.arange(20))['conservative'],0)

    def test_pooled_day_bootstrap_keeps_cross_asset_pairs(self):
        # Two assets concatenated; unequal daily episode counts are intentional.
        values=np.array([[1.,10.],[3.,30.],[8.,80.],[101.,1010.],[103.,1030.],[108.,1080.]])
        days=np.array([10,10,11,10,10,11]);seed=19;reps=100
        got=m.bootstrap(values,days,seed,reps)
        draw=np.random.default_rng(seed).integers(0,2,(reps,2))
        grouped=[values[days==day] for day in [10,11]]
        expected=np.array([np.concatenate([grouped[k] for k in row]).mean(axis=0) for row in draw])
        np.testing.assert_allclose(got,expected)

    def test_calibration_uses_ratio_of_sums(self):
        c={'R':np.array([.4,3.,.2,1.]),'C':np.array([.1,3.,.2,2.])}
        got=m.estimate(c,np.array([1,1,2,2]))
        expected=c['R'].sum()/(2*c['C'].sum())
        self.assertAlmostEqual(got['theta'],expected)
        self.assertAlmostEqual(got['plugin'],expected)
        self.assertNotAlmostEqual(got['theta'],np.mean(c['R']/(2*c['C'])))

if __name__=='__main__':unittest.main()
