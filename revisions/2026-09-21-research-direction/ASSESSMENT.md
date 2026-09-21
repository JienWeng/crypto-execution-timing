# Contribution assessment after the first order-book pilot

## The intended contribution is now explicit

Estimate how the execution value of price forecasts, liquidity forecasts and their combination changes with order size, and identify whether differences come from price timing, spread payments or depth costs. The comparison gives every policy the same current information and execution constraints.

This would improve substantially on a forecast-selection exercise if a longer held-out sample establishes a stable, economically material relationship. The closely related literature means the four-arm design alone does not guarantee novelty.

## What the pilot actually establishes

The computational comparison is implemented and reproducible. Three CC0 order-book datasets supply 691 valid arrival windows across five held-out dates; 685 arrivals complete under all arms and sizes. Thirteen tests pass. An isolated rerun exactly matches episode outputs, fitted models, forecast errors and the sample audit. Independent review reproduces all reported means and accounting identities.

The new learned policies do not improve on the reference in pooled results. At the central size, liquidity forecasts save about 0.090 bps in spread and depth costs but lose 1.950 bps through timing. The relative liquidity-versus-price advantage declines by 0.468 bps from the smallest to largest order size. This is contrary to the initial increasing-relative-value hypothesis. Five dates do not establish either a universal failure or a stable reverse relationship.

The readable economic observation is that reducing the cost of finding buyers can be outweighed by exposure to price changes. That observation is not itself new. The stronger proposed empirical contribution remains unestablished.

## Decision

Preserve the pilot, including its negative baseline comparisons and all dates. Do not present the new report as a submission-ready replacement for the earlier manuscript. Do not add forecasting models or omit dates to obtain a better headline on these held-out observations.

The next substantive requirement is a longer, independently evaluated order-book sample with sufficient variation across assets, venues and market conditions. Use development data to determine precision requirements before freezing the new evaluation; a nominal observation count is not a power calculation. The CC0 Dryad multi-exchange history is a candidate, but its normal public download and API returned 403/401 in this session. Access must be resolved legitimately. The accessible Tardis sample does not meet the requested fully open release conditions, so it is excluded from the public study package.

Existing source-download and provenance tooling can be extended once suitable data are available. The pilot's forecast family also holds some ladder geometry fixed and omits lot/minimum-order rules and endogenous impact; any extension must be defined and validated before inspecting the new evaluation outcomes.

No journal submission, paid data purchase, contact with authors or exchange trade has been made.
