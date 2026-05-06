# Hito 1 — Problem Framing Document

**Team:** Group 18 — F1 Strategy Advisor  
**Members:** Alonso Cárdenas, Benjamín Sánchez  
**Repository:** https://github.com/Benjasncz2/iit414w-lab01-group18  
**Date:** May 6, 2026

---

## 1. Decision Context

**What strategy decision is this tool supporting?**

Whether a driver is expected to finish in the Top 10 (score championship points) given pre-race information and scenario strategy inputs, so the strategy desk can evaluate different pit-stop strategies before the race starts.

**Who makes this decision?**

The race strategy desk on the pit wall, during the Friday evening debrief after FP2 and qualifying simulations.

**When in the race weekend is the decision made?**

Friday evening, after FP2 and before parc fermé conditions lock the car setup. The tool receives pre-race features (grid position, constructor tier) as fixed inputs and strategy features (n_stops, compound_sequence) as user-controlled scenario inputs to compare "what if" alternatives.

**Prediction unit:** One driver × one race (driver-race level).

---

## 2. Target & Primary Metric

**Target (LOCKED):** `is_top10` — binary indicator of whether the driver finishes in positions 1–10 and scores championship points.

**Primary metric:** Brier Score (lower is better).

**Why Brier for this decision?** The strategy desk needs *calibrated probabilities* to compare scenario outcomes, not just a classification label. Brier score directly penalizes poorly calibrated probability forecasts: a model that predicts P(top10) = 0.80 should be correct 80% of the time. Unlike log loss, Brier is bounded [0, 1] and interpretable in absolute terms; unlike Macro F1, it evaluates the quality of the probability output itself, which is the input to the what-if comparison tool.

**Secondary metrics:** ROC-AUC (discrimination ability), log loss (for comparison with docent baseline), calibration curve visual.

**Temporal split (LOCKED):**

| Block       | Seasons       | Use                                                      |
|-------------|---------------|----------------------------------------------------------|
| Train       | 2019–2021     | Fit the model                                            |
| Calibration | 2022          | Fit calibration mapping (isotonic). Never for model selection. |
| Test        | 2023–2024     | Untouched until final evaluation. Look at it once.        |

---

## 3. Baseline Plan

**Baseline approach:** Logistic regression with three features — `grid_position` (pit-lane starts mapped to 20), `constructor_tier` (front / midfield / backmarker, derived from the dataset's existing encoding), and `n_stops` (scenario input). Trained on 2019–2021, calibrated with `CalibratedClassifierCV(cv="prefit", method="isotonic")` on 2022, evaluated on 2023–2024.

**Why is this baseline F1-defendable?** Grid position has a strong monotonic relationship with finishing position (Spearman ρ ≈ −0.82 confirmed in Lab 1 EDA), constructor tier captures structural car competitiveness known before the race, and `n_stops` is a declared pre-race strategy input — all three features are available before the formation lap with zero leakage risk. This baseline can be justified entirely from F1 domain knowledge without ever seeing 2023–2024 data.

**Direction check:** Yes — higher baseline score means higher predicted P(top10). A driver starting P1 in a front-tier constructor with a 1-stop strategy will receive P(is_top10) ≈ 0.95.

**Expected baseline performance vs docent floor:**

| Reference                | Brier (test) | ROC-AUC (test) |
|--------------------------|-------------|----------------|
| Grid-rule docent baseline | 0.208       | —              |
| Calibrated docent model   | 0.132       | 0.892          |
| Our team target           | 0.130–0.150 | 0.880–0.900    |

---

## 4. What-If Comparison Plan

**Strategy variables we will vary:** `n_stops`, `compound_sequence`, `avg_pit_stop_duration_s`.

**Concrete scenarios:**

**Scenario A — Conservative 1-stop at Monza 2024 (LEC, P4, front-tier):**
- `grid_position = 4`, `constructor_tier = front`, `n_stops = 1`
- `compound_sequence = "M-H"`, `avg_pit_stop_duration_s = 23.5`
- Rationale: Low-degradation circuit, protect track position with a single stop.

**Scenario B — Aggressive 2-stop at Monza 2024 (LEC, P4, front-tier):**
- `grid_position = 4`, `constructor_tier = front`, `n_stops = 2`
- `compound_sequence = "S-M-H"`, `avg_pit_stop_duration_s = 23.0`
- Rationale: Attack with fresher tires in the final stint, accepting two pit-lane time penalties.

**Decision metric:** Difference in calibrated P(is_top10) between Scenario A and Scenario B. If |ΔP| < 0.05, the strategy desk should prefer the conservative option to minimize risk.

---

## 5. Limitations Acknowledgment

### Limitation 1: Coverage starts in 2019

The dataset begins in 2019, not earlier. This limits the training window to three seasons (2019–2021) with ~60 races, which constrains the model's ability to learn from diverse regulatory eras (e.g., pre-2019 aero rules). **Consequence for our approach:** The small training window increases variance in parameter estimates, particularly for less-represented constructors like Haas and Williams that may have fewer than 20 training observations each.

### Limitation 2: `qualifying_position` is a stand-in for `grid_position`; `qualifying_time_s` is empty

The column `qualifying_time_s` is systematically empty — it was kept for schema consistency but contains no data. `qualifying_position` is a proxy for `grid_position` and does not capture penalties, pit-lane starts, or grid drops applied after qualifying. **Consequence for our approach:** We use `grid_position` directly and never build features around qualifying time. Treating `qualifying_time_s` as a real signal would be a graded error.

### Limitation 3: Strategy features are observed post-race

Features such as `n_stops`, `compound_sequence`, and `stint_lengths` are post-race observations in the raw data. In any predictive course context, using them as predictors would be textbook target leakage.

**For this capstone, they are explicitly allowed as scenario inputs.** The product is a "what-if" comparison tool: the user intentionally sets these variables to compare strategies. The model receives them as user-controlled inputs, not as information magically known before the race.

> **This distinction is a graded item.** We declare it explicitly: strategy features enter the model as scenario parameters controlled by the user, not as pre-race predictions.

---

## 6. Experiment Plan for Hito 2

### Experiment 1: Feature expansion with driver-level priors

**Hypothesis:** Adding `driver_prior3_avg_finish` and `constructor_prior3_avg_finish` (3-race rolling averages available pre-race) will reduce Brier by ≥ 0.005 compared to the Hito 1 baseline, because recent form captures momentum effects not encoded in static constructor tier.

**Metric:** Brier score on 2023–2024 test set.

### Experiment 2: Gradient Boosted Trees vs. Logistic Regression

**Hypothesis:** A calibrated LightGBM model with ≤ 10 features will achieve Brier < 0.125 on the test set, outperforming the calibrated logistic regression baseline, because tree-based models can capture non-linear interactions between grid position and strategy choice (e.g., aggressive strategies benefit backmarkers more than front-runners).

**Metric:** Brier score and ROC-AUC on 2023–2024 test set.

### Experiment 3: Circuit-type stratification

**Hypothesis:** Model performance differs across circuit types (permanent vs. street vs. semi-street). The model will have Brier > 0.15 on street circuits vs. < 0.12 on permanent circuits, because street circuits have more safety car interventions and overtaking constraints that our model does not capture.

**Metric:** Brier score stratified by `circuit_type` on 2023–2024 test set.

---

## 7. Team Workflow

| Member           | Owns                                                               | Branch / File                          |
|------------------|--------------------------------------------------------------------|----------------------------------------|
| Alonso Cárdenas  | Data pipeline: temporal split, constructor_tier validation, leakage audit | `hito 1/hito1_baseline.ipynb` (cells 1–4) |
| Benjamín Sánchez | Baseline model: LogReg + CalibratedClassifierCV, evaluation, comparison table | `hito 1/hito1_baseline.ipynb` (cells 5–10) |
| Both             | What-if scenarios, framing.md, PROMPTS.md, README.md final review  | `hito 1/framing.md`, `PROMPTS.md`       |

**Commit schedule:**
- **Tuesday EOD (23:59):** Alonso → temporal split cells committed; Benjamín → baseline model cells committed.
- **Wednesday 12:00:** Both → experiment results committed; framing.md updated with actual Brier scores.
- **Wednesday 15:00:** Final merge to main, PROMPTS.md populated, repo clean for 16:20 submission.
