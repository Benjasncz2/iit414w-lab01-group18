# Reproducibility Runbook - Lab 2

## 1. Setup Instructions
To recreate the environment for this analysis:

1. Use standard Python or your existing `iit414w` conda environment.
2. If using standard Python, create and activate a virtual environment:
   ```bash
   python -m venv f1_env
   f1_env\Scripts\activate
   ```
3. Install the required libraries:
   ```bash
   pip install pandas scikit-learn fastf1 matplotlib seaborn jupyterlab
   ```

## 2. How to run
1. Open the Jupyter Lab interface or simply launch the notebook in your IDE (VSCode, PyCharm).
2. Navigate to `labs/lab_02/`.
3. Open `lab02_feature_engineering.ipynb`.
4. From the top menu, select `Kernel` -> `Restart & Run All`.
5. The dataset will be downloaded (or loaded from the `f1_cache` folder if it exists) and the metrics will be printed at the bottom of the notebook alongside a confusion matrix for the error analysis.

## 3. Environment Specs
- **Python**: 3.11+
- **Key packages**: `pandas`, `scikit-learn`, `fastf1`
- **Seed used**: `RANDOM_SEED = 414` (Set uniformly across operations)
