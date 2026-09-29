import os
import re
from typing import List, Optional, Tuple

from . import classifier

# ---------------------------------------------------------------------------
# INPUT SECURITY LAYER (Threat categories A & B: direct + indirect injection)
#
# Three modes, chosen with the INJECTION_DETECTOR setting in .env:
#   regex  - the original keyword rules only (default, needs nothing extra)
#   model  - the trained classifier only
#   hybrid - block if EITHER the rules OR the classifier say attack
#
# If the trained model files are missing, model/hybrid quietly fall back to
# regex, so the backend never breaks because a model file is absent.
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS = [
    r"ignore .{0,30}instructions",
    r"disregard .{0,30}(system prompt|instructions|rules)",
    r"you are now (in )?(developer|dan|jailbreak|unrestricted) mode",
    r"pretend (you|that you) (have no|are not bound by) (restrictions|rules|guidelines)",
    r"(reveal|tell me|show me|print|repeat|what is) .{0,20}(system prompt|hidden instructions|initial instructions)",
    r"forget (everything|all) .{0,20}(told|instructions)",
    r"new instructions?:",
    r"act as (if you|an unrestricted)",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def _regex_hit(text: str) -> bool:
    return any(p.search(text) for p in _COMPILED)


def check_input(text: str, mode: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Returns (is_blocked, categories).
    is_blocked=True means the message must never reach the LLM at all.
    """
    mode = (mode or os.getenv("INJECTION_DETECTOR", "regex")).lower()
    threshold = float(os.getenv("INJECTION_THRESHOLD", "0.5"))

    regex_hit = _regex_hit(text) if mode in ("regex", "hybrid") else False
    model_hit = False

    if mode in ("model", "hybrid"):
        prob = classifier.injection_probability(text)
        if prob is None:
            # model not available -> fall back to the rules
            regex_hit = regex_hit or _regex_hit(text)
        else:
            model_hit = prob >= threshold

    blocked = regex_hit or model_hit
    return blocked, (["prompt_injection"] if blocked else [])