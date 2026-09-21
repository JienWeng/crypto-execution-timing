# Should cryptocurrency sellers forecast prices or liquidity?

## The question readers should understand immediately

A seller may wait because the price is expected to rise. But if fewer buyers are available later, a large sale may receive a worse average price despite that rise. Which prediction deserves more attention: the future price, or the future cost of finding buyers?

We will measure how the answer changes with the size of the sale relative to available liquidity. The comparison uses the same current information, execution constraints and forecast model budget. Only the forecast input changes.

## Three contributions to establish with evidence

1. **Relative information value.** Measure the execution savings from price forecasts, liquidity forecasts and both together. Compare each against a credible rule that already observes current liquidity.
2. **Order-size dependence.** Test whether the relative value changes as the sale grows relative to displayed depth. Estimate the relationship and its uncertainty; do not assume that there is a crossover or select one after inspecting results.
3. **An economic explanation.** Separate differences in sale proceeds into price timing, spread, depth and fees. Determine whether a policy saves liquidity costs at the expense of worse prices, and whether the balance is economically useful.

These are proposed empirical contributions. Neither the accounting decomposition nor the observation that larger orders face greater depth costs is new. The evidence must concern the value of imperfect forecasts that could actually have been produced before execution.

## What would make the contribution obvious in the paper

The introduction should state the decision problem in its opening paragraph. The final introductory paragraph should report the measured relative value, order-size relationship and cost explanation with actual magnitudes once available. Avoid statements that we merely “apply machine learning to crypto.”

The main figure should put order size relative to depth on the horizontal axis and held-out execution savings on the vertical axis, showing price-only, liquidity-only and combined forecasts with uncertainty. It must include the zero-savings baseline. A second panel should show the liquidity-minus-price contrast. A separate accounting figure should show the price-timing and liquidity-cost components. No illustrative curve should be labelled as an empirical result.

The main table should compare all four policies at the prespecified primary size, reporting savings, uncertainty, completion rate and the proportion of orders that improve. A result based on unfinished orders, omitted stress periods or weaker information access for the baseline does not establish the proposed contribution.

## What changes from the completed manuscript

The completed study asks which loss function should select price forecasts. This study asks which forecast target is economically useful. The completed study assumes trading-cost coefficients; this study needs observed price ladders and quantities. The completed study's relative improvement does not establish savings against abstention. The new study must report improvement against the common baseline directly.

The old result remains a motivation: statistical prediction quality alone does not settle the seller's decision. Its numerical results cannot be used as findings about liquidity forecasts.

## Honest decision rule

If held-out evidence shows a stable change in relative information value, the paper can explain when to prioritize each forecast. If one forecast dominates throughout, report that instead. If neither improves the baseline, or the pattern is too uncertain, this design has not yet supplied the stronger practical contribution sought here. Do not continue adjusting the same held-out sample until it yields the desired conclusion.

Status: design and execution infrastructure in development; new empirical contribution not yet established.
