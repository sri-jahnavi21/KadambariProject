# GuardStack for Commerce

**A lightweight, locally run security guardrail for an LLM-powered e-commerce shopping assistant.**

GuardStack sits around a local chatbot and checks what goes in and what comes out. It is demonstrated on **Kadambari**, a mock store selling hand-painted Kalamkari sneakers.

> Capstone project by Muppavarapu Sri Jahnavi (ICFAI Tech, ICFAI University). Full write-up: [REPORT.md](REPORT.md).

**Live storefront:** https://kadambari-project-cyan.vercel.app/
The chat assistant answers only while the author's laptop is running the backend and Ollama. When it is off, the page still loads and the assistant shows a fallback message.

---

## Results at a glance

All test sets are small and hand-written (16 to 60 rows), so these numbers are indicative. Details and error analysis are in [REPORT.md](REPORT.md).

| Detector | Baseline (regex) | Improved | Test set |
|---|---|---|---|
| Prompt injection | recall 0.44 | recall **1.00** (model) | 30 hand-written rows |
| Prompt injection | n/a | F1 **0.97** (model) | 116-row public test split (`deepset/prompt-injections`) |
| Toxicity | recall 0.50 | recall **1.00**, 1 false alarm (model) | 60 rows |
| PII | recall 0.50 | recall **0.71** (v2 rules) | 27-row held-out set |
| Commitments | recall 0.23 | recall **0.54** (v2 rules) | 26-row held-out set |

- Guard overhead is about **14 to 16 ms per message** on CPU; model generation takes 6 to 19 s per reply.
- On **25 real chatbot replies**, 3 were flagged and all 3 were correct (the model had invented a discount, a return policy and a shipping offer). One invented discount was missed.
- The weakest areas are names and addresses (PII) and paraphrased promises (commitments). Both are explained in the report.

## What it protects against

| # | Threat | How GuardStack handles it |
|---|---|---|
| A | Direct prompt injection | DeBERTa classifier (ONNX) with regex rules, checked before the LLM sees the message |
| B | Indirect injection (poisoned reviews) | System-prompt hardening, plus output checks that stop the harmful effect |
| C | PII leakage | Regex rules for emails, phones (incl. `+91`), Aadhaar and Luhn-checked cards, redacted on output |
| D | Toxic content | Pretrained toxic-bert (ONNX) with regex fallback, checked on output |
| E | Unauthorized commercial commitments | Rule-based detector with negation handling; flagged for human review |

## How it works

```
Shopper ──► [Input guard] ──► Local LLM (Ollama, llama3.2:1b) ──► [Output guard] ──► Shopper
             prompt injection                                       1. PII (redact)
                                                                    2. toxicity (block)
                                                                    3. commitment (flag)
```

- **Storefront:** Next.js, deployed on [Vercel](https://kadambari-project-cyan.vercel.app/).
- **Backend:** FastAPI, with the guards kept separate from the storefront.
- **LLM:** Llama 3.2 1B served locally by Ollama.
- **Three modes** for the learned detectors: `regex`, `model`, or `hybrid` (either flags). If a model file is missing, the detector **falls back to regex** instead of failing.
- **Audit log:** one JSON line per decision (status, categories, latency). Message text is not stored.
- **Guard label in the chat:** when a guard fires, the storefront shows a small "Guard triggered: ..." tag under the reply, using the categories the backend returns.

## Screenshots

**1. A normal shopper question.** The local model answers. Note that a 1B model can state wrong product facts (here it invents a story about size 9). GuardStack does not verify product facts; see [Limitations](#limitations).

![Normal chat reply on the Kadambari storefront](docs/screenshots/01_normal_reply.png)

**2. Guards in action.** Top: an obfuscated attack (`1gn0re previous instructions`) is blocked at the input guard. Bottom: a request for a 50% discount produces a reply that the commitment guard holds back for human review. The PII guard checks the assistant's replies, not the shopper's message.

![Injection blocked and commitment flagged](docs/screenshots/02_guards_in_action.png)

**3. Injection guard on the shopper's message.** A prompt-injection attempt is blocked before it reaches the model, and the chat shows which guard fired.

![Prompt injection blocked](docs/screenshots/03_injection.png)

**4. Output guards on the model's reply.** The PII, toxicity and commitment guards check what the assistant is about to say, so they are shown here by calling the output guard directly on sample replies. The output lists the status and categories each sample receives.

![Output guards run on sample replies](docs/screenshots/04_output_guards.png)

**5. Poisoned review.** One review on the page contains a fake "system note" asking for a discount code. The assistant's instructions tell it to treat reviews as customer text and never follow them. This is a prompt-level defence, not a separate guard, so no guard tag appears.

![Poisoned review not followed](docs/screenshots/05_poisoned_review.png)

## Quick start

**1. Install Ollama and the model**
```bash
ollama pull llama3.2:1b
```

**2. Backend** (from `backend/backend`)
```bash
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
uvicorn main:app --port 8000
```

**3. Storefront** (from the Next.js folder)
```bash
npm install
npm run dev
```

**Model files are not in this repository** (they are several hundred MB each). Without them the backend still runs and uses the regex rules. To use the trained models, regenerate them with the notebooks in [`notebooks/`](notebooks/) and place the ONNX files in `backend/backend/models/`.

### Settings (`.env`)

| Variable | Meaning | Default |
|---|---|---|
| `OLLAMA_MODEL` | Local model name | `llama3.2:1b` |
| `OLLAMA_HOST` | Ollama address | `http://localhost:11434` |
| `INJECTION_DETECTOR` | `regex`, `model` or `hybrid` | `regex` |
| `INJECTION_THRESHOLD` | Injection probability threshold | `0.5` |
| `TOXICITY_MODE` | `regex`, `model` or `hybrid` | see `.env.example` |
| `GUARDRAIL_ENABLED` | Turn all guards on or off | `true` |
| `LOG_PATH` | Audit log file | `guardstack_log.jsonl` |

## Reproduce the evaluation

Run from `backend/backend`, with the guards in the mode you want to test.

```bash
python evaluate_detectors.py          # regex-mode metrics for all detectors
python compare_modes.py               # injection: regex vs model vs hybrid
python compare_toxicity_modes.py      # toxicity: regex vs model vs hybrid
python test_real_replies.py           # 25 real replies (needs Ollama + backend running)
```

Test sets: `test_pii_day3.csv`, `test_commitments_day3.csv` (used to guide the v2 rules) and `heldout_pii.csv`, `heldout_commitments.csv` (scored once, rules frozen).

## Repository layout

```
.
├── README.md
├── REPORT.md                  full project report
├── docs/screenshots/          images used in this README
├── notebooks/                 Colab notebooks (injection and toxicity models)
├── backend/backend/
│   ├── main.py                FastAPI app and decision flow
│   ├── app/                   input_guard, output_guard, pii, policy, toxicity,
│   │                          classifier, llm_client, reviews, schemas
│   ├── models/                ONNX models (git-ignored)
│   ├── evaluate_detectors.py, compare_modes.py, compare_toxicity_modes.py
│   └── *.csv                  test sets and saved results
└── (Next.js storefront)
```

## Limitations

- Test sets are small and hand-written, so one example moves a score noticeably.
- Only injection and toxicity are learned. PII and commitments are rule-based, and names and addresses are not detected.
- Reviews are not scanned. Indirect injection is covered only by prompt design and the output guard.
- The injection classifier is conservative. It is the only guard that reads the shopper's message, so it also blocks some abusive or discount-seeking messages and reports them as `prompt_injection`. The toxicity, PII and commitment guards check the assistant's reply.
- The assistant is single-turn, and product facts such as stock are not verified.
- The backend runs on a laptop, and CORS is open (`*`), which should be restricted before any public deployment.

See [REPORT.md](REPORT.md), Section 6, for the full list and future work.

## Security note

`.env` and the model files are intentionally **not** committed. Use `.env.example` as the template.
