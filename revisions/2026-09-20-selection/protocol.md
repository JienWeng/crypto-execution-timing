# Forecast selection experiment — frozen before outcome computation

Recorded 20 September 2026. User authorizes planning and executing a stronger scientific test. This is a historical, retrospectively motivated extension after BTC/ETH outcomes were inspected, not preregistration or prospective replication. No assertion of guaranteed publishability.

## Question and prior art
Does selecting a price-path forecast by its preceding-month execution objective improve next-month execution compared with selecting it by final-price MSE? Kweon, Yim and Min (ICAIF 2024, DOI 10.1145/3677052.3698665) already study decision-focused learning for execution under stochastic liquidity. Our question is a narrow, interpretable model-selection comparison; no first-use claim for decision-focused execution.

## Fixed sample and comparisons
- Primary asset-transfer sample: SOLUSDT, BNBUSDT, XRPUSDT Binance spot monthly 1m klines, Jan–Aug 2026; all three included or sample reported incomplete. Not chosen using outcome returns. These assets are not yet analysed in this project, but share calendar shocks with BTC/ETH.
- Secondary development sample: BTCUSDT, ETHUSDT, same dates, already inspected in earlier analysis.
- Six rolling train/calibrate/evaluate windows: Jan/Feb/Mar through Jun/Jul/Aug, independently fitted per asset. 48 daily decisions at UTC 00:05,00:35,...23:35. Observe bars i−5 through i−1; denominator open i; execute at opens i+1 through i+15. No incomplete bars, future centering, evaluation selection or horizon search.
- Primary eta=2, inventory preference r=1. All six eta in{0.5,2,5}, r in{0,1} retained. Monetary eta=2,r=0 is a prominent secondary model, not estimated real cost.

## Candidate models, shared by all selectors, fixed tie order
1. zero forecast, yielding cost-optimal no-signal baseline;
2. training mean 15-price path;
3. OLS intercept plus one-bar signed taker-volume imbalance;
4. OLS intercept plus five-bar signed taker-volume imbalance;
5. OLS intercept plus five-bar log return from open i−5 to open i, known at decision;
6. ridge with penalty 0.1 on mean-squared training loss;
7. ridge with penalty 1.0 on mean-squared training loss.
Ridge uses five training-standardized predictors: flow1, flow5, log return1, log return5, log(1+five-bar base volume). Intercept is unpenalized. All forecasts include fitted intercepts, except zero. No hyperparameter search. Predictions/feature scaling fit only in training month. Non-finite data or incomplete grids fail loudly. Both ridge penalties fixed regardless of results.

## Selection and baselines
All selection uses only calibration outcomes and chooses one model for the entire following evaluation month. Deterministic tie tolerance 1e−12, favor earlier model (zero first).
- endpoint: minimize mean squared final-price error;
- path: minimize mean squared error over all 15 prices;
- contrasts: minimize MSE after demeaning each forecast and realized price path across its 15 slots (secondary mechanism control);
- economic: maximize mean baseline-relative execution-objective gain under that scenario.
No selector receives unique abstention or attenuation choices. Also report every fixed candidate and baseline. Cost scenario selection occurs separately using the same metric definitions, never evaluation data.

## Primary estimand and secondary diagnostics
Primary: mean paired economic-minus-endpoint objective gain in the three transfer assets, eta2/r1. Equal asset weighting follows complete balanced episodes on every date. Whole-calendar-date means retain all three assets jointly. Conditional percentile 95% intervals use 4,000 circular moving-block draws of seven consecutive dates, seed 20260920. Circular wrap stated explicitly; blocks cross month boundaries. Include 1-day and14-day intervals as prespecified sensitivity; all fitted models and selected IDs held fixed. No full retraining uncertainty or guarantee under arbitrary dependence.
Secondary: economic-minus-zero, economic-minus-path, economic-minus-contrasts; all fixed candidates; perasset and permonth means; selected model identities and baseline frequency; all6cost scenarios; money-scored outcomes; leave-one-evaluation-month-out descriptive checks, no refitting or selecting omissions; objective decomposition into price benefit and scheduling cost. Report break-even additional differential cost simply as observed gain, not as measured spread or fee allowance. Positive primary mean with interval excluding0 supports only in-model relative effectiveness; it does not prove real profitability, full model superiority, or novelty.

## Reproduction, validation and stopping
Write protocol/hash before new-asset extraction or outcome computation. Archive hashes and official checksum/schema checks. Unit tests cover causal feature windows, selection isolation from evaluation outcomes, baseline fairness, projected-gradient KKT and direct objective decomposition, bootstrap shared-date resampling. Test and run once; implementation errors may be corrected transparently with run receipts, never hidden changes in models, sample or outcomes. Preserve all result files, run log, fits and selected IDs. Stop this experiment after reporting the frozen comparisons, whether favorable, unfavorable or uncertain. Do not expand models or months to chase significance. A later research design requires a separately dated rationale and honest re-use disclosure.
