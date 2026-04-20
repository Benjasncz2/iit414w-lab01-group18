# Model Comparison Table

| Model | Features | Validation | Train F1 | Test F1 | Train-Test Gap | WHY this result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Baseline (Majority) | - | 2024 Season | 0.3333 | 0.3329 | 0.0005 | Always predicts "No Points"; fails to identify any scoring drivers resulting in poor Macro F1. |
| Baseline (Domain Heuristic) | `grid <= 10` | 2024 Season | 0.7363 | **0.8351** | -0.0987 | Strong heuristic since starting grid mostly determines final finish. It beat the ML models! |
| Logistic Regression | `grid, circuit_id, constructor_id` | 2024 Season | 0.7656 | 0.8183 | -0.0527 | Good at capturing the strong linear link between starting P1-P5 and scoring. |
| Ridge Classifier | `grid, circuit_id, constructor_id` | 2024 Season | 0.7651 | 0.8117 | -0.0466 | Similar to logistic regression but regularized; fails to capture team interactions. |
| Random Forest | `grid, circuit_id, constructor_id` | 2024 Season | **0.7759** | 0.8161 | -0.0402 | Better at identifying nonlinear team strengths on training data. Slightly overfits but ultimately loses to the pure causal dominance of grid position in the test set. |
