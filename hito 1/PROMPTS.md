# PROMPTS.md — AI Interaction Log

**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  
**Hito:** 1 — Problem Framing + Baseline  
**Date:** May 6, 2026

---

## Interaction 1: Baseline Model Architecture

### Context
We needed to design a baseline model for predicting `is_top10` using the `f1_strategy_race_level.csv` dataset with the locked temporal split (train 2019–2021, calibration 2022, test 2023–2024). We had prior experience from Lab 3 with logistic regression on F1 data but needed to adapt the approach to include calibration on a separate block and strategy features as scenario inputs.

### Prompt
> "I need to build a calibrated logistic regression baseline for predicting is_top10 in F1 races. The features should be grid_position, constructor_tier (categorical: front/midfield/backmarker), and n_stops. Training data is 2019–2021, calibration on 2022 using isotonic regression, test on 2023–2024. How should I structure the sklearn pipeline to include one-hot encoding for constructor_tier and calibration via CalibratedClassifierCV with cv='prefit'?"

### Output
The AI suggested a two-step approach: (1) build a Pipeline with OneHotEncoder for constructor_tier and LogisticRegression, fit it on the training set; (2) wrap the fitted pipeline in CalibratedClassifierCV(cv="prefit", method="isotonic") and fit the calibration wrapper on the 2022 calibration set. It also suggested using `predict_proba` for Brier score evaluation.

### Validation
We verified the approach against the scikit-learn documentation for CalibratedClassifierCV. The `cv="prefit"` mode is correct for our use case — it assumes the base estimator is already fitted and only learns the calibration mapping. We confirmed that isotonic regression is appropriate for our sample size (~400 calibration observations) compared to Platt scaling which assumes sigmoid-shaped miscalibration.

### Adaptations
We modified the AI's suggestion in two ways:
1. Added `grid_position` clipping to [1, 20] to handle pit-lane starts (grid = 0 in the data) — the AI did not account for this edge case.
2. Changed the constructor_tier encoding from one-hot to ordinal (front=2, midfield=1, backmarker=0) after testing both approaches and finding that ordinal encoding produced lower Brier on the calibration set, likely because the three-level hierarchy captures a natural ordering.

### Final Decision
Used the two-step calibrated pipeline with ordinal encoding for constructor_tier. This decision was F1-defensible without reference to the test set.

---

## Interaction 2: Leakage Audit Classification

### Context
The capstone brief requires a leakage audit cell that documents which features are pre-race vs. scenario inputs vs. audit columns. We needed to classify all 46 columns in the dataset correctly to avoid graded errors.

### Prompt
> "Here are the columns in f1_strategy_race_level.csv: [listed all columns]. Classify each column into one of three categories: (1) pre-race features available before the formation lap, (2) scenario inputs that the user controls in the what-if tool, (3) post-race outcomes or audit columns that must NOT be used as predictors. Pay special attention to strategy features like n_stops, compound_sequence, and stint_lengths."

### Output
The AI classified all columns. Most classifications were correct, but it made one critical error: it classified `safety_car_periods` as a pre-race feature, arguing that teams can anticipate safety car likelihood from historical circuit data.

### Validation
We cross-referenced the classification against the capstone brief, which explicitly states: *"Do not silently use race-incident columns such as safety car or weather outcome as if they were known before the race."* The AI's classification of `safety_car_periods` was incorrect — it is a post-race observation, not a pre-race signal.

### Adaptations
1. Moved `safety_car_periods`, `safety_car_laps`, `vsc_laps`, `weather_actual`, and `wet_laps` from "pre-race" to "audit/post-race" category.
2. Added explicit documentation in the leakage audit cell that these columns can only be used as audit slices or scenario stress tests, not as predictors.
3. This AI failure is documented as a concrete example of why human validation is essential even with correct-sounding justifications.

### Final Decision
Adopted the corrected classification with safety car and weather columns explicitly excluded from the model. The framing.md acknowledges this limitation: race-day dynamics are absent from the feature set.

---

## Interaction 3: Framing Document Structure

### Context
We needed to write the `framing.md` document covering all seven sections from the Team Decision Sheet, with specific attention to the strategy-features-as-scenario-inputs distinction and the five known dataset limitations.

### Prompt
> "Help me structure the framing.md for our F1 strategy capstone. It needs 7 sections: decision context, target & metric, baseline plan, what-if comparison plan, limitations acknowledgment (at least 2 of 5), experiment plan for Hito 2 (3 experiments with hypotheses), and team workflow. The key thing I need to get right is explicitly declaring that strategy features like n_stops and compound_sequence are scenario inputs, not pre-race predictions."

### Output
The AI provided a draft structure with all seven sections. The what-if scenarios it suggested were generic: "Compare 1-stop vs 2-stop strategies." This violates the rubric which requires specific feature values.

### Validation
We checked the rubric: *"'Compare 1-stop vs 2-stop' is not a scenario. 'LEC, Mónaco 2024, n_stops=1 with M-H vs n_stops=2 with M-M-H' is a scenario."* The AI's generic scenarios would lose points.

### Adaptations
1. Replaced generic scenarios with specific ones: LEC at Monza 2024 from P4 (front-tier), 1-stop M-H vs 2-stop S-M-H with concrete pit stop durations.
2. Added the decision metric: if |ΔP(is_top10)| < 0.05, prefer conservative option.
3. Expanded limitations from 2 to 3, adding the strategy-confounding limitation per the brief.

### Final Decision
Used the AI's structure but with fully specified scenarios and corrected limitation acknowledgments. The framing document now meets all rubric requirements.
