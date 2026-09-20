# Crypto execution timing

**Choosing price forecasts for cryptocurrency sales** — Lai Jien Weng, Monash University.

[Latest manuscript source](submission/forecast-selection-study/source/main.tex) · [Supporting appendices](submission/forecast-selection-study/source/appendices.tex) · [Experiment report](revisions/2026-09-20-selection/REPORT.md) · [Earlier full paper](manuscript/full/main.tex)

## Reproduce

Python 3.11+, from the repository root:

```bash
python3 -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s revisions/2026-09-20-selection -p 'test*.py'
OPENBLAS_NUM_THREADS=1 python3 revisions/2026-09-20-selection/reproduce.py
python3 revisions/2026-09-20-selection/build_assets.py
```

Forty archived Binance minute-bar files and checksums are included for BTC, ETH, SOL, BNB and XRP, January–August 2026. [Data provenance](data/README.md). The frozen experiment evaluates 44,160 hypothetical orders. Economic selection loses less than final-price selection on the transfer assets, but matches the simpler demeaned-path selector and loses against the no-signal baseline. Costs are assumed; the historical test does not establish real trading savings.

PDFs remain local. Nothing has been submitted. Contact: lai.jienweng@monash.edu
