# main.py — Telegram send-only service for Railway (for Channa)
import os
import logging
import requests
from flask import Flask, request, jsonify

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")
if not GROUP_ID:
    raise RuntimeError("GROUP_ID not set")

TELEGRAM_API = f\"https://api.telegram.org/bot{BOT_TOKEN}\"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("send-only-bot")

app = Flask(__name__)

def send_user_to_group(user_id: int, full_name: str, username: str | None = None):
    \"\"Send formatted user info to target group with 'View profile' button.\"\"
    if not full_name:
        full_name = "-"
    if username:
        username_text = f\"@{username.lstrip('@')}\"
    else:
        username_text = "—"

    text = (
        "📥 New user from respond.io\\n"
        f"🆔 ID: <code>{user_id}</code>\\n"
        f"👤 Name: {full_name}\\n"
        f"🔗 Username: {username_text}"
    )

    payload = {
        "chat_id": GROUP_ID,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "👀 View profile user",
                        "url": f"tg://user?id={user_id}",
                    }
                ]
            ]
        },
    }

    r = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=15)
    if not r.ok:
        log.error("Telegram sendMessage failed: %s %s", r.status_code, r.text)
    else:
        log.info("Sent user info for %s to group %s", user_id, GROUP_ID)

@app.route("/", methods=["GET"])
def index():
    return "OK: send-only bot is running", 200

@app.route("/from-respondio", methods=["POST"])
def from_respondio():
    \"\"Endpoint to be called from respond.io via HTTP Request step.

    Expected JSON body (example):

    {
      "user_id": 123456789,
      "full_name": "Test User",
      "username": "testuser"
    }
    \"\"
    data = request.get_json(silent=True) or {}
    log.info("Received from respond.io: %s", data)

    user_id = data.get("user_id") or data.get("id") or data.get("telegram_id")
    full_name = data.get("full_name") or data.get("name")
    username = data.get("username") or data.get("telegram_username")

    if not user_id:
        return jsonify({"ok": False, "error": "user_id missing"}), 400

    try:
        user_id_int = int(user_id)
    except Exception:
        return jsonify({"ok": False, "error": "user_id must be int"}), 400

    send_user_to_group(user_id_int, full_name or "", username)

    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
