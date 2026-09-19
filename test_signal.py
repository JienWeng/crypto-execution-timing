import unittest
import numpy as np
from signal_diagnostic import episodes, load_month


class SignalTimingChecks(unittest.TestCase):
    def test_first_signal_uses_completed_bars_only(self):
        rows = np.zeros((50, 12))
        rows[:, 0] = np.arange(50)*60_000_000
        rows[:, 1] = 100 + np.arange(50)
        rows[:, 5] = 10
        rows[:, 9] = 7
        x, y, _ = episodes(rows)
        changed = rows.copy()
        changed[5:, 9] = 0
        changed[20, 1] *= 2
        x_changed, y_changed, _ = episodes(changed)
        self.assertAlmostEqual(x[0], .4)
        self.assertEqual(x[0], x_changed[0])
        self.assertNotEqual(y[0], y_changed[0])
        self.assertAlmostEqual(y[0], 10000*(120/105-1))

    def test_august_refused_by_diagnostic(self):
        with self.assertRaises(ValueError):
            load_month('2026-08')


if __name__ == '__main__':
    unittest.main()
