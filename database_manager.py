import sqlite3
import os
import json
import config

DB_PATH = os.path.join(os.path.dirname(__file__), config.DATABASE_FILE)

def setup_database():
    """Creates the database and tables if they don't exist."""
    # This function runs in the main thread, so it doesn't strictly need it,
    # but we add it for consistency.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            telegram_id INTEGER PRIMARY KEY,
            full_name TEXT,
            phone_number TEXT,
            address TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id INTEGER,
            cart_data TEXT,
            total_price REAL,
            status TEXT,
            screenshot_path TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (telegram_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Local database setup complete.")

def find_customer_by_id(user_id):
    """Finds a customer by their Telegram ID from the local database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE telegram_id = ?", (user_id,))
    customer = cursor.fetchone()
    conn.close()
    if customer:
        return {
            "telegram_id": customer[0],
            "full_name": customer[1],
            "phone_number": customer[2],
            "address": customer[3]
        }
    return None

def register_or_update_customer(user_id, full_name, phone_number, address):
    """Adds a new customer or updates an existing one in the local database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customers (telegram_id, full_name, phone_number, address)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
            full_name = excluded.full_name,
            phone_number = excluded.phone_number,
            address = excluded.address
    ''', (user_id, full_name, phone_number, address))
    conn.commit()
    conn.close()
    print(f"LOG: Customer {user_id} data saved/updated in local DB.")

def create_order(order_id, customer_id, cart, total_price):
    """Creates a new order record in the local database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (order_id, customer_id, cart_data, total_price, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (order_id, customer_id, json.dumps(cart), total_price, 'awaiting_screenshot'))
    conn.commit()
    conn.close()
    print(f"LOG: Created new order {order_id} in local DB.")

def update_order_screenshot(order_id, screenshot_path):
    """Updates an order with the screenshot path and changes status."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET screenshot_path = ?, status = 'pending_approval' WHERE order_id = ?", (screenshot_path, order_id))
    conn.commit()
    conn.close()
    print(f"LOG: Updated order {order_id} with screenshot path in local DB.")

def update_order_status(order_id, status):
    """Updates the status of an order (e.g., 'confirmed', 'rejected')."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
    conn.commit()
    conn.close()
    print(f"LOG: Updated order {order_id} status to {status} in local DB.")

def get_order_details(order_id):
    """Retrieves full details of an order from the local database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.order_id, o.cart_data, o.total_price, o.screenshot_path, c.full_name, c.phone_number, c.address
        FROM orders o JOIN customers c ON o.customer_id = c.telegram_id
        WHERE o.order_id = ?
    ''', (order_id,))
    details = cursor.fetchone()
    conn.close()
    if details:
        return {
            "order_id": details[0],
            "cart": json.loads(details[1]),
            "total_price": details[2],
            "screenshot_path": details[3],
            "name": details[4],
            "phone": details[5],
            "address": details[6]
        }
    return None

def get_order_customer_id(order_id):
    """Retrieves the customer's Telegram ID for a specific order."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id FROM orders WHERE order_id = ?", (order_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None