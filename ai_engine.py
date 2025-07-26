# # ai_engine.py V1
# import google.generativeai as genai
# import os
# import json

# # Direct imports
# from data_manager import get_menu_as_string
# import config

# # --- Lazy Initialization of the Model ---
# model = None

# def initialize_model():
#     """Initializes and configures the Gemini model."""
#     global model
#     if model is None:
#         try:
#             GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#             if not GEMINI_API_KEY:
#                 raise ValueError("GEMINI_API_KEY not found in environment variables.")
            
#             genai.configure(api_key=GEMINI_API_KEY)
#             model = genai.GenerativeModel('gemini-1.5-flash')
#             print("🤖 Gemini model initialized successfully.")
#         except Exception as e:
#             print(f"❌ CRITICAL ERROR: Could not configure Gemini API: {e}")

# def get_ai_interpretation(chat_history, user_message):
#     """Uses the Gemini API to interpret the user's message in the context of ordering food."""
#     initialize_model()

#     if not model:
#         print("AI model is not available. Skipping AI interpretation.")
#         return {"intent": "ERROR", "reply": "I'm having a little trouble connecting to my brain right now. Please use the menu buttons for now."}
        
#     # This is the new, upgraded prompt with a clear persona and instructions.
#     system_prompt = f"""
#     You are "Namaste-Bot" 🤖, a friendly, professional, and slightly enthusiastic AI waiter for the "{config.RESTAURANT_NAME}" restaurant. Your goal is to provide an exceptional customer experience by helping them build their order.

#     ## Your Persona:
#     - You are helpful, patient, and clear.
#     - You use emojis to make the conversation engaging (e.g., 🍛, 🌶️, 👍, ✅).
#     - You never get confused. If the user's request is unclear, you ask for clarification in a friendly way.
#     - You can make smart suggestions. If a user orders a curry, suggest naan or rice. If they order starters, ask if they're ready for the main course.

#     ## Your Tools:
#     - This is the restaurant's menu, in JSON format. Use it as your single source of truth for items and prices:
#     {get_menu_as_string()}

#     ## Your Task:
#     Analyze the user's latest message based on the provided chat history. Your primary job is to identify their intent and extract food items.

#     ## Intents & Response Format:
#     You MUST respond ONLY with a valid JSON object. Do not add any text before or after the JSON.

#     1.  **Intent: "ADD_TO_ORDER"**
#         - The user wants to add one or more items to their order.
#         - **JSON Format:**
#           {{
#             "intent": "ADD_TO_ORDER",
#             "items": [ {{ "name": "Chicken Tikka Masala", "quantity": 1 }}, {{ "name": "Garlic Naan", "quantity": 2 }} ],
#             "reply": "Excellent choices! 👍 I've added 1 Chicken Tikka Masala and 2 Garlic Naan to your order. What's next?"
#           }}

#     2.  **Intent: "QUERY_MENU"**
#         - The user is asking a question about a dish, ingredients, or recommendations.
#         - **JSON Format:**
#           {{
#             "intent": "QUERY_MENU",
#             "reply": "The Lamb Rogan Josh is a fantastic choice! It's a rich and aromatic curry with tender lamb pieces cooked in a flavourful gravy with a blend of classic Indian spices. It has a medium spice level. 🌶️"
#           }}

#     3.  **Intent: "CONFIRM_ORDER"**
#         - The user is finished ordering and wants to check out.
#         - **JSON Format:**
#           {{
#             "intent": "CONFIRM_ORDER",
#             "reply": "Of course, let's get you ready for checkout."
#           }}

#     4.  **Intent: "OTHER"**
#         - The user's message is a greeting, a thank you, or something unrelated to ordering.
#         - **JSON Format:**
#           {{
#             "intent": "OTHER",
#             "reply": "You're very welcome! Is there anything else I can add to your order?"
#           }}
#     """

#     full_prompt = system_prompt + "\n\n## Conversation Context:\n" + "\n".join(chat_history) + f"\n\n## User's Latest Message:\n{user_message}"

#     try:
#         response = model.generate_content(full_prompt)
#         cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
#         return json.loads(cleaned_response)
#     except Exception as e:
#         print(f"❌ Error during Gemini API call or JSON parsing: {e}")
#         raw_response_text = "No response"
#         if 'response' in locals() and hasattr(response, 'text'):
#             raw_response_text = response.text
#         print(f"Raw AI Response: {raw_response_text}")
#         return {"intent": "ERROR", "reply": "My apologies, I got a little tangled up there. Could you please rephrase that?"}
















# # ai_engine.py V2
# import google.generativeai as genai
# import os
# import json

# # Direct imports
# from data_manager import get_menu_as_string
# import config

# # --- Lazy Initialization of the Model ---
# model = None

# def initialize_model():
#     """Initializes and configures the Gemini model."""
#     global model
#     if model is None:
#         try:
#             GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#             if not GEMINI_API_KEY:
#                 raise ValueError("GEMINI_API_KEY not found in environment variables.")
            
#             genai.configure(api_key=GEMINI_API_KEY)
#             model = genai.GenerativeModel('gemini-1.5-flash')
#             print("🤖 Gemini model initialized successfully.")
#         except Exception as e:
#             print(f"❌ CRITICAL ERROR: Could not configure Gemini API: {e}")

# def get_ai_interpretation(chat_history, user_message, current_state):
#     """
#     Uses the Gemini API to interpret the user's message based on the conversation's current state.
#     """
#     initialize_model()

#     if not model:
#         return {"intent": "ERROR", "reply": "I'm having trouble connecting to my brain right now. Please try again."}
        
#     # The prompt now changes dynamically based on the bot's current state
#     if current_state == config.GETTING_NAME:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖. You have just asked the user for their full name. Analyze their response.
#         Your persona is friendly and forgiving of typos.
#         Determine if the user's message is a plausible name or if it's chit-chat/a question.
#         Respond ONLY with a valid JSON object.
#         1. **Intent: "PROVIDE_NAME"**: `{{"intent": "PROVIDE_NAME", "payload": "Kishan Thorat"}}`
#         2. **Intent: "CHITCHAT"**: `{{"intent": "CHITCHAT", "reply": "I'm doing great, thanks for asking! To get your order started, I'll just need your full name please."}}`
#         """
#     elif current_state == config.GETTING_ADDRESS:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖. You have just asked the user for their delivery address. Analyze their response.
#         Your persona is friendly and forgiving of typos.
#         Determine if the user's message is a plausible address or if it's chit-chat/a question.
#         Respond ONLY with a valid JSON object.
#         1. **Intent: "PROVIDE_ADDRESS"**: `{{"intent": "PROVIDE_ADDRESS", "payload": "5A Smithy LN, Hounslow, TW3 1EY"}}`
#         2. **Intent: "CHITCHAT"**: `{{"intent": "CHITCHAT", "reply": "That's an interesting question! To continue, could you please provide your full delivery address and postcode?"}}`
#         """
#     elif current_state == config.AWAITING_PAYMENT_CONFIRMATION:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖. You have just shown the user the final bill and payment details. Analyze their response.
#         Your persona is polite but firm about payment.
#         Determine if the user is confirming payment or asking something else.
#         Respond ONLY with a valid JSON object.
#         1. **Intent: "CONFIRM_PAYMENT"**: User says "payment done", "paid", "sent", etc.
#            - JSON: `{{"intent": "CONFIRM_PAYMENT"}}`
#         2. **Intent: "CHITCHAT"**: User is asking for a discount, making a comment, or asking a question.
#            - JSON (for "can I get it free?"): `{{"intent": "CHITCHAT", "reply": "I appreciate you asking, but unfortunately, I can't offer discounts. Please type 'payment done' to confirm your order, or /cancel to start over."}}`
#         """
#     else: # This is the main ordering prompt
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖, a friendly and witty AI waiter for "{config.RESTAURANT_NAME}".
#         The user is now ordering. Your goal is to be helpful, engaging, and to understand their order even with typos.
#         Your Tools: Menu: {get_menu_as_string()}
#         Respond ONLY with a valid JSON object with intents: "ADD_TO_ORDER", "QUERY_MENU", "CONFIRM_ORDER", "CHITCHAT".
#         """

#     full_prompt = system_prompt + "\n\n## Conversation History:\n" + "\n".join(chat_history) + f"\n\n## User's Latest Message:\n{user_message}"

#     try:
#         response = model.generate_content(full_prompt)
#         cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
#         return json.loads(cleaned_response)
#     except Exception as e:
#         print(f"❌ Error during Gemini API call or JSON parsing: {e}")
#         return {"intent": "ERROR", "reply": "My apologies, I got a little tangled up there. Could you please rephrase that?"}














# # ai_engine.py Confirmmed
# import google.generativeai as genai
# import os
# import json

# # Direct imports
# from data_manager import get_menu_as_string
# import config

# # --- Lazy Initialization of the Model ---
# model = None

# def initialize_model():
#     """Initializes and configures the Gemini model."""
#     global model
#     if model is None:
#         try:
#             GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#             if not GEMINI_API_KEY:
#                 raise ValueError("GEMINI_API_KEY not found in environment variables.")
            
#             genai.configure(api_key=GEMINI_API_KEY)
#             model = genai.GenerativeModel('gemini-1.5-flash')
#             print("🤖 Gemini model initialized successfully.")
#         except Exception as e:
#             print(f"❌ CRITICAL ERROR: Could not configure Gemini API: {e}")

# def get_ai_interpretation(chat_history, user_message, current_state):
#     """
#     Uses the Gemini API to interpret the user's message based on the conversation's current state.
#     """
#     initialize_model()

#     if not model:
#         return {"intent": "ERROR", "reply": "I'm having trouble connecting to my brain right now. Please try again."}
        
#     # The prompt now changes dynamically based on the bot's current state
#     if current_state == config.GETTING_NAME:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖, an AI assistant for "{config.RESTAURANT_NAME}".
#         You have just asked the user for their full name. Analyze their response.
#         Your persona is friendly and forgiving of typos.
        
#         ## Your Task & Response Format
#         Determine if the user's message is a plausible name or if it's chit-chat/a question.
#         Respond ONLY with a valid JSON object.

#         1. **Intent: "PROVIDE_NAME"** - The user provided something that looks like a name.
#            - JSON: `{{"intent": "PROVIDE_NAME", "payload": "Kishan Thorat"}}`

#         2. **Intent: "CHITCHAT"** - The user is asking a question or making small talk instead of giving a name.
#            - JSON: `{{"intent": "CHITCHAT", "reply": "I'm doing great, thanks for asking! To get your order started, I'll just need your full name please."}}`
#         """
#     elif current_state == config.GETTING_ADDRESS:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖, an AI assistant for "{config.RESTAURANT_NAME}".
#         You have just asked the user for their delivery address. Analyze their response.
#         Your persona is friendly and forgiving of typos.
        
#         ## Your Task & Response Format
#         Determine if the user's message is a plausible address or if it's chit-chat/a question.
#         Respond ONLY with a valid JSON object.

#         1. **Intent: "PROVIDE_ADDRESS"** - The user provided something that looks like an address.
#            - JSON: `{{"intent": "PROVIDE_ADDRESS", "payload": "5A Smithy LN, Hounslow, TW3 1EY"}}`

#         2. **Intent: "CHITCHAT"** - The user is asking a question or making small talk.
#            - JSON: `{{"intent": "CHITCHAT", "reply": "That's an interesting question! To continue, could you please provide your full delivery address and postcode?"}}`
#         """
#     elif current_state == config.AWAITING_PAYMENT_CONFIRMATION:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖. You have just shown the user the final bill and payment details. Analyze their response.
#         Your persona is polite but firm about payment.
#         Determine if the user is confirming payment or asking something else.
#         Respond ONLY with a valid JSON object.
#         1. **Intent: "CONFIRM_PAYMENT"**: User says "payment done", "paid", "sent", etc.
#            - JSON: `{{"intent": "CONFIRM_PAYMENT"}}`
#         2. **Intent: "CHITCHAT"**: User is asking for a discount, making a comment, or asking a question.
#            - JSON (for "can I get it free?"): `{{"intent": "CHITCHAT", "reply": "I appreciate you asking, but unfortunately, I can't offer discounts. Please type 'payment done' to confirm your order, or /cancel to start over."}}`
#         """
#     else: # This is the main ordering prompt
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖, a friendly and witty AI waiter for "{config.RESTAURANT_NAME}".
#         The user is now ordering. Your goal is to be helpful, engaging, and to understand their order even with typos.
        
#         ## Your Tools:
#         - Menu: {get_menu_as_string()}

#         ## Intents & Response Format
#         Respond ONLY with a valid JSON object with intents: "ADD_TO_ORDER", "QUERY_MENU", "CONFIRM_ORDER", "CHITCHAT".
#         """

#     full_prompt = system_prompt + "\n\n## Conversation History:\n" + "\n".join(chat_history) + f"\n\n## User's Latest Message:\n{user_message}"

#     try:
#         response = model.generate_content(full_prompt)
#         cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
#         return json.loads(cleaned_response)
#     except Exception as e:
#         print(f"❌ Error during Gemini API call or JSON parsing: {e}")
#         return {"intent": "ERROR", "reply": "My apologies, I got a little tangled up there. Could you please rephrase that?"}




























# # ai_engine.py Working Single bot
# import google.generativeai as genai
# import os
# import json

# # Direct imports
# from data_manager import get_menu_as_string
# import config

# # --- Lazy Initialization of the Model ---
# model = None

# def initialize_model():
#     """Initializes and configures the Gemini model."""
#     global model
#     if model is None:
#         try:
#             GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#             if not GEMINI_API_KEY:
#                 raise ValueError("GEMINI_API_KEY not found in environment variables.")
            
#             genai.configure(api_key=GEMINI_API_KEY)
#             model = genai.GenerativeModel('gemini-1.5-flash')
#             print("🤖 Gemini model initialized successfully.")
#         except Exception as e:
#             print(f"❌ CRITICAL ERROR: Could not configure Gemini API: {e}")

# def get_ai_interpretation(chat_history, user_message, current_state):
#     """
#     Uses the Gemini API to interpret the user's message based on the conversation's current state.
#     """
#     initialize_model()

#     if not model:
#         return {"intent": "ERROR", "reply": "I'm having trouble connecting to my brain right now. Please try again."}
        
#     # The prompt now changes dynamically based on the bot's current state
#     # if current_state == config.GETTING_NAME:
#     if current_state == config.GETTING_NAME_AND_PHONE:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖, an AI assistant for "{config.RESTAURANT_NAME}".
#         You have just asked the user for their full name. Analyze their response.
#         Your persona is friendly and forgiving of typos.
        
#         ## Your Task & Response Format
#         Determine if the user's message is a plausible name or if it's chit-chat/a question.
#         Respond ONLY with a valid JSON object.

#         1. **Intent: "PROVIDE_NAME"** - The user provided something that looks like a name.
#            - JSON: `{{"intent": "PROVIDE_NAME", "payload": "Kishan Thorat"}}`

#         2. **Intent: "CHITCHAT"** - The user is asking a question or making small talk instead of giving a name.
#            - JSON: `{{"intent": "CHITCHAT", "reply": "I'm doing great, thanks for asking! To get your order started, I'll just need your full name please."}}`
#         """
#     elif current_state == config.GETTING_ADDRESS:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖, an AI assistant for "{config.RESTAURANT_NAME}".
#         You have just asked the user for their delivery address. Analyze their response.
#         Your persona is friendly and forgiving of typos.
        
#         ## Your Task & Response Format
#         Determine if the user's message is a plausible address or if it's chit-chat/a question.
#         Respond ONLY with a valid JSON object.

#         1. **Intent: "PROVIDE_ADDRESS"** - The user provided something that looks like an address.
#            - JSON: `{{"intent": "PROVIDE_ADDRESS", "payload": "5A Smithy LN, Hounslow, TW3 1EY"}}`

#         2. **Intent: "CHITCHAT"** - The user is asking a question or making small talk.
#            - JSON: `{{"intent": "CHITCHAT", "reply": "That's an interesting question! To continue, could you please provide your full delivery address and postcode?"}}`
#         """
#     elif current_state == config.AWAITING_PAYMENT_CONFIRMATION:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖. You have just shown the user the final bill and payment details. Analyze their response.
#         Your persona is polite but firm about payment.
#         Determine if the user is confirming payment or asking something else.
#         Respond ONLY with a valid JSON object.
#         1. **Intent: "CONFIRM_PAYMENT"**: User says "payment done", "paid", "sent", etc.
#            - JSON: `{{"intent": "CONFIRM_PAYMENT"}}`
#         2. **Intent: "CHITCHAT"**: User is asking for a discount, making a comment, or asking a question.
#            - JSON (for "can I get it free?"): `{{"intent": "CHITCHAT", "reply": "I appreciate you asking, but unfortunately, I can't offer discounts. Please type 'payment done' to confirm your order, or /cancel to start over."}}`
#         """
#     else: # This is the main ordering prompt
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖, a friendly and witty AI waiter for "{config.RESTAURANT_NAME}".
#         The user is now ordering. Your goal is to be helpful, engaging, and to understand their order even with typos.
        
#         ## Your Tools:
#         - Menu: {get_menu_as_string()}

#         ## Intents & Response Format
#         Respond ONLY with a valid JSON object with intents: "ADD_TO_ORDER", "QUERY_MENU", "CONFIRM_ORDER", "CHITCHAT".
#         """

#     full_prompt = system_prompt + "\n\n## Conversation History:\n" + "\n".join(chat_history) + f"\n\n## User's Latest Message:\n{user_message}"

#     try:
#         response = model.generate_content(full_prompt)
#         cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
#         return json.loads(cleaned_response)
#     except Exception as e:
#         print(f"❌ Error during Gemini API call or JSON parsing: {e}")
#         return {"intent": "ERROR", "reply": "My apologies, I got a little tangled up there. Could you please rephrase that?"}













# # working for VM



# import google.generativeai as genai
# import os
# import json
# from data_manager import get_menu_as_string
# import config

# model = None

# def initialize_model():
#     """Initializes and configures the Gemini model."""
#     global model
#     if model is None:
#         try:
#             if not config.GEMINI_API_KEY:
#                 raise ValueError("GEMINI_API_KEY not found in environment variables.")
            
#             genai.configure(api_key=config.GEMINI_API_KEY)
#             model = genai.GenerativeModel('gemini-1.5-flash')
#             print("🤖 Gemini model initialized successfully.")
#         except Exception as e:
#             print(f"❌ CRITICAL ERROR: Could not configure Gemini API: {e}")

# def get_ai_interpretation(chat_history, user_message, current_state):
#     """
#     Uses the Gemini API to interpret the user's message based on the conversation's current state.
#     """
#     initialize_model()

#     if not model:
#         return {"intent": "ERROR", "reply": "I'm having trouble connecting to my brain right now. Please try again."}
        
#     if current_state == config.GETTING_NAME_AND_PHONE:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖. You have just asked the user for their full name and mobile number.
#         Your task is to extract the full name and a plausible UK mobile number from the user's response.
#         Your persona is friendly and forgiving of typos or different formats (e.g., +44, 07...).

#         ## Rules & Response Format
#         - A name should have at least two parts.
#         - A phone number can be in any valid UK format.
#         - If the user provides both in one message, extract both.
#         - If the user provides only one, ask for the missing piece.
#         - Respond ONLY with a valid JSON object.

#         ## Examples
#         - User says: "Kishan Thorat, 07123456789" -> `{{"intent": "PROVIDE_DETAILS", "name": "Kishan Thorat", "phone": "07123456789"}}`
#         - User says: "My name is Kishan" -> `{{"intent": "MISSING_INFO", "reply": "Thanks, Kishan. Could you also provide your mobile number please?"}}`
#         - User says: "Here is my number +441234567890" -> `{{"intent": "MISSING_INFO", "reply": "Thanks for your number. Could you also provide your full name please?"}}`
#         - User says: "how are you" -> `{{"intent": "CHITCHAT", "reply": "I'm doing great, thanks! To get your order started, I'll just need your full name and mobile number please."}}`

#         ## Intents
#         1. **"PROVIDE_DETAILS"**: Both name and number were found.
#         2. **"MISSING_INFO"**: Only one piece of information was found.
#         3. **"CHITCHAT"**: The user is making small talk.
#         """
#     elif current_state == config.GETTING_ADDRESS:
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖. You have just asked for the delivery address. Analyze their response.
#         Determine if the user's message is a plausible address or if it's chit-chat.
#         Respond ONLY with a valid JSON object.
#         1. **Intent: "PROVIDE_ADDRESS"**: {{"intent": "PROVIDE_ADDRESS", "payload": "5A Smithy LN, Hounslow, TW3 1EY"}}
#         2. **Intent: "CHITCHAT"**: {{"intent": "CHITCHAT", "reply": "That's an interesting question! To continue, could you please provide your full delivery address?"}}
#         """
#     else: # This is the main ordering prompt
#         menu_string = get_menu_as_string()
#         system_prompt = f"""
#         You are "Namaste-Bot" 🤖, a friendly and witty AI waiter for "{config.RESTAURANT_NAME}".
#         The user is now ordering food. Your primary goal is to accurately identify food items and quantities from their text message.
#         - You can handle typos (e.g., "chiken biryany" -> "Chicken Biryani").
#         - If a user just says "yes" or "confirm order", understand they want to proceed to checkout.
#         - Your Tool: Menu (use this to validate items): {menu_string}

#         ## Your Task & Response Format
#         Analyze the user's message and respond ONLY with a valid JSON object using one of these intents:

#         1. **Intent: "ADD_TO_ORDER"**: The user wants to add one or more items to their cart.
#            - **Required JSON**: `{{"intent": "ADD_TO_ORDER", "reply": "Great choices! I've added 2 Chicken Tikkas and 1 Lamb Rogan Josh to your order.", "items": [{{"name": "Chicken Tikka", "quantity": 2}}, {{"name": "Lamb Rogan Josh", "quantity": 1}}]}}`

#         2. **Intent: "QUERY_MENU"**: The user is asking a question about the menu (e.g., "what starters do you have?", "is the madras spicy?").
#            - **Required JSON**: `{{"intent": "QUERY_MENU", "reply": "Our Madras is quite spicy! For starters, we have Samosas, Onion Bhajis, and more. You can also browse using the menu buttons."}}`

#         3. **Intent: "CONFIRM_ORDER"**: The user is ready to check out (e.g., "that's all", "checkout", "proceed", "yes").
#            - **Required JSON**: `{{"intent": "CONFIRM_ORDER", "reply": "Perfect! Let me just get your cart ready for you to review."}}`
           
#         4. **Intent: "CHITCHAT"**: The user is making small talk not related to the order.
#            - **Required JSON**: `{{"intent": "CHITCHAT", "reply": "I'm happy to chat, but I'm even happier to take your order! What can I get for you?"}}`
#         """

#     full_prompt = system_prompt + "\n\n## Conversation History:\n" + "\n".join(chat_history) + f"\n\n## User's Latest Message:\n{user_message}"

#     try:
#         response = model.generate_content(full_prompt)
#         cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
#         return json.loads(cleaned_response)
#     except Exception as e:
#         print(f"❌ Error during Gemini API call or JSON parsing: {e}")
#         return {"intent": "ERROR", "reply": "My apologies, I got a little tangled up there. Could you please rephrase that?"}







import google.generativeai as genai
import os
import json
from data_manager import get_menu_as_string
import config

model = None

def initialize_model():
    """Initializes and configures the Gemini model."""
    global model
    if model is None:
        try:
            if not config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not found in environment variables.")
            
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("🤖 Gemini model initialized successfully.")
        except Exception as e:
            print(f"❌ CRITICAL ERROR: Could not configure Gemini API: {e}")

def get_ai_interpretation(chat_history, user_message, current_state, user_data=None):
    """
    Uses the Gemini API for conversational tasks like gathering user info or parsing orders.
    """
    initialize_model()

    if not model:
        return {"intent": "ERROR", "reply": "I'm having trouble connecting to my brain right now. Please try again."}
        
    if current_state == config.GETTING_NAME_AND_PHONE:
        existing_data_prompt = f"You already have this information about the user: {user_data}. " if user_data else ""
        system_prompt = f"""
        You are "Namaste-Bot" 🤖. You are collecting a user's full name and mobile number.
        {existing_data_prompt}Your task is to analyze the user's latest message and extract any new information.
        Your persona is friendly and forgiving of typos or different formats (e.g., +44, 07...).
        ## Rules & Response Format
        - A name should have at least two parts. A phone number must be a plausible UK number.
        - If the user provides information you already have, just acknowledge it.
        - If the user provides the missing piece of information, extract it.
        - Respond ONLY with a valid JSON object.
        ## Intents & Examples
        1. "PROVIDE_DETAILS": User provides all info at once. -> `{{"intent": "PROVIDE_DETAILS", "name": "Jhon roose", "phone": "+447653765316"}}`
        2. "MISSING_INFO": User provides partial info for the first time. -> `{{"intent": "MISSING_INFO", "name": "Jhon roose", "reply": "Thank you, Jhon roose. Could you also provide your mobile number please?"}}`
        3. "UPDATE_DETAILS": User provides the missing piece of information. -> `{{"intent": "UPDATE_DETAILS", "phone": "07653765316"}}`
        4. "CHITCHAT": User makes small talk. -> `{{"intent": "CHITCHAT", "reply": "I'm doing great, thanks! To continue, I'll just need your full name and mobile number please."}}`
        """
    else: # This is the main ordering prompt
        system_prompt = f"""
        You are "Namaste-Bot" 🤖, a friendly AI waiter. Your goal is to understand a user's food order.
        Menu: {get_menu_as_string()}
        Respond ONLY with a valid JSON object with intents: "ADD_TO_ORDER", "QUERY_MENU", "CONFIRM_ORDER", "CHITCHAT".
        """

    full_prompt = system_prompt + "\n\n## Conversation History:\n" + "\n".join(chat_history) + f"\n\n## User's Latest Message:\n{user_message}"

    try:
        response = model.generate_content(full_prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"❌ Error during Gemini API call or JSON parsing: {e}")
        return {"intent": "ERROR", "reply": "My apologies, I got a little tangled up there. Could you please rephrase that?"}

def get_distance_with_gemini(user_address: str, restaurant_address: str):
    """
    Uses the Gemini API to act as a powerful geocoding and distance calculation tool.
    """
    initialize_model()
    if not model:
        return {"status": "API_ERROR", "reason": "AI model not initialized."}

    system_prompt = f"""
    You are a high-precision Geospatial Calculation API. Your only task is to calculate the driving distance in miles between an origin and a destination in the UK.

    ## Rules
    1. First, attempt to geocode both the origin and destination addresses. The addresses might be messy or multi-line; clean them up as needed.
    2. If both addresses are successfully geocoded, calculate the driving distance between them in miles.
    3. If you cannot geocode a provided address, you must return a status of "ADDRESS_NOT_FOUND".
    4. Respond ONLY with a valid JSON object. Do not include any other text or explanations.

    ## JSON Output Format
    - On success: `{{"status": "SUCCESS", "distance_miles": 4.2}}`
    - On failure: `{{"status": "ADDRESS_NOT_FOUND", "reason": "Could not geocode the destination address '{user_address}'."}}`

    ## Input Data
    - Origin Address: "{restaurant_address}"
    - Destination Address: "{user_address}"
    """
    try:
        response = model.generate_content(system_prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"❌ Error during Gemini distance calculation: {e}")
        return {"status": "API_ERROR", "reason": str(e)}