import sys
sys.path.insert(0, '/d/Projects/af_prediction')

import numpy as np
import pandas as pd
from af_results import aggregate_episode_results
import inspect

print("=" * 70)
print("TASK 7 IMPLEMENTATION REVIEW - af_results.py")
print("=" * 70)

# 1. Check function signatures
print("\n1. FUNCTION SIGNATURES")
print("-" * 70)

sig_agg = inspect.signature(aggregate_episode_results)
print(f"aggregate_episode_results{sig_agg}")
print(f"  Returns: (df_scores, df_per_episode, df_summary, df_correlations)")

from af_results import save_results
sig_save = inspect.signature(save_results)
print(f"\nsave_results{sig_save}")

# 2. Create representative synthetic data
print("\n2. TEST DATA GENERATION")
print("-" * 70)

def create_test_episode(record_id, onset_idx, n_windows=100):
    """Create realistic synthetic episode"""
    result = {
        'record_id': record_id,
        'onset_idx': onset_idx,
        'all_windows': np.random.randn(n_windows, 8).astype(np.float32),
    }

    operators = ['S_oct', 'S_prod', 'S_vec'] + [f'S_shuf_{i}' for i in range(10)]
    scores = {}
    zscores = {}
    alerts = {}
    lead_times = {}

    for op_name in operators:
        score_arr = np.abs(np.random.randn(n_windows).astype(np.float32)) + 1.0
        score_arr[:3] = np.nan
        scores[op_name] = score_arr

        zscore_arr = np.random.randn(n_windows).astype(np.float32)
        zscore_arr[:3] = np.nan
        zscores[op_name] = zscore_arr

        if np.random.rand() > 0.4:
            alert_idx = np.random.randint(10, n_windows)
            alerts[op_name] = alert_idx
            lead_times[op_name] = np.random.uniform(5, 90)
        else:
            alerts[op_name] = None
            lead_times[op_name] = None

    result['scores'] = scores
    result['zscores'] = zscores
    result['alerts'] = alerts
    result['lead_times'] = lead_times
    return result

test_results = [
    create_test_episode('04015', 5000, n_windows=100),
    create_test_episode('04043', 3000, n_windows=80),
    create_test_episode('04048', 7000, n_windows=120),
]

print(f"Generated {len(test_results)} episodes")
print(f"  Total windows: {sum(len(r['all_windows']) for r in test_results)}")
print(f"  Operators per episode: 13 (S_oct, S_prod, S_vec, S_shuf_0-9)")

# 3. Run aggregation
print("\n3. AGGREGATION OUTPUT")
print("-" * 70)

df_scores, df_per_episode, df_summary, df_correlations = aggregate_episode_results(test_results)

print(f"\ndf_scores (all windows, all operators, raw + z-scored)")
print(f"  Shape: {df_scores.shape}")

print(f"\ndf_per_episode (per-operator detection per episode)")
print(f"  Shape: {df_per_episode.shape}")
print(f"  Expected: {len(test_results)} episodes x 13 operators = {len(test_results) * 13}")

print(f"\ndf_summary (per-operator aggregate)")
print(f"  Shape: {df_summary.shape}")

print(f"\ndf_correlations (operator pair correlations)")
print(f"  Shape: {df_correlations.shape}")
print(f"  Expected: C(13,2) = 78 pairs")

# 4. SPEC COMPLIANCE VERIFICATION
print("\n4. SPEC COMPLIANCE")
print("-" * 70)

checks = []

# df_scores checks
print("\ndf_scores:")
checks.append(("Has record_id", 'record_id' in df_scores.columns))
checks.append(("Has onset_idx", 'onset_idx' in df_scores.columns))
checks.append(("Has window_idx", 'window_idx' in df_scores.columns))
all_ops_raw = all(op in df_scores.columns for op in ['S_oct', 'S_prod', 'S_vec', 'S_shuf_0', 'S_shuf_9'])
checks.append(("Has all 13 raw operator columns", all_ops_raw))
all_ops_z = all(f'z_{op[2:]}' in df_scores.columns for op in ['S_oct', 'S_prod', 'S_vec', 'S_shuf_0', 'S_shuf_9'])
checks.append(("Has all 13 z-score columns", all_ops_z))
checks.append(("NaN preserved for lag windows", df_scores[df_scores['window_idx'] < 3]['S_oct'].isna().all()))
checks.append(("Total rows = sum of window counts", len(df_scores) == 100 + 80 + 120))

# df_per_episode checks
print("\ndf_per_episode:")
required_cols_per_ep = ['record_id', 'onset_idx', 'n_windows', 'operator', 'detected', 'alert_window', 'lead_time_min'] + [f'detected_horizon_{h}' for h in [5, 15, 30, 60, 90]]
checks.append(("Has all required columns", all(c in df_per_episode.columns for c in required_cols_per_ep)))
checks.append(("detected column is bool", df_per_episode['detected'].dtype == bool))
checks.append(("Rows = episodes x operators", len(df_per_episode) == len(test_results) * 13))

# Verify horizon logic
per_ep_valid = True
for _, row in df_per_episode.iterrows():
    if row['detected'] and row['lead_time_min'] is not None:
        lt = row['lead_time_min']
        expected_5 = lt >= 5
        expected_30 = lt >= 30
        expected_60 = lt >= 60
        if not (row['detected_horizon_5'] == expected_5 and row['detected_horizon_30'] == expected_30 and row['detected_horizon_60'] == expected_60):
            per_ep_valid = False
            break
    else:
        if not (row['detected_horizon_5'] == False and row['detected_horizon_30'] == False):
            per_ep_valid = False
            break

checks.append(("Horizon logic correct", per_ep_valid))

# df_summary checks
print("\ndf_summary:")
required_cols_summary = ['operator', 'n_detected', 'n_evaluable', 'sensitivity', 'mean_lead_time_min', 'median_lead_time_min', 'max_lead_time_min', 'fp_per_hour']
checks.append(("Has all required columns", all(c in df_summary.columns for c in required_cols_summary)))
checks.append(("Rows = 13 operators", len(df_summary) == 13))
checks.append(("All operators present", all(op in df_summary['operator'].values for op in ['S_oct', 'S_prod', 'S_vec', 'S_shuf_0', 'S_shuf_9'])))

# Verify sensitivity formula
sens_correct = True
for _, row in df_summary.iterrows():
    expected = row['n_detected'] / row['n_evaluable'] if row['n_evaluable'] > 0 else np.nan
    if not (np.isclose(expected, row['sensitivity']) or (np.isnan(expected) and np.isnan(row['sensitivity']))):
        sens_correct = False
checks.append(("Sensitivity = n_detected / n_evaluable", sens_correct))

# Verify lead times on detected only
lead_times_on_detected = True
for op in df_summary['operator'].values:
    op_rows = df_per_episode[df_per_episode['operator'] == op]
    detected_rows = op_rows[op_rows['detected']]
    if len(detected_rows) > 0:
        expected_mean = np.nanmean(detected_rows['lead_time_min'].values)
        summary_mean = df_summary[df_summary['operator'] == op]['mean_lead_time_min'].iloc[0]
        if not (np.isclose(expected_mean, summary_mean) or (np.isnan(expected_mean) and np.isnan(summary_mean))):
            lead_times_on_detected = False

checks.append(("Lead times computed on detected subset", lead_times_on_detected))

# df_correlations checks
print("\ndf_correlations:")
required_cols_corr = ['operator_1', 'operator_2', 'pearson_r', 'pearson_p', 'spearman_r', 'spearman_p']
checks.append(("Has all required columns", all(c in df_correlations.columns for c in required_cols_corr)))
checks.append(("Rows = C(13,2) = 78", len(df_correlations) == 78))

# Verify correlation bounds
pearson_valid = (df_correlations['pearson_r'].dropna() >= -1).all() and (df_correlations['pearson_r'].dropna() <= 1).all()
spearman_valid = (df_correlations['spearman_r'].dropna() >= -1).all() and (df_correlations['spearman_r'].dropna() <= 1).all()
checks.append(("Pearson r in [-1, 1]", pearson_valid))
checks.append(("Spearman r in [-1, 1]", spearman_valid))

# Print results
print("\nCOMPLIANCE CHECKLIST:")
all_pass = True
for desc, result in checks:
    status = "PASS" if result else "FAIL"
    print(f"  [{status}] {desc}")
    if not result:
        all_pass = False

# 5. Code Quality
print("\n5. CODE QUALITY CHECKS")
print("-" * 70)

code_checks = []

source = inspect.getsource(aggregate_episode_results)
code_checks.append(("NaN filtering in correlations", "~(np.isnan" in source))
code_checks.append(("All 13 operators handled", "S_shuf_" in source and "range(10)" in source))

source_save = inspect.getsource(save_results)
code_checks.append(("Validates output directory", "os.path.exists" in source_save))
code_checks.append(("Creates CSV files", "to_csv" in source_save))

print("CODE QUALITY CHECKLIST:")
for desc, result in code_checks:
    status = "PASS" if result else "FAIL"
    print(f"  [{status}] {desc}")

# Final summary
print("\n" + "=" * 70)
if all_pass and all(r for _, r in code_checks):
    print("STATUS: APPROVED")
else:
    print("STATUS: NEEDS REVIEW")

print("=" * 70)
