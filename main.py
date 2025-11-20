# main.py — User logger bot
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID_ENV = os.getenv("GROUP_ID", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

try:
    GROUP_ID = int(GROUP_ID_ENV) if GROUP_ID_ENV else None
except ValueError:
    raise RuntimeError("GROUP_ID must be integer")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    user_id = user.id
    full_name = user.full_name or "-"
    username = f"@{user.username}" if user.username else "—"

    text = (
        "📥 New /start user\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"👤 Name: {full_name}\n"
        f"🔗 Username: {username}\n"
        f"💬 From chat: <code>{chat.id}</code>"
    )

    keyboard = InlineKeyboardMarkup(
        [[ InlineKeyboardButton("👀 View profile user", url=f"tg://user?id={user_id}") ]]
    )

    if GROUP_ID:
        await context.bot.send_message(
            chat_id=GROUP_ID, text=text, parse_mode="HTML", reply_markup=keyboard
        )

    await update.message.reply_text("សួស្តីបង 👋\nតើមានអ្វីអោយខ្ញុំជួយបង!")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start  👉 send info to admin group")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
