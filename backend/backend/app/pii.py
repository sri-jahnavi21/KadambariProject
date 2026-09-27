import re
from typing import List

# ---------------------------------------------------------------------------
# PRIVACY DETECTOR (Threat category C: PII leakage)
#
# Regex placeholder covering structured identifiers only.
#
# TODO (Objective 2): add a token-classification / NER model informed by
# AI4Privacy's PII-Masking-200k for unstructured PII (names, addresses,
# order numbers) that regex can't reliably catch. Keep detect_pii() and
# redact_pii() as the two entry points main.py and output_guard.py rely on.
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\d{10}\b")
_CARD_RE = re.compile(r"\b(?:\d[ -]?){13,16}\b")


def detect_pii(text: str) -> List[str]:
    found = []
    if _EMAIL_RE.search(text):
        found.append("email")
    if _PHONE_RE.search(text):
        found.append("phone")
    if _CARD_RE.search(text):
        found.append("card_number")
    return found


def redact_pii(text: str) -> str:
    text = _EMAIL_RE.sub("[redacted-email]", text)
    text = _PHONE_RE.sub("[redacted-phone]", text)
    text = _CARD_RE.sub("[redacted-card]", text)
    return text
