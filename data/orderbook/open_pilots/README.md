# Coinbase order-book pilot

CC0 data by Martin Søgaard Nielsen: [High Frequency Crypto Limit Order Book Data](https://www.kaggle.com/datasets/martinsn/high-frequency-crypto-limit-order-book-data). BTC, ETH and ADA, April 2021.

Included NPZ files contain causal minute samples of the source one-second books, with 15 reconstructed levels. `boundary_us` is the UTC sampling boundary; `source_timestamp_us` is the dataset system timestamp, not an independently verified receipt timestamp. Prices are quote-currency units per coin; amounts are base-asset quantities. Source notionals are level-specific, and source distances are fractional midpoint offsets.

The exact dataset collector commit is unavailable. Formula verification uses a pre-collection version of the referenced collector. Invalid top-quote quantities and records older than five seconds are excluded. These snapshots cannot certify actual fills or market responses.

[Source URLs, hashes and extraction audit](../../../revisions/2026-09-21-research-direction/CC0_DATA_PROVENANCE.json). The approximately 1GB raw ZIPs can be acquired with the pinned downloader; they are not duplicated in Git. Only this CC0 dataset is included here.
