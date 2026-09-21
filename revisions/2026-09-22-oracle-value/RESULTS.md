# How much price and liquidity information was available ex post?

Post-pilot exploratory diagnostic. Oracle schedules use future information and are not implementable strategies. Independent-snapshot replay is the clean optimization upper bound reported below.

| Sale / displayed depth | Learned price | Hindsight price input | Learned liquidity | Hindsight liquidity input | Full oracle | Added liquidity given price |
|---|---:|---:|---:|---:|---:|---:|
| 1% | -3.213 | 25.799 | -1.518 | -1.517 | 25.833 | 0.033 |
| 5% | -3.309 | 25.805 | -1.835 | -1.068 | 25.850 | 0.045 |
| 20% | -1.329 | 27.155 | -0.197 | 0.472 | 27.231 | 0.075 |

Positive values are savings in basis points relative to the seasonal current-book reference. Means give equal weight to each evaluation date and to assets within dates.

At the central size, the hindsight-price schedule saves 25.805 bps and the full oracle saves 25.850 bps. Adding realized future books after future prices are known contributes 0.045 bps. The learned price and liquidity policies instead lose 3.309 and 1.835 bps.

Only the full oracle is an upper bound on proceeds within this planner. The single-input hindsight schedules optimize using one realized input and a reference for the other. The liquidity-only schedule can therefore lose total proceeds when its timing conflicts with subsequent price changes. The initial protocol described all three as upper bounds; that wording was too broad and is corrected here without changing the schedules or results.

The negative learned-to-hindsight comparison shows that the tested forecasts move schedules in the wrong direction on average. It is not an estimate of statistical forecast efficiency. Hindsight value establishes ex-post decision relevance, not forecastability.

## Interpretation

The earlier negative result is not explained by an absence of price-timing opportunity. Future prices dominate this short-horizon replay: once future prices are supplied, adding the realized future book contributes only 0.033, 0.045 and 0.075 bps at the three sizes. The incremental amount rises with size but remains small relative to roughly 26--27 bps of hindsight price value. The research problem is therefore causal price forecasting and safe policy calibration; liquidity forecasts are a secondary refinement under this design.

Five dates, one exchange, snapshot replay and hindsight optimization prevent a publication-grade effectiveness claim. The next study needs longer data and a fresh evaluation period. These observations cannot serve as untouched confirmation after this diagnostic.
