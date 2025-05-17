#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QGroupBox, QSplitter,
                            QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor
import sqlite3

from model.plate_detector import PlateDetector
from database.init_db import DatabaseHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window properties
        self.setWindowTitle("License Plate Recognition System")
        self.setMinimumSize(1200, 800)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #2196F3;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 5px;
                border: none;
            }
            QLabel {
                font-size: 13px;
            }
        """)
        
        # Initialize components
        self.plate_detector = PlateDetector()
        self.db_handler = DatabaseHandler()
        
        # Initialize UI
        self.setup_ui()
        
        # Initialize camera
        self.camera_index = 0
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
    def setup_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Camera feed and detection
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Camera view with border
        camera_frame = QFrame()
        camera_frame.setFrameStyle(QFrame.StyledPanel)
        camera_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #2196F3;
                border-radius: 6px;
                background-color: black;
            }
        """)
        camera_layout = QVBoxLayout(camera_frame)
        
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        camera_layout.addWidget(self.camera_label)
        
        left_layout.addWidget(camera_frame)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.start_button = QPushButton("Start Camera")
        self.start_button.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
        self.start_button.clicked.connect(self.start_camera)
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.setIcon(self.style().standardIcon(self.style().SP_MediaStop))
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        self.detect_button = QPushButton("Detect Plate")
        self.detect_button.setIcon(self.style().standardIcon(self.style().SP_CommandLink))
        self.detect_button.clicked.connect(self.detect_plate)
        self.detect_button.setEnabled(False)
        control_layout.addWidget(self.detect_button)
        
        left_layout.addLayout(control_layout)
        
        # Detection results
        detection_group = QGroupBox("Detection Results")
        detection_layout = QVBoxLayout(detection_group)
        detection_layout.setSpacing(10)
        
        self.plate_label = QLabel("Plate Number: None")
        self.plate_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2196F3;
                padding: 10px;
                background-color: white;
                border-radius: 4px;
            }
        """)
        detection_layout.addWidget(self.plate_label)
        
        left_layout.addWidget(detection_group)
        
        # Right panel - Car and driver information
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Car information
        car_group = QGroupBox("Car Information")
        car_layout = QVBoxLayout(car_group)
        
        self.car_table = QTableWidget(0, 2)
        self.car_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.car_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.car_table.setAlternatingRowColors(True)
        self.car_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #E3F2FD;
            }
        """)
        car_layout.addWidget(self.car_table)
        
        right_layout.addWidget(car_group)
        
        # Driver information
        driver_group = QGroupBox("Driver Information")
        driver_layout = QVBoxLayout(driver_group)
        
        self.driver_table = QTableWidget(0, 2)
        self.driver_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.driver_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.driver_table.setAlternatingRowColors(True)
        self.driver_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #E3F2FD;
            }
        """)
        driver_layout.addWidget(self.driver_table)
        
        right_layout.addWidget(driver_group)
        
        # Add both panels to the main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 600])
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2196F3;
                width: 2px;
            }
        """)
        
        main_layout.addWidget(splitter)
    
    def start_camera(self):
        """Start the camera capture and timer."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if self.cap.isOpened():
                self.timer.start(30)  # Update every 30ms (approx. 33 fps)
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.detect_button.setEnabled(True)
            else:
                QMessageBox.warning(self, "Camera Error", "Failed to open camera. Please check if it's in use by another application.")
        except Exception as e:
            QMessageBox.critical(self, "Camera Error", f"Error starting camera: {str(e)}")
    
    def stop_camera(self):
        """Stop the camera capture and timer."""
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.detect_button.setEnabled(False)
    
    def update_frame(self):
        """Update the camera frame in the UI."""
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None and frame.size > 0:
                try:
                    # Convert to RGB for display (OpenCV uses BGR)
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Convert to QImage and display
                    h, w, ch = rgb_frame.shape
                    bytes_per_line = ch * w
                    q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    self.camera_label.setPixmap(QPixmap.fromImage(q_image).scaled(
                        self.camera_label.width(), self.camera_label.height(), 
                        Qt.KeepAspectRatio))
                except Exception as e:
                    print(f"Error updating frame: {str(e)}")
    
    def detect_plate(self):
        """Detect the license plate in the current frame."""
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                try:
                    # Use the plate detector model
                    plate_text = self.plate_detector.detect_and_recognize(frame)
                    self.plate_label.setText(f"Plate Number: {plate_text}")
                    
                    # Query the database for the plate
                    if plate_text != "None":
                        try:
                            # Add detected car to history
                            self.db_handler.add_detected_car(plate_text)
                            
                            # Get car and driver info
                            car_info, driver_info = self.db_handler.get_info_by_plate(plate_text)
                            if car_info and driver_info:
                                self.update_car_info(car_info)
                                self.update_driver_info(driver_info)
                            else:
                                self.plate_label.setText(f"Plate {plate_text} not found in database")
                                # Clear tables if no data found
                                self.car_table.setRowCount(0)
                                self.driver_table.setRowCount(0)
                        except sqlite3.Error as e:
                            QMessageBox.warning(self, "Database Error", f"Error accessing database: {str(e)}")
                            self.plate_label.setText("Database Error")
                            self.car_table.setRowCount(0)
                            self.driver_table.setRowCount(0)
                except Exception as e:
                    QMessageBox.warning(self, "Detection Error", f"Error detecting plate: {str(e)}")
                    self.plate_label.setText("Detection Error")
                    self.car_table.setRowCount(0)
                    self.driver_table.setRowCount(0)
    
    def update_car_info(self, car_info):
        """Update the car information table."""
        self.car_table.setRowCount(0)
        
        if car_info:
            for i, (key, value) in enumerate(car_info.items()):
                self.car_table.insertRow(i)
                self.car_table.setItem(i, 0, QTableWidgetItem(key))
                self.car_table.setItem(i, 1, QTableWidgetItem(str(value)))
    
    def update_driver_info(self, driver_info):
        """Update the driver information table."""
        self.driver_table.setRowCount(0)
        
        if driver_info:
            for i, (key, value) in enumerate(driver_info.items()):
                self.driver_table.insertRow(i)
                self.driver_table.setItem(i, 0, QTableWidgetItem(key))
                self.driver_table.setItem(i, 1, QTableWidgetItem(str(value)))
    
    def __del__(self):
        """Clean up resources when the window is closed."""
        self.stop_camera()
        if hasattr(self, 'db_handler'):
            del self.db_handler 