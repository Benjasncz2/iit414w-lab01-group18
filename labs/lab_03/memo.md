# Technical Memo: Race Finishing Position Modeling

**To**: Head of Strategy
**From**: AI Workshop Team - Group 18
**Date**: April 20, 2026
**Subject**: Predictive Modeling for Top-10 Points Finishes

### Executive Summary
We have developed a system to predict whether our driver will finish in the Top 10 (and thus score points) based on their starting grid position and the specific track and car characteristics. Accurately predicting a points-finish is critical for our race strategy, as it informs whether we should take conservative risks to protect our position or aggressive strategies when starting from behind.

### Methodology and Results
We tested several predictive models utilizing historical race data from 2018 through 2023, and then simulated a "live test" on the entire 2024 season to evaluate real-world performance. 

Our models were evaluated on their "Macro F1-Score"—a reliability metric representing how accurately the model balances both correct predictions of scoring points and correct predictions of not scoring points. A score of 1.0 means perfect prediction. 

* **The "Always No" Baseline:** Assuming we never score points yielded a baseline score of `0.3329`.
* **The "Grid Heuristic" Baseline:** Simply assuming anyone starting 10th or better will score points yielded a score of `0.8351`. 
* **The Complex Modeler - Random Forest:** By allowing the system to understand complex interactions (like a specific car performing better at a specific track), we achieved a test score of `0.8161`. 
* **The Linear Modeler - Logistic Regression:** This achieved a score of `0.8183`. It was highly stable but lacked the ability to identify dynamic team strengths.

### Strategic Recommendation
Surprisingly, we recommend relying primarily on the **Grid Heuristic** (if a driver starts in the top 10, they finish in the top 10) as our primary baseline expectation for the time being. It beat our machine learning models by roughly 2% in historical accuracy during the 2024 season test. While the Random Forest model was slightly better at memorizing historical track-specific interactions, the pure causal dominance of starting position in modern Formula 1 overshadows complex statistical trends.

### Critical Limitations
This finding highlights a massive limitation in our current data approach. All these models rely heavily on historical trends and starting grid positions. Its largest limitation is that it is fundamentally "blind" to race-day dynamics—such as sudden rain, reliability failures, tire degradation, or multi-car collisions. If a driver starting in 1st place suffers an engine failure on lap 2, our model will still confidently predict them to finish in the points because the starting conditions were perfect. Therefore, the outputs must be used strictly for pre-race expectation setting, rather than dynamic in-race decision making.
