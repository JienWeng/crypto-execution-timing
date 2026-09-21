# Order-book data feasibility audit

Data acquisition checked 21 September 2026 before strategy outcomes. The later CC0 pilot is reported separately in PILOT_RESULTS.md.

## Open-data candidate: Dryad

[Dataset DOI 10.5061/dryad.q2bvq83rn](https://datadryad.org/dataset/doi:10.5061/dryad.q2bvq83rn), Voigt, Hautsch and Scheuch, *Building trust takes time: Limits to arbitrage for blockchain-based assets*. API metadata gives CC0-1.0. Public documentation describes Bitcoin/USD order-book snapshots, January 2018–October 2019, across exchanges. Its general collection description says 25 levels, but SQLite-specific description says levels 1–20: actual schema/depth must be checked after acquisition. Minute snapshots cannot establish event-by-event replenishment or queue position; accompanying trades are not established.

Metadata downloaded using `/api/v2/datasets/doi%3A10.5061%2Fdryad.q2bvq83rn` and `/api/v2/files/2816244`. File `orderbook_data.sqlite`: 27,412,348,928 bytes; publisher SHA256 `81cffe292e1f894bd78c3d14a37469c630f85bcefca3b6dc1300fef1e893f195`. The public download link returned HTTP403; official API download returned401. No credentials or access-control workarounds used. Raw SQLite not acquired; schema claims remain publisher documentation, not validated data.

## Accessible pilot: Tardis Binance spot

[Official datasets API documentation](https://docs.tardis.dev/downloadable-csv-files/api.md) permits keyless downloads for the first day of each month. Exchange metadata identifies BTCUSDT as spot and book_snapshot_25 as available. A normal GET of `https://datasets.tardis.dev/v1/binance/book_snapshot_25/2025/01/01/BTCUSDT.csv.gz` succeeded (HEAD misleadingly returned404).

Pilot downloaded locally: 27,514,056 bytes, 681,957 rows; SHA256 `f634b6b27146ba4505dcb445dd185a62857f0f1d931bdb87c4adfe8f84c08670`. Schema includes exchange, symbol, exchange/local microsecond timestamps and 25 bid/ask price/amount levels. First timestamp 1735689600800886; last 1735775999914000. Gzip decompression completed. Raw snapshot values were inspected for schema only, not forecast or strategy outcomes. Local metadata, checksum and extraction audit are in `data/orderbook/`.

### Usage and reproducibility restriction

[Supplier terms](https://docs.tardis.dev/legal/terms-of-service), modified 13 September 2026, cover sample data too. Sections 9.1 and 9.5 allow internal quantitative research/backtesting. Section 9.2 restricts raw/sampled data redistribution; its derived-data exception specifies aggregation of at least ten minutes. Section 9.5 additionally restricts distribution of models trained on supplied data and imposes recipient conditions on derived-data disclosure. Therefore raw data, sampled NPZs and fitted models must not enter the public repository. These restrictions make this a weaker fit than CC0 Dryad for the user's requested fully open package. Scientific publication of aggregates should not be assumed unrestricted without resolving the terms. No paid account, credentials, or purchase used.

### Extraction

`extract_snapshots.py` takes the last received snapshot at or before each UTC minute boundary, retains its exchange timestamp, and rejects ages above five seconds. It waits until a later record to close a boundary, so records sharing a timestamp are handled without looking ahead. It never extrapolates beyond the last record. It checks monotone local time, complete fields, finite values, uncrossed best quotes, strict price ordering and nonnegative sizes. Output is numerical NPZ without pickle objects. This does not certify continuity of raw L2 updates, which are absent from snapshot CSVs; supplier documentation says disconnect markers are absent from these CSVs. A snapshot replay must state this limitation.

Tardis monthly first days provide discontinuous days, not full months. A 24-day sample has only 24 distinct daily clusters regardless of millions of snapshots. Training/evaluation and dependence inference must respect that; do not describe it as continuous two-year coverage.

## Acquired CC0 pilot: Coinbase BTC, ETH and ADA

[Martin Søgaard Nielsen dataset](https://www.kaggle.com/datasets/martinsn/high-frequency-crypto-limit-order-book-data) public API identifies license CC0 Public Domain. Creator describes Coinbase WebSocket collection using [crypto-rl](https://github.com/sadighian/crypto-rl), 15 levels, approximately 12 days. Downloaded three one-minute files through ordinary public Kaggle endpoints without authentication. Archive checksums and URLs are recorded in `data/orderbook/open_pilots/downloads.json`.

| Asset | Rows | First UTC | Last UTC | Gaps >90 seconds | Maximum gap (seconds) |
|---|---:|---|---|---:|---:|
| BTC | 17,113 | 2021-04-07 11:33:41.122161 | 2021-04-19 09:54:00.386544 | 68 | 148.000617 |
| ETH | 17,110 | 2021-04-07 11:33:49.861733 | 2021-04-19 09:53:00.345392 | 70 | 128.624178 |
| ADA | 17,109 | 2021-04-07 11:33:59.055697 | 2021-04-19 09:49:00.442103 | 67 | 121.061901 |

All reconstructed books have finite values, ordered levels, nonnegative amounts and uncrossed best quotes; timestamps strictly increase. Referenced collector source defines distance as price/midpoint minus one (a fraction, despite dataset description saying percent) and notional as each individual level's price-times-quantity, not cumulative depth. Recover price = midpoint × (1 + distance); quantity = level notional / price. Reconstructed spread differs from supplied spread by at most 0.00000594 USD for BTC, consistent with float32 feature precision. These are schema/accounting checks, not evidence of predictive performance.

Normalized NPZs retain original observation timestamps. Compatibility fields `boundary_us` and `local_timestamp_us` alias `system_time`; they do not establish exact minute boundaries or independently verified local receipt time. Exchange timestamps are unavailable and not invented. UTC offsets are explicit in source strings. Dataset does not pin its collector version, so source inspection cannot by itself certify historical collection/reconstruction correctness.

Other pilots: Fast42 Binance dataset (CC BY4) contains only 59 snapshots over58 seconds, insufficient for empirical inference. KrrDev Binance2026-04-18 snapshots (CC BY-NC4) acquired24MB; single day and noncommercial terms, secondary pipeline candidate only, not used for outcomes. HuggingFace rfab85 sample prohibits substantial redistribution, so it is not selected for an open package.

### Higher-frequency extraction selected for pilot

Downloaded the three CC0 one-second ZIP archives, totaling approximately1.005GB compressed (BTC332,328,327bytes; ETH382,488,871; ADA290,410,697). Their CSV content is streamed without materializing5.35GB uncompressed files. `extract_cc0_seconds.py` retains the latest source snapshot at or before UTC minute boundaries, no older than5seconds, and never extrapolates after the final source record. This supersedes irregular one-minute files for execution input.

Collector formula verified also in pre-collection commit `b02a573fdbc8d81779d3e8edff3c5f5ec3623785` (latest change to book.py before7April2021), [source](https://github.com/sadighian/crypto-rl/blob/b02a573fdbc8d81779d3e8edff3c5f5ec3623785/data_recorder/connector_components/book.py). Its render returns individual price-level distances and notionals; the simulator emits rendered books rather than temporal averages. The dataset does not identify its actual commit, so this supports interpretation without certifying exact historical implementation. The underlying one-second records can repeat unchanged books; age of dataset timestamp does not certify a fresh exchange event.

Use April8–13training and April14–18evaluation as instructed before strategy outcomes. April7and19are partial and excluded. This is an exploratory historical pilot with only five evaluation dates, insufficient alone for broad market-effectiveness claims.

Final causal-minute extraction: BTC1,030,728raw records →17,180minute snapshots (2stale exclusions); ETH1,030,775 →17,181 (0stale); ADA1,030,533 →17,176 (0stale). No invalid books in any asset. Maximum retained source timestamp age3.986264s,2.576239s,1.008321s respectively. All eleven full study dates have1440observations for ETH and ADA. BTC has1439onApril14and18and1440onother full dates. Exact checksums, per-day counts and ranges are in `CC0_DATA_PROVENANCE.json`. No strategy outcomes were computed during acquisition or schema checks.

## Final pre-outcome adapter validation

A stricter executable-book check rejected records with zero displayed quantity at either best quote: BTC 24, ETH 20, ADA 12. Final minute counts are BTC 17,156, ETH 17,161 and ADA 17,164. This correction was completed before the pilot ran. Source timestamps have explicit +00:00 offsets and are stored as `source_timestamp_us`; no independent local receipt or exchange timestamp is invented. Earlier zero-invalid counts describe the initial finite/order checks, not this final screen. Source archives and the published CC0 extracts are independently identifiable through CC0_DATA_PROVENANCE.json.
