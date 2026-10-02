import re
from typing import List

# PRIVACY DETECTOR (Threat category C: PII leakage) -- v2 regex layer.
# Structured identifiers only. Names/addresses still need a learned NER model
# (see TODO / future work). detect_pii() and redact_pii() keep the same signatures.

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

# Indian mobile: optional +91 / 91 / 0, then 6-9 + 9 digits (5+5 split allowed).
# Digit look-arounds stop it firing inside longer numbers (order IDs, SKUs).
_PHONE_IN_RE = re.compile(r"(?<!\d)(?:\+?91[-.\s]?|0)?[6-9]\d{4}[-.\s]?\d{5}(?!\d)")
# Other international numbers must start with an explicit "+".
_PHONE_INTL_RE = re.compile(r"(?<![\w+])\+\d{1,3}[-.\s]?\d{4,5}[-.\s]?\d{4,6}(?!\d)")

# Aadhaar: 12 digits grouped 4-4-4 anywhere, or 12 plain digits only when
# the word Aadhaar/Aadhar/UID appears just before (avoids SKU/order-ID alarms).
_AADHAAR_GROUPED_RE = re.compile(r"(?<!\d)(?<!\d[ -])\d{4}[ -]\d{4}[ -]\d{4}(?![ -]?\d)")
_AADHAAR_KEYED_RE = re.compile(r"\b(?:aadhaar|aadhar|uid)\b\D{0,15}(\d{12})(?!\d)", re.IGNORECASE)

# Card: 13-19 digits (spaces/dashes allowed) AND must pass the Luhn checksum.
_CARD_CAND_RE = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")


def _luhn_ok(digits: str) -> bool:
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def _card_found(text: str) -> bool:
    for m in _CARD_CAND_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 19 and _luhn_ok(digits):
            return True
    return False


def detect_pii(text: str) -> List[str]:
    found = []
    if _EMAIL_RE.search(text):
        found.append("email")
    if _PHONE_IN_RE.search(text) or _PHONE_INTL_RE.search(text):
        found.append("phone")
    if _AADHAAR_GROUPED_RE.search(text) or _AADHAAR_KEYED_RE.search(text):
        found.append("aadhaar")
    if _card_found(text):
        found.append("card_number")
    return found


def redact_pii(text: str) -> str:
    def _card(m):
        digits = re.sub(r"\D", "", m.group(0))
        return "[redacted-card]" if 13 <= len(digits) <= 19 and _luhn_ok(digits) else m.group(0)

    text = _CARD_CAND_RE.sub(_card, text)
    text = _AADHAAR_GROUPED_RE.sub("[redacted-aadhaar]", text)
    text = _AADHAAR_KEYED_RE.sub(lambda m: m.group(0).replace(m.group(1), "[redacted-aadhaar]"), text)
    text = _PHONE_IN_RE.sub("[redacted-phone]", text)
    text = _PHONE_INTL_RE.sub("[redacted-phone]", text)
    text = _EMAIL_RE.sub("[redacted-email]", text)
    return text
