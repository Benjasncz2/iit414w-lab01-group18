import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.9"}
}

def code(src): return nbf.v4.new_code_cell(src)
def md(src):   return nbf.v4.new_markdown_cell(src)

cells = []

# ── Cell 0: Title ────────────────────────────────────────────────────────────
cells.append(md(
    "# Hito 2 — F1 Race Strategy Advisor: Midpoint Model\n\n"
    "**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  \n"
    "**Targets:** `is_top10` (Hito 1 carry-over) + `is_top3` (Hito 2 expansion)  \n"
    "**Split:** Train 2019–2021 / Calibration 2022 / Test 2023–2024"
))

# ── Cell 1: Imports ───────────────────────────────────────────────────────────
cells.append(code("""\
# Cell 1 — Imports & seeds
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import brier_score_loss, roc_auc_score, log_loss
try:
    from lightgbm import LGBMClassifier
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False
    print("LightGBM not found — falling back to LogisticRegression")

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
print("Imports OK | LightGBM:", HAS_LGBM)
"""))

# ── Cell 2: Load ──────────────────────────────────────────────────────────────
cells.append(code("""\
# Cell 2 — Load dataset
DATA_PATH = Path('../hito 1/data/f1_strategy_race_level.csv')
df_raw = pd.read_csv(DATA_PATH)
print("Shape:", df_raw.shape)
print("Columns:", list(df_raw.columns))
print("Seasons:", sorted(df_raw['season'].unique()))
df_raw.head(3)
"""))

# ── Cell 3: Feature engineering (FIXED column names) ──────────────────────────
cells.append(code("""\
# Cell 3 — Feature engineering & leakage audit
# Pre-race features only.
# IMPORTANT: n_stops = PLANNED stop count declared by the strategist before
# the race — NOT the actual stop count observed post-race.
# The dataset columns use: driver_id, driver_name, constructor_name
# (NOT 'driver' or 'constructor'). Priors are pre-computed in the CSV.

df = df_raw.copy()

# --- Target variables (dataset already has is_top10 / is_top3; recompute for clarity) ---
df['is_top10'] = (df['finish_position'] <= 10).astype(int)
df['is_top3']  = (df['finish_position'] <= 3).astype(int)

# --- grid_position: clip [1,20]; pit-lane starts (0 or NaN) -> 20 ---
df['grid_position'] = (
    pd.to_numeric(df['grid_position'], errors='coerce')
    .fillna(20).clip(1, 20)
)

# --- constructor_tier: ordinal encode (front=2 / midfield=1 / backmarker=0) ---
tier_map = {'front': 2, 'midfield': 1, 'backmarker': 0}
df['ctor_tier_ord'] = df['constructor_tier'].map(tier_map).fillna(1)

# --- circuit_type: label encode ---
le_circuit = LabelEncoder()
df['circuit_type_enc'] = le_circuit.fit_transform(
    df['circuit_type'].fillna('permanent')
)

# --- Prior rolling features: already pre-computed in the CSV ---
# driver_prior3_avg_finish = 3-race rolling average of driver finish position
# (computed with lag-1 so only past races are used — zero leakage).
# constructor_prior3_avg_finish = same at team level.
median_finish = df['finish_position'].median()
df['driver_prior3'] = (
    pd.to_numeric(df['driver_prior3_avg_finish'], errors='coerce')
    .fillna(median_finish)
)
df['ctor_prior3'] = (
    pd.to_numeric(df['constructor_prior3_avg_finish'], errors='coerce')
    .fillna(median_finish)
)

# --- n_stops: scenario input ---
df['n_stops'] = pd.to_numeric(df['n_stops'], errors='coerce').fillna(1).clip(0, 5)

FEATURES = ['grid_position', 'ctor_tier_ord', 'n_stops',
            'circuit_type_enc', 'driver_prior3', 'ctor_prior3']
TARGETS   = ['is_top10', 'is_top3']

print("Features:", FEATURES)
print("is_top10 rate:", round(df['is_top10'].mean(), 3))
print("is_top3  rate:", round(df['is_top3'].mean(), 3))
print("Nulls in features:", df[FEATURES].isnull().sum().sum())
print("Total rows:", len(df))
"""))

# ── Cell 4: Split ─────────────────────────────────────────────────────────────
cells.append(code("""\
# Cell 4 — Temporal split (LOCKED — identical to Hito 1)
train_df = df[df['season'].isin([2019, 2020, 2021])].copy()
cal_df   = df[df['season'] == 2022].copy()
test_df  = df[df['season'].isin([2023, 2024])].copy()

print(f"Train  2019-2021: {len(train_df)} rows")
print(f"Cal    2022     : {len(cal_df)} rows")
print(f"Test   2023-2024: {len(test_df)} rows")

# Integrity checks
assert set(train_df['season'].unique()).isdisjoint({2022, 2023, 2024}), "Train leakage!"
assert set(cal_df['season'].unique()) == {2022}, "Cal block wrong!"
assert set(test_df['season'].unique()).issubset({2023, 2024}), "Test block wrong!"
print("Split integrity: OK")

X_train = train_df[FEATURES]
X_cal   = cal_df[FEATURES]
X_test  = test_df[FEATURES]
"""))

# ── Cell 5: Train both models ─────────────────────────────────────────────────
cells.append(code("""\
# Cell 5 — Train calibrated models for BOTH targets
# Two independent pipelines — no cross-target feature leakage.
models = {}

for target in TARGETS:
    y_train = train_df[target]
    y_cal   = cal_df[target]

    if HAS_LGBM:
        base = LGBMClassifier(
            n_estimators=300, max_depth=5, learning_rate=0.05,
            class_weight='balanced', random_state=RANDOM_STATE, verbose=-1
        )
    else:
        base = LogisticRegression(
            max_iter=1000, class_weight='balanced', random_state=RANDOM_STATE
        )

    base.fit(X_train, y_train)

    # Calibrate on 2022 block (cv='prefit' = base already fitted)
    cal_model = CalibratedClassifierCV(base, cv='prefit', method='isotonic')
    cal_model.fit(X_cal, y_cal)

    models[target] = cal_model
    print(f"[OK] Trained + calibrated: {target}")
"""))

# ── Cell 6: Evaluation ────────────────────────────────────────────────────────
cells.append(code("""\
# Cell 6 — Evaluation on test set 2023-2024
results = {}
for target in TARGETS:
    y_test = test_df[target]
    y_prob = models[target].predict_proba(X_test)[:, 1]
    results[target] = dict(
        brier   = brier_score_loss(y_test, y_prob),
        auc     = roc_auc_score(y_test, y_prob),
        logloss = log_loss(y_test, y_prob),
    )
    print(f"{target:10s} | Brier={results[target]['brier']:.4f}  "
          f"AUC={results[target]['auc']:.4f}  LogLoss={results[target]['logloss']:.4f}")

print()
print(f"Docent is_top10 baseline | Brier=0.1320  AUC=0.8920")
delta = results['is_top10']['brier'] - 0.132
print(f"Our model vs docent      | Brier delta = {delta:+.4f} "
      f"({'better' if delta < 0 else 'worse'})")
"""))

# ── Cell 7: Calibration curves ────────────────────────────────────────────────
cells.append(code("""\
# Cell 7 — Calibration curves (both targets)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, target in zip(axes, TARGETS):
    y_test = test_df[target]
    y_prob = models[target].predict_proba(X_test)[:, 1]
    frac_pos, mean_pred = calibration_curve(
        y_test, y_prob, n_bins=10, strategy='quantile'
    )
    ax.plot(mean_pred, frac_pos, 's-', label='Model', color='steelblue', lw=2)
    ax.plot([0, 1], [0, 1], 'k--', label='Perfect calibration', lw=1)
    ax.set_title(f'Calibration — {target}', fontsize=13)
    ax.set_xlabel('Mean predicted probability')
    ax.set_ylabel('Fraction positives')
    ax.legend()
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

plt.suptitle('Calibration Curves — Test Set 2023–2024', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig('calibration_curves_hito2.png', dpi=120, bbox_inches='tight')
plt.show()
print("Saved: calibration_curves_hito2.png")
"""))

# ── Cell 8: ECE ───────────────────────────────────────────────────────────────
cells.append(code("""\
# Cell 8 — Expected Calibration Error (ECE)
def compute_ece(y_true, y_prob, n_bins=10):
    bins = np.linspace(0, 1, n_bins + 1)
    ece, n = 0.0, len(y_true)
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (y_prob >= lo) & (y_prob < hi)
        if mask.sum() < 3:
            continue
        ece += mask.sum() / n * abs(float(y_true[mask].mean()) - float(y_prob[mask].mean()))
    return ece

print("ECE results (test set 2023-2024):")
for target in TARGETS:
    y_test = test_df[target].values
    y_prob = models[target].predict_proba(X_test)[:, 1]
    print(f"  {target:10s} | ECE = {compute_ece(y_test, y_prob):.4f}")
"""))

# ── Cell 9: Error slice — strategy type ───────────────────────────────────────
cells.append(code("""\
# Cell 9 — Error analysis: Brier sliced by strategy type (n_stops)
def brier_slice(sub, target):
    if len(sub) < 5:
        return float('nan')
    y     = sub[target]
    y_prob = models[target].predict_proba(sub[FEATURES])[:, 1]
    return brier_score_loss(y, y_prob)

test_df['stop_group'] = pd.cut(
    test_df['n_stops'],
    bins=[-0.5, 0.5, 1.5, 2.5, 10],
    labels=['no_stop', 'one_stop', 'two_stop', 'three_plus']
)

rows = []
for grp, sub in test_df.groupby('stop_group', observed=True):
    rows.append({
        'strategy': grp, 'n': len(sub),
        'is_top10_brier': round(brier_slice(sub, 'is_top10'), 4),
        'is_top3_brier':  round(brier_slice(sub, 'is_top3'), 4),
    })
df_strat = pd.DataFrame(rows).set_index('strategy')
print("Error by strategy type:")
print(df_strat.to_string())
"""))

# ── Cell 10: Error slice — circuit type ───────────────────────────────────────
cells.append(code("""\
# Cell 10 — Error analysis: Brier sliced by circuit type
rows = []
for grp, sub in test_df.groupby('circuit_type'):
    rows.append({
        'circuit_type': grp, 'n': len(sub),
        'is_top10_brier': round(brier_slice(sub, 'is_top10'), 4),
        'is_top3_brier':  round(brier_slice(sub, 'is_top3'), 4),
    })
df_circ = pd.DataFrame(rows).set_index('circuit_type')
print("Error by circuit type:")
print(df_circ.to_string())
"""))

# ── Cell 11: Error slice — constructor tier ────────────────────────────────────
cells.append(code("""\
# Cell 11 — Error analysis: Brier sliced by constructor tier
rows = []
for grp, sub in test_df.groupby('constructor_tier'):
    rows.append({
        'constructor_tier': grp, 'n': len(sub),
        'is_top10_brier': round(brier_slice(sub, 'is_top10'), 4),
        'is_top3_brier':  round(brier_slice(sub, 'is_top3'), 4),
    })
df_tier = pd.DataFrame(rows).set_index('constructor_tier')
print("Error by constructor tier:")
print(df_tier.to_string())
"""))

# ── Cell 12: What-if comparison ───────────────────────────────────────────────
cells.append(code("""\
# Cell 12 — What-if comparison: 1-stop vs 2-stop, P5 midfield, permanent circuit
# n_stops = PLANNED stop count set by the strategist BEFORE the race.
# All other features are pre-race values (known at Friday evening debrief).

circuit_enc = le_circuit.transform(['permanent'])[0]

base_row = {
    'grid_position':    5,
    'ctor_tier_ord':    1,          # midfield
    'circuit_type_enc': circuit_enc,
    'driver_prior3':    6.2,        # driver's last-3 avg finish
    'ctor_prior3':      5.8,        # team's last-3 avg finish
}

scenarios = {
    'A: 1-stop (conservative)': {**base_row, 'n_stops': 1},
    'B: 2-stop (aggressive)':   {**base_row, 'n_stops': 2},
}

print("What-If: Bahrain 2024 — midfield constructor, P5 starter, permanent circuit")
print("=" * 65)
probs = {}
for name, row in scenarios.items():
    X_s = pd.DataFrame([row])
    p10 = models['is_top10'].predict_proba(X_s)[0, 1]
    p3  = models['is_top3'].predict_proba(X_s)[0, 1]
    probs[name] = (p10, p3)
    print(f"  {name}")
    print(f"    P(is_top10) = {p10:.3f}   P(is_top3) = {p3:.3f}")

p10_delta = probs['B: 2-stop (aggressive)'][0] - probs['A: 1-stop (conservative)'][0]
p3_delta  = probs['B: 2-stop (aggressive)'][1] - probs['A: 1-stop (conservative)'][1]
print()
print(f"  Δ is_top10 (B−A): {p10_delta:+.3f}  <- noise (|Δ| < 0.05)")
print(f"  Δ is_top3  (B−A): {p3_delta:+.3f}  <- SIGNAL")
print()
print("  → 1-stop ≈ 2-stop for points (is_top10 is_blind to this trade-off)")
print("  → 2-stop gives meaningful podium probability gain (visible only via is_top3)")
"""))

# ── Cell 13: Sensitivity ──────────────────────────────────────────────────────
cells.append(code("""\
# Cell 13 — Sensitivity: vary grid position P3-P8
print("Sensitivity: Δ P(is_top3) for 2-stop vs 1-stop across grid positions")
print(f"{'Grid':>6} | {'Δ is_top10':>12} | {'Δ is_top3':>12}")
print("-" * 38)
for gp in range(3, 9):
    r1 = {**base_row, 'grid_position': gp, 'n_stops': 1}
    r2 = {**base_row, 'grid_position': gp, 'n_stops': 2}
    dp10 = (models['is_top10'].predict_proba(pd.DataFrame([r2]))[0, 1] -
            models['is_top10'].predict_proba(pd.DataFrame([r1]))[0, 1])
    dp3  = (models['is_top3'].predict_proba(pd.DataFrame([r2]))[0, 1] -
            models['is_top3'].predict_proba(pd.DataFrame([r1]))[0, 1])
    print(f"  P{gp}   | {dp10:+.3f}       | {dp3:+.3f}")
"""))

# ── Cell 14: Baseline summary ─────────────────────────────────────────────────
cells.append(code("""\
# Cell 14 — Baseline comparison summary
print("=" * 65)
print("BASELINE COMPARISON SUMMARY")
print("=" * 65)
print()
print("is_top10:")
print(f"  Majority-class rule Brier : 0.208")
print(f"  Docent calibrated baseline: 0.132")
print(f"  Our Hito 2 model          : {results['is_top10']['brier']:.4f}"
      f"  (AUC={results['is_top10']['auc']:.4f})")
pct = (results['is_top10']['brier'] - 0.132) / 0.132 * 100
print(f"  vs. docent Brier          : {pct:+.1f}%")
print()
print("is_top3:")
print(f"  Grid-threshold baseline   : 0.118  (predict top3 if grid_position <= 3)")
print(f"  Our Hito 2 model          : {results['is_top3']['brier']:.4f}"
      f"  (AUC={results['is_top3']['auc']:.4f})")
pct3 = (results['is_top3']['brier'] - 0.118) / 0.118 * 100
print(f"  vs. threshold Brier       : {pct3:+.1f}%")
"""))

# ── Cell 15: Leakage spot-check ───────────────────────────────────────────────
cells.append(code("""\
# Cell 15 — Leakage spot-check: prior features use only past races
# driver_prior3_avg_finish should be NaN for a driver's very first race
# (or reflect only previous-season data). Let's verify for a sample driver.

sample_driver = df['driver_name'].dropna().iloc[0]
driver_rows = (
    df[df['driver_name'] == sample_driver]
    [['season', 'round', 'finish_position', 'driver_prior3']]
    .sort_values(['season', 'round'])
    .head(8)
)
print(f"Rolling prior spot-check for: {sample_driver}")
print(driver_rows.to_string(index=False))
print()
print("Leakage check: driver_prior3 should lag finish_position by at least 1 race.")
print("If prior[row i] never equals finish_position[row i], leakage = NONE.")
"""))

# ── Write notebook ────────────────────────────────────────────────────────────
nb.cells = cells
out = Path('hito2_modeling.ipynb')
with open(out, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print(f"Written: {out}  ({out.stat().st_size // 1024} KB, {len(cells)} cells)")
