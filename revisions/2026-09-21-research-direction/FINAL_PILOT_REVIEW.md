# Independent final pilot reporting review

21 September 2026. Reviewed report_pilot.py, PILOT_RESULTS.md and submission/price-liquidity-study/source/research_report.tex against results/episodes.csv and summary.json. No models were refitted, no policies changed, and no new strategy experiments were run.

## Independent verification

Used a separate CSV aggregation with Python statistics.mean, rather than executing report_pilot.py. Verified uniqueness of asset/date/arrival/size/arm records within each replay mode. Both modes contain 691 arrival groups and 685 groups complete across all fifteen size-policy combinations. All fifteen asset-date cells remain represented.

Recomputed means by averaging arrivals within asset-date, assets within date, then the five dates. Every policy/size mean agrees with summary.json within 1e-10 bps. This weighting is described accurately in the reports. It is an equal-date/equal-asset descriptive mean, not notional-weighted portfolio performance.

At the central 5% size, main-replay savings against the reference are:

| Policy | Independently recomputed savings, bps |
|---|---:|
| Price | -3.2451079367332194 |
| Liquidity | -1.860615036347088 |
| Both | -3.7953285247004565 |
| TWAP | -2.5630527991723744 |

Thus liquidity minus price is +1.3844929003861314 bps, while liquidity itself remains worse than the baseline. The large-minus-small relative-value contrast is -0.46775991954514073 bps. The manuscript correctly distinguishes relative improvement from effectiveness and correctly reports the hypothesized increasing relative value as unsupported by this point estimate.

Across complete raw episode rows, the largest monetary identity discrepancy between shortfall and timing/spread/depth/fee components is approximately 1.21e-10 quote-currency units. The component signs in the report now match timing shortfall rather than timing gain. Reported 5% liquidity components sum to the negative net saving. Median 5% arrival notional recomputes to 7430.438206085519, supporting the rounded USD 7,430 statement.

## Completion and support

At 1% and 5%, all 691 arrivals complete for every policy. At 20%, main-replay incomplete counts are reference 2, price 6, liquidity 0, both 5 and TWAP 0. Therefore the minimum size-policy completion rate is 685/691 = 99.13169319826338%, and the >1% incompletion guard is correctly false. Independent-snapshot mode has the same counts. No forecast fallback occurred.

The six large-order failures are excluded from **all headline sizes**, including smaller sizes that did complete, because the report uses one common all-size/all-arm support. This yields a coherent paired size contrast and is clearly disclosed. It still conditions on policy-dependent completion; the guard not triggering is not proof of absence of selection bias. Current report language correctly retains this limitation.

Independent-snapshot central-size results are numerically close to the main mode, as claimed. The largest negative central-size daily savings occur on 18 April for every learned policy and TWAP. This date remains in every reported mean. There is no evidence of an omitted losing date or selective favorable asset/size presentation.

## Claims assessment

The report is appropriately restrained. It states that all three learned policies underperform the reference at every reported size, that five dates are insufficient to establish persistent effectiveness, and that the pipeline does not yet constitute a stronger completed empirical paper. It does not disguise the negative baseline comparisons behind the positive liquidity-minus-price contrast. The old dataset, restricted forecast model, hypothetical fills, unresolved latency and lot-size issues, and lack of novelty certification are visible.

The economic interpretation is supported at the accounting level: the liquidity-only policy saves a small amount in spread/depth payments but incurs a larger price-timing loss. Calling this a pilot observation rather than a causal or persistent market mechanism is necessary and is done.

## Minor improvements before a submission manuscript

1. Add TWAP as a column or row to the compact Markdown main table, and display the per-size completion rates in the same artifact rather than requiring summary.json. They are currently retained and the PDF mentions TWAP, so this is accessibility rather than hidden evidence.
2. Include the 5% positive interaction (+1.310394 bps) only with a reminder that both forecasts still lose more than either single forecast. Positive factorial interaction does not mean the combined policy is useful. The Markdown reports interaction but the PDF avoids emphasizing it.
3. Distinguish “five reporting date clusters” from “five independent dates.” Serial independence of these consecutive days has not been established. Neither report presently uses independence to construct inference, so this does not change numerical results.
4. “No confidence interval ... is justified” in the figure caption is broader than necessary. “Descriptive pilot; no inferential intervals reported” would state the decision without claiming all possible small-sample uncertainty methods are invalid.
5. Raw-record count, source license, reconstruction schema and reproduction claims were not independently re-audited here; they require the existing data/provenance and reproduction records. No contradictory statement was observed.

## Conclusion

No material numerical, accounting, weighting, completion-guard or selective-claim error found. The present results support an honestly reported development pilot and a clearly specified future research question. They do not establish the desired practical contribution or justify a publication-effectiveness claim. No outcome-driven changes are recommended.
