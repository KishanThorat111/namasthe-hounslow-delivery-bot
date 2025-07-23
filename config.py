
# # config.py V1

# # --- Restaurant Details ---
# RESTAURANT_NAME = "Namasthe Hounslow"
# RESTAURANT_ADDRESS = "29-31 Lampton Road, Hounslow, TW3 1JA"
# RESTAURANT_POSTCODE = "TW3 1JA"

# # --- Delivery Settings ---
# DELIVERY_RADIUS_MILES = 5.0
# FREE_DELIVERY_RADIUS_MILES = 2.0
# DELIVERY_CHARGE = 3.50  # Set a default delivery charge

# # --- Google Sheet Settings ---
# GOOGLE_SHEET_NAME = "Namasthe Hounslow Orders"

# # --- Conversational States ---
# # These are used to manage the flow of the conversation
# (GETTING_NAME, GETTING_ADDRESS, 
#  ORDERING, AWAITING_PAYMENT_CONFIRMATION) = range(4)




















# # config.py V2

# # --- Restaurant Details ---
# RESTAURANT_NAME = "Namasthe Hounslow"
# RESTAURANT_ADDRESS = "29-31 Lampton Road, Hounslow, TW3 1JA"
# RESTAURANT_POSTCODE = "TW3 1JA"

# # --- Delivery Settings ---
# DELIVERY_RADIUS_MILES = 5.0
# FREE_DELIVERY_RADIUS_MILES = 2.0
# DELIVERY_CHARGE = 3.50  # Set a default delivery charge

# # --- Google Sheet Settings ---
# GOOGLE_SHEET_NAME = "Namasthe Hounslow Orders"

# # --- Conversational States ---
# # These are used to manage the flow of the conversation
# (GETTING_NAME, GETTING_ADDRESS, 
#  ORDERING, AWAITING_PAYMENT_CONFIRMATION) = range(4)



# # config.py confirmed

# # --- Restaurant Details ---
# RESTAURANT_NAME = "Namasthe Hounslow"
# RESTAURANT_ADDRESS = "29-31 Lampton Road, Hounslow, TW3 1JA"
# RESTAURANT_POSTCODE = "TW3 1JA"

# # --- Delivery Settings ---
# DELIVERY_RADIUS_MILES = 5.0
# FREE_DELIVERY_RADIUS_MILES = 2.0
# DELIVERY_CHARGE = 3.50

# # --- Google Sheet Settings ---
# GOOGLE_SHEET_NAME = "Namasthe Hounslow Orders"

# # --- Conversational States ---
# # These are used to manage the flow of the conversation
# (GETTING_NAME, GETTING_ADDRESS,
#  ORDERING,
#  AWAITING_PAYMENT_CONFIRMATION) = range(4)












# config.py

# --- Restaurant Details ---
RESTAURANT_NAME = "Namasthe Hounslow"
RESTAURANT_ADDRESS = "29-31 Lampton Road, Hounslow, TW3 1JA"
RESTAURANT_POSTCODE = "TW3 1JA"

# --- Delivery Settings ---
DELIVERY_RADIUS_MILES = 5.0
FREE_DELIVERY_RADIUS_MILES = 2.0
DELIVERY_CHARGE = 3.50

# --- Google Sheet Settings ---
GOOGLE_SHEET_NAME = "Namasthe Hounslow Orders"
CUSTOMER_SHEET_NAME = "Customers"

# --- Conversational States ---
# These are used to manage the flow of the conversation
(GETTING_NAME_AND_PHONE, GETTING_ADDRESS,
 CONFIRMING_ADDRESS,
 ORDERING,
 AWAITING_PAYMENT_CONFIRMATION) = range(5)
