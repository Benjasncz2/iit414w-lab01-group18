# Lab 3: Model Comparison - F1 Predictions

This repository contains the deliverables for Lab 3, comparing predictive models for F1 finishing positions.

## Structure
- `data/`: Contains the `jolpica_results_2018_2024.csv` dataset.
- `lab3_model_comparison.ipynb`: The main notebook containing the modeling steps.
- `framing_decision.md`: Justification of business logic and model framing.
- `comparison_table.md`: Results matrix comparing Train and Test Macro F1.
- `memo.md`: Non-technical executive summary.
- `PROMPTS.md`: AI generation documentation and limitation analysis.

## Reproducibility Requirements
1. Ensure your Python environment has `pandas`, `numpy`, `scikit-learn`, and `tabulate` installed.
2. Open `lab3_model_comparison.ipynb` in your preferred Jupyter environment.
3. The Notebook expects `data/jolpica_results_2018_2024.csv` in the relative path.
4. From the top bar, click **Kernel -> Restart & Run All**.
5. Execution time is under 1 minute. We enforce `RANDOM_SEED = 414` across all estimators and data splits for strict reproducibility.

**Note:** The system uses a strict temporal split where $Season < 2024$ acts as the training data, and $Season = 2024$ acts as the validation set.
