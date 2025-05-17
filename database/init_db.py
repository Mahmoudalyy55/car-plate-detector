import sqlite3
from datetime import datetime

DB_NAME = "cars.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Allowed cars table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS allowed_cars (
            plate_number TEXT PRIMARY KEY,
            owner_name TEXT NOT NULL,
            national_id TEXT NOT NULL,
            phone_number TEXT NOT NULL
        )
    ''')

    # Detected cars table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detected_cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def add_allowed_car(plate_number, owner_name, national_id, phone_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO allowed_cars (plate_number, owner_name, national_id, phone_number)
            VALUES (?, ?, ?, ?)
        ''', (plate_number, owner_name, national_id, phone_number))
        conn.commit()
        print(f"✅ Car {plate_number} added successfully.")
    except sqlite3.IntegrityError:
        print(f"⚠️ Car with plate {plate_number} already exists.")
    finally:
        conn.close()

def remove_allowed_car(plate_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM allowed_cars WHERE plate_number = ?', (plate_number,))
    conn.commit()
    if cursor.rowcount == 0:
        print(f"⚠️ No car with plate {plate_number} found.")
    else:
        print(f"🗑️ Car {plate_number} removed successfully.")
    conn.close()

def get_all_allowed_cars():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM allowed_cars')
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_detected_car(plate_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO detected_cars (plate_number, timestamp) VALUES (?, ?)', (plate_number, timestamp))
    conn.commit()
    conn.close()

def get_all_detected_cars():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT plate_number, timestamp FROM detected_cars ORDER BY timestamp DESC')
    results = cursor.fetchall()
    conn.close()
    return results

def get_last_10_detected_cars():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT plate_number, timestamp FROM detected_cars ORDER BY timestamp DESC LIMIT 10')
    results = cursor.fetchall()
    conn.close()
    return results
