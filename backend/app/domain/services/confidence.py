class ConfidenceService:
    weights = {"relevance": .25, "establishment": .2, "action": .2, "action_match": .1, "date": .08, "authority": .07, "source": .1}
    def calculate(self, **signals):
        total = sum(self.weights[k] * max(0, min(1, float(signals.get(k, 0)))) for k in self.weights)
        return round(total, 4)
    def disposition(self, score, auto_threshold=.9, review_threshold=.7):
        return "APPROVED" if score >= auto_threshold else "PENDING_REVIEW" if score >= review_threshold else "REJECTED"

