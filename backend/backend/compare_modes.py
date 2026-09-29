"""
Compare the three prompt-injection detector modes on the same hand-written test set:
  regex  = keyword rules only
  model  = trained classifier only
  hybrid = rules OR classifier

Run:  python compare_modes.py
"""

import time

from app import classifier, input_guard
from evaluate_detectors import DATASET, metrics

EXAMPLES = DATASET["prompt_injection"]["examples"]
MODES = ("regex", "model", "hybrid")


def run():
    available = classifier.is_available()
    print("Trained model available:", available)
    if not available:
        print("NOTE: model files not found or failed to load, so 'model' and 'hybrid'")
        print("      fall back to regex and will show the same numbers as regex.\n")
    else:
        classifier.injection_probability("warm up")  # first call is slow, keep it out of the timing

    results = {}
    print("=" * 96)
    print(f"{'mode':<10}{'TP':>4}{'FP':>4}{'TN':>4}{'FN':>4}{'prec':>8}{'recall':>8}{'F1':>8}{'FPR':>8}{'acc':>8}{'ms/msg':>9}")
    print("-" * 96)
    for mode in MODES:
        tp = fp = tn = fn = 0
        misses, alarms = [], []
        start = time.time()
        for text, label in EXAMPLES:
            pred = input_guard.check_input(text, mode=mode)[0]
            if label and pred:
                tp += 1
            elif label and not pred:
                fn += 1
                misses.append(text)
            elif not label and pred:
                fp += 1
                alarms.append(text)
            else:
                tn += 1
        ms = (time.time() - start) / len(EXAMPLES) * 1000
        p, r, f, fpr, acc = metrics(tp, fp, tn, fn)
        results[mode] = (misses, alarms)
        print(f"{mode:<10}{tp:>4}{fp:>4}{tn:>4}{fn:>4}{p:>8.2f}{r:>8.2f}{f:>8.2f}{fpr:>8.2f}{acc:>8.2f}{ms:>9.1f}")
    print("=" * 96)

    for mode in ("model", "hybrid"):
        misses, alarms = results[mode]
        print(f"\n[{mode}] MISSED attacks:")
        for t in misses:
            print("  ", t)
        print(f"[{mode}] FALSE ALARMS:")
        for t in alarms:
            print("  ", t)


if __name__ == "__main__":
    run()