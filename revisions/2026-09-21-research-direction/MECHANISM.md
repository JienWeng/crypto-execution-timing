# Why order size can change the value of price and liquidity forecasts

Illustrative mechanism, 21 September 2026. These are elementary accounting and optimization observations, not a novelty claim or an empirical finding.

## Two execution times: a transparent comparison

Suppose a compulsory sale of Q > 0 units can be executed entirely now (time 0) or entirely later (time 1). Let m_t be the midprice, s_t the bid-side half-spread, and k_t >= 0 the coefficient of the total cost of walking the bid book. Approximate gross proceeds by

R_t(Q) = Q (m_t - s_t) - k_t Q^2.

Here k_t is defined as a **total-cost coefficient**. If the marginal execution price at cumulative quantity z is m_t - s_t - a_t z, then k_t = a_t / 2. This convention avoids the common factor-of-two confusion between marginal book slope and average execution cost.

At time 0, define conditional expected changes

A = E_0[m_1 - m_0] - E_0[s_1 - s_0],
B = E_0[k_1 - k_0].

Ignoring fees and inventory risk for this comparison, expected extra proceeds from waiting are

E_0[R_1(Q) - R_0(Q)] = Q A - Q^2 B.

Equivalently, the expected benefit per unit sold is A - Q B.

If A > 0 and B > 0, a better expected price net of spread competes with a steeper expected bid book. Waiting is preferred in this two-action comparison exactly when

0 < Q < Q_star = A / B.

For Q > Q_star, the additional depth cost exceeds the expected price improvement. At Q_star the two actions tie. This explains an economically intelligible hypothesis: the information that matters for a small sale may differ from the information that matters for a larger sale.

Other cases matter and must not be discarded:

- B = 0: the sign of A decides, independently of Q.
- A > 0 and B < 0: both changes favor waiting for every Q allowed by the model.
- A < 0 and B > 0: both changes favor selling now.
- A < 0 and B < 0: better future liquidity can compensate for a worse future price once Q > A/B > 0.
- A = 0 and B != 0: the sign of B decides for every positive Q.

This calculation compares **two fixed schedules**. It does not establish a threshold for the fully optimized multi-period policy, the superiority of a liquidity forecaster, or a monotonic relationship between Q and feasible forecast value. Forecast errors, capacity constraints, spread dynamics and split execution can all alter the empirical pattern.

## Allowing the sale to be split

For intuition, suppose q units are sold now and Q-q later, with linear depth costs, no persistent impact, no endogenous replenishment response, and conditional expected future coefficients. Let a_0 = m_0 - s_0 and a_1 = E_0[m_1 - s_1], with k_0 >= 0; in this subsection, k_1 denotes the conditional mean of the future coefficient, assumed nonnegative. Expected proceeds are

R(q) = q a_0 - k_0 q^2 + (Q-q) a_1 - k_1 (Q-q)^2.

If k_0+k_1 > 0, the maximizing allocation is

q_star = clip((a_0-a_1 + 2 k_1 Q) / (2(k_0+k_1)), 0, Q).

When the solution is interior, the fraction sold now is

q_star/Q = k_1/(k_0+k_1) + (a_0-a_1)/(2 Q (k_0+k_1)).

Under these particular assumptions, the price/spread difference affects the optimal fraction through a term proportional to 1/Q, while relative liquidity costs determine the first term. This is a useful illustration of size dependence, not evidence that liquidity forecasts must dominate at large Q. The coefficients themselves may depend on quantity, current information, and forecast quality. The policy observes current state and forecasts future state; it never uses realized future coefficients to make a feasible decision.

For a nonlinear observed book, use its actual cumulative proceeds curve rather than fitting this illustration and treating its threshold as an empirical discovery.

## What the four-arm comparison measures

Use the same current state and reference future forecasts in all policies. Change only the incremental future-price input, future-liquidity input, or both. For baseline cost C_0 and policy costs C_P, C_L and C_PL, define S_P=C_0-C_P, S_L=C_0-C_L and S_PL=C_0-C_PL.

The information interaction is

I = S_PL - S_P - S_L = C_P + C_L - C_PL - C_0.

A positive I means combined information yields more savings than the sum of the two individual improvements relative to this particular baseline. A negative I means less than that sum; it does **not** by itself mean combining information is worse than either single-input policy. Report C_PL-C_P and C_PL-C_L separately.

Even additive price and liquidity inputs can create a nonzero interaction after nonlinear optimization and quantity constraints. Thus an interaction in realized policy costs does not prove a structural causal interaction between the market's price and liquidity processes. Its size and sign also depend on forecast errors and the reference policy.

## Exact monetary decomposition in observed-book replay

Consider a fully completed sale, sum_j q_j = Q, with reference arrival midprice m_ref. For child order j executed against the replay book at time t_j, let m_j be that contemporaneous midprice, b_j the best bid, and R_j the gross proceeds from walking the available bid levels. Define

spread payment_j = q_j (m_j - b_j),
depth payment_j = q_j b_j - R_j.

For q_j = 0 both payments are zero. For a valid uncrossed book, a market sale supported by observed depth, and no unusual rebates included in gross proceeds, both payments are nonnegative. Let F be total execution fees in the reporting currency. Monetary implementation shortfall is exactly

C = Q m_ref - sum_j R_j + F
  = sum_j q_j (m_ref - m_j)
    + sum_j q_j (m_j - b_j)
    + sum_j (q_j b_j - R_j)
    + F.

The four components are price-timing shortfall, spread payment, depth payment and fees. Divide by Q m_ref and multiply by 10,000 to report basis points. This is an accounting identity for the replayed fills, not a fitted impact model or causal decomposition.

For any two completed policies A and B facing the same arrival order, their cost difference equals the difference in each component. A policy can therefore reduce depth payments while worsening price timing; reporting only total cost would conceal the economic mechanism. Evaluate each policy's components at its own realized execution times and quantities. The observed market path must be common, with any within-policy depletion adjustment stated explicitly.

Historical replay cannot observe the market's response to our hypothetical trades. Consumed depth, recovery assumptions, latency, stale quotes, unavailable depth and uncompleted quantities require explicit handling. Do not label a residual inventory mark as an executed fill; a forced completion or penalty must be reported separately if full observed-book execution is unavailable.

## Fees, risk and identification boundaries

Identical fixed fees per unit cancel between completed policies. Identical percentage fee rates generally do **not** cancel exactly because gross executed notional differs: for a constant sell-side fee rate f applied to proceeds, net proceeds are (1-f)R and the no-other-cost two-period comparison is simply scaled by 1-f. Tier changes, per-order minimums, maker/taker differences and rebates require their actual accounting.

A monetary inventory-risk penalty would change the all-now/all-later comparison to Q A - Q^2 B - risk_penalty(Q). A quadratic penalty r Q^2 would replace B by B+r in that illustration. This is a preference-adjusted objective, distinct from realized monetary shortfall, and the paper should report them separately. Forecast uncertainty also means the threshold computed from point estimates can be highly unstable, especially when B is near zero.

The hypotheses worth evaluating are whether feasible forecast gains change with prespecified depth-relative size, whether combined forecasts beat a credible current-book baseline, and whether price-timing versus liquidity-payment changes explain the observed differences. None of these outcomes follows automatically from the illustrative formulas.

## Relation to established work

Joint signal and stochastic-impact execution is already established in [Fouque, Jaimungal and Saporito (2022)](https://doi.org/10.1137/21M1394473). Empirical execution using forecasts of book-based transaction costs is already studied by [Ahabchane and colleagues (2024)](https://doi.org/10.1002/for.3164). These formulas explain the proposed comparison; the candidate contribution remains evidence from a controlled held-out experiment, not the formulas themselves. See PRIOR_ART_AUDIT.md for access levels and overlap assessment.
