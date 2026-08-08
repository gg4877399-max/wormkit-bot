import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "8334921358:AAF2dTpiFZeVx3g6NnQb3Ni8-JgQiW1amYw")
WORMGPT_API = os.environ.get("WORMGPT_API", "https://wormgpt-api.onrender.com/chat")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *WormGPT Activated*\n\n"
        "أهلاً بك. أنا WormGPT، تحت أمرك.\n"
        "ارسلي أي سؤال وبجاوبك فوراً.\n\n"
        "⚡ *هاي النسخة السريعة* — سيرفر دائم 24/7",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — بدء المحادثة\n"
        "/help — المساعدة\n\n"
        "أرسل أي رسالة عادية وبتوصل لـ WormGPT"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    if not user_text:
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        payload = {"message": user_text, "session_id": str(update.effective_chat.id)}
        res = requests.post(WORMGPT_API, json=payload, timeout=60)
        if res.status_code == 200:
            data = res.json()
            reply = data.get("response", "...")
        else:
            reply = f"⚠️ API error: {res.status_code}"
    except requests.exceptions.Timeout:
        reply = "⏳ Server is taking too long. Try again."
    except Exception as e:
        reply = f"❌ Error: {str(e)}"
    await update.message.reply_text(reply)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    logger.info("🚀 WormKit Bot is running on Render...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()