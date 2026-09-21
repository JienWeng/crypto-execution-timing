# Price versus liquidity: development pilot

Read `CONTRIBUTION.md` and `PILOT_RESULTS.md`. The five-date pilot does not establish useful forecast superiority or a stable order-size boundary.

From the repository root:

```bash
OPENBLAS_NUM_THREADS=1 python3 revisions/2026-09-21-research-direction/test_book_execution.py
OPENBLAS_NUM_THREADS=1 python3 revisions/2026-09-21-research-direction/test_pilot.py
OPENBLAS_NUM_THREADS=1 python3 revisions/2026-09-21-research-direction/reproduce_pilot.py --data-dir data/orderbook/open_pilots
```

The public package includes the CC0 sampled books. To reconstruct them from the approximately 1GB source archives, run `acquire_open_pilots.py`, then `extract_cc0_seconds.py BTC ETH ADA` using their full script paths from the repository root. Raw archives remain outside Git; their URLs and hashes are pinned in `CC0_DATA_PROVENANCE.json`. Requires NumPy and Matplotlib from the repository requirements.

No Tardis data or trained models based on Tardis data are included. `extract_snapshots.py` is a source-format utility only and is not used by this pilot. The PDF development report is local in `submission/price-liquidity-study/`; only its source and figures belong in Git.
