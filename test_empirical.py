"""Independent synthetic checks for locked empirical implementation."""
import hashlib
import io
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import numpy as np
import empirical_study as study


class EmpiricalAuditTests(unittest.TestCase):
    def test_qp_against_exhaustive_active_sets(self):
        rng=np.random.default_rng(70)
        for _ in range(15):
            A=rng.normal(size=(4,4));H=A.T@A+np.eye(4);b=rng.normal(size=4)*3
            got,residual=study.qp(H,b)
            candidates=[]
            for width in range(1,5):
                for indices in itertools.combinations(range(4),width):
                    ind=np.array(indices);h=H[np.ix_(ind,ind)]
                    block=np.block([[h,np.ones((width,1))],[np.ones((1,width)),np.zeros((1,1))]])
                    sol=np.linalg.solve(block,np.r_[b[ind],1.])[:width]
                    if sol.min()>=-1e-12:
                        u=np.zeros(4);u[ind]=sol
                        candidates.append((.5*u@H@u-b@u,u))
            objective,expected=min(candidates,key=lambda p:p[0])
            np.testing.assert_allclose(got,expected,atol=1e-10)
            self.assertLess(residual,1e-8)

    def test_gain_decomposition_and_feasibility(self):
        rng=np.random.default_rng(81)
        p=rng.normal(size=(10,7))*5;mu=rng.normal(size=(10,7))*7
        eta=.5;risk=1.;n=7;L=np.tril(np.ones((n,n)))
        c=study.components(p,mu,eta,risk);u0=c['u0'];q0=1-L@u0
        for w in [0.,.1,.5,1.]:
            u=u0+w*c['d'];q=1-u@L.T
            self.assertGreaterEqual(u.min(),-1e-12)
            np.testing.assert_allclose(u.sum(axis=1),1,atol=1e-12)
            base=-p@u0+eta*n*(u0@u0)+risk/n*(q0@q0)
            cost=-np.sum(p*u,axis=1)+eta*n*np.sum(u*u,axis=1)+risk/n*np.sum(q*q,axis=1)
            np.testing.assert_allclose(base-cost,w*c['R']-w*w*c['C'],atol=1e-12)
            money_base=-p@u0+eta*n*(u0@u0)
            money_cost=-np.sum(p*u,axis=1)+eta*n*np.sum(u*u,axis=1)
            np.testing.assert_allclose(money_base-money_cost,w*c['monetary_R']-w*w*c['monetary_C'],atol=1e-12)
        ut=np.ones(n)/n;qt=1-L@ut
        direct=-p@u0+eta*n*u0@u0+risk/n*q0@q0-(-p@ut+eta*n*ut@ut+risk/n*qt@qt)
        np.testing.assert_allclose(direct,c['twap_gain'],atol=1e-12)

    def test_sale_sign_and_nominal_endpoint(self):
        p=np.array([[0.,1.,2.,3.]])
        c=study.components(p,p,1.,0.)
        self.assertGreater((c['u0']+c['d'][0])[-1],c['u0'][-1])
        self.assertGreater(c['R'][0]-c['C'][0],0)

    def test_zero_forecast_is_baseline(self):
        p=np.arange(12.).reshape(3,4)
        c=study.components(p,np.zeros_like(p),2.,1.)
        np.testing.assert_allclose(c['d'],0,atol=1e-12)
        np.testing.assert_allclose(c['R'],0,atol=1e-11)
        np.testing.assert_allclose(c['C'],0,atol=1e-20)

    def test_bootstrap_preserves_episode_weighting(self):
        values=np.array([[0.,2.],[10.,4.],[20.,8.],[100.,16.]])
        days=np.array([10,10,10,20]);seed=92;reps=60
        draws=np.random.default_rng(seed).integers(0,2,(reps,2))
        day_arrays=[values[:3],values[3:]]
        expected=np.array([np.concatenate([day_arrays[d] for d in draw]).mean(axis=0) for draw in draws])
        got=study.bootstrap_means(values,days,seed,reps)
        np.testing.assert_allclose(got,expected)

    def test_episode_timing_and_signal_future_independence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/raw').mkdir(parents=True)
            rows=np.zeros((1440,12));rows[:,0]=1_780_272_000_000_000+np.arange(1440)*60_000_000
            rows[:,1]=100+np.arange(1440)*.01;rows[:,5]=10;rows[:,9]=6
            def persist():
                stream=io.StringIO();np.savetxt(stream,rows,delimiter=',',fmt='%.12g')
                path=root/'data/raw/BTCUSDT-1m-2026-06.zip'
                with zipfile.ZipFile(path,'w') as z:z.writestr('bars.csv',stream.getvalue())
                (root/'data/manifest.json').write_text(json.dumps([{'month':'2026-06','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}]))
            persist()
            with patch.object(study,'Path',side_effect=lambda p:root/p):
                x,p,days,index=study.month_episodes('2026-06')
                self.assertEqual(len(x),48)
                np.testing.assert_array_equal(index,np.arange(5,1425,30))
                np.testing.assert_allclose(x,.2)
                expected=10000*(rows[6:21,1]/rows[5,1]-1)
                np.testing.assert_allclose(p[0],expected)
                self.assertEqual(len(np.unique(days)),1)
                rows[5:21,9]=0;persist()
                altered,_,_,_=study.month_episodes('2026-06')
                self.assertEqual(x[0],altered[0])

    def test_simplex_projection(self):
        for v in [np.array([4.,-2.,.1]),np.array([.3,.3,.4]),np.array([-100.,-100.,-100.])]:
            u=study.simplex(v)
            self.assertGreaterEqual(u.min(),0)
            self.assertAlmostEqual(u.sum(),1)
            positive=u>1e-12
            level=(v-u)[positive].mean()
            np.testing.assert_allclose((v-u)[positive],level,atol=1e-12)
            self.assertTrue(np.all(v[~positive]<=level+1e-12))


if __name__=='__main__':unittest.main()
