Team Decision Sheet — Capstone Hito 1
IIT414W · F1 Race Strategy Advisor · Mon May 4, 2026

Instructions. Complete this sheet in your team repo as framing.md. Every team has 60 minutes during the studio block (14:45–15:45). Required commits: by 15:00 (sections 1–4 populated) and by 15:40 (full sheet + dataset-load notebook). No section can be left blank — write "TBD with rationale" if you are uncertain, but blank entries fail the framing rubric.

Team name: Group 18 — F1 Strategy Advisor
Team members: Alonso Cárdenas, Benjamín Sánchez
GitHub repo URL: https://github.com/Benjasncz2/iit414w-lab01-group18
1. Decision Context
What strategy decision is this tool supporting?

Whether a driver is expected to score championship points (finish Top 10) given their qualifying grid position and constructor history, so the strategy desk can decide how aggressively to race on Sunday.

Who makes this decision?

The race strategy desk on the pit wall, during the Friday evening debrief after FP2 and qualifying simulations.

When in the race weekend is the decision made?

Friday evening, after FP2, before parc fermé conditions lock the car setup, using only pre-race information available at that moment.


2. Target & Metric
Target (LOCKED for Hito 1): is_top10
Primary metric: Macro F1-Score
Why this metric for this decision? (2 sentences max — what does the metric measure that an alternative does not?)

The dataset has a near-perfect 50/50 class balance (10 scoring positions vs 10 non-scoring), which makes accuracy misleading — Macro F1 weights precision and recall equally across both classes, directly capturing whether the model correctly identifies both who will score points and who will not. Unlike accuracy, Macro F1 is not inflated by a dominant class, and it is consistent with our Lab 3 validation where the grid heuristic scored 0.835 and Logistic Regression scored 0.818 on the 2024 test season.

Secondary metric (optional but recommended): Accuracy (for interpretability when communicating results to non-technical stakeholders on the strategy desk)
Temporal split (LOCKED for Hito 1):

Train: seasons 2019, 2020, 2021
Calibration: season 2022 (used to fit calibration mapping; never for model selection)
Test: seasons 2023, 2024 (untouched until final evaluation)


3. Baseline Plan
Baseline approach (one sentence):

Logistic regression on grid_position (pit-lane starts mapped to 20) + constructor_tier (top/mid/back, derived from prior-season constructor standings) + n_stops, trained on 2019–2021 and calibrated on 2022.

Why is this baseline F1-defendable? (One sentence — could you justify it without ever seeing 2023–2024 data?)

Grid position has a Spearman ρ ≈ −0.82 correlation with is_top10 confirmed in our Lab 1 EDA, constructor tier captures structural car competitiveness known before the race, and n_stops is a declared pre-race strategy input — all three features are fully available before the formation lap with zero leakage risk.

Direction check: higher baseline score means higher predicted P(top10). Yes / No / Explain.

Yes — a driver starting P1 in a top-tier constructor declaring a 1-stop strategy will receive a predicted P(is_top10) close to 1.0; the model score increases monotonically as grid position improves and constructor tier rises.

Expected baseline performance vs docent floor:

Grid-rule docent baseline: Brier = 0.208 on test
Calibrated docent model: Brier = 0.132 on test, ROC-AUC = 0.892
Our team's best baseline expected to land near: Brier = 0.150 (our Lab 3 Logistic Regression achieved Macro F1 = 0.818 on a comparable holdout; adding calibration on 2022 and constructor_tier should bring Brier below the grid-rule floor of 0.208 while landing above the fully-calibrated docent model at 0.132)


4. What-If Comparison Plan
Strategy variables we will vary:

 n_stops
 compound_sequence
 stint_lengths (or stint1_length, stint2_length, etc.)
 avg_pit_stop_duration_s
 Other: ____________________

Concrete scenarios to compare (at least two, with specific values):

Scenario A (Conservative 1-stop): grid_position = 8, constructor_tier = mid, n_stops = 1, compound_sequence = ["Medium", "Hard"], avg_pit_stop_duration_s = 24.0 — standard midfield strategy at a low-degradation circuit.


Scenario B (Aggressive 2-stop): grid_position = 8, constructor_tier = mid, n_stops = 2, compound_sequence = ["Soft", "Medium", "Soft"], avg_pit_stop_duration_s = 23.5 — same driver and grid slot as Scenario A, taking an extra tire set to attack positions in the second stint.

Decision metric for the comparison:

Difference in calibrated P(is_top10) between Scenario A and Scenario B, with bootstrap 90% confidence interval across 1,000 resamples of the 2023–2024 test races.


5. Limitations Acknowledgment
Five known dataset limitations are documented in the Capstone Brief. Which TWO most affect our team's specific approach?
Limitation #1 we acknowledge: Race-day dynamics (mechanical failures, weather, safety cars, collisions) are absent from the feature set.

Why it matters for our approach (1 sentence): Our model is trained only on pre-race features, so a driver starting P1 who suffers a lap-2 engine failure will still receive P(is_top10) ≈ 0.95 — our Lab 1 DATA_QUALITY_LOG identified this as the primary source of false positives and the reason even a perfect grid-based model carries ~14% irreducible error.

Limitation #2 we acknowledge: Constructor/team semantic inconsistency across seasons due to rebranding (e.g., AlphaTauri → RB, Racing Point → Aston Martin).

Why it matters for our approach (1 sentence): Without a harmonization mapping, the model treats rebranded teams as entirely new entities with no performance history, corrupting the constructor_tier feature for those teams across the 2019–2024 training and calibration window.


6. Experiment Plan for Hito 1
Three experiments we will run between today and Wednesday 16:20:

Baseline Logistic Regression — fit on 2019–2021 with features grid_position, constructor_tier, n_stops; calibrate with CalibratedClassifierCV(cv="prefit", method="isotonic") on 2022; evaluate Macro F1 and Brier on 2023–2024 test set.
Constructor encoding comparison — compare constructor_tier (3-level manual mapping: top/mid/back) vs. raw constructor_id (one-hot) on the 2022 calibration set to determine which encoding reduces overfitting on small-N teams like Haas and Williams.
Strategy what-if sweep — hold grid_position and constructor_tier fixed at a midfield scenario (P8, mid-tier) and vary n_stops ∈ {1, 2} and compound_sequence across 4 combinations, reporting ΔP(is_top10) with bootstrap 90% CI.

Hypothesis for each (one line each — what do we expect to happen and why?):


We expect Macro F1 ≈ 0.81–0.83 and Brier ≈ 0.145–0.160, beating the grid-rule docent floor (Brier = 0.208) because calibration on 2022 removes overconfidence near the P10/P11 boundary where the heuristic makes most of its errors.
We expect constructor_tier (3-level) to match or slightly outperform raw constructor_id on Brier, since compressing 10+ sparse one-hot columns into three semantically meaningful groups reduces variance on teams with few historical races in the training window.
We expect ΔP(is_top10) between the 1-stop and 2-stop scenarios to be small (< 0.06) for a P8 mid-tier driver, reflecting that the current model is dominated by grid position — a result that would motivate adding real-time tire degradation features in Hito 2.



7. Team Workflow
Who is doing what between now and Wednesday?
MemberOwnsBranch / file in repoAlonso CárdenasData pipeline: temporal split 2019–2021/2022/2023–2024, constructor_tier harmonization mapping, evaluation harness (Macro F1 + Brier)feature/alonso-data-pipeline / labs/capstone/data_pipeline.ipynbBenjamín SánchezBaseline model: LogReg + CalibratedClassifierCV, experiments 1 & 2, comparison tablefeature/benja-baseline-model / labs/capstone/baseline_capstone.ipynbBothWhat-if sweep (Experiment 3), framing.md final review, PROMPTS.md updatemain after merge / framing.md, PROMPTS.md
When does each member commit by? (We need at least one commit per member per day Tue and Wed.)


Tuesday EOD (23:59): Alonso → data pipeline committed and passing with correct temporal split; Benjamín → baseline model cells 1–8 committed with visible outputs.
Wednesday 12:00: Both → experiment results committed; framing.md updated with actual Macro F1 and Brier scores replacing the estimates in Section 3.
Wednesday 15:00: Final merge to main, PROMPTS.md populated with ≥3 entries, repo clean for 16:20 review.



8. Critique Received in Pair Review

Filled during Block 5 (15:45–16:05) after the partner team reviews this sheet.

Reviewing team: ____________________
Concrete critique we received:

(to be completed during Block 5)

How we will address this critique by Wednesday:

(to be completed during Block 5)


Self-Check Before Committing
Before you push this to GitHub, verify:

 Decision context is one sentence, not a paragraph
 Target says exactly is_top10 (not "Top-10" or "P(top10)")
 Temporal split shows three blocks: 2019–2021 / 2022 / 2023–2024
 Baseline is described in code-realistic terms (we could implement it)
 What-if scenarios have specific feature values, not generic words
 At least 2 of the 5 limitations are acknowledged with consequence
 PROMPTS.md exists in the repo (even if empty for now — will be populated by Wednesday)
CompartirContenidoiit414w-lab01-group18-main.zipzipIIT414W_W10Mon_TeamDecisionSheet.md156 líneasmdIIT414W_W10Mon_TeamDecisionSheet.md156 líneasmd