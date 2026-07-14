"""Diagnostic: distribution of shuffled-label AUC across seeds.
Real leakage -> consistently > 0.5. Test-statistic noise -> centered on 0.5, both sides."""
import sys
sys.path.insert(0, r"D:\Projects\pinch_me_50k")
import numpy as np
from src.config import CONFIG
from src.generate_data import generate
from src.features import build_features, MODEL_FEATURES
from src.evaluate import leakage_test

df = build_features(generate(CONFIG))
cut = df["due_date"].quantile(1 - CONFIG["test_fraction_by_time"])
train, test = df[df["due_date"] <= cut], df[df["due_date"] > cut]
Xtr, ytr = train[MODEL_FEATURES].values, train["label"].values
Xte, yte = test[MODEL_FEATURES].values, test["label"].values

aucs = [leakage_test(Xtr, ytr, Xte, yte, seed=s) for s in range(12)]
print("per-seed shuffled-label AUCs:", [round(a, 3) for a in aucs])
print(f"mean={np.mean(aucs):.3f}  min={np.min(aucs):.3f}  max={np.max(aucs):.3f}")
print("n above 0.5:", sum(a > 0.5 for a in aucs), "| n below 0.5:", sum(a < 0.5 for a in aucs))

# direct construction check: does any model feature correlate suspiciously with the CURRENT label
# beyond what history-based features legitimately should?
print("\nfeature vs current-label correlation (train):")
for f in MODEL_FEATURES:
    c = np.corrcoef(train[f].values.astype(float), ytr)[0, 1]
    print(f"  {f:22s} {c:+.3f}")
