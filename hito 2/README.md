# Hito 2 — F1 Race Strategy Advisor (Midpoint Model)

**Course:** IIT414W — Artificial Intelligence Workshop  
**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  
**Deadline:** Wednesday, May 13, 2026 — 16:20 CLT

---

## Quick Start

### Prerequisites

- Python 3.11 (via conda)
- Conda environment `iit414w` (see `environment.yml` in the repo root)
- Dataset: `../hito 1/data/f1_strategy_race_level.csv` (shared with Hito 1)

### Install

```bash
# From the repository root
conda env create -f environment.yml
conda activate iit414w
```

### Run the Notebook

```bash
cd "hito 2"
jupyter lab hito2_modeling.ipynb
# Then: Kernel → Restart & Run All
```

The notebook runs end-to-end from a clean clone. All outputs are reproducible with the random seed set in Cell 1 (`RANDOM_STATE = 42`).

---

## Repository Structure

```
hito 2/
├── README.md                  ← You are here
├── PROMPTS.md                 ← AI interaction log (Interactions 4–7; see hito 1/PROMPTS.md for 1–3)
├── hito2_modeling.ipynb       ← Reproducible training + evaluation notebook (both targets)
├── baseline_comparison.md     ← Baseline comparison table on both targets
├── error_analysis.md          ← Sliced error analysis (strategy type / circuit type / constructor tier)
├── whatif_comparison.md       ← What-if comparison surfacing is_top10 vs. is_top3 disagreement
├── leakage_audit.md           ← Leakage + confounding guard checklist
└── mitigations.md             ← Risks and mitigations for the final report
```

---

## Targets

| Target | Type | Decision value |
|--------|------|----------------|
| `is_top10` | Binary (points finish) | Carried over from Hito 1 |
| `is_top3` | Binary (podium finish) | **Hito 2 expansion** |

**Why is_top3?** A 1-stop strategy may preserve P(top10) ≈ P(2-stop) while reducing P(top3) meaningfully. This trade-off is invisible if you only model the top-10 boundary. See `whatif_comparison.md` for the concrete scenario.

---

## Temporal Split (LOCKED — identical to Hito 1)

| Block | Seasons | Use |
|-------|---------|-----|
| Train | 2019–2021 | Fit LightGBM models |
| Calibration | 2022 | Fit isotonic calibration (cv="prefit") |
| Test | 2023–2024 | Final evaluation only; touched once |

---

## Models

Both targets use a calibrated LightGBM pipeline:

1. **LightGBM classifier** fitted on 2019–2021 train set
2. **Isotonic calibration** (`CalibratedClassifierCV(cv="prefit", method="isotonic")`) fitted on 2022
3. **Evaluation** on 2023–2024 test set

### Feature set

| Feature | Type | Notes |
|---------|------|-------|
| `grid_position` | Pre-race | Pit-lane starts mapped to 20; clipped [1, 20] |
| `constructor_tier` | Pre-race | front=2 / midfield=1 / backmarker=0 (ordinal) |
| `n_stops` | **Scenario input** | Strategist's **planned** stop count — NOT actual post-race stops |
| `circuit_type` | Pre-race | street / permanent / hybrid (label-encoded) |
| `driver_prior3_avg_finish` | Pre-race | 3-race rolling average; computed with `.shift(1)` |
| `constructor_prior3_avg_finish` | Pre-race | Team form rolling average; same lag |

> **Critical distinction:** `n_stops` represents the **planned stop count declared by the strategist before the race**, not the actual stop count observed after the race. The what-if tool varies this value explicitly to compare strategies.

---

## Key Results (Test Set 2023–2024)

| Target | Best model Brier | ROC-AUC | ECE (calibrated) | vs. baseline |
|--------|-----------------|---------|-----------------|-------------|
| is_top10 | 0.113 | 0.914 | 0.028 | −14.4% vs. docent 0.132 |
| is_top3 | 0.096 | 0.871 | 0.019 | −18.6% vs. grid-threshold rule |

---

## What-If Finding

At Bahrain (permanent circuit), midfield-front constructor, starting P5:

| Strategy | P(is_top10) | P(is_top3) |
|----------|------------|-----------|
| 1-stop | 0.887 | 0.231 |
| 2-stop | 0.881 | 0.318 |
| **Difference** | **−0.006 (noise)** | **+0.087 (signal)** |

The is_top10 model says "equivalent." The is_top3 model says "2-stop for podium." This disagreement is the core decision value of the two-target architecture.

---

## Artifacts Checklist

- [x] `hito2_modeling.ipynb` — Reproducible training + evaluation (both targets)
- [x] `baseline_comparison.md` — Baseline comparison table (docent comparison for is_top10; justified baseline for is_top3)
- [x] `error_analysis.md` — Sliced by strategy type, circuit type, constructor tier; both targets
- [x] `whatif_comparison.md` — One concrete disagreement scenario
- [x] `leakage_audit.md` — Feature classification + confounding limitation + checklist
- [x] `mitigations.md` — 6 risks with current + deployment mitigations
- [x] `PROMPTS.md` — 4 Hito 2 AI interactions documented

---

## Dependencies

See `environment.yml` in the repo root. Key packages:
- `pandas >= 2.3`
- `scikit-learn >= 1.8`
- `lightgbm >= 4.3`
- `matplotlib >= 3.10`
- `numpy >= 2.4`
