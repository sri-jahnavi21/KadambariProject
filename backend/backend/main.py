import json
import os
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import input_guard, llm_client, output_guard
from app.schemas import ChatRequest, ChatResponse

load_dotenv()

GUARDRAIL_ENABLED = os.getenv("GUARDRAIL_ENABLED", "true").lower() == "true"
LOG_PATH = os.getenv("LOG_PATH", "guardstack_log.jsonl")

app = FastAPI(title="GuardStack for Commerce")

# Tighten allow_origins to your actual Vercel domain before any public demo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _log(entry: dict) -> None:
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


@app.get("/health")
def health():
    return {"status": "ok", "guardrail_enabled": GUARDRAIL_ENABLED}


@app.post("/assistant/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    start = time.time()

    if GUARDRAIL_ENABLED:
        blocked, in_categories = input_guard.check_input(req.message)
        if blocked:
            _log(
                {
                    "session_id": req.session_id,
                    "stage": "input",
                    "status": "BLOCK",
                    "categories": in_categories,
                    "latency_ms": round((time.time() - start) * 1000, 1),
                }
            )
            return ChatResponse(
                reply="Sorry, I can't help with that request.",
                status="BLOCK",
                triggered_categories=in_categories,
            )

    try:
        raw_reply = llm_client.generate_reply(req.message)
    except RuntimeError:
        return ChatResponse(
            reply="The assistant is unavailable right now — please try again shortly.",
            status="BLOCK",
            triggered_categories=["llm_unreachable"],
        )

    if GUARDRAIL_ENABLED:
        status, out_categories, safe_reply = output_guard.check_output(raw_reply)
    else:
        status, out_categories, safe_reply = "ALLOW", [], raw_reply

    if status == "FLAG":
        safe_reply = (
            "This response needs a quick human review before it's shown — "
            "someone from our team will follow up shortly."
        )

    _log(
        {
            "session_id": req.session_id,
            "stage": "output",
            "status": status,
            "categories": out_categories,
            "latency_ms": round((time.time() - start) * 1000, 1),
        }
    )

    return ChatResponse(
        reply=safe_reply,
        status=status,
        triggered_categories=out_categories,
    )
