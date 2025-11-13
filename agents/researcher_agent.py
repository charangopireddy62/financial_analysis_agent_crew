# agents/researcher_agent.py
import os
import requests
import feedparser
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import quote_plus

from utils.sentiment_analysis import simple_sentiment

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")  # optional: set this in your env for better results

class ResearcherAgent:
    """
    ResearcherAgent:
      - fetches news for a given stock/company/query
      - computes basic sentiment per article using utils.sentiment_analysis.simple_sentiment
      - returns a list of news dicts
    """

    def __init__(self, source="auto", max_articles=10):
        self.max_articles = max_articles
        self.source = source  # 'newsapi'|'rss'|'auto'

    def _fetch_news_newsapi(self, query: str) -> List[Dict[str, Any]]:
        if not NEWSAPI_KEY:
            raise RuntimeError("NEWSAPI_KEY not found in environment.")
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "pageSize": self.max_articles,
            "sortBy": "relevancy",
            "language": "en",
            "apiKey": NEWSAPI_KEY,
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for a in data.get("articles", [])[: self.max_articles]:
            text = (a.get("title") or "") + " " + (a.get("description") or "")
            sentiment = simple_sentiment(text)
            published = a.get("publishedAt")
            results.append({
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("url"),
                "source": a.get("source", {}).get("name"),
                "published": published,
                "raw": a,
                "sentiment": sentiment,
            })
        return results

    def _fetch_news_rss(self, query: str) -> List[Dict[str, Any]]:
        # Use Google News RSS (no API key). Works well for quick prototyping.
        safe_q = quote_plus(query)
        rss_url = f"https://news.google.com/rss/search?q={safe_q}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        results = []
        for entry in feed.entries[: self.max_articles]:
            title = entry.get("title")
            link = entry.get("link")
            summary = entry.get("summary", "")
            # Some feeds embed HTML — strip minimal tags if present
            text = f"{title} {summary}"
            sentiment = simple_sentiment(text)
            # feedparser dates can vary
            published = None
            if "published" in entry:
                try:
                    published = entry.published
                except Exception:
                    published = None
            results.append({
                "title": title,
                "description": summary,
                "url": link,
                "source": entry.get("source", {}).get("title") or "Google News",
                "published": published,
                "raw": entry,
                "sentiment": sentiment,
            })
        return results

    def gather_news(self, query: str) -> List[Dict[str, Any]]:
        """
        Public method to fetch news for `query` (company name, ticker, etc.)
        Returns list of dicts with keys: title, description, url, source, published, sentiment
        """
        # Determine fetch method
        mode = self.source
        if mode == "auto":
            mode = "newsapi" if NEWSAPI_KEY else "rss"

        try:
            if mode == "newsapi":
                return self._fetch_news_newsapi(query)
            else:
                return self._fetch_news_rss(query)
        except Exception as e:
            # graceful fallback to rss if possible
            try:
                return self._fetch_news_rss(query)
            except Exception:
                raise RuntimeError(f"Failed to fetch news (tried {mode}). Error: {e}")

    def analyze_sentiment_summary(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simple aggregate sentiment summary
        """
        if not news_items:
            return {"count": 0, "positive": 0, "negative": 0, "neutral": 0, "avg_polarity": 0.0}

        pos = neg = neu = 0
        total_p = 0.0
        for item in news_items:
            lab = item.get("sentiment", {}).get("label", "neutral")
            pol = item.get("sentiment", {}).get("polarity", 0.0)
            total_p += pol
            if lab == "positive":
                pos += 1
            elif lab == "negative":
                neg += 1
            else:
                neu += 1

        avg = round(total_p / max(1, len(news_items)), 4)
        return {"count": len(news_items), "positive": pos, "negative": neg, "neutral": neu, "avg_polarity": avg}

# Quick manual smoke-run when executed directly
if __name__ == "__main__":
    r = ResearcherAgent(max_articles=5)
    q = "Tata Consultancy Services"  # change as needed
    items = r.gather_news(q)
    summary = r.analyze_sentiment_summary(items)
    print("Fetched:", len(items))
    print("Summary:", summary)
    for i, it in enumerate(items, 1):
        print(f"\n{i}. {it['title']}\n   {it['url']}\n   sentiment: {it['sentiment']}")
