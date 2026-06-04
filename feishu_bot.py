"""
全球格局监控器 - 飞书推送模块
"""
import json
import time
import base64
import hmac
import hashlib
import requests
from typing import List, Dict

from config import FEISHU_WEBHOOK, FEISHU_SECRET


class FeishuBot:
    def __init__(self, webhook=None, secret=None):
        self.webhook = webhook or FEISHU_WEBHOOK
        self.secret = secret or FEISHU_SECRET

    def _gen_sign(self, timestamp):
        if not self.secret:
            return ""
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        return base64.b64encode(hmac_code).decode("utf-8")

    def _send(self, payload):
        if not self.webhook:
            print("[WARN] 未配置飞书 webhook")
            return False
        timestamp = int(time.time())
        sign = self._gen_sign(timestamp)
        if sign:
            payload["timestamp"] = timestamp
            payload["sign"] = sign
        try:
            resp = requests.post(self.webhook, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            result = resp.json()
            if result.get("code") == 0:
                print("[INFO] 飞书推送成功")
                return True
            else:
                print(f"[ERROR] 飞书推送失败: {result}")
                return False
        except Exception as e:
            print(f"[ERROR] 飞书请求异常: {e}")
            return False

    def send_digest(self, title: str, articles: List[Dict]):
        """发送格局速报卡片（绿色）"""
        elements = []
        for art in articles:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**[{art['source']}]** [{art['title']}]({art['url']})\n🔍 {art.get('summary', '')}",
                }
            })
            elements.append({"tag": "hr"})
        if elements:
            elements.pop()

        card = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {"tag": "plain_text", "content": f"🌍 {title}"},
                    "template": "green",
                },
                "elements": elements,
            },
        }
        return self._send(card)

    def send_deep_dive(self, title: str, content: str, url: str):
        """发送深度解读"""
        card = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {"tag": "plain_text", "content": f"💥 格局解读: {title[:50]}..."},
                    "template": "orange",
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": content[:3000]}},
                    {"tag": "action", "actions": [{"tag": "button", "text": {"tag": "plain_text", "content": "阅读原文"}, "url": url, "type": "primary"}]}
                ],
            },
        }
        return self._send(card)
