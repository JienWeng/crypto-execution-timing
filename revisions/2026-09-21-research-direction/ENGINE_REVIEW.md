# Independent execution-engine review

21 September 2026. Reviewed book_execution.py and test_book_execution.py without modifying them. This review concerns accounting and optimization, not empirical strategy effectiveness.

## Verification performed

Independent seed 9281: 300 randomized integer-book cases, each with three times and three strictly descending bid levels, zero/nonzero capacities, varying child caps and total quantities. Compared allocator proceeds with exhaustive enumeration of every feasible integer allocation. All checks passed; maximum objective discrepancy was 5.684341886080802e-14. Total allocated quantity and child caps also passed. This checks continuous optimum against an integer optimum in integer-capacity cases, where the marginal-segment formulation admits integral optimal allocations. SciPy is unavailable in this Python environment, so no independent LP solver check was performed.

Equal-price tie sharing is consistent with objective optimality: strictly descending levels within each time imply each exact-price tie group has at most one segment per time. All higher-price prefixes have already been allocated. Water filling shares the marginal group subject to capacity and does not violate prefix feasibility. Equal prices need not mean equal final totals if previous better-price levels differ; that is correct.

## Findings requiring attention

### 1. Displayed depth increases receive two availability credits

Reproduction:

- Observed size = 100; hypothetical sale = 30; available size = 70; debt = 30.
- Next observed size = 110.
- update() subtracts the observed increase 10 from debt, leaving debt 20, then sets availability to 110 − 20 = 90.

Thus an observed net increase of 10 increases simulated availability by 20. The raw size increase already supplies new displayed volume, and debt forgiveness supplies a second credit. As an expressly chosen recovery scenario this is possible, but it is not simply an observed-replenishment ledger and should not be described as conservative. Recommended conservative sensitivity: retain debt across size increases and set availability=max(displayed−debt,0). If debt recovery is desired, specify it separately and test its sensitivity; snapshots do not identify the true counterfactual recovery rate.

Price disappearance also removes debt entirely, so reappearance resets that price. With truncated snapshots, disappearance can mean moving outside the recorded depth rather than real cancellation. Retaining price debt across disappearance is conservative but may become excessively pessimistic; either convention needs explicit description and sensitivity limits.

### 2. Actual child size can exceed the stated planner cap

Replay carries all backlog into the next execution without an executable child cap. The docstring discloses this, but max_backlog alone does not report the actual cap violation or depth participation. Before comparing empirical policies, return actual attempted and filled child sizes, completion fraction and applicable participation ratios. Prefer enforcing the same execution cap if it is part of the economic design. Otherwise policies can differ through emergency execution aggressiveness as well as forecast information.

### 3. Cost decomposition uses opposite timing sign to the mechanism note

The engine's timing_dollars is sum q*(execution_mid−arrival_mid), a **timing gain**. MECHANISM.md defines timing shortfall with the opposite sign. Current engine accounting is internally correct:

shortfall_dollars = −timing_dollars + spread_dollars + depth_dollars + fee_dollars.

Name/document timing_gain_dollars explicitly, or align the sign with the paper. Existing test checks a zero-total example, so add a nonzero-fee, nonzero-net-shortfall example before consuming columns in manuscript tables.

### 4. Zero-size top quote can produce a misleading reference midpoint

Book permits the first bid size to be zero. Such a level is not executable top-of-book liquidity; using its price and the ask to calculate mid/spread can distort timing/spread attribution even though total revenue accounting remains correct. Adapters should remove zero-volume levels before constructing a Book, require a positive executable best bid, and preserve the true market midpoint separately if working with a depleted shadow book. Ledger zero availability itself is expected and should remain supported.

## Additional scientific limits

- Shortfall dollars for incomplete orders refer only to the filled quantity. The bps result correctly becomes None. Aggregation must not interpret partial-fill dollars as comparable full-order costs or selectively omit completion failures.
- Forecast liquidity changes spread and a common quantity scale while retaining deeper price offsets. This is a restricted liquidity forecast model, not full book-shape prediction. Any conclusion should refer to these particular forecast families; poor liquidity performance may reflect this restriction.
- The snapshot planner assumes independent future capacities whereas depletion replay links them. Its planned optimum need not be optimal under the replay sensitivity. This is disclosed, but comparisons should use matched constraints and report mismatch-driven failures.
- frozen=True does not make stored NumPy arrays immutable. No current mutation was found; callers should not modify book.bids or book.sizes in place.

## Verdict

The marginal-price allocator appears correct under its stated separable continuous-quantity objective, and basic monetary accounting is correct. Resolve the depletion-credit convention and standardize timing-column semantics before empirical use. Enforce/report execution caps and completion consistently to preserve a defensible four-arm comparison. This is a bounded review, not certification of a production simulator.
