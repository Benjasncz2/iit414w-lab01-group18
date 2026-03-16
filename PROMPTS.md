# Entry 1 — Classification of Missing Values (MCAR/MAR/MNAR)

Context:
I was conducting the data quality audit (Requirement 3.7) and needed to technically classify why data was missing in specific columns such as GridPosition and Status.

Prompt(s):
"Help me classify the missing values in my F1 dataset for the columns GridPosition, Position, and Time using the categories MCAR, MAR, and MNAR. Explain the logic behind each one."

Output:
The AI suggested that GridPosition was MCAR (Missing Completely at Random), Position was MAR (Missing at Random) because it depends on disqualification status, and Time was MNAR (Missing Not at Random) since the value is missing when the driver does not finish the race.

Validation:
I consulted the FastF1 API documentation and verified in my own DataFrame that missing values in Position corresponded exactly with records where Status was “Retired” or “Disqualified.”

Adaptations:
I refined the AI’s explanation to explicitly mention that in Formula 1, a missing lap time is not a system error, but rather a direct consequence of a DNF (Did Not Finish).

Final Decision:
Used — It provided the theoretical framework required for the professional data audit in section 3.7.
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Entry 2 — Temporal Split vs Random Split Design

Context:
I needed to define the data splitting strategy (Train/Validation/Test) for Requirement 3.6, avoiding the common mistake of using a random split, which would cause data leakage.

Prompt(s):
"Why is it better to use a temporal split instead of a random train_test_split from sklearn when predicting F1 results? How should I split the 2022, 2023, and 2024 seasons?"

Output:
The model explained the concept of temporal data leakage (predicting the past using future information) and suggested training with 2022–2023 data and validating/testing on 2024.

Validation:
I reviewed the EDA charts from Question 4, where I observed that teams like McLaren drastically changed their performance during mid-2024. This confirmed that a random split would mix very different “versions” of the same team, invalidating the model.

Adaptations:
I decided to be stricter than the AI’s initial suggestion by splitting the 2024 season into two parts:

Rounds 1–12 for validation

Rounds 13–24 for testing

This ensures that the model is evaluated using the most current competitive state of the grid.

Final Decision:
Used — It was fundamental for technically justifying the experimental design and avoiding bias in the predictive model.
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Entry 3 — Conceptualizing the Accuracy Reflection and Naive Baseline

**Context:** I needed to write the reflection on why 85% accuracy is good and what it might be hiding, specifically regarding class balance and the "majority class" trap mentioned in the rubric.

**Prompt(s):** "I am building a rule-based baseline to predict if an F1 driver finishes in the Top 10. My dataset is perfectly balanced (50/50). My rule 'If GridPosition <= 10, predict Top 10' got 85.7% accuracy. Help me reflect on what this accuracy hides and why the majority class naive baseline doesn't undermine this score."

**Output:** The AI explained the concepts of False Positives (e.g., driver crashes) and False Negatives (e.g., overtakes/strategy). It also clarified that a naive majority-class model would only score 50% here, proving the 85.7% is a genuine signal, not an artifact of imbalance.

**Validation:** I cross-referenced the AI's explanation of False Positives/Negatives with F1 domain knowledge (retirements, pit strategy) and verified the math that a 50/50 target distribution means a constant prediction yields 50% accuracy.

**Adaptations:** I summarized the AI's breakdown into my own bullet points in `baseline.ipynb` and explicitly linked it to F1 scenarios (e.g., Ferrari brake failures).

**Final Decision:** Used. The conceptual breakdown helped structure the reflection accurately for the Lab 2 acceptance threshold.
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Entry 4 — Learning Scikit-Learn Stretch Metrics

**Context:** I wanted to attempt the stretch goals (Section 4.6 and 4.7) to compute Precision, Recall, F1-score, and fit a simple Logistic Regression model, but we haven't formally learned `sklearn` yet.

**Prompt(s):** "How do I calculate precision, recall, and F1-score from a confusion matrix in Python? Also, show me the basic syntax to fit a DummyClassifier and LogisticRegression from sklearn using a single feature (GridPosition) to predict a binary target (IsTop10)."

**Output:** The AI provided the mathematical formulas using True Positives/False Positives and generated boilerplate code for `sklearn.dummy.DummyClassifier` and `sklearn.linear_model.LogisticRegression`, including the `fit()` and `predict()` methods.

**Validation:** I checked the mathematical formulas against standard statistical definitions. I ran the provided `sklearn` code in my notebook on the validation set to ensure it executed without errors and compared the Logistic Regression outputs to my manual heuristic outputs.

**Adaptations:** I integrated the `sklearn` imports into my notebook environment, mapped the AI's generic variable names (`X_train`, `y_train`) to my specific validation set columns (`X_val`, `y_val`), and added a zero_division=0 parameter to avoid warnings.

**Final Decision:** Used. The code provided the exact framework needed to complete the stretch goals and prove that the heuristic baseline matches a basic ML model.