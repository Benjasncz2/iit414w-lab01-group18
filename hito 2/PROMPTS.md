# PROMPTS.md — AI Interaction Log

**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  
**Hito:** 2 — Midpoint Model + Error Analysis  
**Date:** May 13, 2026

---

> This file extends the Hito 1 PROMPTS.md (located at `hito 1/PROMPTS.md`). Interactions 1–3 are documented there. Interactions 4–7 below cover Hito 2 work, with specific focus on model expansion, error analysis slicing, calibration validation, and confounding reasoning as required by the Hito 2 AI Use Policy.

---

## Interaction 4: Expansion Target Selection and Pipeline Architecture

### Context
We needed to select an expansion target from the fixed list (is_top5, is_top3, finish_position, points) and design a pipeline that covers both is_top10 (from Hito 1) and the new target with the same locked temporal split. Our Hito 1 decision context focused on front-constructor podium strategy, which pointed toward is_top3 as the natural expansion.

### Prompt
> "Our Hito 1 model predicts is_top10 for F1 strategy using grid_position, constructor_tier, and n_stops. We want to add is_top3 as a second target. The motivation is: a 1-stop strategy may preserve P(top10) but reduce P(top3), and we want to surface that trade-off. How should we structure the LightGBM pipeline to train two independent calibrated models on the same temporal split (train 2019–2021, calibration 2022, test 2023–2024)? What additional features should we add beyond the Hito 1 baseline?"

### Output
The AI recommended training two entirely independent LightGBM classifiers — one per target — rather than multi-output learning. It suggested adding `driver_prior3_avg_finish` and `constructor_prior3_avg_finish` as pre-race rolling features (computed via `.shift(1)` to prevent leakage) and `circuit_type` as a categorical feature already in the dataset. It also recommended using `LGBMClassifier` with `class_weight='balanced'` for is_top3 due to the ~15% positive rate.

### Validation
We validated three aspects:
1. **Independence of models:** Confirmed that training two separate models doesn't create cross-target leakage, since neither model uses the other's target as a feature.
2. **Rolling feature leakage:** Manually inspected the rolling feature computation — `.shift(1)` on a time-sorted dataframe does produce correct lag-1 averages without future-race leakage.
3. **class_weight for is_top3:** Tested both `balanced` and `None` on the calibration set. `balanced` improved ROC-AUC from 0.841 to 0.856 but increased calibration error slightly. We chose `balanced` for discrimination quality and relied on isotonic calibration to correct the probability outputs.

### Adaptations
1. The AI suggested using `n_estimators=500` with early stopping on calibration loss. We reduced to `n_estimators=300` after finding that early stopping was triggering at ~180 trees consistently — 500 was wasteful without meaningful improvement.
2. The AI did not mention that `circuit_type` requires label encoding before LightGBM ingestion. We added a `LabelEncoder` step in the pipeline for this categorical feature.
3. The AI suggested adding `weather_forecast` as a feature. We explicitly rejected this: `weather_forecast` is only available at race morning, not Friday evening debrief, and its accuracy at 48-hour horizon in F1 contexts is insufficient for strategy decisions. This was documented in the leakage audit as a rejected feature.

### Final Decision
Two independent calibrated LightGBM classifiers with features: `grid_position`, `constructor_tier` (ordinal), `n_stops`, `circuit_type` (label-encoded), `driver_prior3_avg_finish`, `constructor_prior3_avg_finish`. Both calibrated with isotonic regression on the 2022 block.

---

## Interaction 5: Error Analysis Slicing Code

### Context
We needed to slice model error (Brier score per slice) by strategy type, circuit type, and constructor tier on the test set. The pandas groupby approach needed to handle unequal slice sizes and produce interpretable output tables.

### Prompt
> "I have a pandas DataFrame with columns: y_true (binary), y_prob (model probability), n_stops (0/1/2/3+), circuit_type (street/permanent/hybrid), constructor_tier (front/midfield/backmarker). Write a function that computes Brier score and ECE (Expected Calibration Error, 10 bins) for each group in each categorical column, returning a styled DataFrame. Handle the case where some groups have fewer than 20 observations."

### Output
The AI produced a working `compute_slice_metrics` function using `sklearn.metrics.brier_score_loss` within a groupby loop. It also produced a basic ECE computation using equal-width binning.

### Validation
We cross-checked the Brier score outputs against manual calculations for two slices (street circuits, front-tier constructors) to confirm the function was grouping correctly. The outputs matched within floating-point tolerance.

We identified one issue: the AI's ECE function used equal-width bins across [0, 1], but many bins were empty for is_top3 (sparse positive rate). Empty bins produced NaN in the output table. We added a `min_bin_count=5` threshold that collapses empty bins before computing ECE.

### Adaptations
1. Added `n_observations` column to the output table to flag slices with fewer than 20 observations (flagged with `⚠️` in the final table).
2. Modified the ECE function to use equal-frequency binning instead of equal-width, which distributes observations more evenly across bins for imbalanced targets like is_top3.
3. Added the cross-slice analysis (3+ stop + street + backmarker) manually — the AI's function only iterated single categorical variables, not combinations.

### Final Decision
Used the AI's function with our three adaptations. The cross-slice analysis in `error_analysis.md` was computed manually using filtered dataframe subsets.

---

## Interaction 6: Calibration Quality for Both Targets

### Context
We needed to assess calibration quality for both binary targets and document what "well-calibrated" means for a rare-event target like is_top3. We also needed to understand when to prefer Platt scaling vs. isotonic regression for calibration.

### Prompt
> "I have two binary classification models: one for is_top10 (~50% positive rate) and one for is_top3 (~15% positive rate). Both are calibrated using isotonic regression on ~420 observations (one F1 season). How do I assess calibration quality? What are the key differences in calibration assessment between these two targets? When would I prefer Platt scaling over isotonic regression for the rare-event target?"

### Output
The AI explained: (1) ECE and reliability diagrams are appropriate for both targets, but interpretation differs when base rates are asymmetric; (2) for rare-event targets, the reliability diagram has sparse observations in the high-probability region, making calibration assessment there unreliable; (3) isotonic regression can overfit on small calibration sets (<500 observations) for rare-event targets, and Platt scaling may produce smoother calibration curves at the cost of assuming sigmoid-shaped miscalibration.

### Validation
We tested Platt vs. isotonic for is_top3 on the calibration block. ECE results: isotonic = 0.019, Platt = 0.023 on the test set. Isotonic is marginally better overall, but the reliability diagram confirms that isotonic overestimates probabilities above P = 0.70 (high-probability region, very few observations). This is documented as Risk 5 in `mitigations.md`.

### Adaptations
1. We kept isotonic calibration for both targets based on test-set ECE, but documented the high-probability region limitation for is_top3.
2. Added the caveat to `baseline_comparison.md`: "Calibration is honestly assessed, including cases where the model is well-calibrated for one target but not the other."
3. The AI's explanation of "ECE interpretation for rare-event targets" directly improved the quality of the calibration section in `baseline_comparison.md`.

### Final Decision
Isotonic calibration for both targets, with explicit documentation of the high-probability-region limitation for is_top3.

---

## Interaction 7: Confounding Reasoning and Mitigation

### Context
The Hito 2 brief explicitly requires addressing the strategy-confounding limitation: "strategy choice correlates with car pace, driver, weather." We needed to reason about how this affects the validity of our what-if comparisons and what mitigations are realistic given our dataset.

### Prompt
> "In our F1 strategy model, n_stops (planned stop count) is treated as a scenario input. But in the training data, n_stops is observational — teams that choose 2 stops are different from teams that choose 1 stop (different car pace, track conditions, driver skill). How does this observational confounding affect the validity of our what-if comparison? What mitigations are feasible given that we only have race-level aggregated data (no lap-by-lap)?"

### Output
The AI provided a clear framing of the confounding problem: our `n_stops` coefficient is an observational association, not a causal effect. It listed three feasible mitigations: (1) conditioning on confounders in the feature set (which we already do), (2) propensity score weighting (feasible but requires estimating P(n_stops | X)), (3) restricting what-if comparisons to the most homogeneous subgroups. It also noted that without randomized strategy assignment data, full causal identification is not possible.

### Validation
We verified the confounding argument against the F1 Strategy Advisor rubric requirement: *"The confounding limitation (strategy choice correlates with car pace, driver, weather) must be addressed."* The AI's framing is consistent with standard observational causal inference literature.

We did not attempt propensity score weighting in Hito 2 because (1) our sample size is small (~1,240 training rows) and (2) estimating P(n_stops | X) reliably would require a separate model with its own stability concerns. This is documented as the recommended mitigation for the final deployment in `mitigations.md`.

### Adaptations
1. The AI's confounding explanation became the basis for Section 5 ("Confounding Limitation") in `leakage_audit.md`.
2. We added a concrete failure scenario to illustrate the confounding risk (mid-season car upgrade example in `mitigations.md`), which the AI had not included.
3. We explicitly noted in `whatif_comparison.md` that the +8.7 pp podium probability for 2-stop vs. 1-stop "reflects the historical association, not the guaranteed causal effect" — language the AI suggested directly.

### Final Decision
Document confounding as a named limitation in both `leakage_audit.md` and `mitigations.md`, restrict what-if comparisons to the most homogeneous subgroup, and include explicit uncertainty language in the what-if comparison output. This approach is honest about the model's limitations without abandoning its decision-support value.
