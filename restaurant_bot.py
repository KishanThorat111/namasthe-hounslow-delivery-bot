from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
import database_manager as db
import services

async def handle_order_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'Confirm' or 'Reject' button presses from the restaurant staff."""
    query = update.callback_query
    await query.answer()

    action, order_ref = query.data.split('_', 1)
    admin_user = query.from_user.full_name

    # FIX: Use context.application.bot_data to get the shared application object
    customer_app = context.application.bot_data.get('customer_app')
    if not customer_app:
        print("FATAL: Customer app not found in restaurant bot context!")
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ ERROR: COULD NOT NOTIFY CUSTOMER.", parse_mode='Markdown')
        return

    customer_chat_id = db.get_order_customer_id(order_ref)
    if not customer_chat_id:
        print(f"ERROR: Could not find customer ID for order {order_ref}")
        await query.edit_message_caption(caption=query.message.caption + f"\n\n❌ ERROR: Customer ID not found for order {order_ref}.", parse_mode='Markdown')
        return

    if action == "confirm":
        db.update_order_status(order_ref, 'confirmed')
        
        await customer_app.bot.send_message(
            chat_id=customer_chat_id,
            text=f"🎉 Great news! Your order *#{order_ref}* has been *CONFIRMED* by the restaurant.\n\nIt's now being prepared and will be with you shortly. Thank you for your order!",
            parse_mode='Markdown'
        )
        
        new_caption = query.message.caption + f"\n\n--- \n✅ *Confirmed* by {admin_user} ---"
        await query.edit_message_caption(caption=new_caption, parse_mode='Markdown', reply_markup=None)
        print(f"LOG: Order {order_ref} confirmed by {admin_user}.")

        # Schedule the Google Sheets sync
        order_details = db.get_order_details(order_ref)
        if order_details and context.application.job_queue:
             context.application.job_queue.run_once(services.sync_order_to_sheet, when=0, data=order_details)

    elif action == "reject":
        db.update_order_status(order_ref, 'rejected')

        await customer_app.bot.send_message(
            chat_id=customer_chat_id,
            text=f"😥 We are very sorry, but your order *#{order_ref}* has been *REJECTED* by the restaurant. This may be due to an issue with payment verification or an item being out of stock. Please contact the restaurant directly or start a new order with /start.",
            parse_mode='Markdown'
        )
        
        new_caption = query.message.caption + f"\n\n--- \n❌ *Rejected* by {admin_user} ---"
        await query.edit_message_caption(caption=new_caption, parse_mode='Markdown', reply_markup=None)
        print(f"LOG: Order {order_ref} rejected by {admin_user}.")

def setup_restaurant_bot_handlers(application: Application, customer_app: Application):
    """Sets up the handlers for the restaurant bot."""
    application.bot_data['customer_app'] = customer_app
    
    application.add_handler(CallbackQueryHandler(handle_order_action, pattern=r"^(confirm_|reject_)"))


# # restaurant_bot.py

# import logging
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()

# # Configure logging for the restaurant bot
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# # --- Get bot token from config ---
# RESTAURANT_BOT_TOKEN = os.getenv("RESTAURANT_BOT_TOKEN")
# if not RESTAURANT_BOT_TOKEN:
#     logger.error("RESTAURANT_BOT_TOKEN not found in .env file.")
#     exit("RESTAURANT_BOT_TOKEN is missing. Please set it in your .env file.")

# # --- Handlers for the Restaurant Bot ---

# async def start_restaurant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Sends a welcome message for the restaurant bot."""
#     # --- ADD THESE LINES TEMPORARILY ---
#     chat_id = update.effective_chat.id
#     logger.info(f"Restaurant bot received /start from {update.effective_user.full_name} (ID: {update.effective_user.id}) in chat ID: {chat_id}")
#     await update.message.reply_text(f"Hello! This chat's ID is: `{chat_id}`", parse_mode='Markdown')
#     # --- END TEMPORARY LINES ---

#     await update.message.reply_text(
#         "Hello! I am the Namasthe Hounslow Restaurant Bot. "
#         "I will notify you about new customer orders. "
#         "Make sure this bot is added to your staff's notification group!"
#     )

# async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Echoes any non-command message received by the restaurant bot (for testing)."""
#     # --- ADD THESE LINES TEMPORARILY (or just the logging) ---
#     chat_id = update.effective_chat.id
#     logger.info(f"Restaurant bot received message from {update.effective_user.full_name} (ID: {update.effective_user.id}) in chat ID: {chat_id}: {update.message.text}")
#     await update.message.reply_text(f"Restaurant bot received: {update.message.text}. Chat ID is: `{chat_id}`", parse_mode='Markdown')
#     # --- END TEMPORARY LINES ---


# def run_restaurant_bot() -> None:
#     """Runs the restaurant bot."""
#     application = Application.builder().token(RESTAURANT_BOT_TOKEN).build()

#     # Handlers
#     application.add_handler(CommandHandler("start", start_restaurant))
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message)) 

#     logger.info("Restaurant Bot is starting polling...")
#     application.run_polling(allowed_updates=Update.ALL_TYPES)


# if __name__ == '__main__':
#     run_restaurant_bot()