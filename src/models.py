import sqlite3
import bcrypt
from datetime import datetime


##### Beshary & Abdelkader #####

# Database connection
DB_PATH = "atm_system.db"

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed

def check_password(password, hashed):
    # Ensure the stored hash is bytes (sqlite may return str or memoryview)
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    if isinstance(hashed, memoryview):
        hashed = bytes(hashed)
    return bcrypt.checkpw(password.encode(), hashed)

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Account Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Account (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE, 
        password BLOB NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        national_id TEXT,
        balance REAL DEFAULT 0,
        currency_type TEXT DEFAULT 'EGP'
    )
    """)
    
    # Create Transactions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        state TEXT NOT NULL,
        sender INTEGER,
        recipient INTEGER,
        FOREIGN KEY(sender) REFERENCES Account(id),
        FOREIGN KEY(recipient) REFERENCES Account(id)
    )
    """)

    # Check if currency_type column exists in Account table, if not add it
    cursor.execute("PRAGMA table_info(Account)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'currency_type' not in columns:
        cursor.execute("ALTER TABLE Account ADD COLUMN currency_type TEXT DEFAULT 'EGP'")

    #create Donations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER,
        organization TEXT,
        amount REAL,
        date TEXT,
        currency_type TEXT DEFAULT 'EGP',
        FOREIGN KEY(donor_id) REFERENCES Account(id)
    )
    """)

     # Create Currency Table 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Currency (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        conversion_rate_to_egp REAL NOT NULL
    )
    """)
    
    # Check if Currency table is empty and insert default currencies
    cursor.execute("SELECT COUNT(*) FROM Currency")
    currency_count = cursor.fetchone()[0]
    
    if currency_count == 0:
        # Insert default currencies with their conversion rates to EGP
        default_currencies = [
            ('EGP', 1.0),      # Egyptian Pound (base currency)
            ('USD', 48.5),     # US Dollar
            ('EUR', 53.2),     # Euro
            ('GBP', 62.1),     # British Pound
            ('SAR', 12.9),     # Saudi Riyal
            ('AED', 13.2),     # UAE Dirham
            ('KWD', 159.8),    # Kuwaiti Dinar
            ('QAR', 13.3),     # Qatari Riyal
            ('JOD', 68.4),     # Jordanian Dinar
        ]
        
        cursor.executemany("""
            INSERT INTO Currency (name, conversion_rate_to_egp) VALUES (?, ?)
        """, default_currencies)
    
    conn.commit()
    conn.close()

##### Beshary & Abdelkader #####

##### HanaGamal

# Account Class
class Account:
    def __init__(self, username, password, email, phone, national_id, balance=0, currency_type='EGP'):
        self.username = username
        self.password = password
        self.email = email
        self.phone = phone
        self.national_id = national_id
        self.balance = balance
        self.currency_type = currency_type
    @staticmethod
    def create_account(username, password, email, phone, national_id, currency_type='EGP'):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(password)  
            cursor.execute("""
                INSERT INTO Account (username, password, email, phone, national_id, balance, currency_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, hashed_password, email, phone, national_id, 0, currency_type))
            conn.commit()
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
        return True

    @staticmethod
    def login(username, password):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Account WHERE username = ?
        """, (username,))
        result = cursor.fetchone()
        conn.close()
        if result:
            hashed_password = result[2]  
            if check_password(password, hashed_password):
                return result  
        return None  
    
    @staticmethod
    def is_username_unique(username):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Account WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is None

    @staticmethod
    def update_account_balance(UserId, amount):
        #Updates the balance of the account associated with the given username.
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            # Update the account balance
            cursor.execute("""
                UPDATE Account SET balance = balance + ? WHERE id = ?
            """, (amount, UserId))

            if cursor.rowcount == 0:  # No account was updated
                return {"success": False, "message": "User not found."}

            conn.commit()
        except sqlite3.Error as e:
            return {"success": False, "message": str(e)}
        finally:
            conn.close()

        return {"success": True}
    
    @staticmethod
    def deposit(user_id, amount):
        if amount <= 0:
            return "Deposit amount must be greater than zero."

        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Account SET balance = balance + ? WHERE id = ?
            """, (amount, user_id))

            if cursor.rowcount == 0:
                return "Account not found."

            conn.commit()
            Account.log_transaction("Deposit", amount, None, user_id)
            return "Deposit successful."
        except sqlite3.Error as e:
            return f"Error: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def log_transaction(transaction_type, amount, sender_id, recipient_id):
        """
        Logs a transaction to the Transactions table.

        Parameters:
        - transaction_type: Type of the transaction (e.g., "Transfer").
        - amount: Amount of the transaction.
        - sender_id: ID of the sender account.
        - recipient_id: ID of the recipient account.
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Transactions (type, date, amount, state, sender, recipient)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (transaction_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), amount, "Completed", sender_id, recipient_id))
            conn.commit()
        finally:
            conn.close()

## Hana Nazmy---------------            
    @staticmethod
    def update_currency_type(user_id, currency_type):
        """Updates the currency type for a specific account."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Account SET currency_type = ? WHERE id = ?
            """, (currency_type, user_id))

            if cursor.rowcount == 0:
                return {"success": False, "message": "User not found."}

            conn.commit()
        except sqlite3.Error as e:
            return {"success": False, "message": str(e)}
        finally:
            conn.close()

        return {"success": True}

    @staticmethod
    def get_account_currency(user_id):
        """Gets the currency type for a specific account."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT currency_type FROM Account WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()    
            
# Mohamed Alsaeed
    @staticmethod
    def view_account_balance(user_id):
        """Returns the current balance for a specific account."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT balance FROM Account WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
        
    @staticmethod
    def deposit(user_id, amount):
        if amount <= 0:
            return "Deposit amount must be greater than zero."

        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Account SET balance = balance + ? WHERE id = ?
            """, (amount, user_id))

            if cursor.rowcount == 0:
                return "Account not found."

            conn.commit()
            Account.log_transaction("Deposit", amount, None, user_id)
            return "Deposit successful."
        except sqlite3.Error as e:
            return f"Error: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def withdraw(user_id, amount):
        if amount <= 0:
            return "Withdrawal amount must be greater than zero."

        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT balance FROM Account WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return "Account not found."

            current_balance = row[0]
            if current_balance < amount:
                return "Insufficient balance."

            cursor.execute("""
                UPDATE Account SET balance = balance - ? WHERE id = ?
            """, (amount, user_id))

            conn.commit()
            Account.log_transaction("Withdraw", amount, user_id, None)
            return "Withdrawal successful."
        except sqlite3.Error as e:
            return f"Error: {str(e)}"
        finally:
            conn.close()

## Fatma ------------------
class Donation:
     @staticmethod
     def add_donation(donor_id, organization, amount, currency_type='EGP'):
        # Use a timeout to reduce likelihood of "database is locked" errors
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Donations (donor_id, organization, amount, date, currency_type)
                VALUES (?, ?, ?, ?, ?)
            """, (donor_id, organization, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), currency_type))
            cursor.execute("""
                UPDATE Account SET balance = balance - ? WHERE id = ?
            """, (amount, donor_id))
            conn.commit()
            return True, "Donation successful."
        except Exception as e:
            print("Error adding donation:", e)
            return False, f"Error: {str(e)}"
        finally:
            conn.close()
## Hana Nazmy
class Currency:
    @staticmethod
    def get_all_currencies():
        #Fetches all available currencies from the database.
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Currency")
        currencies = [row[0] for row in cursor.fetchall()]
        conn.close()
        return currencies
    
    @staticmethod
    def get_conversion_rate(currency_name):
        #Fetches the conversion rate of a specific currency.
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT conversion_rate_to_egp FROM Currency WHERE name = ?", (currency_name,))
        rate_row = cursor.fetchone()
        conn.close()
        return rate_row[0] if rate_row else None
