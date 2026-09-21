# Pre-outcome pilot code review

21 September 2026. Reviewed pilot_study.py against PILOT_PROTOCOL.md, plus forecast tests and the causal-minute adapter. No actual-data strategy outcomes were run or inspected for this review. Engine fixes were supplied by the root agent; this review does not change engine or pilot source.

## Checks and findings

- Executed all 13 existing forecast/engine tests: passed.
- Independently checked synthetic increasing price, spread and depth paths. Targets correctly contain fifteen arithmetic price changes, then fifteen log half-spread ratios, then fifteen log depth ratios. Nine-feature and 45-target shapes are consistent.
- Features use the arrival row and prior rows only. np.roll wraparound is removed by the first-five-row exclusion; valid_indices additionally rejects all windows crossing missing minute boundaries.
- Training labels end before 14 April 2021; evaluation labels end before 19 April. Features may use the preceding interval's history, which is observable and permitted. Evaluation decision filtering is exactly :05/:35 UTC on minute boundaries.
- Training standardization, ridge coefficients, intercept, target clipping percentiles and seasonal coefficients depend only on training rows. No evaluation model selection or attenuation is implemented.
- Seasonal reference predicts changes between the known arrival and future clock times using training-fitted log spread/depth profiles. Use of future clock times is not market-data lookahead. The reference receives the current book and does not receive future realized liquidity.
- Four-arm slicing is consistent: price affects midpoint shift only; liquidity affects spread/depth scaling; disabled learned liquidity is replaced by the same seasonal reference in both relevant arms. Zero incremental predictions are already engine-tested. Both forecast channels use the same training samples and architecture.
- Same quantities, cap, initial book and future replay snapshots are used across arms. Forecast infeasibility falls back to TWAP and records fallback, rather than dropping unfavorable episodes. Input-window validity is common across arms. Completion-based common-support filtering is not implemented here; the separate report must apply and disclose it as required by the protocol.
- Fee sensitivity is correct for a fixed percentage of realized proceeds: add 10*proceeds/arrival_notional bps. It is explicitly hypothetical, not a historical exchange fee claim.
- Protocol hash is verified before processing. Code hashes are written before the run, and existing nonempty output directories are rejected. Input hashes are calculated per asset; a failed run may leave only the initial manifest, so preserve the failure log as well.

## Data prerequisites and minor improvements

1. Source timestamp timezone must be explicit. datetime.fromisoformat(...).timestamp() uses host timezone for naive values. Verify system_time has a timezone suffix, or explicitly assign UTC under a documented source convention. Retained source timestamps are not independently established exchange timestamps.
2. Verify distance columns represent fractional midpoint differences, and notional columns quote-currency value, before reconstructing prices and quantities. The adapter assumes price=midpoint*(1+distance), quantity=notional/price. These are source-schema checks, not statistical assumptions.
3. Adapter validity should include positive reconstructed prices and positive best-bid quantity, matching tightened Book validation. Otherwise a rare invalid row aborts the run instead of entering the common invalid-window exclusion. This is a transparent data-cleaning correction if performed before outcomes.
4. Full consecutive-window selection uses future data availability. This is acceptable for replay feasibility but conditions the sample on complete observations; disclose missing-data exclusions, especially if outages coincide with stressed liquidity. It does not license claims about unavailable periods.
5. The try/except around allocate catches any ValueError and labels it fallback. Expected insufficient depth should ideally be distinguished from a malformed forecast. forecast_books is outside that block and usually rejects malformed arrays first, but a specific exception/reason would improve auditability.
6. Raw episode rows discard child_fills. Summary max-child/cap fields from the corrected engine remain, but preserving per-child output separately would make exact fill audits easier. This is an audit improvement, not a detected outcome error.
7. Reference seasonality is fitted only at rows valid for full training labels, so the final fifteen training minutes and gap-adjacent windows are absent. This is training-only and not leakage; record the actual sample counts rather than claiming every training minute was used.

## Reporting requirements before scientific interpretation

For each size and replay convention, construct paired complete-order contrasts on identical arrival/asset keys, retaining explicit counts for every arm's failures and for the common support. Enforce the protocol's greater-than-1% incompletion interpretation limit. Do not average available arm means and call their difference a paired contrast. Report asset-date outcomes and all five dates; five dates do not support strong significance claims. Show all three sizes even when the hypothesized pattern fails. Keep the original outcome report and avoid retuning this pilot to obtain the desired contribution.

## Assessment

No blocking lookahead, target-ordering, split, reference-input or policy-selection defect was found in pilot_study.py. Proceed only after source-schema/timezone and adapter validity prerequisites are verified. This is an engineering and design review of a development pilot, not evidence that the policies work or that the contribution is established.
