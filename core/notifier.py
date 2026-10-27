"""
Dual Notification Service: Telegram Bot API & CallMeBot WhatsApp Gateway
Sends instant trade executions, trailing stop locks, and circuit breaker shutdowns.
"""
import os
import json
import urllib.request
import urllib.parse
import datetime
from typing import Dict, Optional

class NotificationService:
    @staticmethod
    def _load_config() -> dict:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cfg_path = os.path.join(root, 'config', 'notify_config.json')
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "enabled": False,
            "telegram": {"bot_token": "", "chat_id": ""},
            "whatsapp": {"phone": "", "apikey": ""}
        }

    @classmethod
    def send_telegram(cls, text: str) -> bool:
        cfg = cls._load_config().get("telegram", {})
        token = cfg.get("bot_token", "").strip()
        chat_id = cfg.get("chat_id", "").strip()
        if not token or not chat_id or token.startswith("YOUR_"):
            return False
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}).encode('utf-8')
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"[TELEGRAM ERROR] {e}")
            return False

    @classmethod
    def send_whatsapp(cls, text: str) -> bool:
        cfg = cls._load_config().get("whatsapp", {})
        phone = cfg.get("phone", "").strip().replace("+", "").replace(" ", "")
        apikey = cfg.get("apikey", "").strip()
        if not phone or not apikey or apikey.startswith("YOUR_"):
            return False
        try:
            params = urllib.parse.urlencode({"phone": phone, "text": text, "apikey": apikey})
            url = f"https://api.callmebot.com/whatsapp.php?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "TradingBot/2.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"[WHATSAPP ERROR] {e}")
            return False

    @classmethod
    def broadcast(cls, title: str, details: str, alert_type: str = "INFO"):
        cfg = cls._load_config()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        emoji_map = {
            "BUY": "🚀",
            "SELL": "💰",
            "PROFIT_LOCK": "🎯",
            "LOSS_SHIELD": "🛡️",
            "KILL_SWITCH": "🚨",
            "TEST": "🔔"
        }
        icon = emoji_map.get(alert_type, "⚡")
        full_msg = f"{icon} *{title}*\n📅 {timestamp}\n\n{details}"

        if not cfg.get("enabled", False):
            print(f"[ALERT SIMULATION] {icon} {title} | {details.replace(chr(10), ' | ')}")
            return

        tg_ok = cls.send_telegram(full_msg)
        wa_ok = cls.send_whatsapp(full_msg.replace("*", ""))
        status = []
        if tg_ok: status.append("Telegram ✅")
        if wa_ok: status.append("WhatsApp ✅")
        if status:
            print(f"[NOTIFIED] Sent via {' & '.join(status)}")

    @classmethod
    def test_connection(cls):
        cfg = cls._load_config()
        print("=" * 80)
        print("TESTING TELEGRAM & WHATSAPP DUAL NOTIFICATION CHANNELS")
        print("=" * 80)
        print(f"Master Notification Switch : {'ENABLED' if cfg.get('enabled') else 'DISABLED (Set enabled: true in config/notify_config.json)'}")

        tg = cfg.get('telegram', {})
        tg_ready = bool(tg.get('bot_token') and not tg.get('bot_token').startswith('YOUR_') and tg.get('chat_id'))
        print(f"Telegram Channel          : {'CONFIGURED' if tg_ready else 'NOT CONFIGURED (Add bot_token & chat_id)'}")

        wa = cfg.get('whatsapp', {})
        wa_ready = bool(wa.get('phone') and not wa.get('phone').startswith('+91XXX') and wa.get('apikey') and not wa.get('apikey').startswith('YOUR_'))
        print(f"WhatsApp (CallMeBot)      : {'CONFIGURED' if wa_ready else 'NOT CONFIGURED (Add phone & apikey)'}")
        print("-" * 80)

        test_msg = "Test alert from Autonomous Multi-Agent Trading System.\nConnection verified successfully!"
        cls.broadcast(title="NOTIFICATION TEST", details=test_msg, alert_type="TEST")
        print("=" * 80)
