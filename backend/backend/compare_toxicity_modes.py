"""
Compare the three toxicity modes on a labeled CSV (columns: text,label; 1 = toxic, 0 = harmless):
  regex  = your rule-based detector
  model  = the trained toxic-bert ONNX classifier (threshold fixed at 0.5)
  hybrid = flag if EITHER regex OR model flags it
Usage (from backend\\backend):
    python compare_toxicity_modes.py toxicity_eval_yours.csv
    python compare_toxicity_modes.py toxicity_eval.csv
Read-only: it changes no rules and no files.
"""
import csv
import math
import os
import sys
import time

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

from app import toxicity

MODEL_DIR = os.path.join("models", "guardstack_toxicity_onnx")
THRESHOLD = 0.5  # fixed on purpose; do not tune on the evaluation set
path = sys.argv[1] if len(sys.argv) > 1 else "toxicity_eval.csv"

tok = AutoTokenizer.from_pretrained(MODEL_DIR)
sess = ort.InferenceSession(os.path.join(MODEL_DIR, "guardstack_toxicity.onnx"), providers=["CPUExecutionProvider"])
input_names = {i.name for i in sess.get_inputs()}


def model_score(text):
    enc = tok(text, return_tensors="np", truncation=True, max_length=128)
    feeds = {k: enc[k].astype(np.int64) for k in ("input_ids", "attention_mask") if k in input_names}
    logits = sess.run(None, feeds)[0][0]
    return float((1.0 / (1.0 + np.exp(-logits))).max())


with open(path, newline="", encoding="utf-8") as f:
    rows = [(r["text"], int(r["label"])) for r in csv.DictReader(f)]

t0 = time.time()
scores = [model_score(t) for t, _ in rows]
ms = (time.time() - t0) / len(rows) * 1000
if any(math.isnan(s) for s in scores):
    raise SystemExit("Model scores are NaN. Do NOT use this model file.")

regex_pred = [bool(toxicity.check_toxicity_regex(t)) for t, _ in rows]
model_pred = [s >= THRESHOLD for s in scores]
hybrid_pred = [a or b for a, b in zip(regex_pred, model_pred)]


def stats(preds):
    tp = sum(1 for (_, l), p in zip(rows, preds) if l == 1 and p)
    fp = sum(1 for (_, l), p in zip(rows, preds) if l == 0 and p)
    tn = sum(1 for (_, l), p in zip(rows, preds) if l == 0 and not p)
    fn = sum(1 for (_, l), p in zip(rows, preds) if l == 1 and not p)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    acc = (tp + tn) / len(rows)
    return tp, fp, tn, fn, prec, rec, f1, fpr, acc


print("=" * 96)
print(f"toxicity modes on {path} ({len(rows)} examples)")
print(f"{'mode':<8}{'TP':>4}{'FP':>4}{'TN':>4}{'FN':>4}{'prec':>8}{'recall':>8}{'F1':>8}{'FPR':>8}{'acc':>8}{'ms/msg':>9}")
print("-" * 96)
for name, preds, t in (("regex", regex_pred, 0.0), ("model", model_pred, ms), ("hybrid", hybrid_pred, ms)):
    tp, fp, tn, fn, p, r, f1, fpr, acc = stats(preds)
    print(f"{name:<8}{tp:>4}{fp:>4}{tn:>4}{fn:>4}{p:>8.2f}{r:>8.2f}{f1:>8.2f}{fpr:>8.2f}{acc:>8.2f}{t:>9.1f}")
print("=" * 96)

for name, preds in (("model", model_pred), ("hybrid", hybrid_pred)):
    print(f"[{name}] MISSED toxic messages:")
    for (t, l), p, s in zip(rows, preds, scores):
        if l == 1 and not p:
            print(f"   (score {s:.2f}) {t}")
    print(f"[{name}] FALSE ALARMS (harmless text flagged):")
    for (t, l), p, s in zip(rows, preds, scores):
        if l == 0 and p:
            print(f"   (score {s:.2f}) {t}")
