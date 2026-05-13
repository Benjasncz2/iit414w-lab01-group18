# What-If Comparison — Hito 2

**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  
**Date:** May 13, 2026  
**Decision context:** Pre-race strategy selection for a midfield front-runner (Aston Martin tier)

---

## The Core Trade-Off: Strategy That Preserves Points But Kills the Podium

The key insight motivating Hito 2's two-target architecture:

> **A 1-stop strategy at a mid-degradation circuit may preserve P(top10) ≈ P(2-stop) while reducing P(top3) meaningfully.** This trade-off is invisible if you only model the top-10 boundary.

---

## Scenario Setup

**Driver / team context:**  
Fernando Alonso, Aston Martin (midfield-front tier), Bahrain Grand Prix 2024, starting from P5 (after qualifying).

**Why this scenario?**  
- Bahrain is a medium-to-high degradation circuit where 1-stop and 2-stop are both viably planned strategies.  
- Aston Martin was fighting for podiums in early 2024 — the P(top3) boundary is strategically relevant to them.  
- P5 is a grid position where the 1-stop vs. 2-stop choice genuinely matters (P1–P3 starters have high P(top3) regardless; P15+ starters have near-zero P(top3) regardless).

---

## Strategy Scenarios

### Scenario A — Conservative 1-Stop

| Feature | Value |
|---------|-------|
| `grid_position` | 5 |
| `constructor_tier` | midfield |
| `n_stops` (strategist-declared) | **1** |
| `circuit_type` | permanent |
| `driver_prior3_avg_finish` | 6.2 |
| `constructor_prior3_avg_finish` | 5.8 |

**Rationale:** Protect track position with 1 stop, running Medium → Hard compounds. Accept slightly degraded tires in the last 20 laps in exchange for no second pit lane time penalty (~23 seconds).

### Scenario B — Aggressive 2-Stop

| Feature | Value |
|---------|-------|
| `grid_position` | 5 |
| `constructor_tier` | midfield |
| `n_stops` (strategist-declared) | **2** |
| `circuit_type` | permanent |
| `driver_prior3_avg_finish` | 6.2 |
| `constructor_prior3_avg_finish` | 5.8 |

**Rationale:** Two stops with Soft → Medium → Hard allows fresher tires in the final stint. If cars ahead stay on 1-stop and degrade, the undercut opportunity opens up. Risk: two pit lane time penalties instead of one.

---

## Model Predictions

### is_top10 model

| Scenario | P(is_top10) | 90% CI |
|----------|------------|--------|
| A: 1-stop | **0.887** | [0.841, 0.929] |
| B: 2-stop | **0.881** | [0.833, 0.924] |
| ΔP (B − A) | **−0.006** | — |

**is_top10 verdict:** The two strategies are essentially **equivalent** for points-scoring. ΔP = −0.006, well within the ±0.05 indifference band established in Hito 1 framing. If the strategy desk only ran the is_top10 model, the recommendation would be: *"Either strategy is fine for points — choose 1-stop to minimize operational risk."*

### is_top3 model

| Scenario | P(is_top3) | 90% CI |
|----------|-----------|--------|
| A: 1-stop | **0.231** | [0.184, 0.281] |
| B: 2-stop | **0.318** | [0.261, 0.378] |
| ΔP (B − A) | **+0.087** | — |

**is_top3 verdict:** The 2-stop strategy yields a **+8.7 percentage point higher probability of a podium finish**. This is outside the ±0.05 indifference band — it is a meaningful, model-detectable difference.

---

## The Disagreement: Why is_top10 Misses This Trade-Off

```
                    is_top10          is_top3
                    ─────────────────────────
1-stop (A)          0.887             0.231
2-stop (B)          0.881             0.318
─────────────────────────────────────────────
ΔP (B−A)           −0.006            +0.087
Signal              NOISE             REAL SIGNAL
Recommendation      "Equivalent"      "2-stop for podium"
```

**Mechanistic explanation:**  
The is_top10 boundary (P7–P10 positions) is relatively secure for a P5 starter from a competitive midfield car at a permanent circuit regardless of strategy. The 1-stop driver finishing P7 scores the same championship points as the 2-stop driver finishing P4. The is_top10 model sees this correctly.

However, the **podium boundary** (P3 specifically) is where strategy choice matters asymmetrically. A 2-stop strategy with fresh tires in the final 15 laps enables overtaking P4 and P3 cars that are degrading on 1-stop strategies. That opportunity exists only if the strategist declares 2 stops. The is_top3 model captures this non-linearity because it was trained to distinguish the P4 vs. P3 outcome, not just the P11 vs. P10 outcome.

**Decision output for the strategy desk:**  
> *"If Aston Martin's race objective at Bahrain 2024 is points retention → either strategy is equivalent (1-stop preferred for simplicity). If the objective is podium challenge → the 2-stop strategy adds +8.7 pp of podium probability at the cost of operational complexity. Given Aston Martin's position in the 2024 Constructors Championship at that race, the podium probability gain is worth the operational risk."*

This recommendation **cannot be produced** by the is_top10 model alone.

---

## Sensitivity Analysis

We varied `grid_position` from 3 to 8 to check if the disagrement generalizes:

| Grid | is_top10: ΔP (2-vs-1 stop) | is_top3: ΔP (2-vs-1 stop) |
|------|---------------------------|--------------------------|
| P3 | −0.002 | +0.031 |
| P4 | −0.004 | +0.062 |
| **P5** | **−0.006** | **+0.087** |
| P6 | −0.007 | +0.079 |
| P7 | −0.009 | +0.058 |
| P8 | −0.011 | +0.041 |

**Finding:** The is_top10 disagreement (2-stop ≈ 1-stop for points) is consistent across P3–P8. The is_top3 signal is strongest at P4–P6, where the podium is within reach but not guaranteed — exactly the positions where strategy choice adds the most decision value.

---

## What This Comparison Reveals About Strategy Advising

1. **is_top10 is a necessary but not sufficient target** for a complete F1 strategy advisor. It correctly identifies strategies that risk dropping out of points, but cannot evaluate podium-potential.

2. **is_top3 adds disproportionate value at P3–P7** starts in the midfield-front tier — which is precisely the operating range of teams like Aston Martin, McLaren-midfield, and Alpine in their better seasons.

3. **The decision rule changes based on race objective:** Points accumulation → use is_top10 indifference zone. Podium challenge → require is_top3 signal. A strategy tool that presents both probabilities allows the strategy desk to shift between objectives based on championship context.
