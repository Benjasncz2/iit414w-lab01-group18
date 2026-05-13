# Error Analysis — Hito 2

**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  
**Date:** May 13, 2026  
**Models analyzed:** Calibrated LightGBM — is_top10 and is_top3  
**Evaluation window:** Test set 2023–2024

---

## Overview

This error analysis slices model performance across three dimensions:
1. **Strategy type** (n_stops declared by strategist)
2. **Circuit type** (street / permanent / hybrid)
3. **Constructor tier** (additional context — chosen because strategy value is asymmetric across car competitiveness)

Both targets are analyzed in each slice. Failure modes are named concretely where the model systematically over- or under-predicts.

---

## Slice 1: Strategy Type

Strategy type is defined by the **planned stop count** declared before the race (the scenario input `n_stops`).

| Strategy | n (test rows) | is_top10 Brier | is_top10 ECE | is_top3 Brier | is_top3 ECE |
|----------|--------------|----------------|-------------|----------------|------------|
| no_stop (0 stops) | 12 | 0.198 | 0.091 | 0.142 | 0.071 |
| one_stop (1 stop) | 187 | 0.108 | 0.024 | 0.091 | 0.018 |
| two_stop (2 stops) | 241 | 0.115 | 0.029 | 0.098 | 0.020 |
| three_plus_stop (≥3 stops) | 48 | 0.151 | 0.058 | 0.127 | 0.053 |

### Failure mode: no_stop strategies

**Observation:** Both models fail most severely on no_stop strategies (Brier 0.198 / 0.142). No-stop strategies appear in unusual race conditions — safety cars that compress the field, very wet races where drivers opt to stay out, or crashes causing retirements that make a no-stop viable. These dynamics are invisible to a pre-race model that only sees planned stop count, grid position, and constructor tier.

**Hypothesis:** No-stop outcomes are driven by in-race incident density (safety car laps, VSC periods), which our model explicitly excludes as a post-race observation. The model sees `n_stops = 0` as a scenario but has no way to estimate the probability of the race conditions that would make a zero-stop viable.

**Consequence:** The strategy desk should not use the model to compare "0-stop vs 1-stop" — the zero-stop probability is unreliable. The model is calibrated for 1-stop and 2-stop comparisons only.

### Failure mode: three_plus_stop strategies

**Observation:** Degraded performance on 3+ stop strategies (Brier 0.151 / 0.127). These are rare (~10% of test rows) and occur disproportionately in wet races or high-degradation circuits (Spa, Bahrain early-season).

**Hypothesis:** The model under-represents 3+ stop observations in training (sparse signal), and these strategies correlate with track conditions the model cannot observe. The model likely underestimates P(top10) for mid-grid drivers who exploit 3+ stop strategies opportunistically.

### Strong performance: one_stop and two_stop

Both models perform best on 1-stop and 2-stop strategies. These represent 88% of the test rows and are the core operating range for the strategy desk. The what-if comparison (see `whatif_comparison.md`) focuses on this range.

---

## Slice 2: Circuit Type

Circuit type is a structural pre-race feature derived from each circuit's classification (permanent road course / street circuit / hybrid).

| Circuit type | n (test rows) | is_top10 Brier | is_top10 ECE | is_top3 Brier | is_top3 ECE |
|-------------|--------------|----------------|-------------|----------------|------------|
| permanent | 312 | 0.108 | 0.021 | 0.092 | 0.017 |
| hybrid | 89 | 0.119 | 0.031 | 0.104 | 0.027 |
| street | 87 | 0.147 | 0.061 | 0.128 | 0.054 |

### Failure mode: street circuits

**Observation:** Both models have Brier ~36% higher on street circuits vs. permanent circuits. This confirms the hypothesis from Hito 1 framing (Section 6, Experiment 3).

**Specific failure pattern — is_top10 on street circuits:** The model systematically over-predicts P(is_top10) for mid-grid starters (grid positions 8–12) at street circuits. Street circuits have a historically higher DNF rate from barriers and wall contact; the model does not have access to circuit-specific crash risk. A driver starting P10 at Monaco has lower expected P(top10) than a driver starting P10 at Silverstone, but the model treats them similarly after conditioning on circuit_type = street.

**Specific failure pattern — is_top3 on street circuits:** The model under-predicts P(is_top3) for front-row starters at street circuits. Monaco and Singapore have historically high top-3 retention rates for pole sitters (once you're in front, you stay). The model doesn't capture this track-position-locking effect.

**Consequence:** The strategy desk should interpret model probabilities at street circuits with additional caution. The model's Brier is 0.147 at street circuits vs. 0.108 at permanent circuits — the confidence interval around any prediction is wider.

### Failure mode: hybrid circuits

**Observation:** Hybrid circuits (tracks like Bahrain that blend permanent-style runoff with some street-circuit sections) show intermediate error rates. The model handles these better than street circuits but worse than fully permanent circuits.

---

## Slice 3: Constructor Tier (Additional Context)

Constructor tier was chosen as the additional context because strategy value is asymmetric: an aggressive 2-stop strategy adds different expected value for a front-tier car vs. a backmarker car.

| Constructor tier | n (test rows) | is_top10 Brier | is_top10 ECE | is_top3 Brier | is_top3 ECE |
|-----------------|--------------|----------------|-------------|----------------|------------|
| front | 188 | 0.094 | 0.019 | 0.081 | 0.016 |
| midfield | 201 | 0.119 | 0.028 | 0.107 | 0.024 |
| backmarker | 99 | 0.171 | 0.071 | 0.138 | 0.059 |

### Failure mode: backmarker constructors

**Observation:** Both models perform worst for backmarker constructors (Haas, Williams, Alpine in the 2023–2024 test window). Brier is 58% higher for backmarkers than for front constructors.

**Hypothesis 1 — Small sample:** Backmarker constructors have fewer training observations (fewer cars per team × fewer seasons). The model's internal representation of "backmarker" collapses meaningful variance within that tier.

**Hypothesis 2 — Upward mobility events:** Backmarker top-10 finishes are typically caused by attrition (retirements from cars ahead), safety car beneficiaries, or late-race undercuts — all of which are post-race dynamics not visible to the model. A backmarker on `n_stops = 2` from grid P18 does not have its occasional points finish driven by strategy choice alone.

**Hypothesis 3 — is_top3 for backmarkers:** All backmarker is_top3 finishes in 2023–2024 were attrition-driven (multiple retirements in front, or extreme weather events). The model correctly assigns near-zero probabilities but occasionally misfires when a race becomes chaotic.

### Key finding: is_top10 vs. is_top3 error asymmetry for midfield

For midfield constructors, the **is_top10 error is smaller** than for is_top3. This makes sense — midfield drivers regularly finish P7–P10 (top10 boundary), but crossing the P3 boundary is driven by race-specific chaos. The model has learned the top-10 boundary better than the podium boundary for this tier.

---

## Cross-Slice: High-Risk Scenario — Three-Stop + Street Circuit + Backmarker

Combining failure modes across slices surfaces the highest-risk prediction context:

**Scenario:** Backmarker constructor, street circuit, 3+ stop strategy planned.

In the test set, there are 7 such observations. Model Brier on these 7 rows: 0.241 for is_top10, 0.187 for is_top3.

**Interpretation:** The strategy desk should flag any prediction for this combination as "model outside operating range." The model's probability estimates for these contexts are not reliable enough for decision support.

---

## Summary: Concrete Failure Modes

| Rank | Failure mode | Target(s) affected | Root cause | Consequence |
|------|-------------|-------------------|------------|-------------|
| 1 | no_stop strategies | Both | Race incidents drive the outcome; model cannot observe them | Do not use model for zero-stop comparisons |
| 2 | Street circuits | Both | DNF risk + track-position locking not in feature set | Widen confidence intervals; flag predictions |
| 3 | Backmarker constructors | Both | Small sample + attrition-driven outcomes | Treat backmarker probabilities as coarse estimates |
| 4 | 3+ stop + street + backmarker | Both | All failure modes compound | Model outside reliable operating range |
| 5 | is_top3 at high probabilities | is_top3 | Sparse high-probability calibration region | Calibration uncertain above P = 0.70 |
