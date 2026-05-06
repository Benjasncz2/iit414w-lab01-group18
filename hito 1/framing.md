# Team Decision Sheet — Capstone Hito 1
**IIT414W · F1 Race Strategy Advisor · Mon May 4, 2026**

**Team name:** Group 18 — F1 Strategy Advisor  
**Team members:** Alonso Cárdenas, Benjamín Sánchez  
**GitHub repo URL:** https://github.com/Benjasncz2/iit414w-lab01-group18  

## 1. Decision Context
**What strategy decision is this tool supporting?**  
Whether a driver is expected to score championship points (finish Top 10) given their qualifying grid position and constructor history, so the strategy desk can decide how aggressively to race on Sunday.

**Who makes this decision?**  
The race strategy desk on the pit wall, during the Friday evening debrief after FP2 and qualifying simulations.

**When in the race weekend is the decision made?**  
Friday evening, after FP2, before parc fermé conditions lock the car setup, using only pre-race information available at that moment.

## 2. Target & Metric
**Target:** is_top10

**Primary metric:** Brier Score  
**Why this metric for this decision?** Brier score measures the accuracy of calibrated probability estimates, which is what matters for a scenario comparison tool — the strategy desk needs P(top10) = 0.73 vs P(top10) = 0.61, not just a ranking. 

**Secondary metrics:** Macro F1-Score (retained as a secondary metric for interpretability), ROC-AUC, and log loss.

**Temporal split:**
* Train: seasons 2019, 2020, 2021
* Calibration: season 2022 (used to fit calibration mapping; never for model selection)
* Test: seasons 2023, 2024 (untouched until final evaluation)

## 3. Baseline Plan
**Baseline approach:**  
Logistic regression on grid_position (pit-lane starts mapped to 20) + constructor_tier (top/mid/back, derived from prior-season constructor standings) + n_stops, trained on 2019–2021 and calibrated on 2022.

**Why is this baseline F1-defendable?**  
Grid position has a Spearman ρ ≈ −0.82 correlation with is_top10 confirmed in our Lab 1 EDA, constructor tier captures structural car competitiveness known before the race, and n_stops is a declared pre-race strategy input — all three features are fully available before the formation lap with zero leakage risk.

n_stops, compound_sequence, and stint_lengths are post-race observations in the raw dataset. In any standard modeling context they would constitute target leakage. In this capstone they are intentionally included as user-controlled scenario inputs — the model user sets these values to simulate a strategy decision before the race. This distinction is declared explicitly and applies to all experiments in this project.

**Direction check: higher baseline score means higher predicted P(top10):**  
Yes — a driver starting P1 in a top-tier constructor declaring a 1-stop strategy will receive a predicted P(is_top10) close to 1.0; the model score increases monotonically as grid position improves and constructor tier rises.

**Expected baseline performance vs docent floor:**
* Grid-rule docent baseline: Brier = 0.208 on test
* Calibrated docent model: Brier = 0.132 on test, ROC-AUC = 0.892
* Our team's best baseline expected to land near: Brier = 0.150 (our Lab 3 Logistic Regression achieved Macro F1 = 0.818 on a comparable holdout; adding calibration on 2022 and constructor_tier should bring Brier below the grid-rule floor of 0.208 while landing above the fully-calibrated docent model at 0.132)

## 4. What-If Comparison Plan
**Strategy variables we will vary:**
* n_stops
* compound_sequence
* stint_lengths (or stint1_length, stint2_length, etc.)
* avg_pit_stop_duration_s

**Concrete scenarios to compare:**
* **Scenario A (Conservative 1-stop):** grid_position = 8, constructor_tier = mid, n_stops = 1, compound_sequence = ["Medium", "Hard"], avg_pit_stop_duration_s = 24.0 — standard midfield strategy at a low-degradation circuit.
* **Scenario B (Aggressive 2-stop):** grid_position = 8, constructor_tier = mid, n_stops = 2, compound_sequence = ["Soft", "Medium", "Soft"], avg_pit_stop_duration_s = 23.5 — same driver and grid slot as Scenario A, taking an extra tire set to attack positions in the second stint.

**Decision metric for the comparison:**
Difference in calibrated P(is_top10) between Scenario A and Scenario B, with bootstrap 90% confidence interval across 1,000 resamples of the 2023–2024 test races.

## 5. Limitations Acknowledgment
**Limitation #1 we acknowledge:** Race-day dynamics (mechanical failures, weather, safety cars, collisions) are absent from the feature set.  
**Why it matters for our approach:** Our model is trained only on pre-race features, so a driver starting P1 who suffers a lap-2 engine failure will still receive P(is_top10) ≈ 0.95 — our Lab 1 DATA_QUALITY_LOG identified this as the primary source of false positives and the reason even a perfect grid-based model carries ~14% irreducible error.

**Limitation #2 we acknowledge:** Constructor/team semantic inconsistency across seasons due to rebranding (e.g., AlphaTauri → RB, Racing Point → Aston Martin).  
**Why it matters for our approach:** Without a harmonization mapping, the model treats rebranded teams as entirely new entities with no performance history, corrupting the constructor_tier feature for those teams across the 2019–2024 training and calibration window.

**Limitation #3 we acknowledge:** safety_car_periods is a binary indicator per driver-race, not a full race-control interval count.  
**Why it matters for our approach:** This means our model cannot distinguish a race with one early safety car from one with three late safety cars — both collapse to the same binary signal, understating the variance in race outcomes caused by safety car timing.

## 6. Experiment Plan for Hito 1
**Three experiments we will run between today and Wednesday 16:20:**
1. **Baseline Logistic Regression** — fit on 2019–2021 with features grid_position, constructor_tier, n_stops; calibrate with CalibratedClassifierCV(cv="prefit", method="isotonic") on 2022; evaluate Macro F1 and Brier on 2023–2024 test set.
2. **Constructor encoding comparison** — compare constructor encodings using 3-fold cross-validation on the training set (2019–2021 only) to determine which encoding reduces overfitting on small-N teams like Haas and Williams.
3. **Strategy what-if sweep** — hold grid_position and constructor_tier fixed at a midfield scenario (P8, mid-tier) and vary n_stops ∈ {1, 2} and compound_sequence across 4 combinations, reporting ΔP(is_top10) with bootstrap 90% CI.

**Hypothesis for each:**
1. We expect Macro F1 ≈ 0.81–0.83 and Brier ≈ 0.145–0.160, beating the grid-rule docent floor (Brier = 0.208) because calibration on 2022 removes overconfidence near the P10/P11 boundary where the heuristic makes most of its errors.
2. We expect constructor_tier (3-level) to match or slightly outperform raw constructor_id on Brier, since compressing 10+ sparse one-hot columns into three semantically meaningful groups reduces variance on teams with few historical races in the training window.
3. We expect ΔP(is_top10) between the 1-stop and 2-stop scenarios to be small (< 0.06) for a P8 mid-tier driver, reflecting that the current model is dominated by grid position — a result that would motivate adding real-time tire degradation features in Hito 2.

## 7. Team Workflow
**Who is doing what between now and Wednesday?**

| Member | Owns | Branch / file in repo |
| :--- | :--- | :--- |
| Alonso Cárdenas | Data pipeline: temporal split 2019–2021/2022/2023–2024, constructor_tier harmonization mapping, evaluation harness (Macro F1 + Brier) | `feature/alonso-data-pipeline` / `labs/capstone/data_pipeline.ipynb` |
| Benjamín Sánchez | Baseline model: LogReg + CalibratedClassifierCV, experiments 1 & 2, comparison table | `feature/benja-baseline-model` / `labs/capstone/baseline_capstone.ipynb` |
| Both | What-if sweep (Experiment 3), framing.md final review, PROMPTS.md update | `main` after merge / `framing.md`, `PROMPTS.md` |

**When does each member commit by?**
* Tuesday EOD (23:59): Alonso → data pipeline committed and passing with correct temporal split; Benjamín → baseline model cells 1–8 committed with visible outputs.
* Wednesday 12:00: Both → experiment results committed; framing.md updated with actual Macro F1 and Brier scores replacing the estimates in Section 3.
* Wednesday 15:00: Final merge to main, PROMPTS.md populated with ≥3 entries, repo clean for 16:20 review.

## 8. Critique Received in Pair Review
To be completed during Block 5