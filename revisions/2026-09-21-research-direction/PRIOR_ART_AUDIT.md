# Prior-art audit: price versus liquidity information

Audit date: 21 September 2026. Targeted primary-source screen, not a systematic review or novelty certificate. No experiments or manuscript changes were performed in this audit.

## Main finding

The credible contribution is a held-out, controlled estimate of the **incremental value of forecasting price movements and liquidity costs at different order sizes**, beyond reacting to the currently visible book. Neither joint price/liquidity modelling, forecasting liquidity for execution, nor the observation that order size matters is new. A claim that this is the first such comparison is not supported by this screen.

## Closest evidence

| Study and primary source | Material actually inspected | Established contribution and overlap | Proposed distinction and remaining risk |
|---|---|---|---|
| Ahabchane, Cenesizoglu, Grass and Jena (2024), *Reducing transaction costs using intraday forecasts of limit order book slopes*, Journal of Forecasting 43(8), 2982–3008. [Publisher](https://doi.org/10.1002/for.3164); [institutional working paper](https://www.cirrelt.ca/documentstravail/cirrelt-2021-36.pdf). | Publisher metadata and indexed full-text passages; institutional 2021 predecessor, introduction and execution setup, pp. 1–4. Versions distinguished. | Forecasts book-based transaction costs and optimizes scheduled quantities. Uses NYSE depth and compares seasonal, autoregressive and neural forecasts. Already supplies an empirical economic-value argument for liquidity forecasts. | Our proposed price-only/liquidity-only/both comparison must establish additional value. The predecessor uses fixed morning forecasts and assumes recovery between five-minute intervals; causal updates and conservative replay would differ, but implementation changes alone are weak novelty. |
| Fouque, Jaimungal and Saporito (2022), *Optimal Trading with Signals and Stochastic Price Impact*, SIAM Journal on Financial Mathematics 13(3), 944–968. [Publisher](https://doi.org/10.1137/21M1394473); [author full text, arXiv v3](https://arxiv.org/html/2101.10053). | Full-text introduction, model, sections 2.4 and 4. | Jointly models trading signals and stochastic impact, including their dependence. Compares classical execution, signals with deterministic impact, and stochastic-impact strategies. Estimates impact using fictitious book-walking orders in MSFT, then illustrates strategies in simulation. | Joint modelling or comparing signal-aware versus liquidity-aware execution is already close prior art. Candidate distinction is an empirical four-arm forecast ablation with common observed state, genuinely held-out forecasts and depth-relative size estimates. |
| Kweon, Yim and Min (2024), *Optimizing Sequential Predictions for Order Execution: a Decision Focused Learning Approach*, ICAIF, 719–727. [Institutional abstract](https://snu.elsevierpure.com/en/publications/optimizing-sequential-predictions-for-order-execution-a-decision-/); [author code](https://github.com/sunminkweon/OrderExecutionDFL); DOI 10.1145/3677052.3698665. | Institutional abstract and author repository README; full article not obtained. | Repeatedly re-optimizes liquidation using predicted liquidity and trains forecasts for the execution objective. Code README requires minute-level date/time/volume data and says TAQ input is not supplied. | A price-versus-liquidity information comparison may differ, but absence of that comparison in an abstract is not proof. Obtain full text before final novelty wording. Volume forecasts and displayed-depth forecasts should not be treated as interchangeable. |
| Bank, Cartea and Körber (2026), *Optimal execution and speculation with trade signals*, Finance and Stochastics. [Open publisher article](https://doi.org/10.1007/s00780-026-00602-x). | Publisher full text, especially section 3.3 and numerical setup. Published 10 September 2026. | Models liquidity-dependent order-flow/impact and signals about imminent order flow. Numerically distinguishes information about liquidity taking and liquidity provision; profitability depends on spread. | Cannot claim first comparison of information types or first interaction of signals with liquidity. Ours would compare learned forecasts under a common replay engine, with order-size dependence estimated on historical crypto books rather than claim a new control principle. |
| Chevalier, Hafsi, Ly Vath and Pulido, *Optimal Execution under Liquidity Uncertainty*, arXiv:2506.11813. [Author record](https://arxiv.org/abs/2506.11813). | Record accessible; attempted HTML versions unavailable. | Relevant unresolved overlap with uncertain-liquidity execution. | Full-text assessment remains open; no claim about missing comparisons is justified. |

## Make the contrast economically meaningful

The question should be: **For a compulsory sale of a given size, is it more valuable to predict where the price is going, or how expensive it will be to find buyers?**

Define four policies with the same observed current book, deadline, risk constraint, forecasting budget and feasible actions. Baseline future inputs should use explicit causal persistence or seasonal reference forecasts. Price-only and liquidity-only replace one future input each; both replaces both. Thus “no forecast” means no incremental predictive model beyond the chosen reference, not ignorance of currently visible liquidity. The choice of reference must be reported because it determines the estimand.

For common arrival-price shortfall C and savings S = C_baseline − C_policy, report:

- Relative value: S_liquidity − S_price, by prespecified depth-relative order size.
- Incremental values: S_price and S_liquidity versus the common baseline.
- Complementarity: S_both − S_price − S_liquidity (baseline savings are zero).
- Net usefulness: S_both versus both single-input policies and the baseline, including uncertainty and fees.

The interaction is a replay performance interaction, not causal identification of market equilibrium. Identical reference forecasts must recover identical policies; otherwise the four-arm comparison is confounded by implementation.

## Contribution claim that is available now

“ We design a controlled comparison to measure how the execution value of price and liquidity forecasts changes with order size in cryptocurrency markets. ”

This is a design statement. Replace it with an empirical claim only after evaluation. A useful future finding would identify a stable, economically material change in information value across order sizes, establish whether combining forecasts improves on a credible baseline, and show which cost channel explains it. A crossover is not required to exist and should never be imposed by the model or selected after seeing results.

## Main reviewer risks and required responses

1. **Predictable theory restated as a finding.** Larger quantities mechanically pay greater depth costs. Separate this mechanical fact from the incremental value of imperfect, causal forecasts. Compare feasible policies and report forecasting errors and realized value, not only oracle schedules.
2. **Weak baseline.** Every policy must react to the same current book. Include persistence/seasonality references, TWAP and a feasible causal participation benchmark.
3. **Unrealistic liquidity.** Displayed depth is neither guaranteed fill liquidity nor persistent endogenous impact. Report latency, finite depth, consumed quantities, replenishment assumptions and participation limits.
4. **Sample-selected boundary.** Lock the size grid and primary comparison; report all assets, dates and sizes. A descriptive sign change without precision or stability does not establish a usable threshold.
5. **Crypto relabelling.** A new asset class alone is a weak distinction. The economic contribution must be the measured incremental information value and its stability under realistic costs.
6. **Overstatement of coverage.** This audit does not establish absence of prior four-arm studies. Closest full-text acquisition and backward/forward citation screening remain necessary before submission.

## Recommendation

Proceed with the four-arm design, with the **size-dependent incremental value of information** as the central contribution. Treat an implementation-shortfall decomposition into price-timing and liquidity-payment terms as explanatory accounting, not a new theorem. Keep the earlier forecast-selection result as motivation or an appendix; do not present it as evidence that the new policies work.
