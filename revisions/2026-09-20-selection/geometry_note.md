# Mathematical audit: execution utility and forecast-error geometry

This is a derivation audit, not a novelty claim. The identities follow from standard equality-constrained quadratic optimization and decision regret. They explain which forecast-error components matter under the paper's assumed execution objective; they do not validate those assumed costs empirically.

## Setup and precise conditions

Let U = {u >= 0 : 1'u = 1}. Write K(u) = 0.5 u'Hu + g'u + c with H symmetric positive definite. For this study H = 2 eta N I + (2r/N)L'L and g = -(2r/N)L'1, so eta > 0 and r >= 0 suffice. Define u(mu) = argmin over U of K(u)-mu'u and u0 = u(0). Prices p and forecasts mu use the same units. Realized gain relative to u0 is G(mu,p) = p'[u(mu)-u0] - K(u(mu)) + K(u0).

Define z = H^{-1}1 and Q = H^{-1} - zz'/(1'z). Q is symmetric positive semidefinite, Q1 = 0, and QHQ = Q. It has rank N-1. Common price-level shifts are consequently immaterial to order timing.

The linear representation below requires that the equality-constrained optima for the baseline and each candidate forecast lie in U. Strictly positive components suffice, but are stronger than necessary: a zero component with zero inequality multiplier can also satisfy the formula. Merely observing feasibility of a numerical constrained optimizer is not sufficient; every constrained optimizer is feasible by construction. Check the equality solution or its difference from the constrained solution.

## Equality-constrained solution and proof

With only 1'u = 1, stationarity gives Hu + g - mu + lambda 1 = 0. Solving for lambda and subtracting the mu=0 solution yields

u(mu) = u0 + Q mu.

If both equality optima are nonnegative, strict convexity makes them the simplex optima as well. Since Hu0+g is proportional to 1 and 1'Qmu=0,

K(u0+Qmu)-K(u0) = 0.5 mu'QHQmu = 0.5 mu'Qmu.

Thus

G(mu,p) = mu'Qp - 0.5 mu'Qmu
        = 0.5 p'Qp - 0.5 (mu-p)'Q(mu-p).

For the same evaluation episodes, H, and baseline, maximizing average realized utility is exactly equivalent to minimizing average Q-weighted forecast error. The additive term 0.5 p'Qp is independent of the candidate. The hindsight optimizer u(p) need not be feasible for this algebraic identity to hold: only the baseline and candidate equality solutions must be feasible. However, calling the additive term feasible-oracle gain requires u0+Qp >= 0 as well.

## Zero inventory penalty: demeaned path MSE

For r=0, H=2 eta N I, u0=1/N, and Q=P/(2 eta N), where P=I-11'/N. Hence

G(mu,p) = [||Pp||^2 - ||P(mu-p)||^2]/(4 eta N).

Consequently execution-utility selection and demeaned-path MSE selection must give identical candidate rankings, provided their samples, weighting and feasible equality solutions agree. Numerical near ties require scale-adjusted tolerances for identical tie handling. The experiment uses a fixed absolute tolerance across metrics; observed agreement is checked empirically. Dividing the squared error by N changes no ranking when N is fixed. Raw path MSE also scores common-level errors that cannot change the sale schedule. Final-slot prediction error scores only one coordinate and likewise fails to represent this objective.

This is an especially useful negative control. Any reported advantage of utility selection over demeaned-path MSE in the r=0 interior setting indicates different eligibility rules, aggregation, numerical error, or implementation inconsistency; it is not evidence of a distinct economic criterion.

For r>0, Q gives a weighted contrast-error criterion determined by the cost Hessian. Ordinary demeaning removes the irrelevant common level but generally does not apply the correct weights. A comparison with ordinary demeaned MSE therefore tests the effect of cost-dependent weighting under the assumed objective, rather than a new theory of forecast evaluation.

## Inequality constraints and exact regret

When a baseline or forecast equality solution has negative components, the global affine formula need not apply. The simplex optimizer is piecewise affine; an unchanged support has its own reduced-dimensional quadratic geometry. A candidate changing support can change that geometry. Report the fraction of active-constraint episodes for each candidate and objective specification.

An exact loss valid with constraints is decision regret:

L(mu,p) = [K(u(mu))-p'u(mu)] - [K(u(p))-p'u(p)] >= 0.

It satisfies G(mu,p) = G(p,p) - L(mu,p) for every episode. Therefore selecting the highest average realized utility is always identical to selecting the smallest average exact regret on the same validation sample. This is a bookkeeping identity, not a predictive or out-of-sample guarantee. Computing the hindsight decision on validation or evaluation outcomes is legitimate for scoring, but it must never enter the decision made before those outcomes.

Let d=u(mu)-u(p) and a=Hu(p)+g-p. Quadratic expansion gives

L(mu,p) = 0.5 d'Hd + a'd.

The variational optimality condition implies a'd >= 0. With KKT multipliers nu >= 0 for u >= 0, a=-lambda 1+nu and a'd=nu'u(mu), since nu'u(p)=0. Thus the second term records movement into coordinates excluded by the hindsight optimum. It vanishes for an interior hindsight optimum, and also for decisions confined to its zero-multiplier coordinates. With binding constraints it cannot generally be dropped or replaced by the global Q error metric.

## Conditions that must match in the empirical comparison

1. Use identical candidate forecasts, calibration episodes, calendar weights, cost parameters and tie-breaking for each selection rule.
2. If H varies by episode, use its episode-specific Q and preserve those weights in scoring; a pooled unweighted MSE equivalence no longer follows.
3. A fixed candidate scale or shrinkage changes mu and is part of the candidate definition. Selecting scale using evaluation outcomes invalidates the held-out comparison.
4. Keep forecast selection on calibration data and then freeze its choice for evaluation. The identity is deterministic; estimating which candidate will perform best still involves sampling uncertainty.
5. Distinguish utility under the assumed inventory penalty from realized monetary proceeds. The same Q identity does not automatically describe proceeds-only evaluation when selection includes r>0.
6. Under constrained operation, compute utility directly or use exact regret. Use the Q identity only on rows satisfying its conditions and report that coverage.

## Contribution language supported by the derivation

A defensible claim is: 'We test whether selecting cryptocurrency forecasts with an execution-cost-weighted error criterion improves held-out execution outcomes relative to final-price and unweighted path errors, and quantify when those selection rules coincide.'

A supported diagnostic is the decomposition of forecast error into an irrelevant common-level component and relevant, cost-weighted contrasts. The empirical contribution must establish useful selection differences on held-out observations and suitable baselines. This derivation alone does not establish novelty, profitability, realistic transaction costs, or publication readiness.
