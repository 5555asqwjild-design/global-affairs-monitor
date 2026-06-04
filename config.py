"""
全球格局监控器 - 配置文件
"""
import os
from dataclasses import dataclass
from typing import List


@dataclass
class Source:
    name: str
    url: str
    type: str  # "rss", "api"
    priority: int
    keywords: List[str]


# === 全球格局数据源 ===
SOURCES = [
    Source(
        name="The Economist",
        url="https://www.economist.com/rss/print-edition.xml",
        type="rss",
        priority=5,
        keywords=["geopolitics", "trade", "war", "election", "economy", "China", "US", "Russia", "Europe", "Asia", "Middle East", "Africa", "technology", "AI", "climate", "energy", "migration", "democracy", "sanctions", "tariff", "supply chain", "semiconductor", "nuclear", "diplomacy", "summit", "treaty", "alliance", "NATO", "G7", "BRICS", "UN", "inflation", "recession", "GDP", "cybersecurity", "Ukraine", "Taiwan", "Israel", "Gaza", "Korea"],
    ),
    Source(
        name="Wikipedia Current Events",
        url="https://en.wikipedia.org/w/api.php",
        type="api",
        priority=4,
        keywords=["war", "conflict", "election", "summit", "treaty", "sanctions", "trade", "pandemic", "climate", "disaster", "terrorism", "nuclear", "diplomacy", "geopolitics", "coup", "revolution", "protest", "ceasefire", "alliance"],
    ),
    Source(
        name="Al Jazeera",
        url="https://www.aljazeera.com/xml/rss/all.xml",
        type="rss",
        priority=4,
        keywords=["war", "conflict", "Palestine", "Israel", "Gaza", "Ukraine", "Russia", "Syria", "Yemen", "Iran", "Iraq", "Afghanistan", "Sudan", "Libya", "Ethiopia", "Myanmar", "China", "US", "Turkey", "Saudi", "Egypt", "Africa", "Middle East", "Asia", "migration", "refugee", "human rights", "UN", "ceasefire", "peace", "diplomacy", "sanctions", "nuclear", "climate", "coup", "protest", "election", "genocide", "attack"],
    ),
    Source(
        name="Rest of World",
        url="https://restofworld.org/feed/",
        type="rss",
        priority=3,
        keywords=["technology", "internet", "censorship", "surveillance", "AI", "platform", "social media", "digital rights", "startup", "ecommerce", "fintech", "China", "India", "Africa", "Southeast Asia", "Latin America", "Middle East", "Russia", "Brazil", "Indonesia", "Nigeria", "global south", "digital divide", "misinformation", "deepfake", "regulation", "protest", "migration", "culture"],
    ),
    Source(
        name="Foreign Affairs",
        url="https://www.foreignaffairs.com/rss",
        type="rss",
        priority=5,
        keywords=["geopolitics", "strategy", "diplomacy", "war", "nuclear", "China", "US", "Russia", "Europe", "Asia", "Middle East", "India", "Africa", "Latin America", "trade", "sanctions", "alliance", "NATO", "democracy", "authoritarianism", "climate", "energy", "technology", "AI", "cyber", "space", "migration", "terrorism", "hegemony", "world order", "global governance", "sovereignty", "soft power", "grand strategy", "foreign policy"],
    ),
]

# === 推送配置 ===
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
FEISHU_SECRET = os.getenv("FEISHU_SECRET", "")

# === AI配置 ===
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_API_BASE = os.getenv("AI_API_BASE", "https://api.deepseek.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")

# === 运行配置 ===
CHECK_INTERVAL_HOURS = 12
MAX_ARTICLES_PER_BATCH = 15
SUMMARY_MAX_LENGTH = 150
HISTORY_FILE = "history.json"
