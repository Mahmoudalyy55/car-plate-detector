#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH, DB_SETTINGS

class DatabaseHandler:
    def __init__(self):
        self.setup_database()
    
    def setup_database(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Create tables based on config
            for table_name, table_info in DB_SETTINGS.items():
                columns = [f"{col_name} {col_type}" 
                          for col_name, col_type in table_info["columns"].items()]
                create_table_sql = f'''
                    CREATE TABLE IF NOT EXISTS {table_info["table_name"]} (
                        {", ".join(columns)}
                    )
                '''
                cursor.execute(create_table_sql)

            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def get_info_by_plate(self, plate_number):
        """Get car and driver information for a given plate number."""
        if not plate_number or plate_number == "None":
            return None, None
            
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get car and driver info
            cursor.execute('''
                SELECT plate_number, owner_name, national_id, phone_number, car_model, car_color
                FROM allowed_cars
                WHERE plate_number = ?
            ''', (plate_number,))
            
            result = cursor.fetchone()
            
            if result:
                # Convert to dictionaries
                car_info = {
                    "Plate Number": result[0],
                    "Model": result[4] or "N/A",
                    "Color": result[5] or "N/A"
                }
                
                driver_info = {
                    "Owner Name": result[1],
                    "National ID": result[2],
                    "Phone Number": result[3]
                }
                
                return car_info, driver_info
            
            return None, None
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def add_allowed_car(self, plate_number, owner_name, national_id, phone_number, car_model=None, car_color=None):
        # Validate required fields
        if not all([plate_number, owner_name, national_id, phone_number]):
            raise ValueError("Required fields cannot be empty")
            
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO allowed_cars (plate_number, owner_name, national_id, phone_number, car_model, car_color)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (plate_number, owner_name, national_id, phone_number, car_model, car_color))
            conn.commit()
            print(f"✅ Car {plate_number} added successfully.")
        except sqlite3.IntegrityError:
            print(f"⚠️ Car with plate {plate_number} already exists.")
            raise
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def remove_allowed_car(self, plate_number):
        if not plate_number:
            raise ValueError("Plate number cannot be empty")
            
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM allowed_cars WHERE plate_number = ?', (plate_number,))
            conn.commit()
            if cursor.rowcount == 0:
                print(f"⚠️ No car with plate {plate_number} found.")
            else:
                print(f"🗑️ Car {plate_number} removed successfully.")
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def get_all_allowed_cars(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM allowed_cars')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def add_detected_car(self, plate_number):
        if not plate_number or plate_number == "None":
            return
            
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('INSERT INTO detected_cars (plate_number, timestamp) VALUES (?, ?)', 
                         (plate_number, timestamp))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def get_all_detected_cars(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT plate_number, timestamp FROM detected_cars ORDER BY timestamp DESC')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def get_last_10_detected_cars(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT plate_number, timestamp FROM detected_cars ORDER BY timestamp DESC LIMIT 10')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
