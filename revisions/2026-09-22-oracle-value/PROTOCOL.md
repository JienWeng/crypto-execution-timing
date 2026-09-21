# Development diagnostic: attainable value versus perfect-information value

Recorded 22 September 2026 before running this diagnostic. This is a new exploratory study motivated by the completed five-date pilot. It is not prospective confirmation, and it does not alter or replace the frozen pilot results.

## Question

Did the learned policies fail because future price and liquidity have little decision value, or because the pilot forecasts failed to capture information that would have been valuable?

## Data and sample

Use the same public CC0 Coinbase BTC, ETH and ADA minute books, training dates, evaluation dates, arrival windows, horizons, order sizes, seasonal reference, finite-depth planner, child cap and replay accounting as the frozen pilot. Retain every original policy result unchanged.

## Upper-bound policies

At each evaluation arrival, add three hindsight schedules:

1. **Oracle price:** use the realized future midpoint path with the reference spread and depth paths.
2. **Oracle liquidity:** use the reference midpoint path with realized future bid-side book costs. Preserve each realized future book's midpoint-relative bid-price ladder and quantities.
3. **Full oracle:** optimize directly over the realized future bid books.

All oracle schedules are chosen with information unavailable at the decision time. They are ex-post upper bounds under the replay model, not implementable strategies. Their purpose is to measure decision relevance. They receive the same order-completion constraint and one-third child cap. If finite forecast depth is insufficient, record failure rather than invent depth.

Evaluate all schedules on the same realized books under retained-depletion and independent-snapshot conventions. Because an oracle planner that ignores retained hypothetical depletion can rank schedules imperfectly under the retained-depletion replay, report both conventions and use the independent-snapshot convention as the clean optimization upper bound. Never describe an oracle result as achievable profit.

## Estimands

For each size, report savings relative to the same reference policy for learned price, learned liquidity, oracle price, oracle liquidity and full oracle.

- **Decision-relevance contrast:** oracle liquidity minus oracle price savings.
- **Forecast realization ratio:** learned savings divided by corresponding oracle savings only when oracle savings is positive. Report the numerator and denominator beside every ratio; do not average unstable episode-level ratios.
- **Unused value:** oracle savings minus learned savings.

Report daily and asset means. With five evaluation dates, use descriptive estimates only. A positive oracle result with a negative learned result supports the statement that useful information existed ex post but the tested forecast did not capture it. It does not prove that the information is forecastable.

## Stopping rule

Run the fixed diagnostic once, preserve all outputs, and do not alter oracle definitions or subsets after seeing results. The result determines the next research need:

- Large, stable oracle value plus poor learned value: improve causal forecasting and obtain longer data.
- Small oracle value: the decision/horizon has little room for forecast gains under this replay.
- Unstable oracle value: obtain longer data before refining models.

No manuscript claim of effectiveness follows from this diagnostic alone.
