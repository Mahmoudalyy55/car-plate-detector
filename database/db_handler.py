# database/db_handler.py

# database/db_handler.py

import sqlite3
import os

class DatabaseHandler:
    def __init__(self, db_name="car_plates.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), "..", db_name)
        self.connection = None
        self.create_connection()
        self.create_table()

    def create_connection(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"Connected to database at {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS detected_plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL UNIQUE,
            car_model TEXT,
            driver_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def insert_plate(self, plate_number, car_model="Unknown", driver_name="Unknown"):
        sql = "INSERT OR IGNORE INTO detected_plates (plate_number, car_model, driver_name) VALUES (?, ?, ?)"
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (plate_number, car_model, driver_name))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting plate: {e}")
            return None

    def get_all_plates(self):
        sql = "SELECT * FROM detected_plates ORDER BY timestamp DESC"
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            print(f"Error fetching plates: {e}")
            return []

    def get_info_by_plate(self, plate_number):
        """
        Retrieve car and driver info for a given plate number.
        Returns a tuple: (car_model, driver_name)
        """
        sql = "SELECT car_model, driver_name FROM detected_plates WHERE plate_number = ?"
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (plate_number,))
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            else:
                # Return default values if plate is not found
                return "Unknown", "Unknown"
        except sqlite3.Error as e:
            print(f"Error fetching plate info: {e}")
            return "Unknown", "Unknown"