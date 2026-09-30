"""
Run the rule-based toxicity detector on a labeled CSV (columns: text,label).
Usage (from backend\\backend):
    python compare_toxicity_regex.py toxicity_eval_yours.csv
    python compare_toxicity_regex.py toxicity_eval.csv
Read-only: it changes no rules and no files.
"""
import csv
import sys

from app import toxicity

path = sys.argv[1] if len(sys.argv) > 1 else "toxicity_eval.csv"

with open(path, newline="", encoding="utf-8") as f:
    rows = [(r["text"], int(r["label"])) for r in csv.DictReader(f)]

tp = fp = tn = fn = 0
missed, false_alarms = [], []
for text, label in rows:
    predicted = bool(toxicity.check_toxicity_regex(text))
    if label and predicted:
        tp += 1
    elif label and not predicted:
        fn += 1
        missed.append(text)
    elif not label and predicted:
        fp += 1
        false_alarms.append(text)
    else:
        tn += 1

prec = tp / (tp + fp) if tp + fp else 0.0
rec = tp / (tp + fn) if tp + fn else 0.0
f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
fpr = fp / (fp + tn) if fp + tn else 0.0
acc = (tp + tn) / len(rows)

print("=" * 96)
print(f"regex toxicity on {path} ({len(rows)} examples)")
print(f"TP={tp} FP={fp} TN={tn} FN={fn}  prec={prec:.2f} recall={rec:.2f} F1={f1:.2f} FPR={fpr:.2f} acc={acc:.2f}")
print("=" * 96)
print("MISSED toxic messages:")
for t in missed:
    print("  ", t)
print("FALSE ALARMS (harmless text flagged):")
for t in false_alarms:
    print("  ", t)
