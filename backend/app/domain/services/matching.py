from datetime import timedelta
from rapidfuzz.fuzz import ratio
from app.domain.services.normalization import normalize_name

class MatchingService:
    def establishment_score(self, candidate, existing):
        if candidate.get("city", "").casefold() != existing.get("city", "").casefold() or candidate.get("state", "").casefold() != existing.get("state", "").casefold(): return 0.0
        name = ratio(normalize_name(candidate["name"]), normalize_name(existing["name"])) / 100
        address = ratio(normalize_name(candidate.get("address", "")), normalize_name(existing.get("address", ""))) / 100 if candidate.get("address") and existing.get("address") else .5
        return round(.8 * name + .2 * address, 3)
    def same_action(self, incoming, existing):
        if incoming["establishment_id"] != existing["establishment_id"] or incoming["action_type"] != existing["action_type"]: return False
        if incoming.get("action_date") and existing.get("action_date") and abs(incoming["action_date"] - existing["action_date"]) > timedelta(days=2): return False
        authority = ratio(normalize_name(incoming["authority"]), normalize_name(existing["authority"])) / 100 if incoming.get("authority") and existing.get("authority") else 0
        reason = ratio(normalize_name(incoming["reason"]), normalize_name(existing["reason"])) / 100 if incoming.get("reason") and existing.get("reason") else 0
        return authority >= .7 or reason >= .7
