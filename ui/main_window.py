#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UI_SETTINGS, CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QGroupBox, QSplitter,
                            QFrame, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor
import sqlite3

from model.plate_detector import PlateDetector
from database.init_db import DatabaseHandler
from ui.plate_manager import PlateManagerDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window properties
        self.setWindowTitle(UI_SETTINGS["window_title"])
        self.setMinimumSize(*UI_SETTINGS["window_size"])
        
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
        self.camera_index = CAMERA_INDEX
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Initialize video playback
        self.video_file = None
        self.is_video = False
        
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
        self.camera_label.setMinimumSize(*UI_SETTINGS["camera_size"])
        camera_layout.addWidget(self.camera_label)
        
        left_layout.addWidget(camera_frame)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        # Camera controls
        self.start_button = QPushButton("Start Camera")
        self.start_button.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
        self.start_button.clicked.connect(self.toggle_camera)
        control_layout.addWidget(self.start_button)
        
<<<<<<< Updated upstream
=======
        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.setIcon(self.style().standardIcon(self.style().SP_MediaStop))
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        # File controls
        self.upload_image_button = QPushButton("Upload Image")
        self.upload_image_button.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
        self.upload_image_button.clicked.connect(self.upload_image)
        control_layout.addWidget(self.upload_image_button)
        
        self.upload_video_button = QPushButton("Upload Video")
        self.upload_video_button.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
        self.upload_video_button.clicked.connect(self.upload_video)
        control_layout.addWidget(self.upload_video_button)
        
        # Detection controls
        self.detect_button = QPushButton("Detect Plate")
        self.detect_button.setIcon(self.style().standardIcon(self.style().SP_CommandLink))
        self.detect_button.clicked.connect(self.detect_plate)
        self.detect_button.setEnabled(False)
        control_layout.addWidget(self.detect_button)
        
>>>>>>> Stashed changes
        self.manage_button = QPushButton("Manage Plates")
        self.manage_button.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
        self.manage_button.clicked.connect(self.show_plate_manager)
        control_layout.addWidget(self.manage_button)
        
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

    def upload_image(self):
        """Handle image file upload."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_name:
            # Stop camera if running
            if self.cap is not None:
                self.stop_camera()
            
            # Read and display image
            frame = cv2.imread(file_name)
            if frame is not None:
                self.display_frame(frame)
                self.detect_button.setEnabled(True)
                self.is_video = False
            else:
                QMessageBox.warning(self, "Error", "Failed to load image file.")

    def upload_video(self):
        """Handle video file upload."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_name:
            # Stop camera if running
            if self.cap is not None:
                self.stop_camera()
            
            # Open video file
            self.cap = cv2.VideoCapture(file_name)
            if self.cap.isOpened():
                self.video_file = file_name
                self.is_video = True
                self.timer.start(UI_SETTINGS["refresh_rate"])
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.detect_button.setEnabled(True)
            else:
                QMessageBox.warning(self, "Error", "Failed to load video file.")

    def display_frame(self, frame):
        """Display frame in the UI."""
        # Convert frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to QImage
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale image to fit label while maintaining aspect ratio
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.camera_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Display image
        self.camera_label.setPixmap(scaled_pixmap)
    
<<<<<<< Updated upstream
    def toggle_camera(self):
        """Toggle the camera on/off."""
        if self.cap is None or not self.cap.isOpened():
            try:
                self.cap = cv2.VideoCapture(self.camera_index)
                if self.cap.isOpened():
                    # Set camera properties
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
                    self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
                    
                    self.timer.start(UI_SETTINGS["refresh_rate"])
                    self.start_button.setText("Stop Camera")
                    self.start_button.setIcon(self.style().standardIcon(self.style().SP_MediaStop))
                else:
                    QMessageBox.warning(self, "Camera Error", "Failed to open camera. Please check if it's in use by another application.")
            except Exception as e:
                QMessageBox.critical(self, "Camera Error", f"Error starting camera: {str(e)}")
        else:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.start_button.setText("Start Camera")
            self.start_button.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
            # Clear the camera view
            self.camera_label.clear()
            # Reset plate detection display
            self.plate_label.setText("Plate Number: None")
            self.car_table.setRowCount(0)
            self.driver_table.setRowCount(0)
    
    def update_frame(self):
        """Update the camera frame in the UI and perform automatic plate detection."""
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None and frame.size > 0:
                try:
                    # Convert to RGB for display (OpenCV uses BGR)
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Perform automatic plate detection
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
                        print(f"Error detecting plate: {str(e)}")
                    
                    # Convert to QImage and display
                    h, w, ch = rgb_frame.shape
                    bytes_per_line = ch * w
                    q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    self.camera_label.setPixmap(QPixmap.fromImage(q_image).scaled(
                        self.camera_label.width(), self.camera_label.height(), 
                        Qt.KeepAspectRatio))
                except Exception as e:
                    print(f"Error updating frame: {str(e)}")
    
=======
    def start_camera(self):
        """Start the camera capture and timer."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if self.cap.isOpened():
                # Set camera properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
                self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
                
                self.timer.start(UI_SETTINGS["refresh_rate"])
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.detect_button.setEnabled(True)
                self.is_video = False
            else:
                QMessageBox.warning(self, "Camera Error", "Failed to open camera. Please check if it's in use by another application.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start camera: {str(e)}")

    def stop_camera(self):
        """Stop the camera capture and timer."""
        if self.cap is not None:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.detect_button.setEnabled(False)
            self.camera_label.clear()
            self.video_file = None
            self.is_video = False

    def update_frame(self):
        """Update the camera feed."""
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
            else:
                if self.is_video:
                    # Video ended, restart from beginning
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                else:
                    self.stop_camera()

    def detect_plate(self):
        """Detect license plates in the current frame."""
        if self.camera_label.pixmap() is not None:
            # Get current frame from camera or video
            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    return
            else:
                # Get frame from displayed image
                pixmap = self.camera_label.pixmap()
                image = pixmap.toImage()
                width = image.width()
                height = image.height()
                ptr = image.bits()
                ptr.setsize(height * width * 4)
                arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
                frame = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            
            try:
                # Detect plates
                detected_plates = self.plate_detector.detect_and_recognize(frame)
                
                if detected_plates:
                    # Update display with detection results
                    self.display_frame(frame)
                    
                    # Update plate label with first detected plate
                    plate = detected_plates[0]
                    self.plate_label.setText(f"Plate Number: {plate['text']}")
                    
                    # Look up vehicle information
                    car_info, driver_info = self.db_handler.get_info_by_plate(plate['text'])
                    if car_info and driver_info:
                        self.update_car_info(car_info)
                        self.update_driver_info(driver_info)
                    else:
                        self.car_table.setRowCount(0)
                        self.driver_table.setRowCount(0)
                else:
                    self.plate_label.setText("No plates detected")
                    self.car_table.setRowCount(0)
                    self.driver_table.setRowCount(0)
                    
            except Exception as e:
                QMessageBox.warning(self, "Detection Error", f"Error detecting plate: {str(e)}")

>>>>>>> Stashed changes
    def update_car_info(self, car_info):
        """Update car information table."""
        self.car_table.setRowCount(0)
        if car_info:
            self.car_table.setRowCount(2)
            self.car_table.setItem(0, 0, QTableWidgetItem("Model"))
            self.car_table.setItem(0, 1, QTableWidgetItem(car_info.get('Model', '')))
            self.car_table.setItem(1, 0, QTableWidgetItem("Color"))
            self.car_table.setItem(1, 1, QTableWidgetItem(car_info.get('Color', '')))

    def update_driver_info(self, driver_info):
        """Update driver information table."""
        self.driver_table.setRowCount(0)
        if driver_info:
            self.driver_table.setRowCount(4)
            self.driver_table.setItem(0, 0, QTableWidgetItem("Name"))
            self.driver_table.setItem(0, 1, QTableWidgetItem(driver_info.get('Owner Name', '')))
            self.driver_table.setItem(1, 0, QTableWidgetItem("National ID"))
            self.driver_table.setItem(1, 1, QTableWidgetItem(driver_info.get('National ID', '')))
            self.driver_table.setItem(2, 0, QTableWidgetItem("Phone"))
            self.driver_table.setItem(2, 1, QTableWidgetItem(driver_info.get('Phone Number', '')))
            self.driver_table.setItem(3, 0, QTableWidgetItem("Plate Number"))
            self.driver_table.setItem(3, 1, QTableWidgetItem(driver_info.get('Plate Number', '')))

    def show_plate_manager(self):
        """Show the plate management dialog."""
        dialog = PlateManagerDialog(self.db_handler, self)
        dialog.exec_()

    def __del__(self):
<<<<<<< Updated upstream
        """Clean up resources when the window is closed."""
        self.timer.stop()
        self.cap.release()
        self.cap = None
        if hasattr(self, 'db_handler'):
            del self.db_handler 
=======
        """Clean up resources."""
        if self.cap is not None:
            self.cap.release() 
>>>>>>> Stashed changes
