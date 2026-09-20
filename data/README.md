# Data

Source: [Binance Public Data](https://github.com/binance/binance-public-data), spot monthly one-minute klines, January–August 2026.

- BTCUSDT and ETHUSDT: 16 files, 699,840 rows; [original extension manifest](../revisions/2026-09-19/data_manifest.json).
- SOLUSDT, BNBUSDT and XRPUSDT: 24 files, 1,049,760 rows; [transfer manifest](../revisions/2026-09-20-selection/transfer_manifest.json).

Original ZIPs and exchange CHECKSUM files are in `raw/`. Manifests record source URLs, SHA256 hashes and validation results. No customer-level data are included. These are third-party exchange data; no ownership or additional data licence is asserted.

To recover or validate, run `python3 revisions/2026-09-19/download_extended.py` and `python3 revisions/2026-09-20-selection/acquire.py`. These refresh acquisition manifests; preserve the recorded manifests before rerunning. Experiment reproduction checks the archived files without replacing them.
