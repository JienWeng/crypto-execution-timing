# Crypto execution timing

Reproducibility files for **Return forecasts and execution timing: A matched-endpoint diagnostic for cryptocurrency orders** — Lai Jien Weng, Monash University.

[Paper](output/pdf/crypto_execution_revised.pdf) · [Supplement](output/pdf/crypto_execution_supplement.pdf) · [BibTeX](manuscript/revised/references.bib)

## Reproduce

Python 3.11+; run from the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -p 'test*.py'
python3 -m unittest discover -s revisions/2026-09-19 -p 'test*.py'
python3 revisions/2026-09-19/revision_study.py
python3 revisions/2026-09-19/build_assets.py
```

Build PDFs with Tectonic from `manuscript/revised/`: `tectonic main.tex` and `tectonic supplement.tex`.

Sixteen Binance BTC/ETH minute-bar archives (January–August 2026), checksums, protocols and reported results are included. [Data provenance](data/README.md). The study uses 17,664 hypothetical order episodes. Costs are assumed; results do not establish executable trading savings. The extension is retrospective and exploratory.

Analysis and results are in `revisions/2026-09-19/`; earlier files retain the original calibration and reproduction evidence. Reruns overwrite generated results, so use a clean checkout. The supplement documents methods, limitations and AI assistance.

Contact: lai.jienweng@monash.edu
