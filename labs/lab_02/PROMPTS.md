# Entry 1 — Feature Engineering syntax (Lag and Rolling Aggregates)

**Context:**
I needed to correctly construct the lag feature (driver position in the previous race) and the rolling aggregate over the last 3 races, ensuring no future information was leaked, as required in the strict Leakage guard rules.

**Prompt(s):**
"How do I use pandas to create a lag feature for a driver's position in the previous race, and a rolling average of their position in the last 3 races? The dataset has a `DriverNumber` column and a `Position` column. It is important that I do not leak the current race's position, so the rolling average must strictly rely on past races."

**Output:**
The AI provided the exact syntax using `groupby('DriverNumber')` followed by `.shift(1)` for the lag feature, and `.transform(lambda x: x.rolling(3, min_periods=1).mean().shift(1))` for the rolling average.

**Validation:**
I tested the provided code on the dataset, specifically filtering for one driver (`DriverNumber == 1`, Max Verstappen), and observed that on race N, the rolling average effectively computed the mean of races N-3, N-2, N-1.

**Adaptations:**
Since `shift(1)` produces `NaN` for the very first race of every driver, I chained an explicit `.fillna(20)` to default the missing historical values to position 20, as requested by the baseline F1 domains (if there's no data, assume worst case).

**Final Decision:**
Used. The `.shift(1)` functionality correctly protected against data leakage.

---

# Entry 2 — Logistics Regression Metrics extraction

**Context:**
For the comparison table, I required the extraction of Accuracy, Precision, Recall, F1, and ROC-AUC scores from the simple Logistic Regression model.

**Prompt(s):**
"What is the simplest way to get Accuracy, Precision, Recall, F1, and ROC-AUC from a Logistic Regression model using sklearn? I have my true labels in `y_val` and my predictions in `y_pred`."

**Output:**
The AI suggested importing `accuracy_score, precision_score, recall_score, f1_score, roc_auc_score` from `sklearn.metrics`. Furthermore, it correctly specified that ROC-AUC requires `y_prob = model.predict_proba(X_val)[:, 1]`.

**Validation:**
I evaluated the resulting metrics on the validation dataset (2024 Rounds 1-12) and correctly reproduced the performance baseline comparisons. 

**Adaptations:**
I applied the provided formulas to all baselines (Majority Class, Domain Heuristic, and my trained model) inside a single coherent script.

**Final Decision:**
Used. It was the fastest way to obtain the precise 5 metrics requested by the Lab 2 rubric.
