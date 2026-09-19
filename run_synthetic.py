"""Deterministic scenario sweep and seeded Monte Carlo cross-check."""
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from execution_model import ExecutionModel


def main():
    out = Path('results')
    out.mkdir(exist_ok=True)
    m = ExecutionModel(.1*np.exp(-2*np.arange(30)/30))
    strategies = {'full': 1., 'half': .5,
                  'interval_0.2_0.8': m.safe_amplitude(.2, .8),
                  'interval_minus0.2_0.8': m.safe_amplitude(-.2, .8)}
    rows = []
    for beta in np.linspace(-.5, 1.5, 81):
        for name, a in strategies.items():
            direct = m.objective(m.u0, beta)-m.objective(m.schedule(a), beta)
            formula = m.K*(a*beta-.5*a*a)
            rows.append({'beta': float(beta), 'strategy': name, 'amplitude': a,
                         'objective_gain': direct, 'gain_divided_by_K': direct/m.K,
                         'identity_error': abs(direct-formula)})
    with (out/'synthetic_sweep.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)

    # Independent pathwise accounting: sell at beginning-of-interval prices.
    # Risk term is deterministic; this validates expected objective, not profit.
    seed, paths, beta, a, sigma = 20260918, 50000, .3, .5, .02
    rng = np.random.default_rng(seed)
    increments = beta*m.forecast*m.dt + sigma*np.sqrt(m.dt)*rng.normal(size=(paths,m.n))
    prices = np.column_stack([np.zeros(paths), np.cumsum(increments,axis=1)[:,:-1]])
    u = m.schedule(a)
    q0, q = m.quantity-m.L@m.u0, m.quantity-m.L@u
    penalty0 = m.impact/m.dt*(m.u0@m.u0)+m.risk*m.dt*(q0@q0)
    penalty = m.impact/m.dt*(u@u)+m.risk*m.dt*(q@q)
    gains = (penalty0-prices@m.u0)-(penalty-prices@u)
    expected = m.K*(a*beta-a*a/2)
    se = float(gains.std(ddof=1)/np.sqrt(paths))
    report = {'status': 'synthetic verification only', 'seed': seed, 'paths': paths,
              'K': m.K, 'max_identity_error': max(r['identity_error'] for r in rows),
              'monte_carlo': {'beta': beta, 'amplitude': a, 'mean': float(gains.mean()),
                              'expected': expected, 'standard_error': se,
                              'z_error': float((gains.mean()-expected)/se)},
              'empirical_claims': False}
    (out/'synthetic_summary.json').write_text(json.dumps(report, indent=2)+'\n')
    fig, ax = plt.subplots(figsize=(8, 4.7))
    for name in strategies:
        selected = [r for r in rows if r['strategy']==name]
        ax.plot([r['beta'] for r in selected], [r['gain_divided_by_K'] for r in selected], label=name)
    ax.axhline(0, color='black', linewidth=.8)
    ax.axvline(.5, color='grey', linestyle=':', linewidth=.8)
    ax.set(xlabel='True signal amplitude beta (synthetic)',
           ylabel='Risk-adjusted improvement / K',
           title='Full signal exposure loses below beta = 0.5 in this model')
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out/'synthetic_break_even.png', dpi=180)
    fig.savefig(out/'synthetic_break_even.pdf')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
