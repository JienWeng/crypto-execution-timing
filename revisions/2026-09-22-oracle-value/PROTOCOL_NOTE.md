# Post-run protocol clarification

The locked protocol called all three hindsight-input schedules “upper-bound policies.” That description is correct only for the full oracle within the finite-depth planner. A price-only or liquidity-only schedule still substitutes a reference path for the missing input. Its realized total proceeds can be worse than the baseline because the missing input changes after the schedule is selected.

No schedule or result was changed. Reporting now uses “hindsight price input,” “hindsight liquidity input,” and “full oracle.” The clean incremental quantities are full-oracle savings minus price-input savings, and full-oracle savings minus liquidity-input savings. This correction was made immediately after the first run and before using the diagnostic in a manuscript.
