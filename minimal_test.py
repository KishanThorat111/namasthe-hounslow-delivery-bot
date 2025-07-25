# minimal_test.py
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
# PASTE YOUR CUSTOMER-FACING BOT TOKEN DIRECTLY HERE
TOKEN = "7897181184:AAFmvbzR-aiJ1CnRwhv4qfF6fhst-XIObhg"

# --- Enable Logging ---
# This will give us much more detailed information than print()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the command /start is issued."""
    logger.info("Command /start received")
    await update.message.reply_text("Hi! The minimal bot is working. I will echo your messages.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    logger.info(f"Echoing message: {update.message.text}")
    await update.message.reply_text(update.message.text)

# --- Main Application Logic ---
async def main() -> None:
    """Start the bot."""
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    try:
        logger.info("Starting minimal bot...")
        await app.initialize()
        await app.updater.start_polling()

        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping minimal bot...")
    finally:
        if app.updater and app.updater._running:
            await app.updater.stop()
        if app._initialized:
            await app.shutdown()
        logger.info("Minimal bot shut down.")

if __name__ == "__main__":
    asyncio.run(main())