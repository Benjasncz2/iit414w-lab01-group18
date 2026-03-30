# Model Exploration: F1 Race Outcome Prediction

## 1. Framing & Business Question
**Question:** "Based on our qualifying position and the historical performance of this circuit, what is the probability that we finish in the Top 10 (Points zone)?"
**Framing:** Binary Classification (Target: `scored_points`).
**Justification:** For a midfield team, the difference between P11 and P20 is financially identical ($0), but the jump from P11 to P10 is worth millions in constructor standings.

## 2. Baselines
* **Baseline 1 (Persistence):** Assume the driver finishes exactly where they started on the grid. 
* **Baseline 2 (Majority Class):** Always predict "No Points" (the most frequent outcome for the lower half of the grid).

## 3. Candidate Models
* **Logistic Regression:** To establish a linear relationship between grid position/track temp and the probability of points.
* **Random Forest Classifier:** To capture non-linear interactions (e.g., certain tracks like Monaco make grid position 10x more important than at Spa).

## 4. Evaluation Plan
* **Primary Metric:** Macro F1-Score (to ensure we aren't just getting high accuracy by guessing "No Points" every time).
* **Validation:** Temporal split. Training data: 2010–2023. Testing data: 2024 season. 
* **Justification for Split:** I chose 2010 as the start date because the current point system (25 for a win) was introduced then, ensuring the 'points' target is historically consistent for the model.
* **Seed:** RANDOM_SEED = 414