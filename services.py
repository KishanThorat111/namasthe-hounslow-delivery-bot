# # services.py V1
# import gspread
# from google.oauth2.service_account import Credentials
# from geopy.geocoders import Nominatim
# from geopy.distance import geodesic
# from geopy.exc import GeocoderUnavailable
# import time
# import os

# # Direct import since config.py is in the same folder
# import config

# # --- Google Sheets Service ---

# def get_gspread_client():
#     """
#     Authenticates with the Google Sheets API using service account credentials
#     and returns a gspread client object.
#     """
#     try:
#         scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
#         # Path to the credentials file, now in the root project folder
#         creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        
#         if not os.path.exists(creds_path):
#             raise FileNotFoundError("ERROR: 'credentials.json' not found in the main project folder.")

#         creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
#         client = gspread.authorize(creds)
#         return client
#     except Exception as e:
#         print(f"An error occurred during Google Sheets authentication: {e}")
#         return None

# def log_order_to_sheet(customer_name, customer_address, order_details, total_price):
#     """Logs a completed order to the specified Google Sheet."""
#     client = get_gspread_client()
#     if not client:
#         print("Could not connect to Google Sheets. Order not logged.")
#         return

#     try:
#         sheet = client.open(config.GOOGLE_SHEET_NAME).sheet1
#         timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#         row = [timestamp, customer_name, customer_address, str(order_details), f"£{total_price:.2f}"]
#         sheet.append_row(row)
#         print("Order successfully logged to Google Sheet.")
        
#     except gspread.exceptions.SpreadsheetNotFound:
#         print(f"ERROR: Spreadsheet '{config.GOOGLE_SHEET_NAME}' not found. Please create it and share it.")
#     except Exception as e:
#         print(f"An error occurred while logging the order: {e}")


# # --- Location Service ---

# def get_distance_in_miles(customer_postcode):
#     """
#     Calculates the distance between the restaurant and the customer's postcode.
#     Returns the distance in miles or None if an address cannot be found.
#     """
#     geolocator = Nominatim(user_agent="namasthe_hounslow_bot")
#     try:
#         restaurant_location = geolocator.geocode(config.RESTAURANT_POSTCODE, country_codes="GB")
#         if not restaurant_location:
#             print(f"Could not geocode restaurant postcode: {config.RESTAURANT_POSTCODE}")
#             return None

#         customer_location = geolocator.geocode(customer_postcode, country_codes="GB")
#         if not customer_location:
#             print(f"Could not geocode customer postcode: {customer_postcode}")
#             return None

#         distance = geodesic(
#             (restaurant_location.latitude, restaurant_location.longitude),
#             (customer_location.latitude, customer_location.longitude)
#         ).miles
        
#         return distance
        
#     except GeocoderUnavailable:
#         print("Geocoder service is unavailable. Please try again later.")
#         return None
#     except Exception as e:
#         print(f"An error occurred during geocoding: {e}")
#         return None
































# # services.py V2
# import gspread
# from google.oauth2.service_account import Credentials
# from geopy.geocoders import Nominatim
# from geopy.distance import geodesic
# from geopy.exc import GeocoderUnavailable
# import time
# import os

# # Direct import since config.py is in the same folder
# import config

# # --- Google Sheets Service ---

# def get_gspread_client():
#     """
#     Authenticates with the Google Sheets API using service account credentials
#     and returns a gspread client object.
#     """
#     try:
#         scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
#         # Path to the credentials file, now in the root project folder
#         creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        
#         if not os.path.exists(creds_path):
#             raise FileNotFoundError("ERROR: 'credentials.json' not found in the main project folder.")

#         creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
#         client = gspread.authorize(creds)
#         return client
#     except Exception as e:
#         print(f"An error occurred during Google Sheets authentication: {e}")
#         return None

# def log_order_to_sheet(customer_name, customer_address, order_details, total_price):
#     """Logs a completed order to the specified Google Sheet."""
#     client = get_gspread_client()
#     if not client:
#         print("Could not connect to Google Sheets. Order not logged.")
#         return

#     try:
#         sheet = client.open(config.GOOGLE_SHEET_NAME).sheet1
#         timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#         row = [timestamp, customer_name, customer_address, str(order_details), f"£{total_price:.2f}"]
#         sheet.append_row(row)
#         print("Order successfully logged to Google Sheet.")
        
#     except gspread.exceptions.SpreadsheetNotFound:
#         print(f"ERROR: Spreadsheet '{config.GOOGLE_SHEET_NAME}' not found. Please create it and share it.")
#     except Exception as e:
#         print(f"An error occurred while logging the order: {e}")


# # --- Location Service ---

# def get_distance_in_miles(customer_postcode):
#     """
#     Calculates the distance between the restaurant and the customer's postcode.
#     Returns the distance in miles or None if an address cannot be found.
#     """
#     geolocator = Nominatim(user_agent="namasthe_hounslow_bot")
#     try:
#         restaurant_location = geolocator.geocode(config.RESTAURANT_POSTCODE, country_codes="GB")
#         if not restaurant_location:
#             print(f"Could not geocode restaurant postcode: {config.RESTAURANT_POSTCODE}")
#             return None

#         customer_location = geolocator.geocode(customer_postcode, country_codes="GB")
#         if not customer_location:
#             print(f"Could not geocode customer postcode: {customer_postcode}")
#             return None

#         distance = geodesic(
#             (restaurant_location.latitude, restaurant_location.longitude),
#             (customer_location.latitude, customer_location.longitude)
#         ).miles
        
#         return distance
        
#     except GeocoderUnavailable:
#         print("Geocoder service is unavailable. Please try again later.")
#         return None
#     except Exception as e:
#         print(f"An error occurred during geocoding: {e}")
#         return None






















# # services.py Confirmed
# import gspread
# from google.oauth2.service_account import Credentials
# from geopy.geocoders import Nominatim
# from geopy.distance import geodesic
# from geopy.exc import GeocoderUnavailable
# import time
# import os

# # Direct import since config.py is in the same folder
# import config

# # --- Google Sheets Service ---

# def get_gspread_client():
#     """
#     Authenticates with the Google Sheets API using service account credentials
#     and returns a gspread client object.
#     """
#     try:
#         scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
#         creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
#         if not os.path.exists(creds_path):
#             raise FileNotFoundError("ERROR: 'credentials.json' not found in the main project folder.")
#         creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
#         client = gspread.authorize(creds)
#         return client
#     except Exception as e:
#         print(f"An error occurred during Google Sheets authentication: {e}")
#         return None

# def log_order_to_sheet(customer_name, customer_address, order_details, total_price):
#     """Logs a completed order to the specified Google Sheet."""
#     client = get_gspread_client()
#     if not client:
#         print("Could not connect to Google Sheets. Order not logged.")
#         return

#     try:
#         sheet = client.open(config.GOOGLE_SHEET_NAME).sheet1
#         timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#         row = [timestamp, customer_name, customer_address, str(order_details), f"£{total_price:.2f}"]
#         sheet.append_row(row)
#         print("Order successfully logged to Google Sheet.")
#     except gspread.exceptions.SpreadsheetNotFound:
#         print(f"ERROR: Spreadsheet '{config.GOOGLE_SHEET_NAME}' not found. Please create it and share it.")
#     except Exception as e:
#         print(f"An error occurred while logging the order: {e}")

# # --- Location Service ---

# def get_distance_in_miles(customer_postcode):
#     """
#     Calculates the distance between the restaurant and the customer's postcode.
#     Returns the distance in miles or None if an address cannot be found.
#     """
#     geolocator = Nominatim(user_agent="namasthe_hounslow_bot")
#     try:
#         restaurant_location = geolocator.geocode(config.RESTAURANT_POSTCODE, country_codes="GB")
#         if not restaurant_location:
#             print(f"Could not geocode restaurant postcode: {config.RESTAURANT_POSTCODE}")
#             return None
#         customer_location = geolocator.geocode(customer_postcode, country_codes="GB")
#         if not customer_location:
#             print(f"Could not geocode customer postcode: {customer_postcode}")
#             return None
#         distance = geodesic(
#             (restaurant_location.latitude, restaurant_location.longitude),
#             (customer_location.latitude, customer_location.longitude)
#         ).miles
#         return distance
#     except GeocoderUnavailable:
#         print("Geocoder service is unavailable. Please try again later.")
#         return None
#     except Exception as e:
#         print(f"An error occurred during geocoding: {e}")
#         return None































# # services.py   Working Sngle Bot
# import gspread
# from google.oauth2.service_account import Credentials
# from geopy.geocoders import Nominatim
# from geopy.distance import geodesic
# from geopy.exc import GeocoderUnavailable
# import time
# import os

# # Direct import since config.py is in the same folder
# import config

# # --- Google Sheets Service ---

# def get_gspread_client():
#     """Authenticates with the Google Sheets API and returns a gspread client."""
#     try:
#         scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
#         creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
#         if not os.path.exists(creds_path):
#             raise FileNotFoundError("ERROR: 'credentials.json' not found.")
#         creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
#         client = gspread.authorize(creds)
#         return client
#     except Exception as e:
#         print(f"An error occurred during Google Sheets authentication: {e}")
#         return None

# def log_order_to_sheet(customer_name, customer_address, order_details, total_price):
#     """Logs a completed order to the orders sheet."""
#     client = get_gspread_client()
#     if not client: return
#     try:
#         sheet = client.open(config.GOOGLE_SHEET_NAME).sheet1
#         timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#         row = [timestamp, customer_name, customer_address, str(order_details), f"£{total_price:.2f}"]
#         sheet.append_row(row)
#         print("Order successfully logged to Google Sheet.")
#     except Exception as e:
#         print(f"An error occurred while logging the order: {e}")

# # --- Customer Database Functions ---

# def find_customer_by_id(user_id):
#     """Searches the Customers sheet for a user by their Telegram ID."""
#     client = get_gspread_client()
#     if not client: return None
#     try:
#         sheet = client.open(config.GOOGLE_SHEET_NAME).worksheet(config.CUSTOMER_SHEET_NAME)
#         cell = sheet.find(str(user_id), in_column=1)
#         if cell:
#             customer_row = sheet.row_values(cell.row)
#             return {
#                 "telegram_user_id": customer_row[0],
#                 "full_name": customer_row[1],
#                 "address": customer_row[2],
#                 "mobile_number": customer_row[3] if len(customer_row) > 3 else None
#             }
#         return None
#     except gspread.exceptions.WorksheetNotFound:
#         print(f"ERROR: Customer sheet '{config.CUSTOMER_SHEET_NAME}' not found. Please create it.")
#         return None
#     except Exception as e:
#         print(f"An error occurred while finding a customer: {e}")
#         return None

# def register_or_update_customer(user_id, full_name, address, mobile_number):
#     """Adds a new customer or updates an existing one."""
#     client = get_gspread_client()
#     if not client: return
#     try:
#         sheet = client.open(config.GOOGLE_SHEET_NAME).worksheet(config.CUSTOMER_SHEET_NAME)
#         cell = sheet.find(str(user_id), in_column=1)
#         row = [str(user_id), full_name, address, mobile_number]
#         if cell:
#             sheet.update(f'A{cell.row}:D{cell.row}', [row])
#             print(f"Customer {full_name} updated.")
#         else:
#             sheet.append_row(row)
#             print(f"New customer registered: {full_name}")
#     except Exception as e:
#         print(f"An error occurred while registering/updating a customer: {e}")


# # --- Location Service (Unchanged) ---

# def get_distance_in_miles(customer_postcode):
#     """Calculates the distance between the restaurant and the customer's postcode."""
#     geolocator = Nominatim(user_agent="namaste_hounslow_bot")
#     try:
#         restaurant_location = geolocator.geocode(config.RESTAURANT_POSTCODE, country_codes="GB")
#         if not restaurant_location: return None
#         customer_location = geolocator.geocode(customer_postcode, country_codes="GB")
#         if not customer_location: return None
#         distance = geodesic(
#             (restaurant_location.latitude, restaurant_location.longitude),
#             (customer_location.latitude, customer_location.longitude)
#         ).miles
#         return distance
#     except Exception as e:
#         print(f"An error occurred during geocoding: {e}")
#         return None















# services.py

import gspread
from google.oauth2.service_account import Credentials
import os
import config
import time
from telegram.ext import ContextTypes # Import ContextTypes

def get_gspread_client():
    """Authenticates with the Google Sheets API and returns a gspread client."""
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if not os.path.exists(creds_path):
            raise FileNotFoundError("ERROR: 'credentials.json' not found.")
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"SHEETS ERROR: Could not authenticate with Google Sheets API: {e}")
        return None

async def sync_customer_to_sheet(context: ContextTypes.DEFAULT_TYPE):
    """
    Job queue function to sync customer data to Google Sheets.
    Defined as async to work with the job queue.
    """
    customer = context.job.data
    client = get_gspread_client()
    if not client: return
    
    print(f"SYNC: Attempting to sync customer {customer['user_id']} to Google Sheet.")
    try:
        sheet = client.open(config.GOOGLE_SHEET_NAME).worksheet(config.CUSTOMER_SHEET_NAME)
        cell = sheet.find(str(customer['user_id']), in_column=1)
        row = [
            str(customer['user_id']), 
            customer['full_name'], 
            customer['address'], 
            str(customer['phone_number'])
        ]
        if cell:
            sheet.update(f'A{cell.row}:D{cell.row}', [row])
            print(f"SYNC: Customer {customer['full_name']} updated in Sheet.")
        else:
            sheet.append_row(row)
            print(f"SYNC: New customer {customer['full_name']} added to Sheet.")
    except Exception as e:
        print(f"SHEETS ERROR: Failed to sync customer {customer['user_id']}: {e}")

async def sync_order_to_sheet(context: ContextTypes.DEFAULT_TYPE):
    """
    Job queue function to log a completed order to the orders sheet.
    Defined as async to work with the job queue.
    """
    order = context.job.data
    client = get_gspread_client()
    if not client: return

    print(f"SYNC: Attempting to sync order {order['order_id']} to Google Sheet.")
    try:
        sheet = client.open(config.GOOGLE_SHEET_NAME).worksheet(config.ORDER_SHEET_NAME)
        cart_string = "; ".join([f"{details['quantity']}x {name}" for name, details in order['cart'].items()])
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        row = [
            order['order_id'],
            timestamp,
            order['name'],
            order['address'],
            order['phone'],
            cart_string,
            f"£{order['total_price']:.2f}",
            'Confirmed'
        ]
        sheet.append_row(row)
        print(f"SYNC: Order {order['order_id']} successfully logged to Google Sheet.")
    except Exception as e:
        print(f"SHEETS ERROR: Failed to sync order {order['order_id']}: {e}")