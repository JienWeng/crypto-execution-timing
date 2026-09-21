import unittest
import numpy as np
try:
    import oracle_study as os
except ModuleNotFoundError:
    os=None

class OracleTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(os)

    def test_realized_liquidity_book_preserves_mid_relative_ladder(self):
        prices=np.array([[99.,98.],[101.,99.]])
        asks=np.array([101.,103.])
        sizes=np.array([[1.,2.],[3.,4.]])
        p,s=os.realized_liquidity_books(prices,asks,sizes,100.,np.array([100.,100.]))
        np.testing.assert_allclose(p,[[99.,98.],[99.,97.]])
        np.testing.assert_array_equal(s,sizes)

    def test_oracle_price_uses_realized_mid_only(self):
        mids=np.array([101.,98.]);arrival=100.
        np.testing.assert_allclose(os.oracle_price_bps(mids,arrival),[100.,-200.])

if __name__=='__main__':unittest.main()
