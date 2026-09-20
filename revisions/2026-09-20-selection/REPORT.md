# Forecast selection: completed experiment and contribution assessment

## Material Passport

- Project: cryptocurrency execution timing; follow-up design frozen on 20 September 2026.
- Inputs: public Binance one-minute spot bars for five assets, January–August 2026. BTC/ETH results had already been inspected.
- Primary question: economic selection minus final-price MSE selection on SOL/BNB/XRP, with impact coefficient 2 and inventory preference 1.
- Status: completed, with exact numerical reproduction. Publication suitability remains a separate judgement.
- Protocol and lock: `protocol.md`, `protocol_lock.json`.
- Outputs: `results/study.json`, `fits.json`, `daily.csv.gz`, `primary_episodes.csv.gz`, `run_manifest.json`.
- Reproduce: `OPENBLAS_NUM_THREADS=1 python3 revisions/2026-09-20-selection/reproduce.py`. This uses an isolated output directory and preserves the recorded run.

## Experiment

Seven forecast candidates and four selection criteria share the same calibration observations, cost assumptions and no-signal option. Six monthly training/calibration/evaluation windows produce 48 hypothetical orders per asset per day. Forty verified archives contain 1,749,600 minute bars. The primary historical transfer cohort has 26,496 episodes; the previously inspected BTC/ETH cohort has 17,664.

The seven candidates are zero, a training-mean price path, three single-predictor OLS models and two fixed-penalty ridge models. The selectors use final-price error, full-path error, demeaned-path error or mean execution gain. Models are fitted in the training month; a single choice is fixed in calibration for the following evaluation month. No rule gets an extra abstention or attenuation option.

## Evidence

All numbers below are basis points. Intervals use 4,000 paired seven-day circular moving-block draws, conditional on fitted models and selections.

| Comparison | Mean | Conditional 95% interval |
|---|---:|---:|
| Transfer: economic minus final-price selection | +0.0156367 | [0.0027791, 0.0318384] |
| Transfer: economic minus full-path selection | +0.0112475 | [−0.0000633, 0.0266367] |
| Transfer: economic minus demeaned-path selection | 0 | [0, 0] |
| Transfer: economic versus no-signal baseline | −0.0047949 | [−0.0076617, −0.0022067] |
| BTC/ETH: economic minus final-price selection | −0.0007706 | [−0.0067017, 0.0033132] |

Economic and demeaned-path selectors agree in all eighteen transfer cells across all six cost scenarios, and all twelve BTC/ETH cells at primary costs. The primary final-price comparison remains positive under the specified one-, seven- and fourteen-day blocks and all six cost scenarios. Its effect is 1.56 parts per million of reference notional.

The result is concentrated: SOL supplies about 81% of the improvement, March about 79%, and SOL in March about 66%. Omitting March leaves a positive mean of 0.00397 bps. This is a descriptive check without refitting or a corresponding confidence interval; March remains in the headline estimate.

Economic selection chooses zero in eleven of eighteen primary transfer cells. Every one of its seven nonzero selections subsequently loses against the baseline. Thus lower modelled loss than final-price selection does not establish a profitable strategy or an advantage over abstention. Superiority to full-path MSE remains unresolved, and the BTC/ETH comparison does not show the transfer-sample advantage.

## Contribution and prior work

The earlier paper compared constructed paths from a single forecast. This experiment compares separately fitted candidates, freezes selection before each evaluation month, gives every selector the same no-signal option, and tests the planned primary contrast on newly analysed historical assets.

The useful mechanism is that removing common price-level errors reproduces the economic selector's choices. A quadratic projection identity explains when this equivalence must hold. With zero inventory penalty and feasible equality-constrained solutions, maximizing calibration utility ranks forecasts exactly as demeaned-path MSE. Inequality constraints can break the simple identity; the empirical agreement is therefore checked, not assumed. Numerical near ties require scale-adjusted tolerances for a universal tie-equivalence claim.

The candidate contribution is a transparent comparison of which forecast errors matter for compulsory sales, supported by a controlled model-selection experiment and an explicit baseline. It is not a new general trading algorithm. Kweon, Yim and Min (ICAIF 2024, DOI 10.1145/3677052.3698665) already apply decision-focused learning to execution. `prior_art.md` records the narrower distinction and source-access limits.

This is stronger evidence than a reframing of the original loss. It still does not establish actual execution savings, general superiority or sufficient novelty for acceptance. The new manuscript reports the positive relative comparison alongside the simpler selector's equality and the baseline failure.

## Verification

Eight tests pass, covering feature timing, forecast fitting, shared baseline/ties, isolation from evaluation outcomes, the constrained optimizer, direct objective calculation, paired bootstrap sampling and the demeaned-error identity. An isolated rerun exactly reproduces every study field except completion time. Fitted coefficient bytes and both uncompressed CSV outputs also match exactly.

The maximum QP KKT residual is 1.25×10⁻¹¹. The post-run geometry audit finds a maximum equality-identity discrepancy of 9.10×10⁻¹³. At primary costs, 2,273 of 182,448 transfer calibration candidate-episodes have infeasible equality solutions. Only one of eighteen transfer calibration cells has all candidates feasible. The manuscript does not claim universal interiority.

All 184 evaluation dates are consecutive. Additional monetary contrasts use the unchanged daily records and the specified bootstrap. Neither code, protocol, candidate set nor raw outcomes were altered to improve the result.

## Statistical interpretation audit: 11 concerns considered

| Concern | Assessment |
|---|---|
| Simpson reversal | All three transfer asset means are positive; BTC/ETH is negative and uncertain. Cohorts are reported separately. |
| Ecological inference | Claims concern average hypothetical orders, not every trade or trader. |
| Selection/Berkson bias | Selected surviving assets and one exchange limit representativeness. |
| Collider bias | No post-outcome control adjustment; market causality is not identified. |
| Base-rate neglect | All eighteen cells and eleven baseline selections are reported. |
| Regression to the mean | Calibration selection can overfit; evaluation uses the following month and retains failures. |
| Survivorship | Currently listed assets limit coverage; unavailable archives were not replaced. |
| Look-elsewhere | One primary contrast was frozen. Other intervals are secondary and unadjusted, not independent confirmations. |
| Forking paths | Retrospective motivation is disclosed; the experiment was frozen before this run, with no subsequent model search. |
| Causality | Paired outcomes come from a deterministic replay model, not actual interventions in the market. |
| Reverse causality/leakage | Features, fitting and selection precede their evaluation outcomes; historical assets still share market shocks. |

Block intervals condition on fitted forecasts and choices. They omit full training and selection uncertainty and do not guarantee validity under arbitrary dependence. Cost parameters are assumed, not measured. Historical asset transfer is not prospective confirmation.

## Stopping decision

The frozen experiment is complete. Preserve its results instead of tuning new models or dropping dates for a stronger headline. A distinct next study would need a separately recorded design, measured quotes/depth, explicit order sizes and a fresh future sample. The accompanying paper is a revised research draft; nothing has been submitted.
