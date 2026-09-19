# Data

Source: [Binance Public Data](https://github.com/binance/binance-public-data), spot monthly 1-minute klines for BTCUSDT and ETHUSDT, January–August 2026 (699,840 rows).

Original ZIPs and exchange CHECKSUM files are in `raw/`. [Manifest](../revisions/2026-09-19/data_manifest.json) records source URLs, SHA256 hashes and validation results. No customer-level data are included. These are third-party exchange data; no ownership or additional data licence is asserted.

To recover or validate the archives, run `python3 revisions/2026-09-19/download_extended.py` from the repository root. This refreshes the acquisition manifest; preserve the reported manifest before rerunning.
