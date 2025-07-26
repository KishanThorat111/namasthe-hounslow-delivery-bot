
# # conversation_logic.py V1
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import ContextTypes, ConversationHandler
# import time

# # Direct imports from sibling files
# import config
# import services
# import ai_engine
# from data_manager import get_menu_as_dict, get_item_details

# # --- Helper Functions for Building Keyboards ---

# def get_cart_summary(cart):
#     """
#     Generates a summary of the cart with total price.
#     This function was missing and has now been added back.
#     """
#     if not cart:
#         return "Your cart is currently empty. 🛒", 0.0

#     summary = "🛒 *Your Current Order:*\n\n"
#     total_price = 0.0
#     for item_name, details in cart.items():
#         item_total = details['price'] * details['quantity']
#         summary += f"• {details['quantity']}x {item_name} (£{details['price']:.2f} each) = *£{item_total:.2f}*\n"
#         total_price += item_total
    
#     summary += f"\n*Subtotal: £{total_price:.2f}*"
#     return summary, total_price

# def build_menu_keyboard():
#     """Builds the keyboard for the main menu categories."""
#     menu = get_menu_as_dict()
#     if not menu:
#         return None
    
#     categories = list(menu.keys())
#     keyboard = [
#         [InlineKeyboardButton(f"🍛 {cat}", callback_data=f"cat_{cat}")] for cat in categories
#     ]
#     keyboard.append([InlineKeyboardButton("🛒 View Cart & Checkout", callback_data="view_cart")])
#     return InlineKeyboardMarkup(keyboard)

# def build_items_keyboard(category):
#     """Builds the keyboard for items within a specific category."""
#     menu = get_menu_as_dict()
#     items = menu.get(category, [])
#     keyboard = [
#         [InlineKeyboardButton(f"{item['itemname']} - £{item['price']:.2f}", callback_data=f"add_{item['itemname']}")]
#         for item in items
#     ]
#     keyboard.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="show_menu")])
#     return InlineKeyboardMarkup(keyboard)

# def build_cart_keyboard(cart):
#     """Builds the dynamic keyboard for the cart view with +/- buttons."""
#     keyboard = []
#     for item_name in cart.keys():
#         # Each row has a minus button, the item name/quantity, and a plus button
#         keyboard.append([
#             InlineKeyboardButton(f"➖", callback_data=f"rem_{item_name}"),
#             InlineKeyboardButton(f"{cart[item_name]['quantity']}x {item_name}", callback_data="noop"), # No operation button
#             InlineKeyboardButton(f"➕", callback_data=f"add_{item_name}")
#         ])
    
#     # Add the main action buttons at the bottom
#     keyboard.append([InlineKeyboardButton("✅ Proceed to Checkout", callback_data="checkout")])
#     keyboard.append([InlineKeyboardButton("🛍️ Continue Shopping", callback_data="show_menu")])
#     return InlineKeyboardMarkup(keyboard)


# # --- State Handlers ---

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Starts a new conversation, clearing any previous user data."""
#     context.user_data.clear()
#     context.user_data['cart'] = {}
#     context.user_data['chat_history'] = []
    
#     await update.message.reply_text(
#         f"👋 Welcome to {config.RESTAURANT_NAME}! I'm Namaste-Bot, your personal food assistant.\n\n"
#         "To get started, could you please tell me your full name?"
#     )
#     return config.GETTING_NAME

# async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_name = update.message.text
#     context.user_data['name'] = user_name
#     await update.message.reply_text(
#         f"Thank you, {user_name}! 🙏\n\n"
#         "Please provide your full delivery address and postcode, so I can check we can deliver to you."
#     )
#     return config.GETTING_ADDRESS

# async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     address = update.message.text
#     context.user_data['address'] = address
#     await update.message.reply_text("👍 Thank you. One moment while I check your address...")
#     distance = services.get_distance_in_miles(address)

#     if distance is None:
#         await update.message.reply_text("I'm sorry, I couldn't verify that address. Could you please try again?")
#         return config.GETTING_ADDRESS

#     if distance > config.DELIVERY_RADIUS_MILES:
#         await update.message.reply_text(f"We're so sorry, but at {distance:.1f} miles away, you are outside our delivery radius. 😥")
#         return ConversationHandler.END

#     context.user_data['delivery_charge'] = 0 if distance <= config.FREE_DELIVERY_RADIUS_MILES else config.DELIVERY_CHARGE
#     delivery_message = "🎉 Great news! You qualify for *FREE delivery*." if context.user_data['delivery_charge'] == 0 else f"Excellent, you're in our delivery area! A delivery charge of £{config.DELIVERY_CHARGE:.2f} will apply."
    
#     await update.message.reply_text(f"{delivery_message}\n\nLet's get your order started! 🍽️")
#     return await show_menu(update, context)


# # --- Menu, Cart, and Ordering Logic ---

# async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Displays the main menu categories."""
#     reply_markup = build_menu_keyboard()
#     if not reply_markup:
#         await update.message.reply_text("Sorry, the menu is currently unavailable.")
#         return config.ORDERING

#     message_text = "Please choose a category to explore:"
#     if update.callback_query:
#         await update.callback_query.answer()
#         await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
#     else:
#         await update.message.reply_text(message_text, reply_markup=reply_markup)
        
#     return config.ORDERING

# async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Displays items for a selected category."""
#     query = update.callback_query
#     category = query.data.split("_")[1]
#     reply_markup = build_items_keyboard(category)
#     await query.answer()
#     await query.edit_message_text(f"Here are the items for *{category}*:", reply_markup=reply_markup, parse_mode='Markdown')
#     return config.ORDERING

# async def add_item_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Adds an item to the cart and shows the updated cart."""
#     query = update.callback_query
#     item_name = query.data.split("_", 1)[1]
#     item_details = get_item_details(item_name)
    
#     if item_details:
#         cart = context.user_data.get('cart', {})
#         if item_name in cart:
#             cart[item_name]['quantity'] += 1
#         else:
#             cart[item_name] = {'quantity': 1, 'price': item_details['price']}
#         context.user_data['cart'] = cart
#         return await view_cart(update, context)
#     else:
#         await query.answer("Sorry, that item could not be found.", show_alert=True)
#         return config.ORDERING

# async def remove_item_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Removes one instance of an item from the cart and shows the updated cart."""
#     query = update.callback_query
#     item_name = query.data.split("_", 1)[1]
#     cart = context.user_data.get('cart', {})

#     if item_name in cart:
#         cart[item_name]['quantity'] -= 1
#         if cart[item_name]['quantity'] <= 0:
#             del cart[item_name]
#         context.user_data['cart'] = cart
    
#     return await view_cart(update, context)

# async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Displays the interactive cart view."""
#     query = update.callback_query
#     cart = context.user_data.get('cart', {})
    
#     if not cart:
#         await query.answer("Your cart is empty!", show_alert=True)
#         return await show_menu(update, context)

#     summary_text, _ = get_cart_summary(cart)
#     reply_markup = build_cart_keyboard(cart)
    
#     await query.answer()
#     await query.edit_message_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
#     return config.ORDERING

# async def handle_text_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Handles natural language text inputs for ordering using the AI."""
#     user_message = update.message.text
#     if user_message.lower().strip() == "menu":
#         return await show_menu(update, context)

#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message)
#     await update.message.reply_text(ai_response.get("reply", "Could you rephrase that?"))
#     return config.ORDERING


# # --- Checkout and Payment Logic ---

# async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Shows final bill and presents dummy payment details."""
#     query = update.callback_query
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await query.answer("Your cart is empty!", show_alert=True)
#         return config.ORDERING

#     _, subtotal = get_cart_summary(cart)
#     delivery_charge = context.user_data.get('delivery_charge', 0)
#     total_price = subtotal + delivery_charge
#     context.user_data['total_price'] = total_price
    
#     order_ref = f"NH-{int(time.time())}"
#     context.user_data['order_ref'] = order_ref

#     payment_details = (
#         f"🧾 *Final Bill*\n\n"
#         f"Subtotal: *£{subtotal:.2f}*\n"
#         f"Delivery Charge: *£{delivery_charge:.2f}*\n"
#         f"---------------------\n"
#         f"Total to Pay: *£{total_price:.2f}*\n\n"
#         f"🏦 *Payment Details (For Demo)*\n"
#         f"Please make a bank transfer to the following account:\n\n"
#         f"  - *Account Name:* Namaste-Bot Ltd\n"
#         f"  - *Sort Code:* 01-02-03\n"
#         f"  - *Account No:* 12345678\n"
#         f"  - *Reference:* `{order_ref}`\n\n"
#         f"Once payment is made, please reply with the message `payment done` to confirm your order."
#     )
    
#     await query.answer()
#     await query.edit_message_text(payment_details, parse_mode='Markdown')
#     return config.AWAITING_PAYMENT_CONFIRMATION


# async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Confirms payment after user types 'payment done'."""
#     if 'payment done' in update.message.text.lower():
#         services.log_order_to_sheet(
#             customer_name=context.user_data.get('name'),
#             customer_address=context.user_data.get('address'),
#             order_details=str(context.user_data.get('cart', {})),
#             total_price=context.user_data.get('total_price', 0)
#         )
#         await update.message.reply_text(
#             f"✅ Payment confirmed! Thank you for your order `#{context.user_data.get('order_ref')}`.\n\n"
#             "Your delicious meal will be prepared and delivered shortly. Enjoy! 🍛",
#             parse_mode='Markdown'
#         )
#         return ConversationHandler.END
#     else:
#         await update.message.reply_text("I'm waiting for payment confirmation. Please type 'payment done' or /cancel.")
#         return config.AWAITING_PAYMENT_CONFIRMATION

# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Cancels and ends the conversation."""
#     await update.message.reply_text("Order cancelled. Hope to see you again soon! 👋")
#     context.user_data.clear()
#     return ConversationHandler.END

# # A dummy handler for the item name button in the cart
# async def no_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """A dummy function that does nothing, used for unclickable buttons."""
#     await update.callback_query.answer()






















# # conversation_logic.py V2
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import ContextTypes, ConversationHandler
# import time

# # Direct imports from sibling files
# import config
# import services
# import ai_engine
# from data_manager import get_menu_as_dict, get_item_details

# # --- Helper Functions for Building Keyboards ---

# def get_cart_summary(cart):
#     """Generates a summary of the cart with total price."""
#     if not cart:
#         return "Your cart is currently empty. 🛒", 0.0

#     summary = "🛒 *Your Current Order:*\n\n"
#     total_price = 0.0
#     for item_name, details in cart.items():
#         item_total = details['price'] * details['quantity']
#         summary += f"• {details['quantity']}x {item_name} (£{details['price']:.2f} each) = *£{item_total:.2f}*\n"
#         total_price += item_total
    
#     summary += f"\n*Subtotal: £{total_price:.2f}*"
#     return summary, total_price

# def build_menu_keyboard():
#     """Builds the keyboard for the main menu categories with matching emojis."""
#     menu = get_menu_as_dict()
#     if not menu:
#         return None
    
#     # --- NEW: Emoji mapping for categories ---
#     emoji_map = {
#         "BREAKFAST": "🥞",
#         "STARTERS": "🍢",
#         "CURRIES": "🍛",
#         "TANDOORI": "🔥",
#         "BIRYANIS": "🍚",
#         "RICE/NOODLES": "🍜",
#         "BREADS": "🍞",
#         "WEEKEND SPECIALS": "⭐",
#         "DESSERTS": "🍰",
#         "COCKTAILS": "🍸",
#         "MOCKTAILS": "🍹",
#         "WHISKEY/SCOTCH": "🥃",
#         "BRANDI": "🍷",
#         "TEQUILA": "🌵",
#         "VODKA": "🍸",
#         "GIN & BOTANICAL": "🌿",
#         "RUM": "🧉",
#         "BEERS": "🍺",
#         "WINES (125 ML)": "🍷"
#     }
    
#     categories = list(menu.keys())
#     keyboard = [
#         # Use .get(cat.upper(), "🍽️") to provide a default emoji if a category is not in the map
#         [InlineKeyboardButton(f"{emoji_map.get(cat.upper(), '🍽️')} {cat}", callback_data=f"cat_{cat}")] for cat in categories
#     ]
#     keyboard.append([InlineKeyboardButton("🛒 View Cart & Checkout", callback_data="view_cart")])
#     return InlineKeyboardMarkup(keyboard)

# def build_items_keyboard(category):
#     """Builds the keyboard for items within a specific category."""
#     menu = get_menu_as_dict()
#     items = menu.get(category, [])
#     keyboard = [
#         [InlineKeyboardButton(f"{item['itemname']} - £{item['price']:.2f}", callback_data=f"add_{item['itemname']}")]
#         for item in items
#     ]
#     keyboard.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="show_menu")])
#     return InlineKeyboardMarkup(keyboard)

# def build_cart_keyboard(cart):
#     """Builds the dynamic keyboard for the cart view with +/- buttons."""
#     keyboard = []
#     for item_name in cart.keys():
#         keyboard.append([
#             InlineKeyboardButton(f"➖", callback_data=f"rem_{item_name}"),
#             InlineKeyboardButton(f"{cart[item_name]['quantity']}x {item_name}", callback_data="noop"),
#             InlineKeyboardButton(f"➕", callback_data=f"add_{item_name}")
#         ])
    
#     keyboard.append([InlineKeyboardButton("✅ Proceed to Checkout", callback_data="checkout")])
#     keyboard.append([InlineKeyboardButton("🛍️ Continue Ordering", callback_data="show_menu")])
#     return InlineKeyboardMarkup(keyboard)


# # --- State Handlers ---

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Starts a new conversation, clearing any previous user data."""
#     context.user_data.clear()
#     context.user_data['cart'] = {}
#     context.user_data['chat_history'] = []
    
#     start_message = f"🙏 Welcome to {config.RESTAURANT_NAME}! I'm Namaste-Bot, your personal food assistant.\n\nTo get started, could you please tell me your full name?"
#     context.user_data['chat_history'].append(f"AI: {start_message}")
#     await update.message.reply_text(start_message)
    
#     return config.GETTING_NAME

# async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_message = update.message.text
#     context.user_data['chat_history'].append(f"User: {user_message}")
    
#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.GETTING_NAME)
#     intent = ai_response.get("intent")
    
#     if intent == "PROVIDE_NAME":
#         user_name = ai_response.get("payload")
#         context.user_data['name'] = user_name
#         reply_message = f"Thank you, {user_name}! 🙏\n\nPlease provide your full delivery address and postcode."
#         context.user_data['chat_history'].append(f"AI: {reply_message}")
#         await update.message.reply_text(reply_message)
#         return config.GETTING_ADDRESS
        
#     elif intent == "CHITCHAT":
#         reply = ai_response.get("reply", "That's nice! Could you tell me your name so we can get started?")
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         return config.GETTING_NAME
        
#     else:
#         reply = "I'm sorry, I was expecting a name. Could you please provide your full name to continue?"
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         return config.GETTING_NAME

# async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_message = update.message.text
#     context.user_data['chat_history'].append(f"User: {user_message}")
#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.GETTING_ADDRESS)
#     intent = ai_response.get("intent")
    
#     if intent == "PROVIDE_ADDRESS":
#         address = ai_response.get("payload")
#         context.user_data['address'] = address
#         await update.message.reply_text("👍 Thank you. One moment while I check your address...")
#         distance = services.get_distance_in_miles(address)
#         if distance is None:
#             await update.message.reply_text("I'm sorry, I couldn't verify that address. Could you please try again with a valid UK address and postcode?")
#             return config.GETTING_ADDRESS
#         if distance > config.DELIVERY_RADIUS_MILES:
#             await update.message.reply_text(f"We're so sorry, but at {distance:.1f} miles away, you are outside our delivery radius. 😥")
#             return ConversationHandler.END
#         context.user_data['delivery_charge'] = 0 if distance <= config.FREE_DELIVERY_RADIUS_MILES else config.DELIVERY_CHARGE
#         delivery_message = "🎉 Great news! You qualify for *FREE delivery*." if context.user_data['delivery_charge'] == 0 else f"Excellent, you're in our delivery area! A delivery charge of £{config.DELIVERY_CHARGE:.2f} will apply."
#         await update.message.reply_text(f"{delivery_message}\n\nLet's get your order started! 🍽️")
#         return await show_menu(update, context)

#     elif intent == "CHITCHAT":
#         reply = ai_response.get("reply", "I see! To continue, I'll need your delivery address please.")
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         return config.GETTING_ADDRESS
        
#     else:
#         reply = "I was expecting an address. Could you please provide your full delivery address and postcode?"
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         return config.GETTING_ADDRESS

# # --- Menu, Cart, and Ordering Logic ---

# async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Displays the main menu categories."""
#     reply_markup = build_menu_keyboard()
#     message_text = "Please choose a category to explore:"
#     if update.callback_query:
#         await update.callback_query.answer()
#         await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
#     else:
#         await update.message.reply_text(message_text, reply_markup=reply_markup)
#     return config.ORDERING

# async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Displays items for a selected category."""
#     query = update.callback_query
#     category = query.data.split("_")[1]
#     reply_markup = build_items_keyboard(category)
#     await query.answer()
#     await query.edit_message_text(f"Here are the items for *{category}*:", reply_markup=reply_markup, parse_mode='Markdown')
#     return config.ORDERING

# async def add_item_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Adds an item to the cart and shows the updated cart."""
#     query = update.callback_query
#     item_name = query.data.split("_", 1)[1]
#     item_details = get_item_details(item_name)
#     if item_details:
#         cart = context.user_data.get('cart', {})
#         if item_name in cart:
#             cart[item_name]['quantity'] += 1
#         else:
#             cart[item_name] = {'quantity': 1, 'price': item_details['price']}
#         context.user_data['cart'] = cart
#         return await view_cart(update, context)
#     else:
#         await query.answer("Sorry, that item could not be found.", show_alert=True)
#         return config.ORDERING

# async def remove_item_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Removes one instance of an item from the cart and shows the updated cart."""
#     query = update.callback_query
#     item_name = query.data.split("_", 1)[1]
#     cart = context.user_data.get('cart', {})
#     if item_name in cart:
#         cart[item_name]['quantity'] -= 1
#         if cart[item_name]['quantity'] <= 0:
#             del cart[item_name]
#         context.user_data['cart'] = cart
#     return await view_cart(update, context)

# async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Displays the interactive cart view."""
#     query = update.callback_query
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await query.answer("Your cart is empty!", show_alert=True)
#         return await show_menu(update, context)
#     summary_text, _ = get_cart_summary(cart)
#     reply_markup = build_cart_keyboard(cart)
#     await query.answer()
#     await query.edit_message_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
#     return config.ORDERING

# async def handle_text_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Handles natural language text inputs for ordering using the AI."""
#     user_message = update.message.text
#     context.user_data['chat_history'].append(f"User: {user_message}")
#     # --- NEW: Handle "menu" text input gracefully ---
#     if user_message.lower().strip() == "menu":
#         return await show_menu(update, context)

#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.ORDERING)
#     intent = ai_response.get("intent")
#     reply_text = ai_response.get("reply", "Sorry, I didn't quite catch that.")
#     context.user_data['chat_history'].append(f"AI: {reply_text}")

#     if intent == "ADD_TO_ORDER":
#         cart = context.user_data.get('cart', {})
#         for item_data in ai_response.get("items", []):
#             item_name = item_data.get("name")
#             item_details = get_item_details(item_name)
#             if item_details:
#                 if item_name in cart:
#                     cart[item_name]['quantity'] += item_data.get("quantity", 1)
#                 else:
#                     cart[item_name] = {'quantity': 1, 'price': item_details['price']}
#         context.user_data['cart'] = cart
    
#     elif intent == "CONFIRM_ORDER":
#         await update.message.reply_text(reply_text)
#         return await view_cart_from_text(update, context)

#     await update.message.reply_text(reply_text)
#     return config.ORDERING

# async def view_cart_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """A version of view_cart that sends a new message instead of editing one."""
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await update.message.reply_text("Your cart is empty!", reply_markup=build_menu_keyboard())
#         return config.ORDERING
#     summary_text, _ = get_cart_summary(cart)
#     reply_markup = build_cart_keyboard(cart)
#     await update.message.reply_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
#     return config.ORDERING

# # --- Checkout and Payment Logic ---

# async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Shows final bill and presents dummy payment details."""
#     query = update.callback_query
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await query.answer("Your cart is empty!", show_alert=True)
#         return config.ORDERING
#     _, subtotal = get_cart_summary(cart)
#     delivery_charge = context.user_data.get('delivery_charge', 0)
#     total_price = subtotal + delivery_charge
#     context.user_data['total_price'] = total_price
#     order_ref = f"NH-{int(time.time())}"
#     context.user_data['order_ref'] = order_ref
#     payment_details = (
#         f"🧾 *Final Bill*\n\n"
#         f"Subtotal: *£{subtotal:.2f}*\n"
#         f"Delivery Charge: *£{delivery_charge:.2f}*\n"
#         f"---------------------\n"
#         f"Total to Pay: *£{total_price:.2f}*\n\n"
#         f"🏦 *Payment Details (For Demo)*\n"
#         f"Please make a bank transfer to the following account:\n\n"
#         f"  - *Account Name:* Namaste-Bot Ltd\n"
#         f"  - *Sort Code:* 01-02-03\n"
#         f"  - *Account No:* 12345678\n"
#         f"  - *Reference:* `{order_ref}`\n\n"
#         f"Once payment is made, please reply with a confirmation message (e.g., 'payment done') to complete your order."
#     )
#     await query.answer()
#     await query.edit_message_text(payment_details, parse_mode='Markdown')
#     return config.AWAITING_PAYMENT_CONFIRMATION

# async def handle_payment_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Handles all messages during the payment phase using the AI."""
#     user_message = update.message.text
#     context.user_data['chat_history'].append(f"User: {user_message}")
    
#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.AWAITING_PAYMENT_CONFIRMATION)
#     intent = ai_response.get("intent")

#     if intent == "CONFIRM_PAYMENT":
#         services.log_order_to_sheet(
#             customer_name=context.user_data.get('name'),
#             customer_address=context.user_data.get('address'),
#             order_details=str(context.user_data.get('cart', {})),
#             total_price=context.user_data.get('total_price', 0)
#         )
#         await update.message.reply_text(
#             f"✅ Payment confirmed! Thank you for your order `#{context.user_data.get('order_ref')}`.\n\n"
#             "Your delicious meal will be prepared and delivered shortly. Enjoy! 🍛",
#             parse_mode='Markdown'
#         )
#         return ConversationHandler.END
    
#     else: # CHITCHAT or ERROR
#         reply = ai_response.get("reply", "I'm waiting for payment confirmation. Please type 'payment done' or /cancel.")
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         return config.AWAITING_PAYMENT_CONFIRMATION

# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Cancels and ends the conversation."""
#     await update.message.reply_text("Order cancelled. Hope to see you again soon! 👋")
#     context.user_data.clear()
#     return ConversationHandler.END

# async def no_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """A dummy function that does nothing, used for unclickable buttons."""
#     await update.callback_query.answer()

































# # conversation_logic.py confirmed
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import ContextTypes, ConversationHandler
# from telegram.error import BadRequest
# import time

# # Direct imports
# import config
# import services
# import ai_engine
# from data_manager import get_menu_as_dict, get_item_details

# # --- Helper Functions ---
# def get_cart_summary(cart):
#     if not cart: return "Your cart is currently empty. 🛒", 0.0
#     summary = "🛒 *Your Current Order:*\n\n"
#     total_price = 0.0
#     for item_name, details in cart.items():
#         item_total = details['price'] * details['quantity']
#         summary += f"• {details['quantity']}x {item_name} = *£{item_total:.2f}*\n"
#         total_price += item_total
#     summary += f"\n*Subtotal: £{total_price:.2f}*"
#     return summary, total_price

# def build_menu_keyboard():
#     menu = get_menu_as_dict()
#     if not menu: return None
#     emoji_map = {"BREAKFAST": "🥞", "STARTERS": " appetizers", "CURRIES": "🍛", "TANDOORI": "🔥", "BIRYANI": "🍚", "RICE/NOODLES": "🍜", "BREADS": "🍞", "WEEKEND SPECIALS": "⭐", "DESSERTS": "🍰", "COCKTAILS": "🍸", "MOCKTAILS": "🍹", "WHISKEY/SCOTCH": "🥃", "BRANDI": "🍷", "TEQUILA": "🌵", "VODKA": "🍸", "GIN & BOTANICAL": "🌿", "RUM": "🧉", "BEERS": "🍺", "WINES (125 ML)": "🍷"}
#     categories = list(menu.keys())
#     keyboard = [[InlineKeyboardButton(f"{emoji_map.get(cat.upper(), '🍽️')} {cat}", callback_data=f"cat_{cat}")] for cat in categories]
#     keyboard.append([InlineKeyboardButton("🛒 View Cart & Checkout", callback_data="view_cart")])
#     return InlineKeyboardMarkup(keyboard)

# def build_items_keyboard(category):
#     menu = get_menu_as_dict()
#     items = menu.get(category, [])
#     keyboard = [[InlineKeyboardButton(f"{item['itemname']} - £{item['price']:.2f}", callback_data=f"add_{item['itemname']}")] for item in items]
#     keyboard.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="show_menu")])
#     return InlineKeyboardMarkup(keyboard)

# def build_cart_keyboard(cart):
#     keyboard = []
#     for item_name in cart.keys():
#         keyboard.append([
#             InlineKeyboardButton(f"-", callback_data=f"rem_{item_name}"),
#             InlineKeyboardButton(f"{cart[item_name]['quantity']}x {item_name}", callback_data="noop"),
#             InlineKeyboardButton(f"+", callback_data=f"add_{item_name}")
#         ])
#     keyboard.append([InlineKeyboardButton("✅ Proceed to Checkout", callback_data="checkout")])
#     keyboard.append([InlineKeyboardButton("🛍️ Continue to Order", callback_data="show_menu")])
#     return InlineKeyboardMarkup(keyboard)

# # --- State Handlers ---

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     print("\n--- NEW CONVERSATION STARTED ---")
#     context.user_data.clear()
#     context.user_data['cart'] = {}
#     context.user_data['chat_history'] = []
#     start_message = f"🙏 Welcome to your {config.RESTAURANT_NAME} Personal AI Food Delivery Assistant Bot.\n\nTo get started, could you please tell me your full name?"
#     context.user_data['chat_history'].append(f"AI: {start_message}")
#     await update.message.reply_text(start_message)
#     print("LOG: Bot is now in state: GETTING_NAME")
#     return config.GETTING_NAME

# async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_message = update.message.text
#     print(f"LOG: Received message in GETTING_NAME state: '{user_message}'")
#     context.user_data['chat_history'].append(f"User: {user_message}")
    
#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.GETTING_NAME)
#     intent = ai_response.get("intent")
#     print(f"LOG: AI interpreted intent as: {intent}")
    
#     if intent == "PROVIDE_NAME":
#         user_name = ai_response.get("payload")
#         context.user_data['name'] = user_name
#         reply_message = f"Thank you, {user_name}! 🙏\n\nPlease provide your full delivery address and postcode."
#         context.user_data['chat_history'].append(f"AI: {reply_message}")
#         await update.message.reply_text(reply_message)
#         print("LOG: Name received. Transitioning to state: GETTING_ADDRESS")
#         return config.GETTING_ADDRESS
        
#     elif intent == "CHITCHAT":
#         reply = ai_response.get("reply", "That's nice! Could you tell me your name so we can get started?")
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         print("LOG: Handled chit-chat. Staying in state: GETTING_NAME")
#         return config.GETTING_NAME
        
#     else:
#         reply = "I'm sorry, I was expecting a name. Could you please provide your full name to continue?"
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         print("LOG: Fallback triggered. Staying in state: GETTING_NAME")
#         return config.GETTING_NAME

# async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_message = update.message.text
#     print(f"LOG: Received message in GETTING_ADDRESS state: '{user_message}'")
#     context.user_data['chat_history'].append(f"User: {user_message}")
    
#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.GETTING_ADDRESS)
#     intent = ai_response.get("intent")
#     print(f"LOG: AI interpreted intent as: {intent}")
    
#     if intent == "PROVIDE_ADDRESS":
#         address = ai_response.get("payload")
#         context.user_data['address'] = address
#         await update.message.reply_text("👍 Thank you. One moment while I check your address...")
#         distance = services.get_distance_in_miles(address)
#         if distance is None:
#             await update.message.reply_text("I'm sorry, I couldn't verify that address. Please try again.")
#             print("LOG: Address geocoding failed. Staying in state: GETTING_ADDRESS")
#             return config.GETTING_ADDRESS
#         if distance > config.DELIVERY_RADIUS_MILES:
#             await update.message.reply_text(f"We're so sorry, but at {distance:.1f} miles away, you are outside our delivery radius. 😥")
#             print("LOG: User is out of radius. Ending conversation.")
#             return ConversationHandler.END
        
#         context.user_data['delivery_charge'] = 0 if distance <= config.FREE_DELIVERY_RADIUS_MILES else config.DELIVERY_CHARGE
#         delivery_message = "🎉 Great news! You qualify for *FREE delivery*." if context.user_data['delivery_charge'] == 0 else f"Excellent, you're in our delivery area! A delivery charge of £{config.DELIVERY_CHARGE:.2f} will apply."
#         await update.message.reply_text(f"{delivery_message}\n\nLet's get your order started! 🍽️")
#         print("LOG: Address verified. Transitioning to state: ORDERING")
#         return await show_menu(update, context)

#     elif intent == "CHITCHAT":
#         reply = ai_response.get("reply", "I see! To continue, I'll need your delivery address please.")
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         print("LOG: Handled chit-chat. Staying in state: GETTING_ADDRESS")
#         return config.GETTING_ADDRESS
        
#     else:
#         reply = "I was expecting an address. Could you please provide your full delivery address and postcode?"
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         print("LOG: Fallback triggered. Staying in state: GETTING_ADDRESS")
#         return config.GETTING_ADDRESS

# # --- Menu, Cart, and Ordering Logic ---

# async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     reply_markup = build_menu_keyboard()
#     message_text = "Please choose a category to explore:"
#     if update.callback_query:
#         await update.callback_query.answer()
#         try:
#             await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
#         except BadRequest as e:
#             if "Message is not modified" not in str(e): raise e
#     else:
#         await update.message.reply_text(message_text, reply_markup=reply_markup)
#     return config.ORDERING

# async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     category = query.data.split("_")[1]
#     reply_markup = build_items_keyboard(category)
#     await query.answer()
#     try:
#         await query.edit_message_text(f"Here are the items for *{category}*:", reply_markup=reply_markup, parse_mode='Markdown')
#     except BadRequest as e:
#         if "Message is not modified" not in str(e): raise e
#     return config.ORDERING

# async def add_item_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     item_name = query.data.split("_", 1)[1]
#     item_details = get_item_details(item_name)
#     if item_details:
#         cart = context.user_data.get('cart', {})
#         if item_name in cart:
#             cart[item_name]['quantity'] += 1
#         else:
#             cart[item_name] = {'quantity': 1, 'price': item_details['price']}
#         context.user_data['cart'] = cart
#         return await view_cart(update, context)
#     else:
#         await query.answer("Sorry, that item could not be found.", show_alert=True)
#         return config.ORDERING

# async def remove_item_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     item_name = query.data.split("_", 1)[1]
#     cart = context.user_data.get('cart', {})
#     if item_name in cart:
#         cart[item_name]['quantity'] -= 1
#         if cart[item_name]['quantity'] <= 0:
#             del cart[item_name]
#         context.user_data['cart'] = cart
#     return await view_cart(update, context)

# async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await query.answer("Your cart is empty!", show_alert=True)
#         return await show_menu(update, context)
#     summary_text, _ = get_cart_summary(cart)
#     reply_markup = build_cart_keyboard(cart)
#     await query.answer()
#     try:
#         await query.edit_message_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
#     except BadRequest as e:
#         if "Message is not modified" not in str(e): raise e
#     return config.ORDERING

# async def handle_text_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_message = update.message.text
#     print(f"LOG: Received message in ORDERING state: '{user_message}'")
#     context.user_data['chat_history'].append(f"User: {user_message}")
#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.ORDERING)
#     intent = ai_response.get("intent")
#     reply_text = ai_response.get("reply", "Sorry, I didn't quite catch that.")
#     print(f"LOG: AI interpreted intent as: {intent}")
#     context.user_data['chat_history'].append(f"AI: {reply_text}")

#     if intent == "ADD_TO_ORDER":
#         cart = context.user_data.get('cart', {})
#         for item_data in ai_response.get("items", []):
#             item_name = item_data.get("name")
#             item_details = get_item_details(item_name)
#             if item_details:
#                 if item_name in cart:
#                     cart[item_name]['quantity'] += item_data.get("quantity", 1)
#                 else:
#                     cart[item_name] = {'quantity': 1, 'price': item_details['price']}
#         context.user_data['cart'] = cart
    
#     elif intent == "CONFIRM_ORDER":
#         await update.message.reply_text(reply_text)
#         return await view_cart_from_text(update, context)

#     await update.message.reply_text(reply_text)
#     return config.ORDERING

# async def view_cart_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await update.message.reply_text("Your cart is empty!", reply_markup=build_menu_keyboard())
#         return config.ORDERING
#     summary_text, _ = get_cart_summary(cart)
#     reply_markup = build_cart_keyboard(cart)
#     await update.message.reply_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
#     return config.ORDERING

# async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await query.answer("Your cart is empty!", show_alert=True)
#         return config.ORDERING
#     _, subtotal = get_cart_summary(cart)
#     delivery_charge = context.user_data.get('delivery_charge', 0)
#     total_price = subtotal + delivery_charge
#     context.user_data['total_price'] = total_price
#     order_ref = f"NH-{int(time.time())}"
#     context.user_data['order_ref'] = order_ref
#     payment_details = (
#         f"🧾 *Final Bill*\n\n"
#         f"Subtotal: *£{subtotal:.2f}*\n"
#         f"Delivery Charge: *£{delivery_charge:.2f}*\n"
#         f"---------------------\n"
#         f"Total to Pay: *£{total_price:.2f}*\n\n"
#         f"🏦 *Payment Details (For Demo)*\n"
#         f"Please make a bank transfer to the following account:\n\n"
#         f"  - *Account Name:* Namaste-Bot Ltd\n"
#         f"  - *Sort Code:* 01-02-03\n"
#         f"  - *Account No:* 12345678\n"
#         f"  - *Reference:* `{order_ref}`\n\n"
#         f"Once payment is made, please reply with a confirmation message to complete your order."
#     )
#     await query.answer()
#     try:
#         await query.edit_message_text(payment_details, parse_mode='Markdown')
#     except BadRequest as e:
#         if "Message is not modified" not in str(e): raise e
#     print("LOG: Bill shown. Transitioning to state: AWAITING_PAYMENT_CONFIRMATION")
#     return config.AWAITING_PAYMENT_CONFIRMATION

# async def handle_payment_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_message = update.message.text
#     print(f"LOG: Received message in AWAITING_PAYMENT_CONFIRMATION state: '{user_message}'")
#     context.user_data['chat_history'].append(f"User: {user_message}")
    
#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.AWAITING_PAYMENT_CONFIRMATION)
#     intent = ai_response.get("intent")
#     print(f"LOG: AI interpreted intent as: {intent}")

#     if intent == "CONFIRM_PAYMENT":
#         services.log_order_to_sheet(
#             customer_name=context.user_data.get('name'),
#             customer_address=context.user_data.get('address'),
#             order_details=str(context.user_data.get('cart', {})),
#             total_price=context.user_data.get('total_price', 0)
#         )
#         await update.message.reply_text(
#             f"✅ Payment confirmed! Thank you for your order `#{context.user_data.get('order_ref')}`.\n\n"
#             "Your delicious meal will be prepared and delivered shortly. Enjoy! 🍛",
#             parse_mode='Markdown'
#         )
#         print("LOG: Payment confirmed. Ending conversation.")
#         return ConversationHandler.END
    
#     else: # CHITCHAT or ERROR
#         reply = ai_response.get("reply", "I'm waiting for payment confirmation. Please type 'payment done' or /cancel.")
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         print("LOG: Handled chit-chat. Staying in state: AWAITING_PAYMENT_CONFIRMATION")
#         return config.AWAITING_PAYMENT_CONFIRMATION

# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.message.reply_text("Order cancelled. Hope to see you again soon! 👋")
#     context.user_data.clear()
#     print("\n--- CONVERSATION CANCELLED ---\n")
#     return ConversationHandler.END

# async def no_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.callback_query.answer()

























# # conversation_logic.py Single working Bot
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import ContextTypes, ConversationHandler
# from telegram.error import BadRequest
# import time

# # Direct imports
# import config
# import services
# import ai_engine
# from data_manager import get_menu_as_dict, get_item_details

# # --- Helper Functions ---
# def get_cart_summary(cart):
#     if not cart: return "Your cart is currently empty. 🛒", 0.0
#     summary = "🛒 *Your Current Order:*\n\n"
#     total_price = 0.0
#     for item_name, details in cart.items():
#         item_total = details['price'] * details['quantity']
#         summary += f"• {details['quantity']}x {item_name} = *£{item_total:.2f}*\n"
#         total_price += item_total
#     summary += f"\n*Subtotal: £{total_price:.2f}*"
#     return summary, total_price

# def build_menu_keyboard():
#     menu = get_menu_as_dict()
#     if not menu: return None
#     emoji_map = {"BREAKFAST": "🥞", "STARTERS": "🍢", "CURRIES": "🍛", "TANDOORI": "🔥", "BIRYANI": "🍚", "RICE/NOODLES": "🍜", "BREADS": "🍞", "WEEKEND SPECIALS": "⭐", "DESSERTS": "🍰", "COCKTAILS": "🍸", "MOCKTAILS": "🍹", "WHISKEY/SCOTCH": "🥃", "BRANDI": "🍷", "TEQUILA": "🌵", "VODKA": "🍸", "GIN & BOTANICAL": "🌿", "RUM": "🧉", "BEERS": "🍺", "WINES (125 ML)": "🍷"}
#     categories = list(menu.keys())
#     keyboard = [[InlineKeyboardButton(f"{emoji_map.get(cat.upper(), '🍽️')} {cat}", callback_data=f"cat_{cat}")] for cat in categories]
#     keyboard.append([InlineKeyboardButton("🛒 View Cart & Checkout", callback_data="view_cart")])
#     return InlineKeyboardMarkup(keyboard)

# def build_items_keyboard(category):
#     menu = get_menu_as_dict()
#     items = menu.get(category, [])
#     keyboard = [[InlineKeyboardButton(f"{item['itemname']} - £{item['price']:.2f}", callback_data=f"add_{item['itemname']}")] for item in items]
#     keyboard.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="show_menu")])
#     return InlineKeyboardMarkup(keyboard)

# def build_cart_keyboard(cart):
#     keyboard = []
#     for item_name in cart.keys():
#         keyboard.append([
#             InlineKeyboardButton(f"-", callback_data=f"rem_{item_name}"),
#             InlineKeyboardButton(f"{cart[item_name]['quantity']}x {item_name}", callback_data="noop"),
#             InlineKeyboardButton(f"+", callback_data=f"add_{item_name}")
#         ])
#     keyboard.append([InlineKeyboardButton("✅ Proceed to Checkout", callback_data="checkout")])
#     keyboard.append([InlineKeyboardButton("🛍️ Continue to Order", callback_data="show_menu")])
#     return InlineKeyboardMarkup(keyboard)

# # --- State Handlers ---

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """
#     Starts a new conversation. Checks if the user is a returning customer.
#     """
#     print("\n--- NEW CONVERSATION STARTED ---")
#     context.user_data.clear()
#     context.user_data['cart'] = {}
#     context.user_data['chat_history'] = []
    
#     user_id = update.message.from_user.id
#     customer = services.find_customer_by_id(user_id)
    
#     if customer:
#         # --- RETURNING CUSTOMER FLOW ---
#         context.user_data['name'] = customer['full_name']
#         context.user_data['address'] = customer['address']
#         context.user_data['phone'] = customer.get('mobile_number')
        
#         reply_markup = InlineKeyboardMarkup([
#             [InlineKeyboardButton("✅ Yes, use this address", callback_data="confirm_address_yes")],
#             [InlineKeyboardButton("✏️ No, use a different one", callback_data="confirm_address_no")]
#         ])
        
#         await update.message.reply_text(
#             f"Welcome back, {customer['full_name']}! 🙏\n\n"
#             f"Should I use your saved address for delivery?\n\n"
#             f"📍 *{customer['address']}*",
#             reply_markup=reply_markup,
#             parse_mode='Markdown'
#         )
#         print("LOG: Returning customer found. Awaiting address confirmation.")
#         return config.CONFIRMING_ADDRESS
        
#     else:
#         # --- NEW CUSTOMER FLOW with the new welcome message ---
#         start_message = (
#             f"🙏 Welcome to your {config.RESTAURANT_NAME} Personal AI Food Delivery Assistant Bot.\n\n"
#             "⏰ *Opening Hours*\n"
#             "MON - THUR: 9 AM - 11 PM\n"
#             "FRI - SUN: 9 AM - 12 AM\n\n"
#             f"📍 *Our Address*\n"
#             f"{config.RESTAURANT_ADDRESS}\n\n"
#             "To get started, could you please tell me your *full name and mobile number*?"
#         )
#         context.user_data['chat_history'].append(f"AI: {start_message}")
#         await update.message.reply_text(start_message, parse_mode='Markdown')
#         print("LOG: New customer. Transitioning to state: GETTING_NAME_AND_PHONE")
#         return config.GETTING_NAME_AND_PHONE

# async def get_name_and_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Gets the new customer's name and phone number."""
#     user_message = update.message.text
#     context.user_data['chat_history'].append(f"User: {user_message}")
    
#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.GETTING_NAME_AND_PHONE)
#     intent = ai_response.get("intent")
#     print(f"LOG: AI interpreted intent as: {intent}")
    
#     if intent == "PROVIDE_DETAILS":
#         context.user_data['name'] = ai_response.get("name")
#         context.user_data['phone'] = ai_response.get("phone")
        
#         reply_message = f"Thank you, {context.user_data['name']}! 🙏\n\nPlease provide your full delivery address and postcode."
#         context.user_data['chat_history'].append(f"AI: {reply_message}")
#         await update.message.reply_text(reply_message)
#         print("LOG: Name and phone received. Transitioning to state: GETTING_ADDRESS")
#         return config.GETTING_ADDRESS
        
#     elif intent in ["CHITCHAT", "MISSING_INFO"]:
#         reply = ai_response.get("reply", "I'm sorry, I need both your name and mobile number to continue.")
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         return config.GETTING_NAME_AND_PHONE
        
#     else:
#         reply = "I'm sorry, I was expecting your name and phone number. Could you please provide them to continue?"
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         return config.GETTING_NAME_AND_PHONE

# async def handle_address_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Handles the 'yes' or 'no' button press for a saved address."""
#     query = update.callback_query
#     await query.answer()
    
#     if query.data == 'confirm_address_yes':
#         # --- FIX: Call the check_address_and_proceed function ---
#         return await check_address_and_proceed(update, context, context.user_data['address'])
        
#     elif query.data == 'confirm_address_no':
#         await query.edit_message_text("No problem. Please provide your new delivery address.")
#         print("LOG: Customer wants to change address. Transitioning to state: GETTING_ADDRESS")
#         return config.GETTING_ADDRESS

# async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Gets a new address and registers/updates the customer."""
#     address = update.message.text
#     context.user_data['address'] = address
    
#     services.register_or_update_customer(
#         user_id=update.message.from_user.id,
#         full_name=context.user_data.get('name'),
#         address=address,
#         mobile_number=context.user_data.get('phone')
#     )
    
#     # --- FIX: Call the check_address_and_proceed function ---
#     return await check_address_and_proceed(update, context, address)

# # --- THIS IS THE MISSING FUNCTION THAT HAS BEEN ADDED ---
# async def check_address_and_proceed(update: Update, context: ContextTypes.DEFAULT_TYPE, address: str) -> int:
#     """A shared function to check distance and move to the ordering phase."""
#     message_to_send = "👍 Thank you. One moment while I check the address..."
#     if update.callback_query:
#         await update.callback_query.edit_message_text(message_to_send)
#     else:
#         await update.message.reply_text(message_to_send)

#     distance = services.get_distance_in_miles(address)

#     if distance is None:
#         await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm sorry, I couldn't verify that address. Please provide a different one.")
#         return config.GETTING_ADDRESS

#     if distance > config.DELIVERY_RADIUS_MILES:
#         await context.bot.send_message(chat_id=update.effective_chat.id, text=f"We're so sorry, but at {distance:.1f} miles away, you are outside our delivery radius. 😥")
#         return ConversationHandler.END

#     context.user_data['delivery_charge'] = 0 if distance <= config.FREE_DELIVERY_RADIUS_MILES else config.DELIVERY_CHARGE
#     delivery_message = "🎉 Great news! You qualify for *FREE delivery*." if context.user_data['delivery_charge'] == 0 else f"Excellent, you're in our delivery area! A delivery charge of £{config.DELIVERY_CHARGE:.2f} will apply."
    
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{delivery_message}\n\nLet's get your order started! 🍽️", parse_mode='Markdown')
#     return await show_menu(update, context)

# # --- The rest of the file is unchanged ---
# async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     reply_markup = build_menu_keyboard()
#     message_text = "Please choose a category to explore:"
#     if update.callback_query:
#         await update.callback_query.answer()
#         try:
#             await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
#         except BadRequest as e:
#             if "Message is not modified" not in str(e): raise e
#     else:
#         await update.message.reply_text(message_text, reply_markup=reply_markup)
#     return config.ORDERING

# async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     category = query.data.split("_")[1]
#     reply_markup = build_items_keyboard(category)
#     await query.answer()
#     try:
#         await query.edit_message_text(f"Here are the items for *{category}*:", reply_markup=reply_markup, parse_mode='Markdown')
#     except BadRequest as e:
#         if "Message is not modified" not in str(e): raise e
#     return config.ORDERING

# async def add_item_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     item_name = query.data.split("_", 1)[1]
#     item_details = get_item_details(item_name)
#     if item_details:
#         cart = context.user_data.get('cart', {})
#         if item_name in cart:
#             cart[item_name]['quantity'] += 1
#         else:
#             cart[item_name] = {'quantity': 1, 'price': item_details['price']}
#         context.user_data['cart'] = cart
#         return await view_cart(update, context)
#     else:
#         await query.answer("Sorry, that item could not be found.", show_alert=True)
#         return config.ORDERING

# async def remove_item_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     item_name = query.data.split("_", 1)[1]
#     cart = context.user_data.get('cart', {})
#     if item_name in cart:
#         cart[item_name]['quantity'] -= 1
#         if cart[item_name]['quantity'] <= 0:
#             del cart[item_name]
#         context.user_data['cart'] = cart
#     return await view_cart(update, context)

# async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await query.answer("Your cart is empty!", show_alert=True)
#         return await show_menu(update, context)
#     summary_text, _ = get_cart_summary(cart)
#     reply_markup = build_cart_keyboard(cart)
#     await query.answer()
#     try:
#         await query.edit_message_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
#     except BadRequest as e:
#         if "Message is not modified" not in str(e): raise e
#     return config.ORDERING

# async def handle_text_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_message = update.message.text
#     context.user_data['chat_history'].append(f"User: {user_message}")
#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.ORDERING)
#     intent = ai_response.get("intent")
#     reply_text = ai_response.get("reply", "Sorry, I didn't quite catch that.")
#     context.user_data['chat_history'].append(f"AI: {reply_text}")

#     if intent == "ADD_TO_ORDER":
#         cart = context.user_data.get('cart', {})
#         for item_data in ai_response.get("items", []):
#             item_name = item_data.get("name")
#             item_details = get_item_details(item_name)
#             if item_details:
#                 if item_name in cart:
#                     cart[item_name]['quantity'] += item_data.get("quantity", 1)
#                 else:
#                     cart[item_name] = {'quantity': 1, 'price': item_details['price']}
#         context.user_data['cart'] = cart
    
#     elif intent == "CONFIRM_ORDER":
#         await update.message.reply_text(reply_text)
#         return await view_cart_from_text(update, context)

#     await update.message.reply_text(reply_text)
#     return config.ORDERING

# async def view_cart_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await update.message.reply_text("Your cart is empty!", reply_markup=build_menu_keyboard())
#         return config.ORDERING
#     summary_text, _ = get_cart_summary(cart)
#     reply_markup = build_cart_keyboard(cart)
#     await update.message.reply_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
#     return config.ORDERING

# async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await query.answer("Your cart is empty!", show_alert=True)
#         return config.ORDERING
#     _, subtotal = get_cart_summary(cart)
#     delivery_charge = context.user_data.get('delivery_charge', 0)
#     total_price = subtotal + delivery_charge
#     context.user_data['total_price'] = total_price
#     order_ref = f"NH-{int(time.time())}"
#     context.user_data['order_ref'] = order_ref
#     payment_details = (
#         f"🧾 *Final Bill*\n\n"
#         f"Subtotal: *£{subtotal:.2f}*\n"
#         f"Delivery Charge: *£{delivery_charge:.2f}*\n"
#         f"---------------------\n"
#         f"Total to Pay: *£{total_price:.2f}*\n\n"
#         f"🏦 *Payment Details (For Demo)*\n"
#         f"Please make a bank transfer to the following account:\n\n"
#         f"  - *Account Name:* Namaste-Bot Ltd\n"
#         f"  - *Sort Code:* 01-02-03\n"
#         f"  - *Account No:* 12345678\n"
#         f"  - *Reference:* `{order_ref}`\n\n"
#         f"Once payment is made, please reply with a confirmation message to complete your order."
#     )
#     await query.answer()
#     try:
#         await query.edit_message_text(payment_details, parse_mode='Markdown')
#     except BadRequest as e:
#         if "Message is not modified" not in str(e): raise e
#     return config.AWAITING_PAYMENT_CONFIRMATION

# async def handle_payment_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user_message = update.message.text
#     context.user_data['chat_history'].append(f"User: {user_message}")
#     ai_response = ai_engine.get_ai_interpretation(context.user_data['chat_history'], user_message, current_state=config.AWAITING_PAYMENT_CONFIRMATION)
#     intent = ai_response.get("intent")

#     if intent == "CONFIRM_PAYMENT":
#         services.log_order_to_sheet(
#             customer_name=context.user_data.get('name'),
#             customer_address=context.user_data.get('address'),
#             order_details=str(context.user_data.get('cart', {})),
#             total_price=context.user_data.get('total_price', 0)
#         )
#         await update.message.reply_text(
#             f"✅ Payment confirmed! Thank you for your order `#{context.user_data.get('order_ref')}`.\n\n"
#             "Your delicious meal will be prepared and delivered shortly. Enjoy! 🍛",
#             parse_mode='Markdown'
#         )
#         return ConversationHandler.END
    
#     else: # CHITCHAT or ERROR
#         reply = ai_response.get("reply", "I'm waiting for payment confirmation. Please type 'payment done' or /cancel.")
#         context.user_data['chat_history'].append(f"AI: {reply}")
#         await update.message.reply_text(reply)
#         return config.AWAITING_PAYMENT_CONFIRMATION

# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.message.reply_text("Order cancelled. Hope to see you again soon! 👋")
#     context.user_data.clear()
#     return ConversationHandler.END

# async def no_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.callback_query.answer()



































# # # working for VM

# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
# from telegram.ext import ContextTypes, ConversationHandler
# from telegram.error import BadRequest
# import time
# import os

# import config
# import database_manager as db
# import services
# import ai_engine
# from data_manager import get_menu_as_dict, get_item_details
# from geopy.geocoders import Nominatim
# from geopy.distance import geodesic

# # --- Helper Functions ---
# def get_cart_summary(cart):
#     """Generates a summary of the cart and calculates the subtotal."""
#     if not cart:
#         return "Your cart is currently empty. 🛒", 0.0
#     summary = "🛒 *Your Current Order:*\n\n"
#     total_price = 0.0
#     for item_name, details in cart.items():
#         item_total = details['price'] * details['quantity']
#         summary += f"• {details['quantity']}x {item_name} = *£{item_total:.2f}*\n"
#         total_price += item_total
#     summary += f"\n*Subtotal: £{total_price:.2f}*"
#     return summary, total_price

# def get_distance_in_miles(customer_postcode):
#     """
#     Calculates the delivery distance between the restaurant and the customer using geocoding.

#     How it works:
#     1.  **Geocoding:** It converts real-world addresses (like postcodes) into geographic
#         coordinates (latitude and longitude).
#         - Example: Restaurant at 'TW3 1JA' might become (51.468, -0.372).
#         - Example: Customer at 'SW1A 0AA' might become (51.501, -0.128).
#     2.  **Distance Calculation:** It then uses the 'geodesic' formula to calculate the
#         shortest "as-the-crow-flies" distance between these two points on the Earth's surface.
#     """
#     geolocator = Nominatim(user_agent="namaste_hounslow_bot")
#     try:
#         restaurant_location = geolocator.geocode(config.RESTAURANT_POSTCODE, country_codes="GB")
#         customer_location = geolocator.geocode(customer_postcode, country_codes="GB")
        
#         if not restaurant_location or not customer_location:
#             print(f"GEOCODING FAILED: Could not find coordinates for '{config.RESTAURANT_POSTCODE}' or '{customer_postcode}'.")
#             return None
            
#         distance = geodesic(
#             (restaurant_location.latitude, restaurant_location.longitude),
#             (customer_location.latitude, customer_location.longitude)
#         ).miles
#         print(f"GEOCODING SUCCESS: Distance to '{customer_postcode}' is {distance:.2f} miles.")
#         return distance

#     except Exception as e:
#         print(f"GEOCODING ERROR: An unexpected error occurred: {e}")
#         return None

# def build_menu_keyboard():
#     """Creates the main menu keyboard with categories."""
#     menu = get_menu_as_dict()
#     if not menu: return None
#     emoji_map = {"BREAKFAST": "🥞", "STARTERS": "🍢", "CURRIES": "🍛", "TANDOORI": "🔥", "BIRYANI": "🍚", "RICE/NOODLES": "🍜", "BREADS": "🍞", "WEEKEND SPECIALS": "⭐", "DESSERTS": "🍰"}
#     categories = list(menu.keys())
#     keyboard = [[InlineKeyboardButton(f"{emoji_map.get(cat.upper(), '🍽️')} {cat}", callback_data=f"cat_{cat}")] for cat in categories]
#     keyboard.append([InlineKeyboardButton("🛒 View Cart & Checkout", callback_data="view_cart")])
#     return InlineKeyboardMarkup(keyboard)

# def build_items_keyboard(category):
#     """Creates a keyboard for items within a category."""
#     menu = get_menu_as_dict()
#     items = menu.get(category, [])
#     keyboard = [[InlineKeyboardButton(f"{item['itemname']} - £{item['price']:.2f}", callback_data=f"add_{item['itemname']}")] for item in items]
#     keyboard.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="show_menu")])
#     return InlineKeyboardMarkup(keyboard)

# def build_cart_keyboard(cart):
#     """Creates the interactive keyboard for the shopping cart."""
#     keyboard = []
#     for item_name in cart.keys():
#         keyboard.append([
#             InlineKeyboardButton("➖", callback_data=f"rem_{item_name}"),
#             InlineKeyboardButton(f"{cart[item_name]['quantity']}x {item_name}", callback_data="noop"),
#             InlineKeyboardButton("➕", callback_data=f"add_{item_name}")
#         ])
#     keyboard.append([InlineKeyboardButton("✅ Proceed to Checkout", callback_data="checkout")])
#     keyboard.append([InlineKeyboardButton("🛍️ Continue to Order", callback_data="show_menu")])
#     return InlineKeyboardMarkup(keyboard)

# # --- State Handlers ---

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """
#     Starts a new conversation. Checks if the user is a returning customer.
#     """
#     print("\n--- NEW CONVERSATION STARTED ---")
#     user_id = update.message.from_user.id
#     customer = db.find_customer_by_id(user_id)
    
#     if customer:
#         context.user_data.update(customer)
#         context.user_data['cart'] = {}
#         reply_markup = InlineKeyboardMarkup([
#             [InlineKeyboardButton("✅ Yes, use this address", callback_data="confirm_address_yes")],
#             [InlineKeyboardButton("✏️ No, use a different one", callback_data="confirm_address_no")]
#         ])
#         await update.message.reply_text(
#             f"Welcome back, *{customer['full_name']}*! 🙏\n\nShould I use your saved address for delivery?\n\n📍 _{customer['address']}_",
#             reply_markup=reply_markup, parse_mode='Markdown'
#         )
#         print(f"LOG: Returning customer {user_id} found. Awaiting address confirmation.")
#         return config.CONFIRMING_ADDRESS
#     else:
#         context.user_data.clear()
#         context.user_data['cart'] = {}
#         start_message = (
#             f"🙏 Welcome to *{config.RESTAURANT_NAME}*, your personal AI food delivery assistant!\n\n"
#             "To get started, please tell me your *full name* and *mobile number*."
#         )
#         await update.message.reply_text(start_message, parse_mode='Markdown')
#         print(f"LOG: New customer {user_id}. Transitioning to GETTING_NAME_AND_PHONE.")
#         return config.GETTING_NAME_AND_PHONE

# async def get_name_and_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Handles the user's response for name and phone using the AI engine."""
#     await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
#     user_message = update.message.text
#     ai_response = ai_engine.get_ai_interpretation(
#         context.user_data.get('chat_history', []), user_message, current_state=config.GETTING_NAME_AND_PHONE
#     )
    
#     if ai_response.get("intent") == "PROVIDE_DETAILS":
#         context.user_data['full_name'] = ai_response.get("name")
#         context.user_data['phone_number'] = ai_response.get("phone")
#         await update.message.reply_text(
#             f"Thank you, *{context.user_data['full_name']}*! 🙏\n\nPlease provide your *full delivery address* and postcode.",
#             parse_mode='Markdown'
#         )
#         return config.GETTING_ADDRESS
#     else:
#         await update.message.reply_text(ai_response.get("reply", "I'm sorry, I need both your name and a valid mobile number to continue."))
#         return config.GETTING_NAME_AND_PHONE

# async def handle_address_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Handles callback for confirming a saved address."""
#     query = update.callback_query
#     await query.answer()
#     if query.data == 'confirm_address_yes':
#         return await check_address_and_proceed(update, context, context.user_data['address'])
#     else:
#         await query.edit_message_text("No problem. Please provide your new delivery address.")
#         return config.GETTING_ADDRESS

# async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Gets a new address, saves it, and syncs to the sheet."""
#     address = update.message.text
#     context.user_data['address'] = address
    
#     customer_details = {
#         'user_id': update.message.from_user.id,
#         'full_name': context.user_data.get('full_name'),
#         'phone_number': context.user_data.get('phone_number'),
#         'address': address
#     }
#     db.register_or_update_customer(**customer_details)
#     if context.job_queue:
#         context.job_queue.run_once(services.sync_customer_to_sheet, when=0, data=customer_details)
    
#     return await check_address_and_proceed(update, context, address)

# async def check_address_and_proceed(update: Update, context: ContextTypes.DEFAULT_TYPE, address: str) -> int:
#     """A shared function to check distance and move to the ordering phase."""
#     chat_id = update.effective_chat.id
#     await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
    
#     message_to_send = "👍 Thank you. One moment while I verify the address with our satellites... 🛰️"
#     if update.callback_query:
#         await update.callback_query.edit_message_text(message_to_send)
#     else:
#         await update.message.reply_text(message_to_send)

#     distance = get_distance_in_miles(address)
    
#     if distance is None:
#         await context.bot.send_message(
#             chat_id=chat_id, 
#             text="I'm sorry, I couldn't verify that address. Please provide a different one, including the postcode."
#         )
#         return config.GETTING_ADDRESS

#     if distance > config.DELIVERY_RADIUS_MILES:
#         await context.bot.send_message(
#             chat_id=chat_id, 
#             text=f"We're so sorry, but you are outside our delivery radius of {config.DELIVERY_RADIUS_MILES} miles. 😥"
#         )
#         return ConversationHandler.END

#     context.user_data['delivery_charge'] = 0 if distance <= config.FREE_DELIVERY_RADIUS_MILES else config.DELIVERY_CHARGE
#     delivery_message = "🎉 Great news! You qualify for *FREE delivery*." if context.user_data['delivery_charge'] == 0 else f"Excellent, you're in our delivery area! A delivery charge of *£{config.DELIVERY_CHARGE:.2f}* will apply."
    
#     await context.bot.send_message(
#         chat_id=chat_id, 
#         text=f"{delivery_message}\n\nLet's get your order started! 🍽️", 
#         parse_mode='Markdown'
#     )
#     return await show_menu(update, context)

# async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Displays the main menu categories."""
#     reply_markup = build_menu_keyboard()
#     message_text = "Please choose a category to explore, or type your order directly:"
#     if update.callback_query:
#         await update.callback_query.answer()
#         try:
#             await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
#         except BadRequest as e:
#             if "Message is not modified" not in str(e): raise e
#     else:
#         await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=reply_markup)
#     return config.ORDERING

# async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Shows items for a selected category."""
#     query = update.callback_query
#     category = query.data.split("_", 1)[1]
#     reply_markup = build_items_keyboard(category)
#     await query.answer()
#     await query.edit_message_text(f"Here are the items for *{category}*:", reply_markup=reply_markup, parse_mode='Markdown')
#     return config.ORDERING

# async def add_item_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Adds an item to the cart via button press."""
#     query = update.callback_query
#     item_name = query.data.split("_", 1)[1]
#     item_details = get_item_details(item_name)
    
#     if item_details:
#         cart = context.user_data.get('cart', {})
#         if item_name in cart:
#             cart[item_name]['quantity'] += 1
#         else:
#             cart[item_name] = {'quantity': 1, 'price': item_details['price']}
#         context.user_data['cart'] = cart
#         await query.answer(f"Added {item_name}!")
#         return await view_cart(update, context)
#     else:
#         await query.answer("Sorry, that item could not be found.", show_alert=True)
#         return config.ORDERING

# async def remove_item_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Removes an item from the cart via button press."""
#     query = update.callback_query
#     item_name = query.data.split("_", 1)[1]
#     cart = context.user_data.get('cart', {})
    
#     if item_name in cart:
#         cart[item_name]['quantity'] -= 1
#         if cart[item_name]['quantity'] <= 0:
#             del cart[item_name]
#         context.user_data['cart'] = cart
#         await query.answer(f"Removed one {item_name}")
    
#     if not cart:
#         await query.answer("Your cart is now empty.")
#         return await show_menu(update, context)
#     else:
#         return await view_cart(update, context)

# async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Displays the current cart contents and total."""
#     query = update.callback_query
#     cart = context.user_data.get('cart', {})
    
#     if not cart:
#         await query.answer("Your cart is empty!", show_alert=True)
#         return await show_menu(update, context)
        
#     summary_text, _ = get_cart_summary(cart)
#     reply_markup = build_cart_keyboard(cart)
#     await query.answer()
#     await query.edit_message_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
#     return config.ORDERING

# async def handle_text_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Handles a text-based order using the AI engine."""
#     await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
#     user_message = update.message.text
#     ai_response = ai_engine.get_ai_interpretation(
#         context.user_data.get('chat_history', []), user_message, current_state=config.ORDERING
#     )
#     intent = ai_response.get("intent")
#     reply_text = ai_response.get("reply", "Sorry, I didn't quite catch that.")

#     if intent == "ADD_TO_ORDER":
#         cart = context.user_data.get('cart', {})
#         items_added = []
#         for item_data in ai_response.get("items", []):
#             item_name = item_data.get("name")
#             item_details = get_item_details(item_name)
#             if item_details:
#                 quantity = item_data.get("quantity", 1)
#                 if item_name in cart:
#                     cart[item_name]['quantity'] += quantity
#                 else:
#                     cart[item_name] = {'quantity': quantity, 'price': item_details['price']}
#                 items_added.append(item_name)
        
#         if items_added:
#             context.user_data['cart'] = cart
#             await update.message.reply_text(reply_text)
#             return await view_cart_from_text(update, context)
#         else:
#             await update.message.reply_text("I'm sorry, I couldn't find those items on our menu. Please try again or use the buttons.")

#     elif intent == "CONFIRM_ORDER":
#         await update.message.reply_text(reply_text)
#         return await view_cart_from_text(update, context)
    
#     else: # Handles QUERY_MENU, CHITCHAT, ERROR
#         await update.message.reply_text(reply_text)
        
#     return config.ORDERING

# async def view_cart_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Displays the cart in response to a text command."""
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await update.message.reply_text("Your cart is empty!", reply_markup=build_menu_keyboard())
#         return config.ORDERING
        
#     summary_text, _ = get_cart_summary(cart)
#     reply_markup = build_cart_keyboard(cart)
#     await update.message.reply_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
#     return config.ORDERING

# async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Finalizes the order and presents the bill."""
#     query = update.callback_query
#     await context.bot.send_chat_action(chat_id=query.message.chat_id, action=constants.ChatAction.TYPING)
#     cart = context.user_data.get('cart', {})
#     if not cart:
#         await query.answer("Your cart is empty!", show_alert=True)
#         return config.ORDERING
        
#     summary, subtotal = get_cart_summary(cart)
#     delivery_charge = context.user_data.get('delivery_charge', 0)
#     total_price = subtotal + delivery_charge
#     order_ref = f"NH-{int(time.time())}"
#     context.user_data['order_ref'] = order_ref
    
#     db.create_order(order_ref, update.effective_user.id, cart, total_price)
    
#     payment_details = (
#         f"🧾 *Final Bill*\n\n{summary}\n"
#         f"Delivery Charge: *£{delivery_charge:.2f}*\n"
#         f"---------------------\n*Total to Pay: £{total_price:.2f}*\n\n"
#         f"🏦 *Payment Details (For Demo)*\nPlease make a bank transfer to:\n\n"
#         f"  - *Account Name:* Namaste-Bot Ltd\n"
#         f"  - *Sort Code:* 01-02-03\n"
#         f"  - *Account No:* 12345678\n"
#         f"  - *Reference:* `{order_ref}`\n\n"
#         f"After paying, please upload a *screenshot* of the confirmation as proof."
#     )
    
#     await query.answer()
#     await query.edit_message_text(payment_details, parse_mode='Markdown')
#     print(f"LOG: Bill shown for {order_ref}. Transitioning to AWAITING_SCREENSHOT.")
#     return config.AWAITING_SCREENSHOT

# async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Handles the payment screenshot, saves it, and forwards to the restaurant bot."""
#     await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_PHOTO)
#     print("LOG: Received photo in AWAITING_SCREENSHOT state.")
#     photo = update.message.photo[-1]
#     order_ref = context.user_data.get('order_ref')
    
#     screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
#     os.makedirs(screenshot_dir, exist_ok=True)
    
#     file = await photo.get_file()
#     screenshot_path = os.path.join(screenshot_dir, f'{order_ref}.jpg')
#     await file.download_to_drive(screenshot_path)
#     print(f"LOG: Screenshot for order {order_ref} saved to {screenshot_path}")

#     db.update_order_screenshot(order_ref, screenshot_path)
    
#     order_details = db.get_order_details(order_ref)
#     if not order_details:
#         await update.message.reply_text("There was an issue finding your order. Please contact support.")
#         return ConversationHandler.END

#     cart_summary, _ = get_cart_summary(order_details['cart'])
#     order_caption = (
#         f"🔔 *New Pending Order: #{order_ref}*\n\n"
#         f"👤 *Customer:* {order_details['name']}\n"
#         f"📞 *Phone:* {order_details['phone']}\n"
#         f"🏠 *Address:* {order_details['address']}\n\n"
#         f"{cart_summary}\n\n"
#         f"*Total Paid: £{order_details['total_price']:.2f}*"
#     )
    
#     keyboard = InlineKeyboardMarkup([
#         [
#             InlineKeyboardButton("✅ Confirm Order", callback_data=f"confirm_{order_ref}"),
#             InlineKeyboardButton("❌ Reject Order", callback_data=f"reject_{order_ref}")
#         ]
#     ])

#     restaurant_bot = context.application.bot_data['restaurant_bot']
#     await restaurant_bot.send_photo(
#         chat_id=config.RESTAURANT_CHAT_ID, 
#         photo=open(screenshot_path, 'rb'), 
#         caption=order_caption, 
#         reply_markup=keyboard, 
#         parse_mode='Markdown'
#     )
    
#     await update.message.reply_text("Thank you! Your order has been sent to the restaurant for confirmation. You'll be notified shortly. ⏳")
#     print(f"LOG: Order {order_ref} forwarded to restaurant group. User in PENDING_CONFIRMATION.")
#     return config.PENDING_CONFIRMATION

# async def handle_text_instead_of_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Handles the user sending text when a screenshot is expected."""
#     await update.message.reply_text("I'm waiting for a payment screenshot. Please upload an image, or type /cancel to stop.")
#     return config.AWAITING_SCREENSHOT

# async def pending_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Informs the user their order is still pending."""
#     await update.message.reply_text("Your order is still pending confirmation. You will be notified as soon as the restaurant reviews it! Please wait a moment. 😊")
#     return config.PENDING_CONFIRMATION

# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Cancels the entire conversation."""
#     await update.message.reply_text("Order cancelled. Hope to see you again soon! 👋")
#     context.user_data.clear()
#     print("\n--- CONVERSATION CANCELLED ---\n")
#     return ConversationHandler.END

# async def no_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """A dummy handler for unclickable buttons."""
#     await update.callback_query.answer()






























from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest
import time
import os

import config
import database_manager as db
import services
import ai_engine
from data_manager import get_menu_as_dict, get_item_details
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# --- Helper Functions ---
def get_cart_summary(cart):
    """Generates a summary of the cart and calculates the subtotal."""
    if not cart:
        return "Your cart is currently empty. 🛒", 0.0
    summary = "🛒 *Your Current Order:*\n\n"
    total_price = 0.0
    for item_name, details in cart.items():
        item_total = details['price'] * details['quantity']
        summary += f"• {details['quantity']}x {item_name} = *£{item_total:.2f}*\n"
        total_price += item_total
    summary += f"\n*Subtotal: £{total_price:.2f}*"
    return summary, total_price

def get_distance_in_miles(clean_address):
    """Calculates delivery distance using a clean, single-line address."""
    geolocator = Nominatim(user_agent="namaste_hounslow_bot")
    try:
        restaurant_location = geolocator.geocode(config.RESTAURANT_POSTCODE, country_codes="GB")
        customer_location = geolocator.geocode(clean_address, country_codes="GB")
        
        if not restaurant_location or not customer_location:
            print(f"GEOCODING FAILED: Could not find coordinates for '{config.RESTAURANT_POSTCODE}' or '{clean_address}'.")
            return None
            
        distance = geodesic(
            (restaurant_location.latitude, restaurant_location.longitude),
            (customer_location.latitude, customer_location.longitude)
        ).miles
        print(f"GEOCODING SUCCESS: Distance to '{clean_address}' is {distance:.2f} miles.")
        return distance
    except Exception as e:
        print(f"GEOCODING ERROR: An unexpected error occurred: {e}")
        return None

def build_menu_keyboard():
    # ... (This function is unchanged) ...
    menu = get_menu_as_dict()
    if not menu: return None
    emoji_map = {"BREAKFAST": "🥞", "STARTERS": "🍢", "CURRIES": "🍛", "TANDOORI": "🔥", "BIRYANI": "🍚", "RICE/NOODLES": "🍜", "BREADS": "🍞", "WEEKEND SPECIALS": "⭐", "DESSERTS": "🍰"}
    categories = list(menu.keys())
    keyboard = [[InlineKeyboardButton(f"{emoji_map.get(cat.upper(), '🍽️')} {cat}", callback_data=f"cat_{cat}")] for cat in categories]
    keyboard.append([InlineKeyboardButton("🛒 View Cart & Checkout", callback_data="view_cart")])
    return InlineKeyboardMarkup(keyboard)

def build_items_keyboard(category):
    # ... (This function is unchanged) ...
    menu = get_menu_as_dict()
    items = menu.get(category, [])
    keyboard = [[InlineKeyboardButton(f"{item['itemname']} - £{item['price']:.2f}", callback_data=f"add_{item['itemname']}")] for item in items]
    keyboard.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="show_menu")])
    return InlineKeyboardMarkup(keyboard)

def build_cart_keyboard(cart):
    # ... (This function is unchanged) ...
    keyboard = []
    for item_name in cart.keys():
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"rem_{item_name}"),
            InlineKeyboardButton(f"{cart[item_name]['quantity']}x {item_name}", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data=f"add_{item_name}")
        ])
    keyboard.append([InlineKeyboardButton("✅ Proceed to Checkout", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🛍️ Continue to Order", callback_data="show_menu")])
    return InlineKeyboardMarkup(keyboard)

# --- State Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (This function is unchanged) ...
    print("\n--- NEW CONVERSATION STARTED ---")
    user_id = update.message.from_user.id
    customer = db.find_customer_by_id(user_id)
    
    if customer:
        context.user_data.update(customer)
        context.user_data['cart'] = {}
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, use this address", callback_data="confirm_address_yes")],
            [InlineKeyboardButton("✏️ No, use a different one", callback_data="confirm_address_no")]
        ])
        await update.message.reply_text(
            f"Welcome back, *{customer['full_name']}*! 🙏\n\nShould I use your saved address for delivery?\n\n📍 _{customer['address']}_",
            reply_markup=reply_markup, parse_mode='Markdown'
        )
        print(f"LOG: Returning customer {user_id} found. Awaiting address confirmation.")
        return config.CONFIRMING_ADDRESS
    else:
        context.user_data.clear()
        context.user_data['cart'] = {}
        start_message = (
            f"🙏 Welcome to *{config.RESTAURANT_NAME}*, your personal AI food delivery assistant!\n\n"
            "To get started, please tell me your *full name* and *mobile number*."
        )
        await update.message.reply_text(start_message, parse_mode='Markdown')
        print(f"LOG: New customer {user_id}. Transitioning to GETTING_NAME_AND_PHONE.")
        return config.GETTING_NAME_AND_PHONE

async def get_name_and_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's response for name and phone, remembering previous inputs."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
    
    # Check for existing data to pass to the AI
    existing_data = {}
    if context.user_data.get('full_name'):
        existing_data['name'] = context.user_data['full_name']
    if context.user_data.get('phone_number'):
        existing_data['phone'] = context.user_data['phone_number']

    user_message = update.message.text
    ai_response = ai_engine.get_ai_interpretation(
        context.user_data.get('chat_history', []),
        user_message,
        current_state=config.GETTING_NAME_AND_PHONE,
        user_data=existing_data if existing_data else None
    )
    
    intent = ai_response.get("intent")
    
    # Update context.user_data with any new info from the AI
    if "name" in ai_response:
        context.user_data['full_name'] = ai_response["name"]
    if "phone" in ai_response:
        context.user_data['phone_number'] = ai_response["phone"]

    # Now, check if we have everything
    if context.user_data.get('full_name') and context.user_data.get('phone_number'):
        await update.message.reply_text(
            f"Thank you, *{context.user_data['full_name']}*! 🙏\n\nPlease provide your *full delivery address* and postcode.",
            parse_mode='Markdown'
        )
        return config.GETTING_ADDRESS
    else:
        # If still missing info, send the AI's reply
        await update.message.reply_text(ai_response.get("reply", "I'm sorry, I need a little more information."))
        return config.GETTING_NAME_AND_PHONE

async def handle_address_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (This function is unchanged) ...
    query = update.callback_query
    await query.answer()
    if query.data == 'confirm_address_yes':
        return await check_address_and_proceed(update, context, context.user_data['address'])
    else:
        await query.edit_message_text("No problem. Please provide your new delivery address.")
        return config.GETTING_ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets and cleans a new address using the AI, then saves and checks it."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
    
    user_message = update.message.text
    
    # Use the AI to parse and clean the address first
    ai_response = ai_engine.get_ai_interpretation(
        chat_history=[], user_message=user_message, current_state=config.GETTING_ADDRESS
    )

    if ai_response.get("intent") == "PROVIDE_ADDRESS":
        clean_address = ai_response.get("payload")
        context.user_data['address'] = clean_address
        
        customer_details = {
            'user_id': update.message.from_user.id,
            'full_name': context.user_data.get('full_name'),
            'phone_number': context.user_data.get('phone_number'),
            'address': clean_address
        }
        db.register_or_update_customer(**customer_details)
        if context.job_queue:
            context.job_queue.run_once(services.sync_customer_to_sheet, when=0, data=customer_details)
        
        return await check_address_and_proceed(update, context, clean_address)
    else:
        # Handle chit-chat
        await update.message.reply_text(ai_response.get("reply", "I'm sorry, I didn't understand that as an address."))
        return config.GETTING_ADDRESS

async def check_address_and_proceed(update: Update, context: ContextTypes.DEFAULT_TYPE, address: str) -> int:
    # ... (This function is unchanged but now receives a clean address) ...
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
    
    message_to_send = "👍 Thank you. One moment while I verify the address with our satellites... 🛰️"
    if update.callback_query:
        await update.callback_query.edit_message_text(message_to_send)
    else:
        await update.message.reply_text(message_to_send)

    distance = get_distance_in_miles(address)
    
    if distance is None:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="I'm sorry, I couldn't verify that address. Please provide a different one, including the postcode."
        )
        return config.GETTING_ADDRESS

    if distance > config.DELIVERY_RADIUS_MILES:
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"We're so sorry, but you are outside our delivery radius of {config.DELIVERY_RADIUS_MILES} miles. 😥"
        )
        return ConversationHandler.END

    context.user_data['delivery_charge'] = 0 if distance <= config.FREE_DELIVERY_RADIUS_MILES else config.DELIVERY_CHARGE
    delivery_message = "🎉 Great news! You qualify for *FREE delivery*." if context.user_data['delivery_charge'] == 0 else f"Excellent, you're in our delivery area! A delivery charge of *£{config.DELIVERY_CHARGE:.2f}* will apply."
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text=f"{delivery_message}\n\nLet's get your order started! 🍽️", 
        parse_mode='Markdown'
    )
    return await show_menu(update, context)

# ... The rest of the functions (show_menu, checkout, handle_screenshot, etc.) are unchanged ...
# ... I'm omitting them here for brevity but they should remain in your file ...

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the main menu categories."""
    reply_markup = build_menu_keyboard()
    message_text = "Please choose a category to explore, or type your order directly:"
    if update.callback_query:
        await update.callback_query.answer()
        try:
            await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
        except BadRequest as e:
            if "Message is not modified" not in str(e): raise e
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=reply_markup)
    return config.ORDERING

async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows items for a selected category."""
    query = update.callback_query
    category = query.data.split("_", 1)[1]
    reply_markup = build_items_keyboard(category)
    await query.answer()
    await query.edit_message_text(f"Here are the items for *{category}*:", reply_markup=reply_markup, parse_mode='Markdown')
    return config.ORDERING

async def add_item_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Adds an item to the cart via button press."""
    query = update.callback_query
    item_name = query.data.split("_", 1)[1]
    item_details = get_item_details(item_name)
    
    if item_details:
        cart = context.user_data.get('cart', {})
        if item_name in cart:
            cart[item_name]['quantity'] += 1
        else:
            cart[item_name] = {'quantity': 1, 'price': item_details['price']}
        context.user_data['cart'] = cart
        await query.answer(f"Added {item_name}!")
        return await view_cart(update, context)
    else:
        await query.answer("Sorry, that item could not be found.", show_alert=True)
        return config.ORDERING

async def remove_item_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Removes an item from the cart via button press."""
    query = update.callback_query
    item_name = query.data.split("_", 1)[1]
    cart = context.user_data.get('cart', {})
    
    if item_name in cart:
        cart[item_name]['quantity'] -= 1
        if cart[item_name]['quantity'] <= 0:
            del cart[item_name]
        context.user_data['cart'] = cart
        await query.answer(f"Removed one {item_name}")
    
    if not cart:
        await query.answer("Your cart is now empty.")
        return await show_menu(update, context)
    else:
        return await view_cart(update, context)

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the current cart contents and total."""
    query = update.callback_query
    cart = context.user_data.get('cart', {})
    
    if not cart:
        await query.answer("Your cart is empty!", show_alert=True)
        return await show_menu(update, context)
        
    summary_text, _ = get_cart_summary(cart)
    reply_markup = build_cart_keyboard(cart)
    await query.answer()
    await query.edit_message_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
    return config.ORDERING

async def handle_text_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles a text-based order using the AI engine."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
    user_message = update.message.text
    ai_response = ai_engine.get_ai_interpretation(
        context.user_data.get('chat_history', []), user_message, current_state=config.ORDERING
    )
    intent = ai_response.get("intent")
    reply_text = ai_response.get("reply", "Sorry, I didn't quite catch that.")

    if intent == "ADD_TO_ORDER":
        cart = context.user_data.get('cart', {})
        items_added = []
        for item_data in ai_response.get("items", []):
            item_name = item_data.get("name")
            item_details = get_item_details(item_name)
            if item_details:
                quantity = item_data.get("quantity", 1)
                if item_name in cart:
                    cart[item_name]['quantity'] += quantity
                else:
                    cart[item_name] = {'quantity': quantity, 'price': item_details['price']}
                items_added.append(item_name)
        
        if items_added:
            context.user_data['cart'] = cart
            await update.message.reply_text(reply_text)
            return await view_cart_from_text(update, context)
        else:
            await update.message.reply_text("I'm sorry, I couldn't find those items on our menu. Please try again or use the buttons.")

    elif intent == "CONFIRM_ORDER":
        await update.message.reply_text(reply_text)
        return await view_cart_from_text(update, context)
    
    else: # Handles QUERY_MENU, CHITCHAT, ERROR
        await update.message.reply_text(reply_text)
        
    return config.ORDERING

async def view_cart_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the cart in response to a text command."""
    cart = context.user_data.get('cart', {})
    if not cart:
        await update.message.reply_text("Your cart is empty!", reply_markup=build_menu_keyboard())
        return config.ORDERING
        
    summary_text, _ = get_cart_summary(cart)
    reply_markup = build_cart_keyboard(cart)
    await update.message.reply_text(text=summary_text, reply_markup=reply_markup, parse_mode='Markdown')
    return config.ORDERING

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Finalizes the order and presents the bill."""
    query = update.callback_query
    await context.bot.send_chat_action(chat_id=query.message.chat_id, action=constants.ChatAction.TYPING)
    cart = context.user_data.get('cart', {})
    if not cart:
        await query.answer("Your cart is empty!", show_alert=True)
        return config.ORDERING
        
    summary, subtotal = get_cart_summary(cart)
    delivery_charge = context.user_data.get('delivery_charge', 0)
    total_price = subtotal + delivery_charge
    order_ref = f"NH-{int(time.time())}"
    context.user_data['order_ref'] = order_ref
    
    db.create_order(order_ref, update.effective_user.id, cart, total_price)
    
    payment_details = (
        f"🧾 *Final Bill*\n\n{summary}\n"
        f"Delivery Charge: *£{delivery_charge:.2f}*\n"
        f"---------------------\n*Total to Pay: £{total_price:.2f}*\n\n"
        f"🏦 *Payment Details (For Demo)*\nPlease make a bank transfer to:\n\n"
        f"  - *Account Name:* Namaste-Bot Ltd\n"
        f"  - *Sort Code:* 01-02-03\n"
        f"  - *Account No:* 12345678\n"
        f"  - *Reference:* `{order_ref}`\n\n"
        f"After paying, please upload a *screenshot* of the confirmation as proof."
    )
    
    await query.answer()
    await query.edit_message_text(payment_details, parse_mode='Markdown')
    print(f"LOG: Bill shown for {order_ref}. Transitioning to AWAITING_SCREENSHOT.")
    return config.AWAITING_SCREENSHOT

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the payment screenshot, saves it, and forwards to the restaurant bot."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_PHOTO)
    print("LOG: Received photo in AWAITING_SCREENSHOT state.")
    photo = update.message.photo[-1]
    order_ref = context.user_data.get('order_ref')
    
    screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
    os.makedirs(screenshot_dir, exist_ok=True)
    
    file = await photo.get_file()
    screenshot_path = os.path.join(screenshot_dir, f'{order_ref}.jpg')
    await file.download_to_drive(screenshot_path)
    print(f"LOG: Screenshot for order {order_ref} saved to {screenshot_path}")

    db.update_order_screenshot(order_ref, screenshot_path)
    
    order_details = db.get_order_details(order_ref)
    if not order_details:
        await update.message.reply_text("There was an issue finding your order. Please contact support.")
        return ConversationHandler.END

    cart_summary, _ = get_cart_summary(order_details['cart'])
    order_caption = (
        f"🔔 *New Pending Order: #{order_ref}*\n\n"
        f"👤 *Customer:* {order_details['name']}\n"
        f"📞 *Phone:* {order_details['phone']}\n"
        f"🏠 *Address:* {order_details['address']}\n\n"
        f"{cart_summary}\n\n"
        f"*Total Paid: £{order_details['total_price']:.2f}*"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm Order", callback_data=f"confirm_{order_ref}"),
            InlineKeyboardButton("❌ Reject Order", callback_data=f"reject_{order_ref}")
        ]
    ])

    restaurant_bot = context.application.bot_data['restaurant_bot']
    await restaurant_bot.send_photo(
        chat_id=config.RESTAURANT_CHAT_ID, 
        photo=open(screenshot_path, 'rb'), 
        caption=order_caption, 
        reply_markup=keyboard, 
        parse_mode='Markdown'
    )
    
    await update.message.reply_text("Thank you! Your order has been sent to the restaurant for confirmation. You'll be notified shortly. ⏳")
    print(f"LOG: Order {order_ref} forwarded to restaurant group. User in PENDING_CONFIRMATION.")
    return config.PENDING_CONFIRMATION

async def handle_text_instead_of_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user sending text when a screenshot is expected."""
    await update.message.reply_text("I'm waiting for a payment screenshot. Please upload an image, or type /cancel to stop.")
    return config.AWAITING_SCREENSHOT

async def pending_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Informs the user their order is still pending."""
    await update.message.reply_text("Your order is still pending confirmation. You will be notified as soon as the restaurant reviews it! Please wait a moment. 😊")
    return config.PENDING_CONFIRMATION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the entire conversation."""
    await update.message.reply_text("Order cancelled. Hope to see you again soon! 👋")
    context.user_data.clear()
    print("\n--- CONVERSATION CANCELLED ---\n")
    return ConversationHandler.END

async def no_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """A dummy handler for unclickable buttons."""
    await update.callback_query.answer()