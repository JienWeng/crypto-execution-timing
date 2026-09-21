# Frozen development pilot: price versus liquidity

Recorded 21 September 2026 before strategy evaluation on the new order-book data. This is a development pilot, not a preregistered or adequately powered confirmatory study. No strategy outcomes have been inspected when writing this version. Source metadata and data-quality counts have been inspected.

## Data and timing

Source: Martin Søgaard Nielsen's CC0 Coinbase BTC, ETH and ADA order-book dataset, April 2021. Use the one-second snapshot files if their acquisition fits the 5GB raw-data budget. Convert to the last snapshot at or before each UTC minute boundary, retaining original timestamps and rejecting age above five seconds. Do not manufacture local receipt timestamps. Dataset timestamp interpretation and aggregation must be verified first. If only irregular minute snapshots are accessible, do not silently use them as this protocol's input; record a protocol amendment before outcomes.

Training: 8–13 April 2021 inclusive (six complete calendar days). Evaluation: 14–18 April 2021 inclusive (five complete calendar days). Partial 7 and 19 April are excluded in advance. All three assets retained regardless of outcomes. This is a small historical sample from one exchange; no claim about all crypto markets or present-day execution is justified.

Features require the preceding five minute boundaries; labels require the following fifteen. Use only fully valid consecutive windows, with the entire future target inside the assigned training or evaluation interval. Decision arrivals every thirty minutes at :05 and :35 UTC. Predict once at arrival and hold the planned schedule fixed, subject only to carrying unsupported quantities. Execute at the next fifteen minute boundaries. Every policy sees the same current book and historical features.

## Forecasts and reference

One fixed ridge model per asset with an unpenalized intercept and penalty 1 on mean squared error. Training standardization only; features clipped at five training standard deviations at prediction. No parameter search, model selection or evaluation-based attenuation.

Features: one- and five-minute log midprice returns in basis points; log bid-side half-spread in basis points; log total displayed bid quantity; displayed bid/ask quantity imbalance; one-minute log changes of half-spread and bid depth; and sine/cosine UTC time of day. All features observed by arrival.

Targets at each of fifteen horizons: arithmetic midprice change in basis points relative to arrival, log half-spread ratio, and log displayed bid-depth ratio. Clip predicted targets to the training target's 1st and 99th percentiles, per horizon. All forecasts use the same architecture and training data. Report forecast errors separately from execution outcomes.

Reference price path: current midprice. Reference liquidity: current spread and quantities adjusted by the change in a training-only sine/cosine time-of-day profile for log half-spread and log bid depth. Also report plain TWAP. This reference observes current liquidity and incorporates predictable daily seasonality.

Four arms: reference/reference, learned price/reference liquidity, reference price/learned liquidity, learned price/learned liquidity. Preserve the current relative bid-price ladder beyond the half-spread and scale quantities by predicted total-depth ratios. This restricted book forecast does not predict changes in every price-level gap; its limitations constrain interpretation.

## Orders, optimization and accounting

Sale quantities: 1%, 5% and 20% of the arrival snapshot's total displayed bid quantity. Report both quantity and arrival notional summaries. Primary descriptive size contrast: change in liquidity-minus-price savings from 1% to 20%. The 5% size is the primary policy-level table. Report every size and arm.

Planner maximizes predicted proceeds over the fifteen snapshots, subject to nonnegative quantities, complete sale and each child quantity at most one third of the parent quantity. It walks finite predicted depth and shares exact marginal-price ties equally across times. If forecast depth is insufficient, use TWAP and report the fallback count. No extrapolation beyond depth.

Observed replay evaluates against finite bid ladders. Unfilled child quantity is carried forward subject to the same cap; remaining quantity at the deadline is reported as incomplete, never assigned an invented fill. Main replay retains consumed quantity at each price while it remains in the observed top levels, subtracting that debt from later displayed quantity. When a price leaves the observed levels, its debt is forgotten; this is a snapshot convention, not identification of cancellation or recovery. Report independent-snapshot replenishment as a sensitivity. Neither replay captures endogenous market response or actual fills.

Use zero fees for the primary mechanical-cost comparison and 10bps proportional sale fees as an explicit illustrative sensitivity, not a claim about the exchange's historical fee tier. No inventory-risk penalty. Continuous order quantities are a pilot approximation; exchange tick/lot/minimum-notional constraints and subsecond latency are unresolved for submission-grade replay.

Report arrival-midprice implementation shortfall, decomposed exactly into price timing, spread, depth and fees. For incomplete orders, complete-order shortfall is missing and filled-quantity accounting remains separate. Report completion and backlog for every arm. Compute matched complete-order contrasts only with transparent common-support counts; if any arm's incompletion exceeds 1%, do not interpret these contrasts as evidence for the intended population.

## Inference and stopping

The five held-out dates are the independent reporting clusters; numerous intraday observations do not create hundreds of independent days. Report paired daily means, pooled descriptive means and per-asset means. Do not produce publication-style significance claims or an acceptance conclusion from five dates. Show the size pattern even if it is flat, negative, or unstable.

Freeze source and protocol hashes before running the pilot. Preserve the initial run and all failures. Numerical/accounting bugs can be corrected with a recorded reason and a full rerun; changing model choices because of outcomes creates a new exploratory experiment and cannot rescue this pilot's evidence.

The pilot's stopping point is a verified pipeline, transparent results and a decision about the data required for a larger frozen study. A positive pilot is not a demonstrated general contribution. A negative pilot does not authorize searching assets, sizes or dates until an attractive result appears.
