# Framing Decision

**Business question**: "Given our qualifying position and track characteristics, what is the probability that we finish in the points (Top 10)?"

**Target variable**: Binary Classification (`is_points_finish`), where `1 = Position <= 10` and `0 = Position > 10` (or DNF).

**Metric**: Macro F1-Score. This metric is appropriate for this framing because points-scoring finishes are roughly balanced (10 positions vs 10 non-scoring positions), but we care equally about identifying when we actually will score points (the positive class) and when we will not (the negative class). Midfield teams need to accurately manage race expectations for both states. 

**Rejected alternative**: Regression (predicting exact points). We rejected this because the numerical difference between P11 and P20 is always zero points. A regression model would struggle with this zero-inflation and high volume of identical "0" target values, whereas classification focuses directly on the defining business threshold: whether a team is inside or outside the points.
