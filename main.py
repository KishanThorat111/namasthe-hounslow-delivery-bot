# # main.py V1
# import os
# from dotenv import load_dotenv
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     ConversationHandler,
#     CallbackQueryHandler,
#     filters,
# )

# # Direct imports from sibling files
# import conversation_logic
# import config

# def main() -> None:
#     """Run the bot."""
#     load_dotenv()
    
#     TOKEN = os.getenv("TELEGRAM_TOKEN")
#     if not TOKEN:
#         print("❌ ERROR: TELEGRAM_TOKEN not found in .env file.")
#         return

#     application = Application.builder().token(TOKEN).build()

#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler("start", conversation_logic.start)],
#         states={
#             config.GETTING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.get_name)],
#             config.GETTING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.get_address)],
            
#             # The main ordering state, handling all buttons and text
#             config.ORDERING: [
#                 CallbackQueryHandler(conversation_logic.show_category_items, pattern="^cat_"),
#                 CallbackQueryHandler(conversation_logic.add_item_to_cart, pattern="^add_"),
#                 CallbackQueryHandler(conversation_logic.remove_item_from_cart, pattern="^rem_"),
#                 CallbackQueryHandler(conversation_logic.view_cart, pattern="^view_cart$"),
#                 CallbackQueryHandler(conversation_logic.checkout, pattern="^checkout$"),
#                 CallbackQueryHandler(conversation_logic.show_menu, pattern="^show_menu$"),
#                 CallbackQueryHandler(conversation_logic.no_op, pattern="^noop$"),
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.handle_text_order),
#             ],
            
#             # The new state waiting for the user to type 'payment done'
#             config.AWAITING_PAYMENT_CONFIRMATION: [
#                 MessageHandler(filters.Regex(r'(?i)payment done'), conversation_logic.process_payment)
#             ],
#         },
#         fallbacks=[CommandHandler("cancel", conversation_logic.cancel)],
#     )

#     application.add_handler(conv_handler)

#     print("✅ Bot is running...")
#     application.run_polling()


# if __name__ == "__main__":
#     main()




























# # main.py V2
# import os
# from dotenv import load_dotenv
# from telegram import Update
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     ConversationHandler,
#     CallbackQueryHandler,
#     filters,
#     ContextTypes,
# )

# # Direct imports
# import conversation_logic
# import config

# # --- New function to handle greetings outside of an order ---
# async def handle_idle_greetings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handles simple greetings when no conversation is active."""
#     await update.message.reply_text(
#         "Hello there! 👋 I'm ready to take your order. "
#         "Just type /start to begin!"
#     )

# def main() -> None:
#     """Run the bot."""
#     load_dotenv()
    
#     TOKEN = os.getenv("TELEGRAM_TOKEN")
#     if not TOKEN:
#         print("❌ ERROR: TELEGRAM_TOKEN not found in .env file.")
#         return

#     application = Application.builder().token(TOKEN).build()

#     entry_point_regex = r'(?i)^(hi|hello|yo|how are you|what you do|how can i start|how can i order|menu)'

#     conv_handler = ConversationHandler(
#         entry_points=[
#             CommandHandler("start", conversation_logic.start),
#             MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), conversation_logic.start)
#         ],
#         states={
#             config.GETTING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.get_name)],
#             config.GETTING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.get_address)],
#             config.ORDERING: [
#                 CallbackQueryHandler(conversation_logic.show_category_items, pattern="^cat_"),
#                 CallbackQueryHandler(conversation_logic.add_item_to_cart, pattern="^add_"),
#                 CallbackQueryHandler(conversation_logic.remove_item_from_cart, pattern="^rem_"),
#                 CallbackQueryHandler(conversation_logic.view_cart, pattern="^view_cart$"),
#                 CallbackQueryHandler(conversation_logic.checkout, pattern="^checkout$"),
#                 CallbackQueryHandler(conversation_logic.show_menu, pattern="^show_menu$"),
#                 CallbackQueryHandler(conversation_logic.no_op, pattern="^noop$"),
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.handle_text_order),
#             ],
#             # --- UPGRADE: This state now handles ANY text message ---
#             config.AWAITING_PAYMENT_CONFIRMATION: [
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.handle_payment_conversation)
#             ],
#         },
#         fallbacks=[CommandHandler("cancel", conversation_logic.cancel)],
#     )

#     application.add_handler(conv_handler)
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), handle_idle_greetings))

#     print("✅ Bot is running and ready for conversations...")
#     application.run_polling()


# if __name__ == "__main__":
#     main()


























# # main.py Confirmed
# import os
# from dotenv import load_dotenv
# from telegram import Update
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     ConversationHandler,
#     CallbackQueryHandler,
#     filters,
#     ContextTypes,
# )

# # Direct imports
# import conversation_logic
# import config

# # --- New function to handle greetings outside of an order ---
# async def handle_idle_greetings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handles simple greetings when no conversation is active."""
#     await update.message.reply_text(
#         "Hello there! 👋 I'm ready to take your order. "
#         "Just type /start to begin!"
#     )

# def main() -> None:
#     """Run the bot."""
#     load_dotenv()
    
#     TOKEN = os.getenv("TELEGRAM_TOKEN")
#     if not TOKEN:
#         print("❌ ERROR: TELEGRAM_TOKEN not found in .env file.")
#         return

#     application = Application.builder().token(TOKEN).build()

#     # Regex for catching any kind of initial greeting or question
#     entry_point_regex = r'(?i)^(hi|hello|yo|how are you|what you do|how can i start|how can i order|menu)'

#     conv_handler = ConversationHandler(
#         entry_points=[
#             CommandHandler("start", conversation_logic.start),
#             MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), conversation_logic.start)
#         ],
#         states={
#             config.GETTING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.get_name)],
#             config.GETTING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.get_address)],
#             config.ORDERING: [
#                 CallbackQueryHandler(conversation_logic.show_category_items, pattern="^cat_"),
#                 CallbackQueryHandler(conversation_logic.add_item_to_cart, pattern="^add_"),
#                 CallbackQueryHandler(conversation_logic.remove_item_from_cart, pattern="^rem_"),
#                 CallbackQueryHandler(conversation_logic.view_cart, pattern="^view_cart$"),
#                 CallbackQueryHandler(conversation_logic.checkout, pattern="^checkout$"),
#                 CallbackQueryHandler(conversation_logic.show_menu, pattern="^show_menu$"),
#                 CallbackQueryHandler(conversation_logic.no_op, pattern="^noop$"),
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.handle_text_order),
#             ],
#             config.AWAITING_PAYMENT_CONFIRMATION: [
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.handle_payment_conversation)
#             ],
#         },
#         fallbacks=[CommandHandler("cancel", conversation_logic.cancel)],
#     )

#     # The ConversationHandler has priority. It will handle messages if a conversation is active.
#     application.add_handler(conv_handler)
    
#     # --- New Handler for Idle State ---
#     # If the ConversationHandler is not active, this handler will catch greetings.
#     # The `~filters.COMMAND` ensures it doesn't interfere with /start or /cancel.
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), handle_idle_greetings))

#     print("✅ Bot is running and ready for conversations...")
#     application.run_polling()


# if __name__ == "__main__":
#     main()

























# # main.py   Working Single Bot
# import os
# from dotenv import load_dotenv
# from telegram import Update
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     ConversationHandler,
#     CallbackQueryHandler,
#     filters,
#     ContextTypes,
# )

# # Direct imports
# import conversation_logic
# import config

# async def handle_idle_greetings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handles simple greetings when no conversation is active."""
#     await update.message.reply_text(
#         "Hello there! 👋 I'm ready to take your order. "
#         "Just type /start to begin!"
#     )

# def main() -> None:
#     """Run the bot."""
#     load_dotenv()
#     TOKEN = os.getenv("TELEGRAM_TOKEN")
#     if not TOKEN:
#         print("❌ ERROR: TELEGRAM_TOKEN not found in .env file.")
#         return

#     application = Application.builder().token(TOKEN).build()

#     entry_point_regex = r'(?i)^(hi|hello|yo|how are you|what you do|how can i start|how can i order|menu)'

#     conv_handler = ConversationHandler(
#         entry_points=[
#             CommandHandler("start", conversation_logic.start),
#             MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), conversation_logic.start)
#         ],
#         states={
#             config.GETTING_NAME_AND_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.get_name_and_phone)],
#             config.GETTING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.get_address)],
#             config.CONFIRMING_ADDRESS: [CallbackQueryHandler(conversation_logic.handle_address_confirmation)],
#             config.ORDERING: [
#                 CallbackQueryHandler(conversation_logic.show_category_items, pattern="^cat_"),
#                 CallbackQueryHandler(conversation_logic.add_item_to_cart, pattern="^add_"),
#                 CallbackQueryHandler(conversation_logic.remove_item_from_cart, pattern="^rem_"),
#                 CallbackQueryHandler(conversation_logic.view_cart, pattern="^view_cart$"),
#                 CallbackQueryHandler(conversation_logic.checkout, pattern="^checkout$"),
#                 CallbackQueryHandler(conversation_logic.show_menu, pattern="^show_menu$"),
#                 CallbackQueryHandler(conversation_logic.no_op, pattern="^noop$"),
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.handle_text_order),
#             ],
#             config.AWAITING_PAYMENT_CONFIRMATION: [
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.handle_payment_conversation)
#             ],
#         },
#         fallbacks=[CommandHandler("cancel", conversation_logic.cancel)],
#     )

#     application.add_handler(conv_handler)
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), handle_idle_greetings))

#     print("✅ Bot is running and ready for conversations...")
#     application.run_polling()


# if __name__ == "__main__":
#     main()









# main.py (Final Version with All Fixes) For Local Version

# import asyncio
# import threading
# import time
# from telegram import Update
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     ConversationHandler,
#     CallbackQueryHandler,
#     filters,
# )

# import config
# import conversation_logic as customer_handlers
# import restaurant_bot as restaurant_handlers
# import database_manager as db
# import data_manager

# def run_bot_in_thread(application: Application) -> None:
#     """
#     Target function for a thread. Creates a new asyncio event loop
#     and runs the bot's polling function inside it.
#     """
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
    
#     loop.run_until_complete(application.run_polling(allowed_updates=Update.ALL_TYPES))

# def main() -> None:
#     """Initializes and runs both bots in separate threads."""

#     if not all([config.TELEGRAM_TOKEN, config.RESTAURANT_BOT_TOKEN, config.GEMINI_API_KEY, config.RESTAURANT_CHAT_ID]):
#         print("❌ CRITICAL ERROR: One or more required environment variables are missing.")
#         return

#     db.setup_database()
#     data_manager._initialize_menu()

#     customer_app = Application.builder().token(config.TELEGRAM_TOKEN).build()
#     restaurant_app = Application.builder().token(config.RESTAURANT_BOT_TOKEN).build()

#     entry_point_regex = r'(?i)^(hi|hello|yo|menu|order|start)$'

#     conv_handler = ConversationHandler(
#         entry_points=[
#             CommandHandler("start", customer_handlers.start),
#             MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), customer_handlers.start)
#         ],
#         states={
#             config.GETTING_NAME_AND_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, customer_handlers.get_name_and_phone)],
#             config.GETTING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, customer_handlers.get_address)],
#             config.CONFIRMING_ADDRESS: [CallbackQueryHandler(customer_handlers.handle_address_confirmation)],
#             config.ORDERING: [
#                 CallbackQueryHandler(customer_handlers.show_category_items, pattern="^cat_"),
#                 CallbackQueryHandler(customer_handlers.add_item_to_cart, pattern="^add_"),
#                 CallbackQueryHandler(customer_handlers.remove_item_from_cart, pattern="^rem_"),
#                 CallbackQueryHandler(customer_handlers.view_cart, pattern="^view_cart$"),
#                 CallbackQueryHandler(customer_handlers.checkout, pattern="^checkout$"),
#                 CallbackQueryHandler(customer_handlers.show_menu, pattern="^show_menu$"),
#                 CallbackQueryHandler(customer_handlers.no_op, pattern="^noop$"),
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, customer_handlers.handle_text_order),
#             ],
#             config.AWAITING_SCREENSHOT: [
#                 MessageHandler(filters.PHOTO, customer_handlers.handle_screenshot),
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, customer_handlers.handle_text_instead_of_screenshot),
#             ],
#             # FIX: Added entry points to the PENDING_CONFIRMATION state
#             # This allows the user to start a new order after the current one is confirmed.
#             config.PENDING_CONFIRMATION: [
#                 CommandHandler("start", customer_handlers.start),
#                 MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), customer_handlers.start),
#                 MessageHandler(filters.ALL, customer_handlers.pending_message) # Catches any other message
#             ],
#         },
#         fallbacks=[CommandHandler("cancel", customer_handlers.cancel)],
#         per_user=True,
#         per_chat=True,
#     )
#     customer_app.add_handler(conv_handler)

#     restaurant_handlers.setup_restaurant_bot_handlers(restaurant_app, customer_app)
#     customer_app.bot_data['restaurant_bot'] = restaurant_app.bot

#     print("✅ Customer and Restaurant bots initialized.")
    
#     customer_thread = threading.Thread(target=run_bot_in_thread, args=(customer_app,))
#     restaurant_thread = threading.Thread(target=run_bot_in_thread, args=(restaurant_app,))

#     customer_thread.daemon = True
#     restaurant_thread.daemon = True

#     print("🤖 Starting both bots in separate threads... Press Ctrl+C to stop.")
    
#     customer_thread.start()
#     restaurant_thread.start()
    
#     # FIX: Replaced .join() with a loop for better Ctrl+C handling.
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("\n🛑 Shutting down bots...")

#     print("✅ Program has been shut down.")

# if __name__ == "__main__":
#     main()





























# main.py (Final Production Version with Threading and Signal Fix)

import asyncio
import threading
import time
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)

import config
import conversation_logic as customer_handlers
import restaurant_bot as restaurant_handlers
import database_manager as db
import data_manager

def run_bot_in_thread(application: Application) -> None:
    """
    Target function for a thread. Creates a new asyncio event loop
    and runs the bot's polling function inside it.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # The crucial change is here: stop_signals=None
    # This tells the library not to set up its own signal handlers in this thread,
    # preventing the "main thread" error inside Docker.
    loop.run_until_complete(application.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None))

def main() -> None:
    """Initializes and runs both bots in separate threads."""

    if not all([config.TELEGRAM_TOKEN, config.RESTAURANT_BOT_TOKEN, config.GEMINI_API_KEY, config.RESTAURANT_CHAT_ID]):
        print("❌ CRITICAL ERROR: One or more required environment variables are missing.")
        return

    db.setup_database()
    data_manager._initialize_menu()

    customer_app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    restaurant_app = Application.builder().token(config.RESTAURANT_BOT_TOKEN).build()

    entry_point_regex = r'(?i)^(hi|hello|yo|menu|order|start)$'

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", customer_handlers.start),
            MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), customer_handlers.start)
        ],
        states={
            config.GETTING_NAME_AND_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, customer_handlers.get_name_and_phone)],
            config.GETTING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, customer_handlers.get_address)],
            config.CONFIRMING_ADDRESS: [CallbackQueryHandler(customer_handlers.handle_address_confirmation)],
            config.ORDERING: [
                CallbackQueryHandler(customer_handlers.show_category_items, pattern="^cat_"),
                CallbackQueryHandler(customer_handlers.add_item_to_cart, pattern="^add_"),
                CallbackQueryHandler(customer_handlers.remove_item_from_cart, pattern="^rem_"),
                CallbackQueryHandler(customer_handlers.view_cart, pattern="^view_cart$"),
                CallbackQueryHandler(customer_handlers.checkout, pattern="^checkout$"),
                CallbackQueryHandler(customer_handlers.show_menu, pattern="^show_menu$"),
                CallbackQueryHandler(customer_handlers.no_op, pattern="^noop$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, customer_handlers.handle_text_order),
            ],
            config.AWAITING_SCREENSHOT: [
                MessageHandler(filters.PHOTO, customer_handlers.handle_screenshot),
                MessageHandler(filters.TEXT & ~filters.COMMAND, customer_handlers.handle_text_instead_of_screenshot),
            ],
            config.PENDING_CONFIRMATION: [
                CommandHandler("start", customer_handlers.start),
                MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), customer_handlers.start),
                MessageHandler(filters.ALL, customer_handlers.pending_message)
            ],
        },
        fallbacks=[CommandHandler("cancel", customer_handlers.cancel)],
        per_user=True,
        per_chat=True,
    )
    customer_app.add_handler(conv_handler)

    restaurant_handlers.setup_restaurant_bot_handlers(restaurant_app, customer_app)
    customer_app.bot_data['restaurant_bot'] = restaurant_app.bot

    print("✅ Customer and Restaurant bots initialized.")
    
    customer_thread = threading.Thread(target=run_bot_in_thread, args=(customer_app,))
    restaurant_thread = threading.Thread(target=run_bot_in_thread, args=(restaurant_app,))

    customer_thread.daemon = True
    restaurant_thread.daemon = True

    print("🤖 Starting both bots in separate threads...")
    
    customer_thread.start()
    restaurant_thread.start()
    
    # This loop keeps the main thread alive and allows the program to
    # catch a KeyboardInterrupt (Ctrl+C) gracefully.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down bots...")

    print("✅ Program has been shut down.")

if __name__ == "__main__":
    main()