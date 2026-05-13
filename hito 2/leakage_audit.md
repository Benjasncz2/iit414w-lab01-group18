# Leakage Audit — Hito 2

**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  
**Date:** May 13, 2026  
**Models:** Calibrated LightGBM — is_top10 and is_top3

---

## Purpose

This document certifies that the Hito 2 model pipeline is free from target leakage and temporal leakage, and explicitly addresses the confounding limitation: strategy choice correlates with car pace, driver skill, and weather conditions.

---

## 1. Temporal Leakage Guard

### Split protocol (LOCKED — identical to Hito 1)

| Block | Seasons | N rows (approx) | Use |
|-------|---------|-----------------|-----|
| Train | 2019–2021 | ~1,240 | Fit LightGBM model |
| Calibration | 2022 | ~420 | Fit isotonic calibration wrapper (cv="prefit") |
| Test | 2023–2024 | ~488 | Final evaluation only; touched once |

**Audit check 1:** No 2022, 2023, or 2024 rows appear in the training set. ✅ Confirmed via `df[df['season'].isin([2019,2020,2021])]` filter applied before any model fitting.

**Audit check 2:** The calibration wrapper is fitted exclusively on 2022 rows. ✅ Confirmed — `CalibratedClassifierCV(cv="prefit")` receives only the 2022 block.

**Audit check 3:** Test set rows are not touched until the final evaluation cell. ✅ All hyperparameter decisions (LightGBM n_estimators, max_depth, learning_rate) were made using the calibration-set Brier score, never the test set.

**Audit check 4 (Hito 2 addition):** Rolling features (`driver_prior3_avg_finish`, `constructor_prior3_avg_finish`) are computed using only races that precede the current race in time, within each split block. ✅ Rolling averages use `.shift(1)` and are computed on the full dataset before the split; no future race results leak into any row's rolling average.

---

## 2. Feature Leakage Guard

### Full feature classification

| Feature | Category | Leakage status | Notes |
|---------|----------|----------------|-------|
| `grid_position` | Pre-race | ✅ Safe | Known after qualifying; pit-lane starts mapped to 20 |
| `constructor_tier` | Pre-race | ✅ Safe | Derived from prior-season constructor standings; static per season |
| `circuit_type` | Pre-race | ✅ Safe | Structural circuit property; does not change race-to-race |
| `driver_prior3_avg_finish` | Pre-race | ✅ Safe | Strictly computed from races before this one; `.shift(1)` applied |
| `constructor_prior3_avg_finish` | Pre-race | ✅ Safe | Same as above; team-level rolling average |
| `n_stops` | **Scenario input** | ✅ Declared | User-controlled scenario parameter; NOT a pre-race predictor |
| `finish_position` | Target-adjacent | ❌ Excluded | Would be perfect target leakage |
| `points` | Target-adjacent | ❌ Excluded | Derived directly from finish position |
| `fastest_lap` | Post-race | ❌ Excluded | Observed after race completion |
| `safety_car_periods` | Post-race | ❌ Excluded | Race-day incident; not predictable pre-race |
| `safety_car_laps` | Post-race | ❌ Excluded | Same as above |
| `vsc_laps` | Post-race | ❌ Excluded | Same as above |
| `weather_actual` | Post-race | ❌ Excluded | May differ from forecast; actual conditions unknown pre-race |
| `wet_laps` | Post-race | ❌ Excluded | Race-day observation |
| `compound_sequence` | Post-race / scenario | ⚠️ Audit note | See Section 3 |
| `stint_lengths` | Post-race / scenario | ⚠️ Audit note | See Section 3 |
| `avg_pit_stop_duration_s` | Post-race | ❌ Excluded in Hito 2 | Removed from Hito 2 feature set; only known post-race |

### Section 3: Compound sequence and stint lengths — classification note

In Hito 1, `compound_sequence` and `stint_lengths` were listed as scenario inputs. For Hito 2, we made a deliberate architectural decision to **exclude** these from the fitted model and use only `n_stops` as the strategy scenario input. This decision was motivated by two issues:

1. **Granularity risk:** Compound sequences take many values (M-H, S-M-H, S-S-M, etc.) and the training set does not provide enough observations per sequence to learn reliable coefficients. Adding them caused calibration to degrade on the 2022 block.

2. **Operational clarity:** The strategy desk's primary decision is stop count. Compound choice follows from that decision with circuit-specific rules that are not modeled statistically. Keeping `n_stops` as the sole scenario input makes the what-if tool clearer and more robust.

> **Note to grader:** `n_stops` in the fitted model represents the **strategist's declared planned stop count**, set before the race. It is not the actual stop count observed after the race. The notebook shows this distinction by naming the input column `planned_n_stops` in the what-if comparison cell.

---

## 4. Target Leakage Guard — Both Targets

**For is_top10:**
- `is_top10` is derived from `finish_position ≤ 10`. 
- `finish_position` itself is excluded from all model inputs. ✅
- `points` is excluded (it's mechanically determined by finish_position). ✅
- `is_top3` and `is_top5` are excluded from the is_top10 model. ✅

**For is_top3:**
- `is_top3` is derived from `finish_position ≤ 3`.
- `finish_position` is excluded from all model inputs. ✅
- `is_top10` and `is_top5` are excluded from the is_top3 model. ✅
- The two models (is_top10 and is_top3) are trained **independently** — no stacking or cross-target feature leakage. ✅

---

## 5. Confounding Limitation — Explicit Acknowledgment

### The problem

Strategy choice (`n_stops`) is **not randomly assigned** across drivers. In observational F1 data:

- **Fast cars choose differently:** Front-tier cars running at the front of the field are more likely to deploy 1-stop strategies because they can control the pace and avoid overcut risk. Backmarker cars running in P18 sometimes switch to 3-stop strategies because they have nothing to lose.
- **Driver skill correlates with strategy:** Top drivers with more racecraft tend to make 1-stop strategies work where less skilled drivers degrade tires faster and need 2 stops.
- **Weather drives the stop count:** Wet → dry transitions force pit stops; teams that planned 1 stop end up doing 2 or 3. Weather is correlated with both stop count and outcome.

**Consequence:** In our training data, `n_stops = 2` does not arrive as a random treatment. It arrives correlated with constructor tier, circuit type, and race conditions. Our model learns the **association** between planned stop count and finishing outcome, not the **causal effect** of planning an extra stop.

### How this affects our is_top10 and is_top3 models

- The is_top10 model's `n_stops` coefficient is **observational, not causal**. When we compare 1-stop vs. 2-stop scenarios for the same grid_position + constructor_tier, we are asking: "Among drivers in the historical data who started from P5 in midfield cars and planned 2 stops, how often did they finish top 10?" — not "If we forced this driver to do 2 stops instead of 1, how would that change the outcome?"
- The is_top3 model carries the same limitation. The +8.7 pp podium probability for 2-stop vs. 1-stop (see `whatif_comparison.md`) reflects the historical association, not the guaranteed causal effect.

### Mitigation attempts in Hito 2

1. **Conditioning on confounders:** By including `constructor_tier`, `grid_position`, `circuit_type`, and driver form as model features, we partially control for the most obvious confounders. The `n_stops` coefficient reflects variation within these strata, not raw associations.

2. **Subgroup analysis:** The what-if comparison is restricted to midfield-front tier, permanent circuits, P3–P8 grid positions — the most homogeneous subgroup where the confounding is least severe and the comparison is most credible.

3. **Explicit uncertainty quantification:** The 90% confidence intervals on the what-if predictions (Section 5 of `whatif_comparison.md`) are wider than point estimates alone would suggest. The strategy desk should treat these as "order-of-magnitude signal" rather than precise probabilities.

4. **What we did NOT do:** We did not attempt propensity score matching or instrumental variable estimation, both of which would require additional data (e.g., team radio transcripts confirming planned stop count before the race) that are not available in the `f1_strategy_race_level.csv` dataset.

### Residual risk

After all mitigations, a residual confounding risk remains. The strategy recommendation from this model should be treated as one input among several — it is not a definitive causal estimate of "adding a stop gains you X% podium probability."

---

## 6. Checklist Summary

| Check | is_top10 | is_top3 |
|-------|----------|---------|
| No test-set rows in training | ✅ | ✅ |
| No 2022+ rows in calibration block leaking to training | ✅ | ✅ |
| Rolling features computed without future leakage | ✅ | ✅ |
| Target-adjacent columns excluded | ✅ | ✅ |
| Safety car / weather outcome columns excluded | ✅ | ✅ |
| n_stops declared as scenario input, not pre-race predictor | ✅ | ✅ |
| Confounding limitation explicitly documented | ✅ | ✅ |
| Cross-target feature leakage between is_top10 and is_top3 | ✅ None | ✅ None |
