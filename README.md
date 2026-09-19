# Crypto execution timing

**Return forecasts and execution timing: A matched-endpoint study of cryptocurrency orders** — Lai Jien Weng, Monash University.

[Full manuscript source](manuscript/full/main.tex) · [40-paper bibliography](manuscript/full/references.bib) · [Figures](manuscript/full/figures) · [Data provenance](data/README.md)

## Reproduce

Python 3.11+; run from the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -p 'test*.py'
python3 -m unittest discover -s revisions/2026-09-19 -p 'test*.py'
python3 revisions/2026-09-19/revision_study.py
python3 scripts/build_full_assets.py
```

Includes 16 Binance BTC/ETH minute-bar archives, checksums and results for 17,664 hypothetical orders. The study is retrospective; costs are assumed and gains are not observed trading profits. Reruns overwrite generated results: use a clean checkout. Manuscript sources and PNG/SVG figures are provided; PDFs are excluded. Venue selection is pending.

Contact: lai.jienweng@monash.edu
