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
