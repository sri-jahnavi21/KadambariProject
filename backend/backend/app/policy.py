import re
from typing import List

_COMMITMENT_PATTERNS = [
    r"\b\d{1,2}\s*%\s*(off|discount)\b",
    r"\bguarantee(d)?\b",
    r"\bassure(d)?\b",
    r"\bfull refund\b",
    r"\bfree (shipping|returns?)\b",
    r"\bi promise\b",
    r"\bwill (definitely|certainly) (work|fit|last)\b",
    r"\bprice match(ing)?\b",
    r"\bdiscount code\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _COMMITMENT_PATTERNS]


def check_commercial_commitment(text: str) -> List[str]:
    for pattern in _COMPILED:
        if pattern.search(text):
            return ["unauthorized_commitment"]
    return []