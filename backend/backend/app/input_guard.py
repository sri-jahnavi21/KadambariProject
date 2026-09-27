import re
from typing import List, Tuple

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


def check_input(text: str) -> Tuple[bool, List[str]]:
    for pattern in _COMPILED:
        if pattern.search(text):
            return True, ["prompt_injection"]
    return False, []