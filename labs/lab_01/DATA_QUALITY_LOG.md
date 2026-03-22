# Issue 1: Status — Survivorship Bias (DNF)

What:
Drivers with status “Retired,” “Accident,” or “Collision” have missing lap-time values and never finish in the Top 10.

Classification:
MAR (Missing At Random).

Impact:
If these records are removed, the model would become overly optimistic about the probability of finishing a race.

Decision:
Flag / Keep. All “Retired” drivers were labeled as IsTop10 = 0.

Justification:
Ignoring retirements would hide the reliability risk associated with certain teams and drivers.

# Issue 2: GridPosition — Domain Validity

What:
Existence of starting positions outside the 1–20 range (e.g., Pit Lane starts labeled as 0 or unusually high values).

Classification:
Outlier / Domain Validity.

Impact:
This can distort the Spearman correlation calculation and the average of the probability “ladder.”

Decision:
Standardize. All Pit Lane starts were mapped to position 20 to preserve the ordinal structure.

Justification:
Starting from the Pit Lane is functionally equivalent to starting last, but with an additional time penalty.

# Issue 3: Points / Position — Data Leakage

What:
The columns points scored and final position are present in the original dataset.

Classification:
Temporal Availability / Data Leakage.

Impact:
If these variables are used as predictors, the model would achieve artificially perfect accuracy, since they represent the outcome rather than the cause.

Decision:
Drop from features.

Justification:
Only variables known before the race start (pre-race) should be used as predictors.

# Issue 4: TeamName — Semantic Consistency (Rebranding)

What:
Teams that changed names between 2022 and 2024 (e.g., AlphaTauri → RB / Racing Bulls).

Classification:
Type / Semantic Consistency.

Impact:
The model could treat “AlphaTauri” and “RB” as different entities, fragmenting the team’s performance history.

Decision:
Keep & Document. For Lab 1, the original API names are preserved.

Justification:
This ensures full traceability with the data source; a name consolidation mapping is recommended for Lab 2.

# Issue 5: Time / Gap — Missing Values in Non-Finishers

What:
Drivers who do not finish the race lack a record of total race time or gap with the leader.

Classification:
MCAR (Missing At Random).

Impact:
This prevents using lap time as a continuous performance metric across the entire dataset.

Decision:
Drop for specific metric. Not needed for Top-10 binary classification.

Justification:
The value is missing because the event (finishing the race) did not occur. For Top-10 classification, it is sufficient to know that the driver did not finish.

# Issue 6: False Positives in Baseline — Mechanical Reliability vs Grid Position

What:
The heuristic rule "If GridPosition ≤ 10, predict Top 10" produces False Positives: drivers starting in top 10 who do not finish due to mechanical failures, accidents, or pit strategy errors. For example, a Ferrari starting P2 can retire due to brake failure and finish outside the Top 10.

Classification:
Feature Limitation / Incomplete Information.

Impact:
The baseline achieves ~85.7% accuracy, but approximately 14.3% of predictions are wrong, primarily driven by reliability factors not captured in the qualifying result. This sets the ceiling for the heuristic approach and motivates the need for additional features (e.g., team reliability history) in Lab 2 models.

Decision:
Keep and document. The baseline intentionally uses only pre-race information; reliability data will be engineered in Lab 2.

Justification:
GridPosition alone is insufficient because Formula 1 outcomes depend on car reliability and race strategy, not just qualifying pace. Documenting this gap justifies why ML models should exceed the baseline by learning reliability patterns from historical data.

# Issue 7: Discrete Decision Boundary vs Continuous Correlation

What:
The EDA shows a strong negative Spearman correlation (ρ = −0.82) between GridPosition and IsTop10, but the actual baseline rule uses a discrete cutoff: position 11 is the breakpoint. Positions 1–10 have >90% Top-10 probability, while position 11 drops to <50%. This discontinuity suggests the correlation is driven by a categorical effect, not a linear one.

Classification:
Feature Engineering / Modeling Assumption.

Impact:
A continuous predictor (e.g., logistic regression with GridPosition as a linear term) might underperform the discrete rule because the relationship is fundamentally non-linear. This could lead to models that are more "accurate" by AIC/BIC but less interpretable or robust.

Decision:
Document for Lab 2 feature engineering. Consider binning GridPosition (e.g., "top 10 group" vs "rest of grid") rather than treating it as continuous.

Justification:
The discrete cutoff reflects F1 domain knowledge: points are awarded only to positions 1–10, creating an artificial but real threshold. Machine learning models in Lab 2 should respect this structure rather than assume smooth gradients.

# Issue 8: Class Balance Paradox — Accuracy Is Not Actionable Without Baseline Context

What:
The dataset is perfectly balanced (50/50 IsTop10), which means a naive constant predictor ("always predict Top 10") achieves exactly 50% accuracy. The baseline rule achieves ~85.7%, which looks impressive in isolation but requires the naive baseline as a reference point to prove it's a genuine signal.

Classification:
Metric Interpretation / Experimental Design.

Impact:
If the baseline is reported as "85.7% accuracy" without context, it could be misinterpreted as excellent performance. However, the actual improvement over random guessing is only +35.7 percentage points. Lab 2 models must exceed 85.7% to be worth deploying; otherwise the simple rule is preferable.

Decision:
Keep and document. Always report accuracy alongside the naive baseline (50%) and the confusion matrix (TP/FP/TN/FN) for transparency.

Justification:
Academic integrity and model transparency require contextualizing accuracy metrics. In a balanced dataset, accuracy alone masks whether the model is learning real patterns or just slightly overfitting the majority class. The confusion matrix breakdown reveals that the baseline has a higher False Positive rate than False Negative rate, which is domain-relevant for F1 (missing an overtake opportunity is less costly than incorrectly predicting a driver who will crash).