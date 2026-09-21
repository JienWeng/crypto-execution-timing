# Price information versus liquidity information in cryptocurrency execution

Status: research design, 21 September 2026. No new empirical result or novelty certification. The completed forecast-selection study remains unchanged.

## Recommended question

Does forecasting available liquidity reduce cryptocurrency sale costs more than forecasting prices, and how does their relative value change with order size?

Working title: **Should cryptocurrency sellers forecast prices or liquidity?**

The economic mechanism to test is a trade-off: waiting can improve the sale price but can also expose a larger order to a thinner book. The relative importance of these channels may depend on order size relative to available depth. This is a hypothesis, not a finding. Liquidity and price forecasting are already established execution topics; their use alone is not the proposed contribution.

## Contrast with the completed study

| Dimension | Completed study | Proposed study |
|---|---|---|
| Question | Which forecast-selection loss is useful? | Which kind of information is worth forecasting? |
| Information | Price forecasts | Price, liquidity, and their interaction |
| Costs | Assumed quadratic coefficients | Observed spread and depth, with explicit limits on counterfactual impact |
| Scale | Normalized compulsory sale | Explicit order sizes and depth-relative sizes |
| Main comparison | Economic versus endpoint-error selection | Liquidity-only versus price-only execution |
| Economic insight | Some forecast errors do not affect schedules | Conditions under which price information or liquidity information is more valuable |
| Main limitation | No advantage over the no-signal baseline | Requires suitable order-book data and fresh evaluation |

## Controlled comparison

Use a two-by-two information design under one execution engine:

1. Neither forecast: current observable market state and a frozen baseline schedule rule.
2. Price forecast only: the same engine with price predictions.
3. Liquidity forecast only: the same engine with spread/depth predictions.
4. Both forecasts: the same engine with both inputs.

All policies observe current quotes, have identical constraints, update times, training windows, model-selection budgets, and completion deadlines. The baseline must already respond to current liquidity; otherwise the experiment would confound forecasting with access to current information. Include TWAP and a causal volume-participation rule as practical secondary benchmarks. Do not use realized future volume to implement a purportedly feasible VWAP strategy.

Primary contrast: liquidity-only minus price-only savings, measured against the same arrival-price implementation-shortfall convention. Also report each policy against the no-forecast baseline. Define the interaction as savings(both) - savings(price) - savings(liquidity) + savings(neither). This is a controlled replay comparison, not causal identification of market responses.

Before evaluating new data, lock one primary horizon, one primary size convention, asset universe, forecast candidates, cost accounting, missing-data rules and inference method. Predefine a small secondary size grid to test the hypothesized size relationship. Report the whole grid, including reversals and failures. A boundary between price-dominated and liquidity-dominated regions is a possible result, not an assumption; report its uncertainty and allow that no stable boundary exists.

## Data and realism requirements

- Timestamped bid/ask prices and quantities, depth updates or adequately frequent snapshots, and trades. Validate sequence continuity and document coverage.
- State explicit order sizes, fees, latency assumptions, depth coverage, and the reference price.
- Small market-order child trades avoid unobservable passive queue-priority assumptions. Account for consumed depth within the simulation; do not repeatedly reuse the same displayed quantity.
- Historical replay does not reveal how the market would respond to our own orders. Limit participation and depth consumption, report sensitivities, and distinguish mechanical book-walking costs from persistent endogenous impact.
- Exclude or bound orders exceeding observed depth according to a frozen rule; do not extrapolate missing depth silently.
- Existing January–August 2026 bars are development evidence. Existing inspected outcomes cannot become an untouched confirmation sample. Lock future collection/evaluation dates only once feed feasibility and sample precision have been assessed.
- No purchases, exchange orders or credential use are required by this design. Redistribution rights must be checked before adding third-party data to the public repository.

## Execution sequence and stopping rules

1. Audit closest papers at full-text level and confirm whether they already make the same information-by-order-size comparison. Narrow or abandon a duplicated claim.
2. Verify affordable/public order-book history with sufficient duration and permitted redistribution, or establish a validated prospective feed. Binance's public bar archives do not by themselves establish historical spot depth coverage.
3. Build and validate replay accounting with synthetic known-cost examples, missing-update cases, and no-lookahead checks. Freeze the design after a development-only precision assessment.
4. Evaluate all four policies on the same held-out orders. Use paired date-level inference that respects overlapping orders and common market shocks. Include uncertainty from fitting where computationally feasible; otherwise qualify intervals explicitly.
5. Treat baseline superiority, magnitude, stability across assets/dates, and cost realism as separate requirements. Positive comparisons against a weak forecast policy are insufficient.
6. Write the manuscript around supported findings. If no useful advantage or stable mechanism emerges, retain that result rather than searching subsets until a positive claim appears.

## Prior-art screen and remaining gap

- Kweon, Yim and Min (2024), *Optimizing Sequential Predictions for Order Execution: a Decision Focused Learning Approach*, ICAIF, DOI 10.1145/3677052.3698665. Institutional abstract inspected: liquidity forecasting integrated into adaptive liquidation and decision-focused training already exists. https://snu.elsevierpure.com/en/publications/optimizing-sequential-predictions-for-order-execution-a-decision-/
- Bank, Cartea and Körber (2026), *Optimal execution and speculation with trade signals*, DOI 10.1007/s00780-026-00602-x. Publisher page inspected: signals, liquidity provision and spreads already interact in execution theory. https://link.springer.com/article/10.1007/s00780-026-00602-x
- Chevalier, Hafsi, Ly Vath and Pulido, *Optimal Execution under Liquidity Uncertainty*, arXiv:2506.11813, version revised 11 April 2026. Record inspected; full-text assessment remains required. https://arxiv.org/abs/2506.11813
- Irshad and Biswas (2026), *Uncertainty-Aware AI: Conformal Prediction versus Reinforcement Learning for Optimal Trade Execution*, DOI 10.19139/soic-2310-5070-4159. Previously verified publisher abstract and author repository show uncertainty-based execution controls already exist. https://github.com/Asadullah-Irshad/Conformal-VWAP-Execution/
- Official Binance archive documentation: https://github.com/binance/binance-public-data

This targeted screen supports the choice of a more substantive empirical comparison, not a claim that nobody has studied it. The candidate contribution is a measured, reproducible estimate of the relative value and interaction of price and liquidity forecasts across order sizes in cryptocurrency execution. Its novelty and effectiveness still need evidence.
