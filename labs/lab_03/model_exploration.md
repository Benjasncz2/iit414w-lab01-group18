# Model Exploration - Benjamin Sanchez - Alonso Cárdenas
## IIT414W - Lab 3 - Initial exploration - March 30, 2026

## 0. Framing Decision (initial - you can revise for Lab 3 final submission)
- **Business question:** "Given our qualifying position and track characteristics, what is the probability that we finish in the points (Top 10)?"
- **Target:** Binary Classification (Target: `is_points_finish`, where 1 = Position ≤ 10)
- **Metric:** Macro F1-Score
- **Why this framing:** Midfield teams care most about the binary threshold of scoring points vs. not scoring, as it dictates constructor championship payouts.
- **Rejected alternative:** Regression (predicting exact points), because the difference between P11 and P20 is zero points, and regression would struggle with the high volume of "0" values.

## 1. Models Trained
| Model | Key Hyperparameters | Features Used |
|---|---|---|
| Logistic Regression | C=1.0, random_state=414 | grid, alt, circuit_id |
| Random Forest | n_estimators=100, max_depth=5 | grid, alt, circuit_id, constructor_id |

## 2. Comparison Table (same metric, same validation)
| Model | Features | Validation | Train F1 | Test F1 | WHY this result |
|---|---|---|---|---|---|
| Baseline (Majority) | - | 2024 Season | 0.00 | 0.00 | Always predicts "No Points"; fails to identify any scoring drivers. |
| Logistic Regression | grid, alt, circuit_id | 2024 Season | 0.82 | 0.79 | Good at capturing the strong linear link between starting P1-P5 and scoring. |
| Random Forest | All listed above | 2024 Season | 0.88 | 0.81 | Better at identifying midfield "climbers" but showing slight overfitting signs. |

## 3. Best Model Justification (3+ sentences)
The Random Forest model is currently the best performer because it successfully captures non-linear interactions, such as how certain constructors (top-tier teams) can score points even when starting from the back of the grid. While the Logistic Regression is stable, it lacks the flexibility to account for team-specific performance variance. The small gap between the Train F1 (0.88) and Test F1 (0.81) suggests the model is generalizing well, though further tuning of `max_depth` could reduce the remaining noise.

## 4. One Honest Limitation
The model heavily relies on `grid` position as the primary feature, which makes it "blind" to race-day chaos like sudden rain or multi-car collisions. If a top-10 driver DNFs (Did Not Finish) early, the model still predicts they will score points based on their starting position, leading to false positives that the current feature set cannot resolve.