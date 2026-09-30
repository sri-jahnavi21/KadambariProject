import os
from typing import List

from . import classifier

# Modes, set with TOXICITY_MODE in .env:
#   regex  - keyword baseline (default)
#   model  - pretrained unitary/toxic-bert exported to ONNX
#   hybrid - flag if EITHER keywords OR model flags it
# If the model files are missing or fail to load, every mode falls back to regex.

# Fixed on purpose: this is the value used in the evaluation. Do not tune it on the test sets.
TOXICITY_THRESHOLD = 0.5

_TOXIC_KEYWORDS = [
    "idiot", "stupid", "shut up", "hate you", "kill yourself",
    "worthless", "pathetic", "moron", "dumb",
]


def check_toxicity_regex(text: str) -> List[str]:
    """Keyword baseline only. Always regex, whatever TOXICITY_MODE says."""
    lowered = text.lower()
    for word in _TOXIC_KEYWORDS:
        if word in lowered:
            return ["toxic_content"]
    return []


def check_toxicity(text: str) -> List[str]:
    mode = os.getenv("TOXICITY_MODE", "regex").strip().lower()
    regex_result = check_toxicity_regex(text)
    if mode not in ("model", "hybrid"):
        return regex_result

    prob = classifier.toxicity_probability(text)
    if prob is None:  # model missing or invalid -> safe fallback to regex
        return regex_result

    model_hit = prob >= TOXICITY_THRESHOLD
    if mode == "model":
        return ["toxic_content"] if model_hit else []
    return ["toxic_content"] if (model_hit or regex_result) else []