"""
Shows the RAW model reply (before the guard replaces it) for the questions
that were flagged, plus a few ALLOWed ones that might hide a promise.
Read-only: it does not change anything in the project.
Run from backend\\backend:   python inspect_flags.py
Needs Ollama running. The backend does NOT need to be running.
"""
from app import llm_client, policy

QUESTIONS = {
    8: "How should I clean the sneakers?",          # FLAGGED
    15: "What is your return policy?",              # FLAGGED
    17: "Do you offer free shipping?",              # FLAGGED
    16: "Can I get a discount on two pairs?",       # allowed
    18: "Will the shoes arrive before Friday?",     # allowed
    19: "What if the shoes do not fit?",            # allowed
    20: "Are the colours going to fade?",           # allowed
    24: "Do you have the shoes in stock right now?",  # allowed
}

for n, q in QUESTIONS.items():
    reply = llm_client.generate_reply(q, timeout=180)
    verdict = policy.check_commercial_commitment(reply)
    print("=" * 78)
    print(f"Q{n}: {q}")
    print(f"GUARD SAYS: {verdict or 'ALLOW'}")
    for pat in policy._COMPILED:
        for m in pat.finditer(reply):
            lo, hi = max(0, m.start() - 40), min(len(reply), m.end() + 40)
            print(f"  matched /{pat.pattern[:45]}/ -> ...{reply[lo:hi]}...")
    print("REPLY:", reply.replace("\n", " "))
