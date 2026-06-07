"""
全球格局监控器 - 主控模块
"""
import os
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Set

from config import SOURCES, HISTORY_FILE, MAX_ARTICLES_PER_BATCH
from scraper import scrape_all, Article
from ai_processor import AIProcessor
from feishu_bot import FeishuBot


class HistoryManager:
    def __init__(self, filepath=HISTORY_FILE):
        self.filepath = filepath
        self.history: Set[str] = set()
        self.data = {"articles": [], "last_check": None}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                    self.history = {a["id"] for a in self.data.get("articles", [])}
            except:
                pass

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def is_new(self, article_id):
        return article_id not in self.history

    def add(self, article):
        self.data["articles"].append(article.to_dict())
        self.history.add(article.id)
        self.data["articles"] = self.data["articles"][-100:]
        self.data["last_check"] = datetime.now().isoformat()
        self.save()


def fetch_content(url):
    import requests
    from bs4 import BeautifulSoup
    try:
        resp = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }, timeout=20)
        soup = BeautifulSoup(resp.text, "html.parser")
        for sel in ["article", "main", ".content", ".post-content", ".entry-content"]:
            el = soup.select_one(sel)
            if el:
                return el.get_text(separator="\n", strip=True)[:5000]
        paragraphs = soup.find_all("p")
        return "\n".join(p.get_text(strip=True) for p in paragraphs[:20])
    except Exception as e:
        print(f"[WARN] 获取内容失败 {url}: {e}")
        return ""


def run_monitor(dry_run=False):
    print(f"\n{'='*60}")
    print(f"🌍 全球格局监控启动 @ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    history = HistoryManager()
    print(f"[INFO] 历史记录: {len(history.history)} 条")

    articles = scrape_all()
    if not articles:
        print("[WARN] 未抓取到任何文章")
        return

    cutoff = datetime.now() - timedelta(days=3)
    new_articles = [a for a in articles if history.is_new(a.id) and (not a.published or a.published >= cutoff)]

    if not new_articles:
        print("[INFO] 没有新文章")
        return

    print(f"[INFO] 发现 {len(new_articles)} 条新文章")

    ai = AIProcessor()
    to_push = []
    for art in new_articles[:MAX_ARTICLES_PER_BATCH]:
        print(f"[INFO] 处理: {art.title[:60]}...")
        content = fetch_content(art.url)
        art.summary = ai.summarize(art.title, content)
        
        # AI 智能分类
        classify_result = ai.classify(art.title, content)
        art.content_type = classify_result.get("content_type", "国际动态")
        art.region_tags = classify_result.get("region_tags", [])
        print(f"[INFO] 分类结果: {art.content_type} | 地区: {', '.join(art.region_tags) if art.region_tags else '全球'}")
        
        to_push.append(art)

    if not dry_run and to_push:
        bot = FeishuBot()
        date_str = datetime.now().strftime('%m-%d')
        
        # 按 content_type 分组推送
        type_groups = {}
        for a in to_push:
            ctype = getattr(a, 'content_type', '国际动态')
            type_groups.setdefault(ctype, []).append(a)
        
        for ctype, type_arts in type_groups.items():
            push_data = [{
                "title": a.title,
                "summary": a.summary,
                "url": a.url,
                "source": a.source,
                "region_tags": getattr(a, 'region_tags', []),
            } for a in type_arts]
            
            title = f"{ctype} ({date_str})"
            bot.send_digest(title, push_data, content_type=ctype)
        
        for art in to_push:
            history.add(art)

    print(f"\n{'='*60}")
    print(f"✅ 完成: 推送 {len(to_push)} 条")
    type_counts = {}
    for a in to_push:
        ctype = getattr(a, 'content_type', '国际动态')
        type_counts[ctype] = type_counts.get(ctype, 0) + 1
    for ctype, count in type_counts.items():
        print(f"  • {ctype}: {count} 条")
    print(f"{'='*60}\n")


def run_deep_dive(url, focus=""):
    print(f"\n💥 格局解读: {url}\n")
    content = fetch_content(url)
    if not content:
        print("[ERROR] 无法获取内容")
        return
    ai = AIProcessor()
    result = ai.deep_dive("指定文章", content, focus)
    print("\n" + "="*60)
    print(result)
    print("="*60 + "\n")
    bot = FeishuBot()
    bot.send_deep_dive("指定文章", result, url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="全球格局监控器")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--deep-dive", type=str, help="对指定URL进行格局解读")
    parser.add_argument("--focus", type=str, default="", help="重点关注领域")
    args = parser.parse_args()

    if args.deep_dive:
        run_deep_dive(args.deep_dive, args.focus)
    else:
        run_monitor(dry_run=args.dry_run)
