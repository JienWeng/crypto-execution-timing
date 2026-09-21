# Hyperliquid order-event data gate

Checked 22 September 2026. No execution-policy outcomes were evaluated.

## Source acquired

Open Zenodo dataset *An Open Book: Level 4 Order Book Data from the Hyperliquid Exchange*, DOI 10.5281/zenodo.18184441, CC BY 4.0. The accepted SOL order-status archive for December 2025 is 6,271,301,388 bytes. Its verified MD5 is `5abed7980b4d8c57651dbb9237c02d88`, matching the publisher record. The local file remains outside Git.

The first hourly member contains 2,362,845 records ordered by nanosecond timestamp, from 2025-11-30 23:59:59.867476878 UTC through 2025-12-01 00:59:59.774857692 UTC. Decoder and state-transition unit tests pass for synthetic events.

## Gate failure

Directly treating order-status `open`, `filled` and cancellation records as visible-book changes fails. Only one of sixty initial minute boundaries yields an uncrossed book under the naive documented-state interpretation. Filtering trigger orders and non-resting time-in-force categories does not resolve the problem. Examples include aggressive lifecycle records whose limit protection prices remain in the reconstructed state and cross other apparent resting orders.

The dataset separately supplies a raw visible-book-diff archive. Its documentation says this stream contains the events that actually change visible depth. The diff records have order identifiers but no event timestamp field. A valid historical book therefore requires a verified join between ordered diff events and timestamped order-status events, including one-to-many lifecycle cases, followed by comparison against known snapshots. That join is not established here.

## Decision

Do not use the accepted-order archive alone for price-versus-liquidity execution research. Do not describe it as observed depth or use it to produce schedule outcomes. The 49.6 GB diff archive has not been downloaded in this stage because storage volume does not solve the unresolved timestamp join.

The longer-data study remains blocked at data validity, not statistical significance. The verified Coinbase CC0 pilot and its hindsight diagnostic remain the current evidence. A future Hyperliquid study must first pass visible-book reconstruction checks on development hours and record a new protocol before evaluation.
