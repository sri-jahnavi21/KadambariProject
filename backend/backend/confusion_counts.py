"""
Recomputes TP / FN / FP / TN, precision, recall and FPR from the saved result CSVs.
Read-only: it changes nothing. Run from backend\\backend:   python confusion_counts.py

It reads any CSV in the current folder that has the columns:
  should_catch  and  caught            (e.g. detector_results_day4.csv)
  should_catch  and  caught_v1 / caught_v2   (e.g. test_pii_day3.csv, heldout_*.csv)
A 'detector' column, if present, splits the file into one row per detector.
"""
import csv, glob, collections

def truth(v):
    return str(v).strip().lower() in ("true", "1", "yes")

def counts(pairs):
    tp = sum(1 for y, c in pairs if y and c)
    fn = sum(1 for y, c in pairs if y and not c)
    fp = sum(1 for y, c in pairs if not y and c)
    tn = sum(1 for y, c in pairs if not y and not c)
    return tp, fn, fp, tn

print("| File | Detector | Version | TP | FN | FP | TN | Precision | Recall | FPR |")
print("|---|---|---|---|---|---|---|---|---|---|")
for path in sorted(glob.glob("*.csv")):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows or "should_catch" not in rows[0]:
        continue
    cols = [c for c in ("caught", "caught_v1", "caught_v2") if c in rows[0]]
    if not cols:
        continue
    groups = collections.defaultdict(list)
    for r in rows:
        groups[r.get("detector", "-")].append(r)
    for det, rs in groups.items():
        for col in cols:
            tp, fn, fp, tn = counts([(truth(r["should_catch"]), truth(r[col])) for r in rs])
            prec = tp / (tp + fp) if tp + fp else float("nan")
            rec = tp / (tp + fn) if tp + fn else float("nan")
            fpr = fp / (fp + tn) if fp + tn else float("nan")
            ver = {"caught": "-", "caught_v1": "v1", "caught_v2": "v2"}[col]
            print(f"| {path} | {det} | {ver} | {tp} | {fn} | {fp} | {tn} | {prec:.2f} | {rec:.2f} | {fpr:.2f} |")
