# Review-driven revision protocol

Date: 19 September 2026. Recorded before computing this extension's outcomes. This is a RETROSPECTIVE EXPLORATORY extension after viewing the original BTC June/July/August results, not independent confirmation or preregistration.

## Economic question

Does directional prediction at the end of a fixed-volume execution horizon contain enough information to determine the value of changing the within-horizon schedule? What economic information is removed by a directional endpoint summary, and how stable is the value of a single forecast's temporal shape across asset/month windows?

Analytical expectation: common shifts of all forecast prices do not change fixed-volume optimal schedules. Forecasts with identical terminal prediction can have different within-horizon shapes and therefore different schedules, costs and price exposure. This is an elementary implication of fixed-volume execution, not a claimed first theorem. Demonstrate its economic relevance through matched-endpoint comparisons and exact cost decomposition.

## Fixed data and chronology

BTCUSDT and ETHUSDT Binance spot monthly one-minute klines, January–August 2026 (eight complete months). Reuse unchanged existing BTC inputs. Source and checksum validation required. Any unavailable archive is reported, never silently substituted. For each asset, use six rolling windows: train Jan/calibrate Feb/evaluate Mar; then shift one month at a time through train Jun/calibrate Jul/evaluate Aug. Windows share training/calibration observations and market regimes; 12 asset-month evaluations are not independent studies. BTC Aug overlaps the original evaluation and is explicitly retained as a reproduction check.

Episodes: same fixed 48/day starts minute5,35,...,1415; imbalance of the five completed predecision bars; normalized sell order; execution proxies opens i+1,...,i+15. Training: same intercept-plus-imbalance OLS for each horizon; center signal by training mean and discard fitted unconditional intercept. No new predictors, optimized horizons, market selection or parameter tuning.

## Matched-terminal forecast comparison

Let mu=(mu1,...,mu15) be the training-fitted signal-only price profile. All four profile variants below have exactly the SAME terminal prediction mu15 in every episode:
1. learned: mu;
2. parallel: mu15*1 (control; optimizer must equal no-signal schedule);
3. ramp: (j/15)*mu15;
4. mirror: 2*mu15*1-mu (shape reversed around the identical terminal level; diagnostic counterfactual, not a trained alternative model).
The point is identification by an endpoint metric, not to select a winner. All variants/comparisons are fixed here. No additional shape search. Evaluate full exposure for each variant, and half/plug-in/lower-percentile exposure for learned. Terminal forecast RMSE, out-of-sample R² versus zero signal and directional hit rate must be identical across these variants by construction. Report the price-profile errors separately if helpful; do not call the mirror equally well estimated or equally plausible.

## Objective and calibration

Primary eta=2,r=1 bps; robustness all six original eta in{0.5,2,5},r in{0,1}. Same constrained quadratic objective and exact decomposition R=price_alignment-baseline_cost_gradient, C=curvature. Write price_alignment=delta'p; baseline_cost_gradient=2etaN u0'delta-2r/N q0'Ldelta, nonnegative at the cost-minimizing baseline up to numerical tolerance. Net gain=price_alignment-gradient-C at full exposure. Curvature strictly positive for nonzero direction. Feasible convex mixtures preserve completion.

Plug-in and conservative weights follow original definitions and 2000 daily bootstrap resamples of calibration only. Use fixed seeds20260919 for new calibration and20260920 evaluation; also reproduce original BTC Aug using original seed as a separate check, not expect identical new bootstrap endpoints. Common weights held fixed within evaluation month. Report all asset/month weights, rather than hiding policy equality or lack of benefit.

## Results and uncertainty

Report paired mean objective/monetary gains versus baseline, price_alignment, baseline_gradient,C, shifted quantity (halfL1distance), active-constraint frequency, terminal forecast diagnostics. For primary learned/ramp/mirror gains and learned-minus-ramp/mirror differences, resample whole UTC calendar days2000times. Within pooled evidence, group both assets on the same calendar day (preserve co-movement) and retain asset/month policy identities. Treat daily bootstrap intervals as conditional descriptive summaries; do not claim arbitrary cross-day dependence protection or propagate full retraining uncertainty.

Report all12primary evaluation rows, all six cost-scenario pooled summaries, all profile variants and comparison directions regardless of outcome. No significance-driven sample additions. Include an equal-month diagnostic or describe episode-weighting explicitly (primary pooled estimate episode-weighted). Distinguish algebraic insufficiency of endpoint metrics from statistical superiority of the learned profile: the former does not imply the latter.

## Boundaries

The Bitcoin/Ether comparison broadens the illustration but does not establish a crypto-specific structural law. Kline opens are proxies; parent size, spreads, depth, fills and impact are unobserved. Impact/risk weights are assumed, so no actual profit or executable saving claim. The economic deliverable is a diagnostic for deciding what forecasting evidence is relevant to execution, plus an honest stability assessment, not a new generic predictor or trading system.
