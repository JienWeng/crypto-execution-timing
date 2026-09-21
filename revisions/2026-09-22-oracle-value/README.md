# Hindsight information-value diagnostic

This post-pilot exploratory diagnostic separates ex-post decision relevance from feasible forecast performance. Read `RESULTS.md`, `PROTOCOL.md` and `PROTOCOL_NOTE.md` together. Hindsight schedules are not implementable strategies.

```bash
OPENBLAS_NUM_THREADS=1 python3 revisions/2026-09-22-oracle-value/test_oracle.py
OPENBLAS_NUM_THREADS=1 python3 revisions/2026-09-22-oracle-value/reproduce.py --data-dir data/orderbook/open_pilots
```

The five-date sample shows a large unused price-timing opportunity and only a small incremental contribution from future liquidity once future prices are supplied. This is development evidence, not a population claim.
