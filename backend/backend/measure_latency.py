"""
Latency statistics for the guards, using the saved 25-question run.
Read-only. Run from backend\\backend (Ollama and the backend do NOT need to be running):
    python measure_latency.py
It times input_guard.check_input on the 25 questions and output_guard.check_output
on the ALLOWed replies, 10 repeats each, with one warm-up call first. The end-to-end
column comes from the 'seconds' column of real_replies_day5.csv (one run, n=25).
"""
import csv, statistics, time
from dotenv import load_dotenv
load_dotenv()
from app import input_guard, output_guard

REPEATS = 10
rows = list(csv.DictReader(open("real_replies_day5.csv", encoding="utf-8")))

def timed(fn, text):
    fn(text)  # warm-up (loads models on first use)
    out = []
    for _ in range(REPEATS):
        t = time.perf_counter(); fn(text); out.append((time.perf_counter() - t) * 1000)
    return out

in_samples, out_samples, in_med, out_med = [], [], [], []
for r in rows:
    s = timed(input_guard.check_input, r["question"])
    in_samples += s; in_med.append(statistics.median(s))
    if r["status"] == "ALLOW":
        s = timed(output_guard.check_output, r["reply"])
        out_samples += s; out_med.append(statistics.median(s))

total = [a + b for a, b in zip(in_med, [out_med[i] for i in range(len(out_med))])] if len(in_med) == len(out_med) else None
e2e = [float(r["seconds"]) * 1000 for r in rows]
guard_mean = statistics.mean(in_samples) + statistics.mean(out_samples)
gen = [x - guard_mean for x in e2e]

def line(name, xs):
    xs = sorted(xs); n = len(xs)
    p95 = xs[min(n - 1, round(0.95 * (n - 1)))]
    sd = statistics.stdev(xs) if n > 1 else 0.0
    print(f"{name:<40}{n:>5}{statistics.median(xs):>10.1f}{statistics.mean(xs):>10.1f}{sd:>9.1f}{p95:>10.1f}{xs[0]:>9.1f}{xs[-1]:>10.1f}")

print(f"{'(all times in ms)':<40}{'n':>5}{'median':>10}{'mean':>10}{'SD':>9}{'p95':>10}{'min':>9}{'max':>10}")
line("Input guard", in_samples)
line("Output guards (ALLOWed replies)", out_samples)
if total:
    line("Total guard overhead (paired items)", total)
line("End-to-end request (1 run)", e2e)
line("Model generation (end-to-end minus guards)", gen)
print("Modes in effect:", __import__("os").getenv("INJECTION_DETECTOR"), "/", __import__("os").getenv("TOXICITY_MODE"))
