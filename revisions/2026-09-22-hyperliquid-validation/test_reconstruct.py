import unittest
import numpy as np
try:import reconstruct_books as rb
except ModuleNotFoundError:rb=None

class ReconstructTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(rb)
    def test_decode_fixed_point(self):
        encoded=(2<<29)|12345
        self.assertAlmostEqual(rb.decode(np.array([encoded],np.uint32))[0],123.45,places=4)
    def test_open_partial_fill_and_cancel(self):
        state={};levels={}
        rb.apply(state,levels,1,False,100.,3.,rb.OPEN)
        rb.apply(state,levels,2,False,100.,2.,rb.OPEN)
        self.assertEqual(rb.top(levels,False,2),[(100.,5.)])
        rb.apply(state,levels,1,False,100.,1.,rb.FILLED)
        self.assertEqual(rb.top(levels,False,2),[(100.,3.)])
        rb.apply(state,levels,2,False,100.,0.,rb.CANCELED)
        self.assertEqual(rb.top(levels,False,2),[(100.,1.)])
    def test_price_change_replaces_oid(self):
        state={};levels={}
        rb.apply(state,levels,1,True,101.,2.,rb.OPEN)
        rb.apply(state,levels,1,True,102.,3.,rb.OPEN)
        self.assertEqual(rb.top(levels,True,2),[(102.,3.)])
    def test_asks_ascending_bids_descending(self):
        levels={(False,99.):2.,(False,100.):1.,(True,102.):4.,(True,101.):3.}
        self.assertEqual(rb.top(levels,False,2),[(100.,1.),(99.,2.)])
        self.assertEqual(rb.top(levels,True,2),[(101.,3.),(102.,4.)])
if __name__=='__main__':unittest.main()
