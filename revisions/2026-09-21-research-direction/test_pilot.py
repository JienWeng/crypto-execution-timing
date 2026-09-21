import unittest
import numpy as np
try:
    import pilot_study as ps
except ModuleNotFoundError:
    ps = None


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(ps, 'pilot_study must implement frozen forecast design')

    def test_future_values_cannot_change_current_features(self):
        n=100
        d={'boundary_us':np.arange(n,dtype=np.int64)*60_000_000,
           'bids_price':np.tile([99.,98.],(n,1)), 'asks_price':np.tile([101.,102.],(n,1)),
           'bids_amount':np.ones((n,2)), 'asks_amount':np.ones((n,2))}
        x=ps.features(d)[20].copy()
        d['bids_price'][21:]*=2;d['asks_price'][21:]*=2
        np.testing.assert_array_equal(x,ps.features(d)[20])

    def test_targets_never_cross_training_end_or_missing_minute(self):
        times=np.arange(100,dtype=np.int64)*60_000_000
        ix=ps.valid_indices(times,20*60_000_000,50*60_000_000)
        self.assertEqual(ix[0],20)
        self.assertEqual(ix[-1],34)
        times[30:]+=60_000_000
        ix=ps.valid_indices(times,0,100*60_000_000)
        self.assertFalse(any(15<=i<=34 for i in ix))

    def test_ridge_fit_is_training_only_and_intercept_unpenalized(self):
        x=np.arange(100.).reshape(50,2)
        y=np.ones((50,3))*np.array([2.,3.,4.])
        model=ps.fit_ridge(x,y)
        np.testing.assert_allclose(ps.predict_ridge(model,np.array([[1e9,-1e9]])),[[2.,3.,4.]])


if __name__=='__main__':unittest.main()
