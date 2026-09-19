"""Preliminary June/July signal diagnostic. August is never opened here."""
import io
import json
import zipfile
from pathlib import Path
import numpy as np


def load_month(month):
    if month not in ('2026-06', '2026-07'):
        raise ValueError('only estimation/validation months permitted in this diagnostic')
    path = Path('data/raw')/f'BTCUSDT-1m-{month}.zip'
    with zipfile.ZipFile(path) as z:
        return np.loadtxt(io.BytesIO(z.read(z.namelist()[0])), delimiter=',')


def episodes(rows):
    # Disjoint forward 15-minute windows; last five completed bars form signal.
    index = np.arange(5, len(rows)-15, 15)
    signal = []
    for i in index:
        volume = rows[i-5:i, 5].sum()
        signal.append((2*rows[i-5:i, 9].sum()-volume)/volume if volume>0 else 0.)
    x = np.asarray(signal)
    y = 10000*(rows[index+15, 1]/rows[index, 1]-1)
    days = (rows[index, 0].astype(np.int64)//86_400_000_000).astype(int)
    return x, y, days


def coefficients(x, y):
    return np.linalg.lstsq(np.column_stack([np.ones(len(x)),x]), y, rcond=None)[0]


def diagnostic(month):
    x, y, days = episodes(load_month(month))
    intercept, slope = coefficients(x, y)
    rng = np.random.default_rng(20260918)
    unique = np.unique(days)
    groups = [np.flatnonzero(days==day) for day in unique]
    boot = []
    for _ in range(2000):
        chosen = rng.integers(0, len(groups), len(groups))
        idx = np.concatenate([groups[j] for j in chosen])
        boot.append(coefficients(x[idx], y[idx])[1])
    return {'month': month, 'episodes': len(x), 'days': len(unique),
            'intercept_bps': float(intercept), 'slope_bps_per_unit_imbalance': float(slope),
            'slope_day_bootstrap_percentile_95_interval': np.quantile(boot,[.025,.975]).tolist(),
            'signal_std': float(x.std(ddof=1)), 'return_std_bps': float(y.std(ddof=1)),
            'correlation': float(np.corrcoef(x,y)[0,1])}


def main():
    results = [diagnostic(month) for month in ('2026-06','2026-07')]
    report = {'status': 'exploratory diagnostic; not execution evidence',
              'signal': 'last 5 completed one-minute bars signed-volume imbalance',
              'target': 'next 15-minute open-to-open return in bps',
              'bootstrap': '2000 independent resamples of whole UTC days; seed 20260918',
              'limitations': ['Only 30/31 day clusters; no guarantee under regime changes',
                              'No execution prices, spread, depth or market impact observed',
                              'No alternative signals or horizons searched',
                              'August evaluation outcomes not computed'],
              'results': results}
    Path('results/signal_diagnostic.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
