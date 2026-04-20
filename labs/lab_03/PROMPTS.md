# AI Documentation and Prompts Log

**Tool Used:** Gemini / ChatGPT 

## Entry 1: Temporal Splitting and API Hallucinations
- **My Prompt:** "I have a pandas dataframe with F1 results from 2018 to 2024. I need to do a temporal train/test split where the train set is 2018-2023 and the test set is 2024. How do I do this with scikit-learn?"
- **AI Response:** The AI suggested using `sklearn.model_selection.TimeSeriesSplit` or `train_test_split(X, y, test_size=0.15, shuffle=False)`.
- **AI Failure & Resolution (Critical Distance):** This was a poor suggestion. `TimeSeriesSplit` creates multiple rolling-origin splits which is not what the assignment asks for (we just need one fixed temporal holdout). On the other hand, `train_test_split` with `shuffle=False` blindly splits by index, which is dangerous since our dataset has multiple rows per race and might not be perfectly sorted by date. I explicitly rejected the AI's `scikit-learn` approach and wrote a manual boolean mask instead to guarantee accuracy: `train_df = df[df['season'] < 2024]` and `test_df = df[df['season'] == 2024]`. (See Cell 5 in the notebook).

## Entry 2: Imputing Values and Domain Logic
- **My Prompt:** "I'm using 'grid' as a feature for my Random Forest. But I have some missing values in the grid column. How should I handle them in my pipeline?"
- **AI Response:** The AI proposed adding a `SimpleImputer(strategy='mean')` into my `ColumnTransformer`.
- **Traceability & Critical Distance:** I quickly realized that imputing the mean grid position (which could result in a float like `10.4`) doesn't make logical sense in F1. More importantly, missing grid data usually implies a pit-lane start, a crash in Q1, or a penalty, which is functionally equivalent to starting last. I overrode the AI's idea and applied domain reasoning: `pd.to_numeric(df['grid'], errors='coerce').fillna(20)` directly on my dataframe to assign them to P20. (Implemented in Cell 6).

## Entry 3: Operational Friction (The Markdown Table Error)
- **My Prompt:** "I am trying to export my evaluation dataframe `results_df` to a markdown format at the end of my notebook using `print(results_df.to_markdown(index=False))` but I am getting this exact error: `ImportError: Missing optional dependency 'tabulate'. Use pip or conda to install tabulate.`"
- **AI Response & Resolution:** The AI pointed out that `pandas` dynamic functions sometimes require external packages that aren't included in the base environment. It advised me to run `pip install tabulate` in the terminal. I ran it, re-executed the cell without needing to restart the kernel, and the exact comparison table was successfully printed with the Train F1 vs Test F1 evaluation. (Outputs visible in Cell 13).
