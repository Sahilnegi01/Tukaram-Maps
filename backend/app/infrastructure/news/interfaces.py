from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
@dataclass
class FeedItem:
    title: str; url: str; published_at: datetime | None=None; summary: str | None=None
class NewsSourceAdapter(ABC):
    @abstractmethod
    async def fetch_feed_items(self): ...
    async def fetch_article_metadata(self,item): return item
    async def fetch_article_content_if_permitted(self,item): return None

