"""
全球格局监控器 - AI 格局解读模块
"""
from openai import OpenAI
from config import AI_API_KEY, AI_API_BASE, AI_MODEL, SUMMARY_MAX_LENGTH


class AIProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=AI_API_KEY, base_url=AI_API_BASE)

    def _call(self, prompt: str, system: str = "", max_tokens: int = 500) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system or "你是一位地缘政治分析专家，擅长透过新闻表象看清背后的格局与博弈。"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens, temperature=0.3,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] AI调用失败: {e}")
            return ""

    def summarize(self, title: str, content: str) -> str:
        """一句话格局解读"""
        content = content[:3000] if content else ""
        prompt = f"""请对以下文章生成一句精简的中文格局解读（不超过{SUMMARY_MAX_LENGTH}字）。
要求：不要复述事实，点明背后的格局与博弈
格式：【格局定位】+ 【背后博弈】+ 【可能走向】

标题：{title}
内容：{content}

格局解读："""
        result = self._call(prompt, system="你是一位地缘政治分析专家，擅长透过新闻表象看清背后的格局与博弈。输出简洁、一针见血。", max_tokens=200)
        return result.replace("格局解读：", "").strip() or f"{title[:50]}..."

    def classify(self, title: str, content: str) -> dict:
        """
        对全球局势文章进行智能分类
        返回 {"content_type": "大国博弈|区域冲突|经济战|技术竞争|价值观冲突", "region_tags": ["中美", "欧洲", ...]}
        """
        content = content[:2000] if content else ""
        system = "你是一位地缘政治分类专家，熟悉国际关系和全球格局。只输出JSON格式，不要任何解释。"
        prompt = f"""请对以下国际政治/经济文章进行分类，只输出JSON，不要任何其他文字。

分类规则：
1. content_type（议题类型，单选）：
   - "大国博弈" — 中美、美俄、中俄等大国之间的战略竞争、外交博弈
   - "区域冲突" — 地区战争、军事冲突、领土争端、恐怖主义
   - "经济战" — 贸易战、制裁、关税、能源价格、金融博弈、供应链
   - "技术竞争" — 芯片、AI、半导体、科技封锁、技术主权
   - "价值观冲突" — 意识形态、民主vs专制、人权、文化冲突
   - "国际动态" — 不符合以上类型的其他国际新闻

2. region_tags（涉及地区/国家，可多选，最多3个）：
   ["中美", "美国", "中国", "俄罗斯", "欧洲", "中东", "亚太", "非洲", "拉美", "全球"]
   如果都不匹配则留空数组 []

标题：{title}
内容：{content}

请严格按以下JSON格式输出（不要markdown代码块）：
{{"content_type":"...","region_tags":["..."]}}
"""
        result = self._call(prompt, system=system, max_tokens=150)
        try:
            import json
            result = result.strip()
            if result.startswith("```"):
                result = result.split("\n", 1)[1]
            if result.endswith("```"):
                result = result.rsplit("\n", 1)[0]
            result = result.strip()
            data = json.loads(result)
            return {
                "content_type": data.get("content_type", "国际动态"),
                "region_tags": data.get("region_tags", [])
            }
        except Exception:
            # 回退：根据关键词简单分类
            text = (title + " " + content).lower()
            if any(k in text for k in ["中美", "美俄", "中俄", "大国", "霸权", "战略"]):
                ctype = "大国博弈"
            elif any(k in text for k in ["战争", "冲突", "军事", "导弹", "轰炸", "领土", "恐怖"]):
                ctype = "区域冲突"
            elif any(k in text for k in ["贸易", "关税", "制裁", "经济", "金融", "能源", "石油", "通胀"]):
                ctype = "经济战"
            elif any(k in text for k in ["芯片", "半导体", "ai", "科技", "技术", "封锁", "华为"]):
                ctype = "技术竞争"
            elif any(k in text for k in ["民主", "人权", "价值观", "意识形态", "文化"]):
                ctype = "价值观冲突"
            else:
                ctype = "国际动态"
            
            tags = []
            tag_keywords = {
                "中美": ["中美", "美中"],
                "美国": ["美国", "美方", "华盛顿", "拜登"],
                "中国": ["中国", "中方", "北京"],
                "俄罗斯": ["俄罗斯", "俄方", "普京", "俄乌"],
                "欧洲": ["欧洲", "欧盟", "北约", "德国", "法国", "英国"],
                "中东": ["中东", "以色列", "伊朗", "沙特", "巴勒斯坦", "叙利亚"],
                "亚太": ["亚太", "日本", "韩国", "印度", "东南亚", "菲律宾"],
                "非洲": ["非洲", "尼日利亚", "南非"],
                "拉美": ["拉美", "巴西", "墨西哥", "阿根廷"],
            }
            for tag, kws in tag_keywords.items():
                if any(k in text for k in kws):
                    tags.append(tag)
            if not tags:
                tags = ["全球"]
            return {"content_type": ctype, "region_tags": tags[:3]}

    def deep_dive(self, title: str, content: str, focus: str = "") -> str:
        """深度格局解读"""
        content = content[:8000]
        hint = f"重点关注：{focus}" if focus else ""
        prompt = f"""你是一位地缘政治分析专家。请对以下文章进行深度格局解读。

{hint}

输出格式：
## 📌 格局定位
（这件事在全球棋盘上的位置）

## 🎯 利益博弈
- 利益方A：...
- 利益方B：...
（各方诉求、动机、手段）

## 📈 趋势预判
（可能的走向、关键节点、转折信号）

## 🧠 历史参照
（类似历史事件及经验教训）

标题：{title}
内容：{content}
"""
        return self._call(prompt, max_tokens=2000)
