# Issue 1: Status — Survivorship Bias (DNF)

What:
Drivers with status “Retired,” “Accident,” or “Collision” have missing lap-time values and never finish in the Top 10.

Classification:
MAR (Missing At Random).

Impact:
If these records are removed, the model would become overly optimistic about the probability of finishing a race.

Decision:
Flag / Keep. All “Retired” drivers were labeled as IsTop10 = 0.

Justification:
Ignoring retirements would hide the reliability risk associated with certain teams and drivers.

# Issue 2: GridPosition — Domain Validity

What:
Existence of starting positions outside the 1–20 range (e.g., Pit Lane starts labeled as 0 or unusually high values).

Classification:
Outlier / Domain Validity.

Impact:
This can distort the Spearman correlation calculation and the average of the probability “ladder.”

Decision:
Standardize. All Pit Lane starts were mapped to position 20 to preserve the ordinal structure.

Justification:
Starting from the Pit Lane is functionally equivalent to starting last, but with an additional time penalty.

# Issue 3: Points / Position — Data Leakage

What:
The columns points scored and final position are present in the original dataset.

Classification:
Temporal Availability / Data Leakage.

Impact:
If these variables are used as predictors, the model would achieve artificially perfect accuracy, since they represent the outcome rather than the cause.

Decision:
Drop from features.

Justification:
Only variables known before the race start (pre-race) should be used as predictors.

# Issue 4: TeamName — Semantic Consistency (Rebranding)

What:
Teams that changed names between 2022 and 2024 (e.g., AlphaTauri → RB / Racing Bulls).

Classification:
Type / Semantic Consistency.

Impact:
The model could treat “AlphaTauri” and “RB” as different entities, fragmenting the team’s performance history.

Decision:
Keep & Document. For Lab 1, the original API names are preserved.

Justification:
This ensures full traceability with the data source; a name consolidation mapping is recommended for Lab 2.

# Issue 5: Time / Gap — Missing Values in Non-Finishers

What:
Drivers who do not finish the race lack a record of total race time or gap with the leader.

Classification:
MNAR (Missing Not At Random).

Impact:
This prevents using lap time as a continuous performance metric across the entire dataset.

Decision:
Impute with placeholder / Drop for specific metric.

Justification:
The value is missing because the event (finishing the race) did not occur. For Top-10 classification, it is sufficient to know that the driver did not finish.