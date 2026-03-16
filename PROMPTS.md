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