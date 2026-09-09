from datetime import date
from app.domain.services.confidence import ConfidenceService
from app.domain.services.filtering import is_relevant_candidate
from app.domain.services.matching import MatchingService
from app.domain.services.normalization import normalize_name, normalize_url
from app.infrastructure.ai.classifiers.strategies import RuleBasedArticleClassifier
from app.infrastructure.ai.extractors.rules import RuleEntityExtractor
def test_regex_requires_both_signals():
 assert is_relevant_candidate("PMC sealed ABC Restaurant for a violation")
 assert not is_relevant_candidate("Authorities may take action against shops")
def test_normalization_and_tracking_url():
 assert normalize_name("ABC Restaurant Pvt. Ltd.")=="abc restaurant"
 assert normalize_url("HTTPS://Example.COM/story/?utm_source=x&a=1")=="https://example.com/story?a=1"
def test_same_name_different_city_is_not_match():
 svc=MatchingService(); assert svc.establishment_score({"name":"ABC Restaurant","city":"Pune","state":"Maharashtra"},{"name":"ABC Restaurant","city":"Mumbai","state":"Maharashtra"})==0
def test_two_articles_match_one_action():
 svc=MatchingService(); a={"establishment_id":"1","action_type":"SEALED","authority":"PMC","reason":"license violation","action_date":date(2026,8,20)}; b={**a,"authority":"Pune Municipal Corporation","reason":"license violation"}
 assert svc.same_action(a,b)
def test_confidence_thresholds():
 svc=ConfidenceService(); high=svc.calculate(relevance=.98,establishment=.98,action=.98,action_match=.95,date=.95,authority=.95,source=.95)
 assert svc.disposition(high)=="APPROVED"; assert svc.disposition(.78)=="PENDING_REVIEW"; assert svc.disposition(.5)=="REJECTED"
def test_classifier_and_entity_extraction():
 text="Pune Municipal Corporation sealed ABC Restaurant in Pune for a license violation"
 assert RuleBasedArticleClassifier().classify(text).is_relevant
 entity=RuleEntityExtractor().extract(text)
 assert entity["establishment_name"]=="ABC Restaurant"; assert entity["city"]=="Pune"; assert entity["action_type"]=="SEALED"
