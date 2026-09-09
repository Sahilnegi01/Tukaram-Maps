import re
from abc import ABC, abstractmethod
from dateutil import parser
from app.domain.enums import ActionType, EstablishmentType
class EntityExtractor(ABC):
    @abstractmethod
    def extract(self,text): ...
class RuleEntityExtractor(EntityExtractor):
    actions={"sealed":ActionType.SEALED,"fined":ActionType.FINED,"raided":ActionType.RAIDED,"notice":ActionType.NOTICE_ISSUED,"reopened":ActionType.REOPENED,"re-opened":ActionType.REOPENED}
    def extract(self,text):
        lower=text.lower(); action=next((v for k,v in self.actions.items() if k in lower),ActionType.OTHER)
        name=re.search(r"(?:seal(?:s|ed)?|fine[sd]?|raid(?:s|ed)?|notice to|re-?open(?:s|ed)?)\s+([A-Z][\w&'. -]+?(?:Restaurant|Hotel|Cafe|Dhaba|Resort|Bar))",text,re.I)
        city=next((x for x in ["Pune","Mumbai","Nagpur","Nashik","Thane","Delhi","Bengaluru","Jaipur"] if x.lower() in lower),None)
        return {"establishment_name":name.group(1).strip() if name else None,"establishment_type":EstablishmentType.HOTEL if name and "hotel" in name.group(1).lower() else EstablishmentType.RESTAURANT,"city":city,"state":"Maharashtra" if city in ["Pune","Mumbai","Nagpur","Nashik","Thane"] else None,"action_type":action,"current_status_signal":"OPEN" if action==ActionType.REOPENED else None}
class LLMEntityExtractor(EntityExtractor):
    def __init__(self,provider=None): self.provider=provider
    def extract(self,text): return None
