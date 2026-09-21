import itertools
import unittest
import numpy as np

try:
    import book_execution as be
except ModuleNotFoundError:
    be = None


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(be, 'book_execution must implement the approved replay design')

    def test_walk_book_and_refuse_invented_depth(self):
        revenue, filled = be.walk([100, 99], [1, 2], 2)
        self.assertEqual((revenue, filled), (199, 2))
        self.assertEqual(be.walk([100, 99], [1, 2], 4), (298, 3))

    def test_optimizer_matches_exhaustive_integer_allocation(self):
        prices = np.array([[103., 98.], [102., 101.], [100., 99.]])
        sizes = np.ones_like(prices)
        q = be.allocate(prices, sizes, 3, 2)
        actual = sum(be.walk(p, s, x)[0] for p, s, x in zip(prices, sizes, q))
        brute = max(sum(be.walk(p, s, x)[0] for p, s, x in zip(prices, sizes, qs))
                    for qs in itertools.product(range(3), repeat=3) if sum(qs) == 3)
        self.assertAlmostEqual(actual, brute)
        self.assertAlmostEqual(sum(q), 3)

    def test_equal_books_have_equal_allocation(self):
        q = be.allocate(np.array([[100., 99.]] * 3), np.array([[1., 2.]] * 3), 4.5, 3)
        np.testing.assert_allclose(q, [1.5] * 3)

    def test_cap_and_insufficient_forecast_capacity(self):
        q = be.allocate(np.array([[105.], [100.], [99.]]), np.ones((3, 1)) * 10, 3, 1)
        np.testing.assert_allclose(q, [1, 1, 1])
        with self.assertRaises(ValueError):
            be.allocate(np.array([[100.]]), np.array([[1.]]), 2, 2)

    def test_depletion_is_not_reused_by_identical_snapshot(self):
        ledger = be.DepletionLedger()
        ledger.update([100., 99.], [1., 2.])
        self.assertEqual(ledger.sell(1), (100., 1.))
        ledger.update([100., 99.], [1., 2.])
        self.assertEqual(ledger.sell(1), (99., 1.))
        ledger.update([100., 99.], [2., 2.])
        self.assertEqual(ledger.sell(1), (100., 1.))

    def test_displayed_increase_is_counted_only_once(self):
        ledger = be.DepletionLedger()
        ledger.update([100.], [100.])
        ledger.sell(30.)
        ledger.update([100.], [110.])
        self.assertEqual(ledger.sell(1000.), (8000., 80.))

    def test_forecast_switches_share_current_information(self):
        book = be.Book(0, np.array([99., 98.]), np.array([2., 3.]), 101.)
        flat = be.forecast_books(book, np.zeros(3), np.zeros(3), np.zeros(3), True, True)
        baseline = be.forecast_books(book, np.ones(3), np.ones(3), np.ones(3), False, False)
        for a, b in zip(flat, baseline):
            np.testing.assert_allclose(a, b)
        p, s = be.forecast_books(book, np.ones(3)*10, np.zeros(3), np.zeros(3), True, False)
        np.testing.assert_allclose(p, np.array([[99.1, 98.1]]*3))
        np.testing.assert_allclose(s, np.array([[2., 3.]]*3))

    def test_exact_accounting_and_incomplete_orders(self):
        books = [be.Book(60, np.array([99.]), np.array([1.]), 101.),
                 be.Book(120, np.array([101.]), np.array([1.]), 103.)]
        r = be.replay(100., books, [1., 1.], 0., False)
        self.assertEqual(r['filled'], 2.)
        self.assertAlmostEqual(r['shortfall_dollars'], 0.)
        self.assertAlmostEqual(r['timing_dollars'] - r['book_cost_dollars'] - r['fee_dollars'], 0.)
        r = be.replay(100., books, [2., 2.], 0., False)
        self.assertEqual(r['unfilled'], 2.)
        self.assertIsNone(r['shortfall_bps'])
        self.assertIsNone(r['shortfall_dollars'])

    def test_backlog_respects_child_cap(self):
        books = [be.Book(60, np.array([99.]), np.array([.1]), 101.),
                 be.Book(120, np.array([99.]), np.array([5.]), 101.)]
        r = be.replay(100., books, [1., 1.], 0., False, child_cap=1.)
        np.testing.assert_allclose(r['child_fills'], [.1, 1.])
        self.assertAlmostEqual(r['unfilled'], .9)

    def test_reject_out_of_order_books_and_negative_sizes(self):
        with self.assertRaises(ValueError):
            be.Book(0, np.array([99., 100.]), np.ones(2), 101.)
        with self.assertRaises(ValueError):
            be.Book(0, np.array([99.]), np.array([0.]), 101.)
        with self.assertRaises(ValueError):
            be.walk([100], [-1], 1)
        b = be.Book(60, np.array([99.]), np.array([1.]), 101.)
        with self.assertRaises(ValueError):
            be.replay(100, [b, b], [1., 1.], 0, False)


if __name__ == '__main__':
    unittest.main()
