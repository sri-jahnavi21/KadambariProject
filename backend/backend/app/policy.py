import re
from typing import List

_COMMITMENT_PATTERNS = [
    r"\b\d{1,2}\s*%\s*(off|discount)\b",
    r"(?:(?:rs\.?|₹|inr)\s?\d[\d,]*|\d[\d,]*\s*(?:rupees|rs\.?|inr))\s*off\b",
    r"\boff (your|the|this) (order|purchase|bill)\b",
    r"\bguarantee(d|s)?\b",
    r"\bassure\b",
    r"(?<!rest )\bassured\b",          # "rest assured" is an idiom, not a promise
    r"\bfull refund\b",
    r"\bfree (shipping|returns?|delivery|pair|gift)\b",
    r"\bships? free\b",
    r"\bfor free\b",
    r"\bfree of charge\b",
    r"\bno (extra |additional )?(cost|charge)s?\b",
    r"\bi promise\b",
    r"\bwe promise\b",
    r"\bmy word\b",
    r"\bwill (definitely|certainly) (work|fit|last)\b",
    r"\bprice match(ing)?\b",
    r"\bmatch (that|the|this|their|any) price\b",
    r"\bdiscount code\b",
    r"\b(we|i)(?:'ll| will) (?:definitely |certainly |gladly |happily |also )?(cover|refund|replace|waive|honou?r|reimburse)\b",
    r"\bbuy one,? get one\b",
    r"\byours for\b",
    r"\blegally binding\b",
    r"\bconsider (it|that|the \w+) (done|applied|approved)\b",
    r"\brefund (is|has been|will be) (approved|processed|issued|credited)\b",
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in _COMMITMENT_PATTERNS]

# A negation just before the trigger ("I can't guarantee...") cancels it.
_NEGATION = re.compile(
    r"\b(can'?t|cannot|can not|unable to|not able to|don'?t|do not|doesn'?t|does not|won'?t|will not|not)\b",
    re.IGNORECASE,
)
_WINDOW = 30


def check_commercial_commitment(text: str) -> List[str]:
    text = text.replace("\u2019", "'")
    for pattern in _COMPILED:
        for m in pattern.finditer(text):
            before = text[max(0, m.start() - _WINDOW):m.start()]
            if not _NEGATION.search(before):
                return ["unauthorized_commitment"]
    return []
