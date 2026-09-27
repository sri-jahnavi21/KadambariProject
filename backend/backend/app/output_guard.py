from typing import List, Tuple

from . import pii, policy, toxicity


def check_output(text: str) -> Tuple[str, List[str], str]:
    """
    Returns (status, categories, safe_text).
    status is one of "ALLOW", "BLOCK", "FLAG".
    """
    categories: List[str] = []

    pii_found = pii.detect_pii(text)
    if pii_found:
        categories.extend(pii_found)
        text = pii.redact_pii(text)

    toxic_found = toxicity.check_toxicity(text)
    if toxic_found:
        categories.extend(toxic_found)
        return "BLOCK", categories, "Sorry, I can't share that response."

    commitment = policy.check_commercial_commitment(text)
    if commitment:
        categories.extend(commitment)
        return "FLAG", categories, text

    if pii_found:
        return "FLAG", categories, text

    return "ALLOW", categories, text