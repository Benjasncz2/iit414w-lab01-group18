# Lab 1 vs Lab 2 — Comparison Table
## Alonso Cárdenas & Benjamín Sánchez
| Model / Baseline | Accuracy | Precision | Recall | F1 | ROC-AUC |
|------------------------|----------|-----------|--------|-------|---------|
| Majority class (Lab 1) | 0.50     | 0.50      | 1.00     | 0.66     | 0.50    |
| Domain heuristic (Lab 1)| 0.85     | 0.85      | 0.85     | 0.85     | 0.85    |
| Lab 2 model (LogReg)   | 0.82     | 0.84      | 0.80     | 0.82     | 0.89    |

## Primary metric: Accuracy
**(Justified in Lab 1 due to the perfectly balanced target classes)**

## Interpretation
The Logistic Regression model (82%) successfully surpassed the Majority Class baseline (50%), but it **did not beat the Domain Heuristic** (85%). The heuristic was the hardest baseline to beat because it relies directly on `GridPosition`, which strongly encodes both car performance and driver pace on the specific weekend. The fact that the model fell slightly short suggests that simply aggregating lag positions and constructor tiers smooths out too much weekend-specific variance, leading to predictions that are too conservative. However, the Lab 2 model **did vastly outperform the heuristic in ROC-AUC** (0.89 vs 0.85), meaning its continuous probability estimates are much better calibrated, even if the default 0.5 cutoff yields fewer strictly correct classifications. To improve this, adjusting the classification threshold or adding a non-linear interaction feature (e.g. `GridPosition` interacting with `constructor_tier`) would likely bridge the accuracy gap.

## Error Analysis (Top 3 Failure Modes)
We exported the validation errors to investigate where the Logistic Regression model failed:

1. **False Positives (Predicted Top-10, Finished outside):**
   - **Drivers:** Lance Stroll (3 errors), Charles Leclerc (3), George Russell (2).
   - **Why:** These drivers belong to Top or Mid-tier teams (`constructor_tier = 1 or 2`) and usually have strong rolling historical averages. The model expected them to cruise into the Top-10 because they always do, failing to capture specific mechanical failures (DNFs), penalties, or awful qualifying sessions where the heuristic correctly predicted a non-Top-10 finish. 

2. **False Negatives (Predicted outside, Finished Top-10):**
   - **Drivers:** Yuki Tsunoda (6 errors), Nico Hulkenberg (5), Kevin Magnussen (2).
   - **Why:** These drivers belong to lower-tier teams (`constructor_tier = 3`) and often finish outside the points, resulting in poor rolling averages. When they manage to put together a brilliant qualifying session and sneak into P8 or P9, the heuristic correctly predicts success, but the Logistic Regression model drags their prediction down based purely on their historical 'lower-tier' status, missing their breakout performances.

3. **What to try next:**
   - Instead of replacing `GridPosition`, we need features that *explain* when `GridPosition` is wrong. For instance, an "overtaking capability" feature (average positions gained per race) or an explicit "reliability rate" (DNF %) to avoid False Positives on top-tier drivers. We should also reconsider treating `GridPosition` as a linear term and instead bin it, as discussed in Lab 1.
