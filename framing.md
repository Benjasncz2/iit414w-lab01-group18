# Team Decision Sheet — Capstone Hito 1
### IIT414W · F1 Race Strategy Advisor · Mon May 4, 2026

> **Instructions.** Complete this sheet in your team repo as `framing.md`. Every team has 60 minutes during the studio block (14:45–15:45). Required commits: by 15:00 (sections 1–4 populated) and by 15:40 (full sheet + dataset-load notebook). No section can be left blank — write "TBD with rationale" if you are uncertain, but blank entries fail the framing rubric.

**Team name:** Group 18 — F1 Strategy Advisor
**Team members:** Alonso Cárdenas, Benjamín Sánchez
**GitHub repo URL:** https://github.com/Benjasncz2/iit414w-lab01-group18

---

## 1. Decision Context

**What strategy decision is this tool supporting?**
> Whether a driver is expected to score championship points (finish Top 10) given their qualifying grid position and constructor history, so the strategy desk can decide how aggressively to race on Sunday.

**Who makes this decision?**
> The race strategy desk on the pit wall, during the Friday evening debrief after FP2 and qualifying simulations.

**When in the race weekend is the decision made?**
> Friday evening, after FP2 and before parc fermé conditions lock the car setup, using only pre-race information available at that moment.

---

## 2. Target & Metric

**Target (LOCKED for Hito 1):** `is_top10`

**Primary metric:** Brier Score (calibrated probability loss)

**Why this metric for this decision?** (2 sentences max)
> The strategy desk needs calibrated probabilities to weigh risk trade-offs (e.g., P(top10) = 0.55 vs 0.80 changes whether to gamble on a 2-stop), not just a binary label — Brier Score directly penalizes overconfident or poorly calibrated predictions. Unlike Macro F1, Brier Score rewards models that output well-calibrated P(is_top10) values, which is the actual input to the what-if comparison in Section 4.

**Secondary metric (optional but recommended):** ROC-AUC (for discriminative power ranking, complementing the calibration focus of Brier)

**Temporal split (LOCKED for Hito 1):**
- Train: seasons 2019, 2020, 2021
- Calibration: season 2022 (used to fit calibration mapping; never for model selection)
- Test: seasons 2023, 2024 (untouched until final evaluation)

---

## 3. Baseline Plan

**Baseline approach (one sentence):**
> Calibrated logistic regression using `grid_position` (mapped: pit-lane starts → 20) and `constructor_tier` (top/mid/back, derived from constructor championship standings at season start) as the only pre-race features.

**Why is this baseline F1-defendable?** (One sentence)
> Grid position has a documented Spearman ρ ≈ −0.82 correlation with `is_top10` in our EDA (Labs 1–3), and constructor tier captures the car's structural competitiveness — both are known before the formation lap with zero leakage risk.

**Direction check:** higher baseline score means higher predicted P(top10). **Yes** — the model outputs P(is_top10 = 1); a driver starting P1 in a top-tier car will receive a score close to 1.0.

**Expected baseline performance vs docent floor:**
- Grid-rule docent baseline: Brier = 0.208 on test
- Calibrated docent model: Brier = 0.132 on test, ROC-AUC = 0.892
- Our team's best baseline expected to land near: Brier = **0.145** (we expect to land between the two docent benchmarks; our Lab 3 grid heuristic with F1 = 0.835 suggests strong discriminative power, but calibration on the 2019–2022 window may widen the Brier gap slightly vs the 2019–2024 docent)

---

## 4. What-If Comparison Plan

**Strategy variables we will vary:**
- [x] `n_stops`
- [x] `compound_sequence`
- [ ] `stint_lengths` (or stint1_length, stint2_length, etc.)
- [x] `avg_pit_stop_duration_s`
- [ ] Other: ____________________

**Concrete scenarios to compare (at least two, with specific values):**

> **Scenario A (Conservative 1-stop):** `n_stops = 1`, `compound_sequence = ["Medium", "Hard"]`, `avg_pit_stop_duration_s = 24.0` — baseline expectation for a midfield driver (grid P8, constructor_tier = mid) at a standard-degradation circuit.

> **Scenario B (Aggressive 2-stop):** `n_stops = 2`, `compound_sequence = ["Soft", "Medium", "Soft"]`, `avg_pit_stop_duration_s = 23.5` — same driver and starting conditions as Scenario A, but taking an extra tire set to attack grid positions.

**Decision metric for the comparison:**
> Difference in calibrated P(is_top10) between Scenario A and Scenario B, with bootstrap 90% confidence interval across 1,000 resamples of the 2023–2024 test races.

---

## 5. Limitations Acknowledgment

**Five known dataset limitations are documented in the Capstone Brief. Which TWO most affect our team's specific approach?**

**Limitation #1 we acknowledge:** Race-day dynamics are not captured (mechanical reliability, weather, safety cars, collisions).
> Why it matters for our approach: Our model is trained only on pre-race features (grid, constructor tier, tire strategy), so a driver starting P1 who suffers a lap-2 engine failure will still receive P(is_top10) ≈ 0.95 — our Lab 1 DATA_QUALITY_LOG explicitly identified this as the primary false-positive driver and the reason the heuristic baseline has ~14–19% error.

**Limitation #2 we acknowledge:** Team/constructor semantic inconsistency across seasons due to rebranding (e.g., AlphaTauri → RB, Racing Point → Aston Martin).
> Why it matters for our approach: If we encode `constructor_tier` from raw team names without harmonization, the model treats rebranded teams as new entities with no performance history, breaking the constructor_tier feature for 2022–2024 and potentially inflating variance in our calibration set.

---

## 6. Experiment Plan for Hito 1

**Three experiments we will run between today and Wednesday 16:20:**

1. **Baseline calibrated logistic regression** — fit on 2019–2021, calibrate on 2022 using `CalibratedClassifierCV` (isotonic), evaluate Brier + AUC on 2023–2024.
2. **Constructor-tier encoding comparison** — test raw `constructor_id` (one-hot, high cardinality) vs. manually-mapped `constructor_tier` (3 levels: top/mid/back) to assess which reduces Brier on the calibration set without overfitting to the 2022 grid order.
3. **Strategy-variable what-if sweep** — fix a midfield driver scenario (grid P7–P12) and vary `n_stops` ∈ {1, 2} and `compound_sequence` across 4 combinations to measure the range of ΔP(is_top10) with 90% bootstrap CI.

**Hypothesis for each:**
> 1. We expect Brier ≈ 0.140–0.155; the model should beat the grid-rule docent baseline (0.208) because calibration removes overconfidence near P10/P11 boundary.
> 2. We expect `constructor_tier` (3-level) to generalize better than raw `constructor_id` (≥10 levels) — lower Brier on 2022 calibration by ~0.01 due to reduced overfitting on small-N teams like Haas.
> 3. We expect the 2-stop strategy (Scenario B) to yield ΔP(is_top10) ≈ +0.04 to +0.08 for mid-grid starters, with wide CI (±0.06) reflecting the noise in our race-day-blind model.

---

## 7. Team Workflow

**Who is doing what between now and Wednesday?**

| Member | Owns | Branch / file in repo |
|---|---|---|
| Alonso Cárdenas | Data pipeline: temporal split 2019–2022 load, constructor_tier mapping, Brier/AUC evaluation harness | `feature/alonso-data-pipeline` / `labs/capstone/data_pipeline.ipynb` |
| Benjamín Sánchez | Baseline model: LogReg + CalibratedClassifierCV, experiment 1 & 2, comparison table | `feature/benja-baseline-model` / `labs/capstone/baseline_capstone.ipynb` |
| Both | What-if sweep (Experiment 3), framing.md final review, PROMPTS.md update | `main` after merge / `framing.md`, `PROMPTS.md` |

**When does each member commit by?**
> - **Tuesday EOD (23:59):** Alonso → data pipeline committed + passing; Benjamín → baseline model cell 1–8 committed with outputs visible.
> - **Wednesday 12:00:** Both → experiment results committed; framing.md updated with actual Brier scores (replace estimates in Section 3).
> - **Wednesday 15:00:** Final merge to main, PROMPTS.md populated with ≥3 entries, repo clean for 16:20 review.

---

## 8. Critique Received in Pair Review

> *Filled during Block 5 (15:45–16:05) after the partner team reviews this sheet.*

**Reviewing team:** ____________________

**Concrete critique we received:**

> *(to be completed during Block 5)*

**How we will address this critique by Wednesday:**

> *(to be completed during Block 5)*

---

## Self-Check Before Committing

Before you push this to GitHub, verify:

- [x] Decision context is one sentence, not a paragraph
- [x] Target says exactly `is_top10` (not "Top-10" or "P(top10)")
- [x] Temporal split shows three blocks: 2019–2021 / 2022 / 2023–2024
- [x] Baseline is described in code-realistic terms (we could implement it)
- [x] What-if scenarios have specific feature values, not generic words
- [x] At least 2 of the 5 limitations are acknowledged with consequence
- [ ] PROMPTS.md exists in the repo (even if empty for now — will be populated by Wednesday)