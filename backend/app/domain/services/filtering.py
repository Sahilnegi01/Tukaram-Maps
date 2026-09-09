import re
ESTABLISHMENT = re.compile(r"\b(restaurant|hotel|caf[eé]|eatery|dhaba|food outlet|resort|bar)\b", re.I)
ACTION = re.compile(r"\b(seal(?:ed)?|fin(?:e|ed)|raid(?:ed)?|notice|licen[cs]e cancelled|demolish(?:ed|tion)?|shut down|penalty|violation|re-?opened)\b", re.I)
def is_relevant_candidate(text: str) -> bool:
    return bool(ESTABLISHMENT.search(text or "") and ACTION.search(text or ""))

