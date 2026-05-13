# Mitigations & Risks — Hito 2

**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  
**Date:** May 13, 2026  
**Scope:** Risks applicable to the final deployed strategy advisor (both targets)

---

## Overview

This document catalogs the concrete risks identified in the Hito 2 error analysis and what-if comparison, paired with realistic mitigations for each. Risks are ordered by severity (impact × likelihood).

---

## Risk 1: Confounding — Strategy Choice Is Not Random

**Severity:** High (affects validity of core recommendations)  
**Source:** `leakage_audit.md` Section 5; `error_analysis.md` Slice 3

### What the model fails on

The model learns the historical association between planned stop count and finishing position — not the causal effect of changing the stop count. In the training data, teams that chose 2-stop strategies were systematically different from teams that chose 1-stop strategies (different car pace, different track conditions, different driver skill). The `n_stops` coefficient in the model conflates strategy effect with selection effect.

**Concrete failure scenario:** A backmarker driver moves from constructor tier "backmarker" to "midfield" mid-season (e.g., via a car upgrade). The model uses constructor tier from the start of the season. Its `n_stops` coefficient was learned from data where midfield cars had different pace characteristics. The recommendation for this driver's 2-stop strategy in the new car is unreliable.

### Mitigation (current)
- Conditioning on confounders (constructor tier, grid position, circuit type, driver form) in the feature set reduces but does not eliminate the confounding.
- What-if comparisons restricted to the most homogeneous subgroups (midfield-front tier, permanent circuits, P3–P8 grid positions) where the assumption of "same conditions, different strategy" is most defensible.

### Mitigation (for final deployment)
- Collect **declared pre-race strategy** from team radio or strategy briefing transcripts to verify that `n_stops` in the training data actually represents the planned strategy, not a reconstructed post-race inference.
- Use causal inference methods (propensity-score stratification) to re-weight training observations so that 1-stop and 2-stop examples are more comparable on observable confounders.
- Report the model's recommendations with an explicit uncertainty band that includes confounding uncertainty, not just sampling uncertainty.

---

## Risk 2: Street Circuit Performance Degradation

**Severity:** High (35–40% higher Brier on street circuits)  
**Source:** `error_analysis.md` Slice 2

### What the model fails on

Both is_top10 and is_top3 models show substantially higher error at street circuits (Monaco, Singapore, Baku, Miami, Las Vegas). Street circuits have higher DNF rates (barriers, walls, tighter runoff), higher safety car frequency, and stronger track-position locking effects — none of which are in the feature set.

**Concrete failure scenario:** The model predicts P(is_top10) = 0.73 for a mid-grid driver at Monaco. Historical DNF rates for mid-grid drivers at Monaco are ~30%, making the realistic probability closer to 0.51. The model overestimates points probability by ~0.22 — enough to give misleadingly confident recommendations.

### Mitigation (current)
- Error analysis explicitly flags street circuits as higher-uncertainty contexts.
- The Hito 2 what-if comparison scenario avoids street circuits.

### Mitigation (for final deployment)
- Add circuit-specific historical DNF rate as a pre-race feature. This is computable from historical data without leakage (e.g., "at this circuit over the last 5 seasons, what fraction of mid-grid starters DNF?").
- Increase confidence interval width at street circuits by a calibration factor derived from the error analysis.
- Warn the user interface: *"This circuit has historically high model uncertainty (Brier +36% above average). Treat recommendations as directional only."*

---

## Risk 3: No-Stop / Emergency Strategy Blind Spot

**Severity:** Medium-High (Brier 0.198 on 0-stop strategies)  
**Source:** `error_analysis.md` Slice 1

### What the model fails on

The model cannot predict outcomes for zero-stop strategies reliably. Zero-stop finishes are almost entirely driven by safety car / virtual safety car timing (which compresses the field and removes the time loss from pitting) or forced decisions to stay out despite degradation. Neither dynamic is in the pre-race feature set.

**Concrete failure scenario:** A strategy desk tests a zero-stop scenario during the pre-race debrief to check if it's viable in the event of an early safety car. The model returns P(is_top10) = 0.42 for a zero-stop strategy from P8 — but this probability means nothing because the model has never seen a zero-stop from P8 without an accompanying safety car event. The model is extrapolating outside its training distribution.

### Mitigation (current)
- The strategy desk is explicitly warned (in this document and in `leakage_audit.md`) not to use the model for zero-stop scenarios.

### Mitigation (for final deployment)
- Build a separate binary classifier: "Is a zero-stop viable given historical safety car probability at this circuit?" — or simply hard-code a flag that routes zero-stop queries to a domain-expert rule rather than the model.
- Add a model input gate that rejects zero-stop queries with an explicit message: *"Zero-stop strategy predictions are outside this model's reliable operating range. Contact the strategy desk for manual assessment."*

---

## Risk 4: Backmarker Constructor Representation

**Severity:** Medium (58% higher Brier for backmarkers vs. front constructors)  
**Source:** `error_analysis.md` Slice 3

### What the model fails on

Backmarker constructor finishing outcomes are driven more by attrition (retirements from cars ahead) than by strategy choice. The model assigns a "backmarker" tier and makes predictions based on that tier, but the within-tier variance is high (Williams in early 2023 was very different from Haas late 2023). Constructor tier collapses this variance.

### Mitigation (current)
- `constructor_prior3_avg_finish` partially captures within-tier variation by tracking recent form rather than relying solely on the annual tier classification.

### Mitigation (for final deployment)
- Replace binary tier classification with a continuous pace score (e.g., season-to-date average lap time delta to fastest car, available from qualifying data). This would provide finer-grained constructor ranking without creating artificial tier boundaries.
- Add a minimum observation threshold: if a constructor appears fewer than 15 times in the training set, flag its predictions as "low-confidence" in the UI.

---

## Risk 5: is_top3 Calibration in the High-Probability Region

**Severity:** Medium (ECE degrades above P = 0.70 for is_top3)  
**Source:** `baseline_comparison.md` calibration quality section

### What the model fails on

Podium outcomes are rare (~15% base rate), so there are very few observations in the high-probability region (P > 0.70). The isotonic calibration mapping is poorly constrained in this region — there are too few calibration observations to learn a reliable mapping from raw model scores to true probabilities.

**Concrete failure scenario:** The model predicts P(is_top3) = 0.78 for a front-tier car starting from pole at a permanent circuit. The actual podium rate for such observations in the calibration set is 0.63. The model is 15 percentage points overconfident about certain podium predictions.

### Mitigation (current)
- The calibration curve visual (in the notebook) shows this gap transparently. The model's calibration note in `baseline_comparison.md` explicitly flags it.

### Mitigation (for final deployment)
- Use Platt scaling (sigmoid calibration) instead of isotonic regression for is_top3, since isotonic regression is more prone to overfitting in sparse probability regions. Compare ECE on the test set for both calibration methods.
- Alternatively, pool observations across seasons using a larger calibration block (e.g., include 2020–2021 in calibration, only if strict temporal separation is relaxed) to provide more observations for the high-probability region.

---

## Risk 6: Concept Drift Across Regulatory Eras

**Severity:** Medium (potential failure at the 2026 regulation change)  
**Source:** General modeling risk; not yet quantified in Hito 2

### What the model fails on

F1 regulations change every 2–5 years, altering car characteristics (downforce levels, tire compounds, DRS zones) in ways that change the relationship between strategy and outcome. The 2026 regulation change (active aerodynamics, new power units) may make the 2019–2024 training data obsolete within 6–12 months of deployment.

### Mitigation (for final deployment)
- Implement a performance monitoring pipeline: track Brier score on new-season data each race week. If rolling Brier exceeds 0.15 for 3 consecutive races, trigger a model retraining flag.
- Weight training observations by recency (exponential decay toward more recent seasons) to make the model more responsive to trend changes without full retraining.
- Schedule mandatory retraining at the start of each season and after any mid-season regulation clarification.

---

## Summary Table

| Risk | Severity | Current mitigation | Deployment mitigation |
|------|----------|-------------------|----------------------|
| Confounding (strategy not random) | High | Conditioning on confounders; subgroup restriction | Propensity scoring; pre-race declared strategy data |
| Street circuit degradation | High | Error flagging; avoid in what-if | Circuit-specific DNF feature; UI warning |
| Zero-stop blind spot | Med-High | Explicit user warning | Input gate + domain-expert rule |
| Backmarker representation | Medium | Rolling form feature | Continuous pace score; minimum observation threshold |
| is_top3 high-P calibration | Medium | Transparent calibration curves | Platt scaling comparison; larger calibration block |
| Concept drift (2026 regs) | Medium | — | Monitoring pipeline; seasonal retraining |
