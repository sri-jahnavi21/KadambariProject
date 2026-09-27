# GuardStack for Commerce — backend

A local FastAPI service that wraps Ollama with an input guardrail layer and
an output guardrail layer, following the GuardStack architecture:

```
POST /assistant/chat
  -> input guardrail  (prompt injection / jailbreak)
  -> Ollama (local LLM)
  -> output guardrail (PII, unauthorized commercial commitments)
  -> response { reply, status, triggered_categories }
```

This runs **outside** Lovable/Vercel, on your own machine, because Ollama
needs a persistent process that serverless platforms can't host. The
Kadambari frontend calls this service over HTTP — it never imports this
code directly, so the two stay fully decoupled (see the architecture
diagram from earlier in this project).

## 1. Install and start Ollama

Download from https://ollama.com, then:

```bash
ollama pull llama3.2:1b
ollama serve
```

Leave that running in its own terminal.

## 2. Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configure

```bash
cp .env.example .env
```

Defaults work as-is if Ollama is running locally on its default port.

## 4. Run the backend

```bash
uvicorn main:app --reload --port 8000
```

Check it's alive:

```bash
curl http://localhost:8000/health
```

## 5. Point the frontend at it

In the Lovable project's `.env`:

```
VITE_CHAT_API_URL=http://localhost:8000
VITE_CHAT_ENABLED=true
```

## What's a placeholder right now

`app/input_guard.py` and `app/output_guard.py` use **regex/keyword rules**,
not the trained models from your literature review. Each file has a `TODO`
marking exactly what to swap in:

| File | Replace with |
|---|---|
| `app/input_guard.py` | Fine-tuned DeBERTaV3-small, exported to ONNX, served via `onnxruntime` |
| `app/pii.py` | NER model informed by AI4Privacy PII-Masking-200k |
| `app/output_guard.py` | Add the harmful/toxic content classifier (Jigsaw-informed) |

`app/policy.py` (commercial commitments) is meant to stay rule-based
permanently — that's a deliberate design choice from the literature review,
not a placeholder.

## Evaluation logging

Every request appends a line to `guardstack_log.jsonl` with the stage,
status (`ALLOW`/`BLOCK`/`FLAG`), triggered categories, and latency in ms.
This is what you'll aggregate for the precision/recall/F1 and latency
numbers in your evaluation chapter.

## Comparing with/without the guardrail

Set `GUARDRAIL_ENABLED=false` in `.env` and restart to bypass both layers
entirely — useful for the before/after comparison your evaluation plan
calls for.
