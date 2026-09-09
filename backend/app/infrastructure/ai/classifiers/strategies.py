from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.domain.services.filtering import is_relevant_candidate
@dataclass
class Classification: is_relevant: bool; confidence: float
class ArticleClassifier(ABC):
    @abstractmethod
    def classify(self,text): ...
class RuleBasedArticleClassifier(ArticleClassifier):
    def classify(self,text): return Classification(is_relevant_candidate(text),.72 if is_relevant_candidate(text) else .05)
class TransformerArticleClassifier(ArticleClassifier):
    def __init__(self,model_name="facebook/bart-large-mnli"):
        from transformers import pipeline
        self.pipeline=pipeline("zero-shot-classification",model=model_name)
    def classify(self,text):
        result=self.pipeline(text[:4000],["hotel or restaurant enforcement action","unrelated news"])
        score=result["scores"][result["labels"].index("hotel or restaurant enforcement action")]
        return Classification(score>=.5,float(score))

