# Reproducibility Runbook - Lab 1

### (a) Header

* **Members:** Alonso Cárdenas, Benjamín Sánchez
* **Date:** March 15, 2026

### (b) System Info

* **Operating System:** Windows 10 / 11
* **Python Version:** 3.11.x
* **Conda/Pip Version:** Pip 24.0 / Conda 24.x

### (c) Setup Instructions

To recreate the exact environment used for this analysis, please follow these steps:

1. **Clone the repository and navigate to the directory:**
```bash
git clone [YOUR_REPOSITORY_URL]
cd [YOUR_FOLDER_NAME]

```


2. **If using Conda (Recommended):** Create the environment using the provided `environment.yml` file:
```bash
conda env create -f environment.yml
conda activate iit414w_lab1

```


3. **Launch Jupyter Lab:**
```bash
jupyter lab

```



*(Alternative using standard Python venv)*:

```bash
python -m venv f1_env
f1_env\Scripts\activate
pip install pandas seaborn matplotlib fastf1 requests scikit-learn

```

### (d) How to run

1. **Execution Order:** Run the main notebook from top to bottom (`Kernel -> Restart & Run All Cells`).
2. **Cache Configuration:** Ensure the cell that enables `fastf1.Cache` has write permissions in the local directory to store race telemetry.
3. **Dependencies:** Do not skip the initial library import cells, as they configure the `seaborn` styles and matplotlib parameters required to correctly render the KDE plots and histograms in Section 3.3.

### (e) Problems encountered

Here are two technical issues encountered during the EDA and their respective solutions:

1. **Data Type Mismatch during Merging:**
* **Problem:** When joining Jolpica API data with FastF1 results, the `DriverNumber` was loaded as a `float` in one set and as an `object` (string) in the other, causing the merge to return an empty DataFrame.
* **Solution:** I applied `.astype(int)` to both columns prior to the merge to ensure referential integrity and successful matching.


2. **Survivorship Bias in IsTop10 Construction:**
* **Problem:** Initially, drivers who did not finish the race appeared with null values in the final position field, which meant they were being excluded from both success and failure counts.
* **Solution:** I implemented a cleanup logic where any `Status` other than 'Finished' or '+n Laps' (indicating a DNF or DSQ) is automatically mapped to `IsTop10 = 0`, preventing survivorship bias and accurately reflecting race risk.



### (f) Expected outputs

Upon a successful run, you should observe the following:

1. **Class Balance Analysis (3.2):** A count plot showing an almost perfect 50/50 distribution (680 for class `1` vs. 679 for class `0`).
2. **Temporal Pattern Analysis (3.3):** A Kernel Density Estimate (KDE) plot comparing 2022 vs. 2024, showing that in 2024, the density of successful outcomes is more tightly concentrated within the Top 5 grid positions.
3. **Correlation Matrix (3.4):** A Heatmap where `GridPosition` displays a strong negative correlation (approx. $-0.82$) with the `IsTop10` target.
4. **1-3-1 Summary (3.8):** A final Markdown cell following the "1 Most Important Finding, 3 Key Insights, 1 Recommendation" structure.
