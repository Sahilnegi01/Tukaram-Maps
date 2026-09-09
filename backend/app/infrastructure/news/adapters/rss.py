from datetime import datetime, timezone
import feedparser, httpx
from app.infrastructure.news.interfaces import FeedItem, NewsSourceAdapter
class RSSAdapter(NewsSourceAdapter):
    def __init__(self,source): self.source=source
    async def fetch_feed_items(self):
        if not self.source.feed_url: return []
        async with httpx.AsyncClient(timeout=15,headers={"User-Agent":"IndiaEnforcementMap/1.0 (public-interest research; respectful RSS polling)"}) as client:
            response=await client.get(self.source.feed_url); response.raise_for_status()
        feed=feedparser.loads(response.content); items=[]
        for x in feed.entries:
            stamp=getattr(x,"published_parsed",None); published=datetime(*stamp[:6],tzinfo=timezone.utc) if stamp else None
            items.append(FeedItem(x.get("title","Untitled"),x.get("link",""),published,x.get("summary")))
        return items
class TimesOfIndiaAdapter(RSSAdapter): pass
class IndianExpressAdapter(RSSAdapter): pass

