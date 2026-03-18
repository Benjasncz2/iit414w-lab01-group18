# Baseline Report — Lab 1 Group

## 1. Prediction target
Predict whether a Formula 1 driver finishes in the Top-10 (points-scoring positions 1–10) based on their qualifying grid position, evaluated on 2024 season validation data (Rounds 1–12).

## 2. Majority-class baseline
- Metric: Accuracy
- Value: 50.70%
- Code: `DummyClassifier(strategy='most_frequent', random_state=414)`

The majority-class baseline predicts "Top-10" for every driver (always predicts the majority class from training data, which is 50.7% Top-10). This achieves 50.7% accuracy by doing nothing—equivalent to a coin flip. It demonstrates that any real model must beat this trivial threshold.

## 3. Domain heuristic baseline
- Rule: If GridPosition ≤ 10, predict Top-10 finish. Otherwise, predict Not-Top-10.
- Metric (same as above): Accuracy = 80.69%
- Code cell:
```python
val_df['baseline_prediction'] = (val_df['GridPosition'] <= 10).astype(int)
```

Achieves 80.69% accuracy, a +30 percentage point improvement over majority-class. This rule encodes domain knowledge: starting in the top half of the grid (positions 1–10) strongly predicts finishing in the Top-10. The +30pp improvement proves grid position adds genuine discriminative value. However, the ~20% error rate reveals grid alone cannot capture race-day chaos like mechanical reliability failures and safety cars.

## 4. Metric choice + justification

I chose **Accuracy** as my primary metric because my dataset has a class balance of approximately 50/50 (perfectly balanced). With balanced classes, accuracy is a valid and interpretable metric—it directly tells us the fraction of all predictions that are correct. The majority-class baseline achieves 50.7% accuracy by always predicting "Top-10," which is essentially a coin flip. Our heuristic beats this by 30 percentage points, proving that grid position is a real, exploitable signal. A false positive means predicting Top-10 for a driver who retires or loses positions, and a false negative means missing a driver who overcomes a bad grid. Both errors matter equally in this balanced context, so accuracy fairly represents overall model performance.

## 5. Leakage guard item

(a) **Item checked:** #3 — "No feature is a direct encoding of the target"

(b) **What I found:** The FastF1 dataset includes post-race columns (`Position`, `Points`, `Status`) that are determined only AFTER the race ends.

(c) **Fix applied:** ✅ **YES, required.** I excluded post-race columns from predictors and reserved them only for target label creation. The baseline uses **only GridPosition** (pre-race, qualifying-determined), with zero leakage risk.

## 6. Baseline comparison & interpretation

(a) The **domain heuristic (80.69% accuracy) is harder to beat than majority-class (50.7% accuracy)**. The gap of +30 percentage points proves that grid position adds genuine discriminative value—substantial and real, not a statistical artifact. However, the remaining ~20% error rate shows this is fundamentally difficult. These errors are driven by factors grid alone cannot capture: mechanical reliability, pit strategy mistakes, safety cars, and penalties. Any ML model must beat 80.69% to justify adding more features or complexity.

(b) If a trained model scores **below 80.69%**, I would conclude it has **failed to learn anything beyond our simple domain heuristic**. I would then: (1) check feature engineering—did I add new pre-race features the heuristic doesn't use?; (2) audit the temporal split for leakage; (3) try simpler models first (Logistic Regression) to isolate the problem; (4) re-examine the target variable definition; (5) accept if needed that grid position is the dominant predictor. A model underperforming its baseline is diagnostic feedback, not a bug.
```

---