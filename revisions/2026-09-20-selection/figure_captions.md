# Figure captions

## transfer_selectors

Primary-cost (eta=2, r=1) transfer results over 26,496 episodes and 184 calendar dates. Bars are the frozen conditional 95% seven-calendar-day circular moving-block bootstrap intervals, with transfer assets resampled jointly by date. The economic and contrast selectors choose identical candidates and have identical results; they are not independent successes. All four selectors have negative mean gains relative to the zero baseline.

## transfer_cost_sensitivity

Transfer-sample paired economic-minus-endpoint differences for all six specified cost scenarios. Bars are the frozen conditional 95% seven-calendar-day circular moving-block bootstrap intervals, not independently constructed policy intervals. Positive differences indicate lower loss relative to endpoint selection, not positive gains relative to the zero baseline. Costs are assumed rather than empirically estimated.

## transfer_monthly_differences

All eighteen transfer asset-month paired mean differences under the primary costs; month labels 03–08 denote March–August 2026. No cell is excluded, and no cell-level confidence intervals are implied. SOL in March accounts for most of the aggregate improvement. This heterogeneity cautions against interpreting the pooled contrast as a uniformly beneficial selection rule.

## Exact diagnostic notes

Primary transfer economic-minus-endpoint: {'cohort': 'transfer', 'eta': 2.0, 'risk': 1, 'policy': 'economic_minus_endpoint', 'mean_gain': 0.015636706484945, 'ci95': [0.00277906230040504, 0.031838352040108896], 'dates': 184, 'episodes': 26496, 'block_sensitivity': {'1': [0.0057226382762947175, 0.026502152023638776], '14': [0.0008072927524612922, 0.03735380878424215]}, 'leave_month_out': {'3': 0.003971927681424143, '4': 0.01868281813785637, '5': 0.016120184558453723, '6': 0.018682818137856366, '7': 0.020450517465442557, '8': 0.01587215447565762}}. Economic nonzero selections: 7/18; all have negative gain relative to baseline. SOL March contributes 66.0394% of the aggregate episode-weighted paired difference. Economic and contrast candidate IDs coincide in all 30 primary windows. Fixed-candidate columns: ['development', 'transfer']. All results frozen; no refitting.
