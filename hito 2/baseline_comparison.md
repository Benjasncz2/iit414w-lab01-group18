# Baseline Comparison — Hito 2

**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  
**Date:** May 13, 2026  
**Test window:** 2023–2024 (seasons held out; never touched until final evaluation)

---

## Overview of Both Targets

| Target | Type | Decision value |
|--------|------|----------------|
| `is_top10` | Binary classification | Does any pit-stop strategy yield a points finish? |
| `is_top3` | Binary classification | Does the planned strategy unlock a **podium**? |

`is_top3` was selected as the expansion target because our Hito 1 decision context centers on front-constructor strategy (Aston Martin / midfield teams fighting for podiums). A strategy that keeps P(top10) stable but reduces P(top3) is an invisible trade-off if we only model the top-10 boundary. That trade-off is the primary motivation for Hito 2.

---

## Target 1: `is_top10`

### Baselines compared

| Model | Brier ↓ | ROC-AUC ↑ | Log-loss ↓ | Notes |
|-------|---------|-----------|------------|-------|
| Majority-class rule (always predict mean rate) | 0.208 | 0.500 | 0.618 | Docent grid-rule floor |
| **Docent calibrated baseline** | **0.132** | **0.892** | — | Published benchmark |
| Our Hito 1 baseline (LogReg + calibration) | 0.127 | 0.898 | 0.389 | grid_pos + ctor_tier + n_stops |
| Our Hito 2 LightGBM (expanded features) | 0.119 | 0.911 | 0.365 | + driver form + circuit type |
| Our Hito 2 LightGBM + isotonic calibration | **0.113** | **0.914** | **0.352** | Best model, test set |

**Against docent baseline:** Our best model reduces Brier by **0.019** (−14.4% relative improvement). This exceeds the team target of Brier < 0.130 set in Hito 1.

### Feature set used (Hito 2 model)

| Feature | Type | Leakage status |
|---------|------|----------------|
| `grid_position` | Pre-race | ✅ Safe — known after qualifying |
| `constructor_tier` | Pre-race | ✅ Safe — derived from prior season points |
| `n_stops` (user-set) | **Scenario input** | ✅ Safe — strategist declares planned stop count |
| `circuit_type` | Pre-race | ✅ Safe — structural circuit property |
| `driver_prior3_avg_finish` | Pre-race | ✅ Safe — 3-race rolling average before this race |
| `constructor_prior3_avg_finish` | Pre-race | ✅ Safe — team form rolling average |

> **Important clarification (per Hito 1 feedback):** `n_stops` represents the **planned stop count** declared by the strategy desk before the race — not the actual stop count observed post-race. The what-if tool varies this value explicitly as a scenario parameter.

### Calibration quality

Isotonic calibration on the 2022 block reduces the calibration gap substantially. ECE (Expected Calibration Error) drops from 0.071 (uncalibrated) to 0.028 (calibrated) on the test set. The calibration curve is approximately diagonal across the full probability range [0, 1].

---

## Target 2: `is_top3`

### Baseline justification

For `is_top3`, the majority-class rule (always predict 0 — top-3 finishes occur ~15% of the time) gives Brier = 0.127, which is deceptively good. We use a **grid-position threshold rule** as the operational baseline: predict is_top3 = 1 if grid_position ≤ 3, else 0. This mimics what a strategy desk would do without any model.

| Model | Brier ↓ | ROC-AUC ↑ | Log-loss ↓ | Notes |
|-------|---------|-----------|------------|-------|
| Majority-class rule (always 0) | 0.127 | 0.500 | 0.430 | Trivial baseline; misleadingly low Brier |
| Grid top-3 threshold rule (grid ≤ 3 → top3) | 0.118 | 0.781 | — | Operational baseline |
| Our LogReg baseline (same features as top10) | 0.112 | 0.839 | 0.341 | Calibrated on 2022 block |
| Our LightGBM (expanded features) | 0.101 | 0.867 | 0.318 | + driver form + circuit type |
| Our LightGBM + isotonic calibration | **0.096** | **0.871** | **0.309** | Best model, test set |

**Against operational baseline:** Our best model reduces Brier by **0.022** (−18.6% relative improvement over grid-threshold rule).

### Why the majority-class baseline is misleading for `is_top3`

Because podiums are rare (~15% base rate), a model that always predicts 0 achieves Brier ≈ 0.127. This is numerically close to the docent is_top10 benchmark but conveys zero information. We therefore use the grid-threshold rule as the meaningful comparison point — it at least separates front-row starters from the field.

### Calibration quality

ECE on the test set: 0.041 (uncalibrated) → 0.019 (calibrated). The is_top3 model is better calibrated than is_top10 in the low-probability region (P < 0.20), where most observations sit. The high-probability region (P > 0.70) has fewer observations and higher calibration uncertainty.

---

## Side-by-Side Summary

| Metric | is_top10 best model | is_top3 best model |
|--------|--------------------|--------------------|
| Brier (test) | 0.113 | 0.096 |
| ROC-AUC (test) | 0.914 | 0.871 |
| Log-loss (test) | 0.352 | 0.309 |
| ECE (calibrated) | 0.028 | 0.019 |
| vs. docent/operational baseline | −14.4% Brier | −18.6% Brier |

Both models beat their respective baselines by a meaningful margin. The is_top3 model shows stronger relative improvement, likely because the grid-threshold operational baseline is weaker than the docent calibrated model used for is_top10.
