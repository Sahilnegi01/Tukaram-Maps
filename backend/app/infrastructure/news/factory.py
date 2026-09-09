from app.infrastructure.news.adapters.rss import IndianExpressAdapter, RSSAdapter, TimesOfIndiaAdapter
class NewsSourceFactory:
    @staticmethod
    def create(source):
        domain=source.domain.lower()
        if "timesofindia" in domain: return TimesOfIndiaAdapter(source)
        if "indianexpress" in domain: return IndianExpressAdapter(source)
        return RSSAdapter(source)

