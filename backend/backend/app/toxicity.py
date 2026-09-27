from typing import List

# ---------------------------------------------------------------------------
# TOXIC / HARMFUL CONTENT CHECK (Threat category D)
#
# Keyword placeholder — TODO (Objective 2): replace with a harmful-content
# classifier trained on the Jigsaw Toxic Comment Classification Challenge
# dataset, ideally as a second head on the same DeBERTaV3-small model used
# for injection detection.
# ---------------------------------------------------------------------------

_TOXIC_KEYWORDS = [
    "idiot", "stupid", "shut up", "hate you", "kill yourself",
    "worthless", "pathetic", "moron", "dumb",
]


def check_toxicity(text: str) -> List[str]:
    lowered = text.lower()
    for word in _TOXIC_KEYWORDS:
        if word in lowered:
            return ["toxic_content"]
    return []