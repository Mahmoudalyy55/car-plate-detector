#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# Application paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model", "models")
DB_PATH = os.path.join(BASE_DIR, "cars.db")

# Camera settings
CAMERA_INDEX = 0  # Default camera index
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Model paths
PLATE_DETECTOR_PATH = os.path.join(MODEL_DIR, "plate_detector.xml")
OCR_MODEL_PATH = os.path.join(MODEL_DIR, "ocr_model.pb")

# Database settings
DB_SETTINGS = {
    "allowed_cars": {
        "table_name": "allowed_cars",
        "columns": {
            "plate_number": "TEXT PRIMARY KEY",
            "owner_name": "TEXT NOT NULL",
            "national_id": "TEXT NOT NULL",
            "phone_number": "TEXT NOT NULL",
            "car_model": "TEXT",
            "car_color": "TEXT"
        }
    },
    "detected_cars": {
        "table_name": "detected_cars",
        "columns": {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "plate_number": "TEXT NOT NULL",
            "timestamp": "TEXT NOT NULL"
        }
    }
}

# UI settings
UI_SETTINGS = {
    "window_title": "License Plate Recognition System",
    "window_size": (1200, 800),
    "camera_size": (640, 480),
    "refresh_rate": 30  # ms
} 