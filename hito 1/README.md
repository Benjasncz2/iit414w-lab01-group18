# Hito 1 — F1 Race Strategy Advisor (Baseline)

**Course:** IIT414W — Artificial Intelligence Workshop  
**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  
**Deadline:** Wednesday, May 6, 2026 — 16:20 CLT

---

## Quick Start

### Prerequisites

- Python 3.11 (via conda)
- Conda environment `iit414w` (see `environment.yml` in the repo root)

### Install

```bash
# From the repository root
conda env create -f environment.yml
conda activate iit414w
```

### Run the Notebook

```bash
cd "hito 1"
jupyter lab hito1_baseline.ipynb
# Or: jupyter notebook hito1_baseline.ipynb
# Then: Kernel → Restart & Run All
```

The notebook runs end-to-end from a clean clone. All outputs are reproducible with the random seed set in Cell 1.

---

## Repository Structure

```
hito 1/
├── README.md                 ← You are here
├── framing.md                ← Problem framing document (7 sections)
├── hito1_baseline.ipynb      ← Executable baseline notebook
├── PROMPTS.md                ← AI interaction log (6-field format)
└── data/
    └── f1_strategy_race_level.csv  ← Dataset (2019–2024)
```

---

## What's Inside

| File | Description |
|------|-------------|
| `framing.md` | Decision context, target justification, baseline plan, what-if scenarios, limitations, experiment plan, workflow |
| `hito1_baseline.ipynb` | Data loading → temporal split → leakage audit → baseline model → calibration → evaluation → what-if scenarios |
| `PROMPTS.md` | Documented AI interactions with context, prompts, validation, and adaptations |

---

## Key Design Decisions

- **Target:** `is_top10` (locked for Hito 1)
- **Split:** Train 2019–2021 / Calibration 2022 / Test 2023–2024
- **Baseline:** Calibrated Logistic Regression (grid_position + constructor_tier + n_stops)
- **Primary metric:** Brier Score
- **Docent floor:** Brier = 0.132, ROC-AUC = 0.892

---

## Dependencies

See `environment.yml` in the repo root. Key packages:
- `pandas >= 2.3`
- `scikit-learn >= 1.8`
- `matplotlib >= 3.10`
- `numpy >= 2.4`
