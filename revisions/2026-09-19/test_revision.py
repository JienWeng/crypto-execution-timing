import unittest
import numpy as np
import revision_study as m

class RevisionChecks(unittest.TestCase):
    def test_matched_endpoint_and_parallel_invariance(self):
        rng=np.random.default_rng(51); mu=rng.normal(size=(9,15)); p=rng.normal(size=(9,15))
        variants=m.profiles(mu)
        for value in variants.values():np.testing.assert_allclose(value[:,-1],mu[:,-1],atol=1e-14)
        a=m.components(p,mu,2,1); shifted=m.components(p,mu+17.3,2,1)
        np.testing.assert_allclose(a['d'],shifted['d'],atol=1e-12)
        b=m.components(p,variants['parallel'],2,1)
        np.testing.assert_allclose(b['d'],0,atol=1e-12)

    def test_fast_solver_against_locked_qp_active_and_interior(self):
        rng=np.random.default_rng(33);p=rng.normal(size=(17,15));mu=rng.normal(0,10,(17,15))
        for eta,risk in [(.5,1),(2,1),(5,0)]:
            fast=m.components(p,mu,eta,risk); ref=m.original.components(p,mu,eta,risk)
            for key in ['R','C','d','u0','monetary_R','monetary_C']:
                np.testing.assert_allclose(fast[key],ref[key],atol=2e-10)
            self.assertGreaterEqual(fast['gradient'].min(),-1e-9)

    def test_cost_and_inventory_increment_identities(self):
        rng=np.random.default_rng(42);p=rng.normal(size=(11,15));mu=rng.normal(0,4,(11,15));c=m.components(p,mu,.5,1)
        n=15;L=np.tril(np.ones((n,n)));u=c['u0'];v=u+.7*c['d']
        J=lambda U:-np.sum(p*U,axis=-1)+.5*n*np.sum(U*U,axis=-1)+np.sum((1-U@L.T)**2,axis=-1)/n
        np.testing.assert_allclose(J(u)-J(v),.7*c['R']-.49*c['C'],atol=1e-12)
        np.testing.assert_allclose(c['alignment'],-np.sum(np.cumsum(c['d'],axis=1)[:,:-1]*np.diff(p,axis=1),axis=1),atol=1e-12)

    def test_constructed_terminal_counterexample(self):
        p=np.array([[3.,2.]])
        for forecast,expected in [([2,2],0),([3,2],.125),([1,2],-.375)]:
            c=m.components(p,np.array([forecast]),.5,0)
            self.assertAlmostEqual(float(c['R'][0]-c['C'][0]),expected,places=12)

    def test_calendar_day_pooling_preserves_assets(self):
        values=np.array([1.,3.,10.,20.]);days=np.array([10,10,11,11])
        got=m.bootstrap(values,days,91,reps=40)
        draws=np.random.default_rng(91).integers(0,2,(40,2))
        expected=np.array([2.,15.])[draws].mean(axis=1)
        np.testing.assert_allclose(got[:,0],expected)

    def test_invalid_minute_grid_is_rejected(self):
        from download_extended import validate_rows
        # Incomplete grids and nonfinite fields must stop before positional indexing.
        x=np.ones((20,12));x[:,0]=np.arange(20)*60000000+1767225600000000
        with self.assertRaises(ValueError):validate_rows(x.tolist(),'2026-01')
        x[1,0]=x[0,0]
        with self.assertRaises(ValueError):validate_rows(x.tolist(),'2026-01')

if __name__=='__main__':unittest.main()
