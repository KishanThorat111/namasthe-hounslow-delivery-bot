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

























# main.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# Direct imports
import conversation_logic
import config

async def handle_idle_greetings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles simple greetings when no conversation is active."""
    await update.message.reply_text(
        "Hello there! 👋 I'm ready to take your order. "
        "Just type /start to begin!"
    )

def main() -> None:
    """Run the bot."""
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        print("❌ ERROR: TELEGRAM_TOKEN not found in .env file.")
        return

    application = Application.builder().token(TOKEN).build()

    entry_point_regex = r'(?i)^(hi|hello|yo|how are you|what you do|how can i start|how can i order|menu)'

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", conversation_logic.start),
            MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), conversation_logic.start)
        ],
        states={
            config.GETTING_NAME_AND_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.get_name_and_phone)],
            config.GETTING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.get_address)],
            config.CONFIRMING_ADDRESS: [CallbackQueryHandler(conversation_logic.handle_address_confirmation)],
            config.ORDERING: [
                CallbackQueryHandler(conversation_logic.show_category_items, pattern="^cat_"),
                CallbackQueryHandler(conversation_logic.add_item_to_cart, pattern="^add_"),
                CallbackQueryHandler(conversation_logic.remove_item_from_cart, pattern="^rem_"),
                CallbackQueryHandler(conversation_logic.view_cart, pattern="^view_cart$"),
                CallbackQueryHandler(conversation_logic.checkout, pattern="^checkout$"),
                CallbackQueryHandler(conversation_logic.show_menu, pattern="^show_menu$"),
                CallbackQueryHandler(conversation_logic.no_op, pattern="^noop$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.handle_text_order),
            ],
            config.AWAITING_PAYMENT_CONFIRMATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_logic.handle_payment_conversation)
            ],
        },
        fallbacks=[CommandHandler("cancel", conversation_logic.cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(entry_point_regex), handle_idle_greetings))

    print("✅ Bot is running and ready for conversations...")
    application.run_polling()


if __name__ == "__main__":
    main()
