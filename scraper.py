"""
全球格局监控器 - 数据抓取模块
"""
import re
import time
import hashlib
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import SOURCES, MAX_ARTICLES_PER_BATCH


class Article:
    def __init__(self, title: str, url: str, source: str, published: Optional[datetime] = None,
                 summary: str = "", content: str = "", author: str = ""):
        self.title = title
        self.url = url
        self.source = source
        self.published = published or datetime.now()
        self.summary = summary
        self.content = content
        self.author = author
        self.id = hashlib.md5(f"{title}:{url}".encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "id": self.id, "title": self.title, "url": self.url,
            "source": self.source,
            "published": self.published.isoformat() if self.published else None,
            "summary": self.summary, "author": self.author,
        }


class BaseScraper:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, application/atom+xml, text/html",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, source):
        self.source = source
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def scrape(self) -> List[Article]:
        raise NotImplementedError


class RSSScraper(BaseScraper):
    """通用 RSS 抓取器"""
    def scrape(self) -> List[Article]:
        try:
            resp = self.session.get(self.source.url, timeout=30, allow_redirects=True)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)

            if not feed.entries:
                print(f"[WARN] {self.source.name}: RSS 返回 0 条 (status={resp.status_code}, url={resp.url})")
                return []

            articles = []
            for entry in feed.entries[:20]:
                title = entry.title
                if not any(kw.lower() in title.lower() for kw in self.source.keywords):
                    continue
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                articles.append(Article(
                    title=title, url=entry.link, published=published, source=self.source.name
                ))
            print(f"[INFO] {self.source.name}: {len(feed.entries)} 条, 匹配 {len(articles)} 条")
            return articles
        except Exception as e:
            print(f"[ERROR] {self.source.name}: {e}")
            return []


class WikipediaScraper(BaseScraper):
    """Wikipedia Current Events"""
    def scrape(self) -> List[Article]:
        articles = []
        try:
            params = {
                "action": "query", "titles": "Portal:Current_events",
                "prop": "revisions", "rvprop": "content", "format": "json",
            }
            resp = self.session.get("https://en.wikipedia.org/w/api.php", params=params, timeout=30, verify=False)
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                revisions = page.get("revisions", [])
                if not revisions:
                    continue
                content = revisions[0].get("*", "")
                for line in content.split("\n"):
                    line = line.strip()
                    match = re.match(r'\*+\s*\[\[(.+?)\]\]', line)
                    if match:
                        event_title = match.group(1).split("|")[0]
                        if not any(kw.lower() in event_title.lower() for kw in self.source.keywords):
                            continue
                        url = f"https://en.wikipedia.org/wiki/{event_title.replace(' ', '_')}"
                        articles.append(Article(title=event_title, url=url, source=self.source.name))
            print(f"[INFO] Wikipedia: {len(articles)} 条相关事件")
        except Exception as e:
            print(f"[ERROR] Wikipedia: {e}")
        return articles[:15]


SCRAPER_MAP = {
    "The Economist": RSSScraper,
    "Wikipedia Current Events": WikipediaScraper,
    "Al Jazeera": RSSScraper,
    "Rest of World": RSSScraper,
    "Foreign Affairs": RSSScraper,
}


def scrape_all() -> List[Article]:
    all_articles = []
    for source in SOURCES:
        scraper_class = SCRAPER_MAP.get(source.name, RSSScraper)
        scraper = scraper_class(source)
        try:
            articles = scraper.scrape()
            all_articles.extend(articles)
        except Exception as e:
            print(f"[ERROR] {source.name}: {e}")
        time.sleep(2)
    return all_articles


if __name__ == "__main__":
    articles = scrape_all()
    print(f"\n共抓取 {len(articles)} 条文章")
    for a in articles:
        print(f"🌍 [{a.source}] {a.title[:60]}")
