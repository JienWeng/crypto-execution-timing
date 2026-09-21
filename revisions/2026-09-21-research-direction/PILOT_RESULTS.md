# Price versus liquidity: development pilot results

five-date development pilot; descriptive, not confirmatory.

This is an implementation and research-feasibility test. It does not replace the existing manuscript with a validated new empirical contribution.

Training: 8–13 April 2021. Evaluation: 14–18 April 2021. Assets: BTC, ETH and ADA on Coinbase. Forecasts and order sizes were fixed before strategy outcomes.

Valid arrival windows: 691. Common complete arrivals across all three sizes and all five policies: 685. Means give equal weight to each date and, within a date, each represented asset.

| Sale / displayed depth | Price savings | Liquidity savings | Both savings | Liquidity − price | Interaction |
|---|---:|---:|---:|---:|---:|
| 1% | -3.126566 | -1.525282 | -3.839610 | 1.601284 | 0.812239 |
| 5% | -3.245108 | -1.860615 | -3.795329 | 1.384493 | 1.310394 |
| 20% | -1.329045 | -0.195520 | -1.782121 | 1.133524 | -0.257556 |

All entries are basis points; positive savings means lower cost than the seasonal current-book reference.

Prespecified large-minus-small contrast in relative liquidity value: -0.467760 bps. This is a point estimate, not an established crossover.

Completion guard triggered (>1% incomplete in any arm/size): **False**. Consult summary.json for every completion rate. If triggered, complete-order contrasts do not support claims for the original arrival population.

## Cost explanation at the 5% size

| Policy | Price-timing savings | Spread savings | Depth savings | Total |
|---|---:|---:|---:|---:|
| price | -3.267153 | 0.037385 | -0.015340 | -3.245108 |
| liquidity | -1.950141 | 0.060141 | 0.029385 | -1.860615 |
| both | -3.825120 | 0.046060 | -0.016268 | -3.795329 |

The components are an exact accounting identity, not causal effects. Common proportional fees scale differences in gross proceeds; the 10bps illustrative sensitivity is retained in episodes.csv.

## Interpretation limits

- Five evaluation dates cannot establish reliable population uncertainty or persistent effectiveness. No significance tests or confidence intervals are presented.
- The sample is from April 2021 and a single exchange. Current-market and cross-venue generalization are untested.
- Snapshot replay lacks counterfactual market responses, queue information, independently observed receipt latency, and exchange lot/minimum-order enforcement.
- Retained consumed depth is a stated sensitivity convention. A price leaving the top levels does not prove cancellation. Independent-snapshot results are separately retained.
- Full-window quality exclusions condition on subsequent data availability; completion exclusions can introduce policy-dependent selection. Counts and the completion guard must accompany every claim.
- The restricted liquidity model changes spread and total quantity while preserving other ladder gaps. A weak result can reflect this approximation and forecast error; it does not establish that liquidity information is intrinsically worthless.

See CONTRIBUTION.md for the intended empirical claim, PRIOR_ART_AUDIT.md for close predecessors, and PILOT_PROTOCOL.md for frozen design.

## Completion and practical benchmark

| Policy | 5% savings (bps) | Completion at 1% | Completion at 5% | Completion at 20% |
|---|---:|---:|---:|---:|
| reference | 0.000000 | 100.0000% | 100.0000% | 99.7106% |
| price | -3.245108 | 100.0000% | 100.0000% | 99.1317% |
| liquidity | -1.860615 | 100.0000% | 100.0000% | 100.0000% |
| both | -3.795329 | 100.0000% | 100.0000% | 99.2764% |
| twap | -2.563053 | 100.0000% | 100.0000% | 100.0000% |

TWAP is a secondary benchmark. Its loss against the reference is descriptive evidence on these same dates, not independent confirmation of the reference policy.
