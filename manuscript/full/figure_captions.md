# Full-paper figure captions

## fig01_endpoint_example

Synthetic two-slot example, not observed cryptocurrency data. The realised price vector is (3,2), total volume is one, and K(u)=u1²+u2². Forecasts (3,2), (2,2), and (1,2) share terminal forecast 2 but imply schedules (0.75,0.25), (0.5,0.5), and (0.25,0.75). Gains relative to the flat-forecast baseline are 0.125, 0, and −0.375 in arbitrary objective units. Thus identical endpoint accuracy need not identify execution timing value.

## fig02_rolling_design

Rolling calendar design for each asset. Every evaluation month uses the preceding month for exposure calibration and the month before that for forecast fitting. January–August 2026 supply six evaluation windows per asset. This is a review-driven retrospective exploratory extension: calendar ordering prevents within-window look-ahead but does not make the study prospectively preregistered or the entire sample previously unseen.

## fig03_benefit_cost

Primary costs (eta=2, r=1), pooled across 17,664 episodes. Panel (a) reports episode-weighted A, −B and −C, whose sum is objective gain at full exposure. B is numerically zero at these interior solutions. Panel (b) shows frozen-result 95% calendar-day bootstrap intervals; both assets are resampled jointly on each of 184 dates. The parallel profile is analytically equivalent to the baseline (floating-point residuals below plotting resolution). The mirror is a deliberate diagnostic counterfactual, not an independently estimated competitor.

## fig04_monthly_gains

All twelve asset-month evaluation cells under the primary costs. Points are full-exposure learned and ramp mean objective gains; bars are their stored 95% within-window calendar-day bootstrap intervals. Intervals are conditional on the fitted forecasts and calibrated design, with no multiple-comparison adjustment. Overlapping rolling windows are not independent replications.

## fig05_calibrated_exposure

Primary-cost schedule-mixture weights determined using the preceding calibration month, displayed against the subsequent evaluation month. The plug-in rule selects positive weights in six of twelve cells. The conservative rule selects zero in all cells, exactly reproducing the baseline. These are implemented ex ante within each retrospective split, not weights chosen from evaluation outcomes.

## fig06_objective_monetary

Objective and monetary gains under the primary costs. Objective gain includes the specified inventory preference; monetary gain omits that preference but retains the assumed temporary-impact charge. Both use the same replay prices and schedules. Bars are stored 95% calendar-day bootstrap intervals. Monetary gain is a model-based replay estimand, not realised profit after observed exchange execution costs.

## fig07_cost_sensitivity

All six specified cost scenarios, with full learned exposure on the left and the prior-month plug-in schedule mixture on the right. Points and 95% calendar-day bootstrap intervals are drawn directly from the frozen analysis. Eta is an assumed impact coefficient and r an inventory preference; neither is estimated from exchange order-book execution. This scenario analysis does not constitute a calibrated real-world cost estimate.

## fig08_descriptive_influence

Additional ex post descriptive diagnostics from unchanged primary episode results; no forecasts, weights or schedules are refitted. Panel (a) averages learned gains across both assets for each UTC date. Panel (b) excludes one evaluation month from both assets and recomputes the remaining episode-weighted means; the dashed line is the all-month learned mean. No confidence intervals or robustness claims are implied. This display diagnoses sample concentration and must not be used to select months for the headline estimate.
