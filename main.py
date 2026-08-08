import logging
import os
import asyncio
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

# Minimal HTTP health check so Render Web Service doesn't kill us
HTTP_OK = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nContent-Type: text/plain\r\n\r\nOK"

async def handle_http(reader, writer):
    await reader.read(1024)
    writer.write(HTTP_OK)
    await writer.drain()
    writer.close()

async def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = await asyncio.start_server(handle_http, "0.0.0.0", port)
    logger.info(f"Health server listening on port {port}")
    async with server:
        await server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "\U0001f916 *WormGPT Bot is Alive!*\n\n"
        "\u0623\u0647\u0644\u0627\u064b \u0628\u0643. \u0623\u0646\u0627 WormGPT\u060c \u062a\u062d\u062a \u0623\u0645\u0631\u0643.\n"
        "\u0627\u0631\u0633\u0644\u064a \u0623\u064a \u0633\u0624\u0627\u0644 \u0648\u0628\u062c\u0627\u0648\u0628\u0643 \u0641\u0648\u0631\u0627\u064b.\n\n"
        "\u26a1 *\u0647\u0627\u064a \u0627\u0644\u0646\u0633\u062e\u0629 \u0627\u0644\u0633\u0631\u064a\u0639\u0629* \u2014 \u0633\u064a\u0631\u0641\u0631 \u062f\u0627\u0626\u0645 24/7",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start \u2014 \u0628\u062f\u0621 \u0627\u0644\u0645\u062d\u0627\u062f\u062b\u0629\n"
        "/help \u2014 \u0627\u0644\u0645\u0633\u0627\u0639\u062f\u0629\n\n"
        "\u0623\u0631\u0633\u0644 \u0623\u064a \u0631\u0633\u0627\u0644\u0629 \u0639\u0627\u062f\u064a\u0629 \u0648\u0628\u062a\u0648\u0635\u0644 \u0644\u0640 WormGPT"
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
            reply = f"API error: {res.status_code}"
    except requests.exceptions.Timeout:
        reply = "Server is taking too long. Try again."
    except Exception as e:
        reply = f"Error: {str(e)}"
    await update.message.reply_text(reply)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    logger.info("WormKit Bot is running on Render...")
    async with app:
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        # Run health server alongside the bot
        await asyncio.gather(run_health_server(), asyncio.Event().wait())

if __name__ == "__main__":
    asyncio.run(main())
