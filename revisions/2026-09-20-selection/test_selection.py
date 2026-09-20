import unittest
import numpy as np
import selection_study as s
class SelectionTests(unittest.TestCase):
 def test_feature_causality(self):
  a=np.ones((1440,12));a[:,0]=np.arange(1440)*60_000_000;a[:,1]=100+np.arange(1440)*.001;a[:,5]=2;a[:,9]=1
  x,y,days,ix=s.features(a);b=a.copy();b[6:20,1]=1000;b[5:20,5]=900;b[5:20,9]=850
  xx,yy,_,_=s.features(b);np.testing.assert_array_equal(x[0],xx[0]);self.assertFalse(np.array_equal(y[0],yy[0]));self.assertEqual(ix[-1],1415)
 def test_training_reproducible_and_zero(self):
  rng=np.random.default_rng(4);x=rng.normal(size=(80,5));y=rng.normal(size=(80,15));model=s.fit(x,y);p=s.predict(model,x)
  self.assertEqual(p.shape,(7,80,15));np.testing.assert_array_equal(p[0],0);np.testing.assert_allclose(p[1],np.broadcast_to(y.mean(0),(80,15)))
 def test_shared_baseline_and_ties(self):
  pred=np.zeros((7,10,15));truth=np.zeros((10,15));g=np.zeros((7,10));chosen,_=s.selection(pred,truth,g);self.assertTrue(all(v==0 for v in chosen.values()))
 def test_selection_has_no_evaluation_input(self):
  import inspect
  self.assertEqual(list(inspect.signature(s.selection).parameters),['pred','truth','gain'])
  pred=np.zeros((7,10,15));pred[1]=2;truth=np.ones((10,15))*2;g=np.zeros((7,10));g[2]=1
  chosen,_=s.selection(pred,truth,g);self.assertEqual(chosen['endpoint'],1);self.assertEqual(chosen['economic'],2);self.assertEqual(chosen['contrasts'],0)
 def test_qp_objective_and_common_level(self):
  rng=np.random.default_rng(3);mu=rng.normal(size=(7,20,15))*30;mu[0]=0;P=rng.normal(size=(20,15));U,res=s.solve(mu,.5,1)
  self.assertLess(res,1e-7);np.testing.assert_allclose(U.sum(2),1,atol=1e-10);self.assertGreaterEqual(U.min(),-1e-10)
  V,_=s.solve(mu+7,.5,1);np.testing.assert_allclose(U,V,atol=1e-9)
  c=s.score(U,P,.5,1);J=.5*15*(U**2).sum(2)+(1-np.cumsum(U,2)) .__pow__(2).sum(2)/15-(U*P).sum(2)
  np.testing.assert_allclose(c['gain'],J[0]-J,atol=1e-10);np.testing.assert_allclose(c['gain'][0],0,atol=1e-10)
 def test_bootstrap_pairing_and_seed(self):
  x=np.arange(28,dtype=float);v=np.column_stack([x,x+2]);bs=s.bootstrap(v,reps=50);np.testing.assert_allclose(bs[:,1]-bs[:,0],2);np.testing.assert_array_equal(bs,s.bootstrap(v,reps=50))

class GeometryTests(unittest.TestCase):
 def test_unconstrained_contrast_identity(self):
  rng=np.random.default_rng(11);mu=rng.normal(size=(7,40,15))*.05;mu[0]=0;P=rng.normal(size=(40,15));U,_=s.solve(mu,2,0);self.assertTrue((U>0).all())
  gained=s.score(U,P,2,0)['gain'];dm=mu-mu.mean(2,keepdims=True);dp=P-P.mean(1,keepdims=True)
  expected=((dp*dp).sum(1)[None,:]-((dm-dp)**2).sum(2))/(4*2*15)
  np.testing.assert_allclose(gained,expected,atol=1e-12)
  chosen,_=s.selection(mu,P,gained);self.assertEqual(chosen['economic'],chosen['contrasts'])
 def test_evaluation_outcomes_cannot_change_frozen_choice(self):
  rng=np.random.default_rng(30);xc=rng.normal(size=(60,5));yc=rng.normal(size=(60,15));xe=rng.normal(size=(40,5));model=s.fit(xc,yc)
  pc=s.predict(model,xc);uc,_=s.solve(pc,2,1);choices,_=s.selection(pc,yc,s.score(uc,yc,2,1)['gain'])
  pe=s.predict(model,xe);ue,_=s.solve(pe,2,1);p1=rng.normal(size=(40,15));p2=p1+np.arange(15)*100
  gain1=s.score(ue,p1,2,1);gain2=s.score(ue,p2,2,1)
  again,_=s.selection(pc,yc,s.score(uc,yc,2,1)['gain']);self.assertEqual(choices,again);np.testing.assert_array_equal(ue,s.solve(s.predict(model,xe),2,1)[0]);self.assertFalse(np.allclose(gain1['gain'],gain2['gain']))

if __name__=='__main__':unittest.main()
