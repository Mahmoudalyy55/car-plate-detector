#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os

class PlateDetector:
    def __init__(self):
        """Initialize the license plate detector with pre-trained models."""
        # Define paths to models (these would be your actual model paths)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Placeholder paths for the pre-trained models
        self.plate_cascade_path = os.path.join(current_dir, "models", "plate_detector.xml")
        self.ocr_model_path = os.path.join(current_dir, "models", "ocr_model.pb")
        
        # Load license plate detector cascade (using OpenCV's cascade as placeholder)
        try:
            self.plate_cascade = cv2.CascadeClassifier(self.plate_cascade_path)
            # If your pre-trained model is not a cascade, replace with appropriate model loading
            print("License plate detector loaded successfully.")
        except Exception as e:
            print(f"Warning: Could not load license plate detector: {e}")
            # Fallback to OpenCV's default cascade as a placeholder
            self.plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Load OCR model (placeholder - replace with actual model loading)
        try:
            # This is a placeholder for your actual OCR model loading code
            print("OCR model loaded successfully.")
        except Exception as e:
            print(f"Warning: Could not load OCR model: {e}")
    
    def detect_plate(self, frame):
        """
        Detect license plates in a frame.
        
        Args:
            frame: Image frame from the camera
            
        Returns:
            List of detected license plate regions (x, y, w, h)
        """
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply some preprocessing to improve detection
        gray = cv2.equalizeHist(gray)
        
        # Detect license plates
        # In a real implementation, this would use your custom license plate detection model
        plates = self.plate_cascade.detectMultiScale(gray, 
                                                    scaleFactor=1.1, 
                                                    minNeighbors=5, 
                                                    minSize=(30, 30))
        
        return plates
    
    def preprocess_plate(self, plate_img):
        """
        Preprocess the license plate image for better OCR results.
        
        Args:
            plate_img: Cropped license plate image
            
        Returns:
            Preprocessed image ready for OCR
        """
        # Resize to a fixed size for OCR
        resized = cv2.resize(plate_img, (240, 80))
        
        # Convert to grayscale
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get black and white image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Additional preprocessing steps could include:
        # - Noise removal
        # - Perspective correction
        # - Character segmentation
        
        return thresh
    
    def recognize_characters(self, plate_img):
        """
        Recognize characters on the license plate using OCR.
        
        Args:
            plate_img: Preprocessed license plate image
            
        Returns:
            Recognized text from the license plate
        """
        # This is a placeholder for your actual OCR implementation
        # In a real implementation, this would use your pre-trained OCR model
        
        # Example OCR implementation using a deep learning model would go here
        # Your model would take the plate_img and return the recognized text
        
        # For this placeholder, we'll return a dummy license plate number
        return "ABC123"
    
    def detect_and_recognize(self, frame):
        """
        Detect license plates in the frame and recognize the characters.
        
        Args:
            frame: Image frame from the camera
            
        Returns:
            Recognized license plate text, or "None" if no plate is detected
        """
        # Make a copy of the frame for drawing
        result_frame = frame.copy()
        
        # Detect license plates
        plates = self.detect_plate(frame)
        
        # If no plates are detected, return None
        if len(plates) == 0:
            return "None"
        
        # Process each detected plate
        for (x, y, w, h) in plates:
            # Draw rectangle around the plate
            cv2.rectangle(result_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Extract the plate region
            plate_img = frame[y:y+h, x:x+w]
            
            # Preprocess the plate for OCR
            processed_plate = self.preprocess_plate(plate_img)
            
            # Recognize characters on the plate
            plate_text = self.recognize_characters(processed_plate)
            
            # Display the recognized text above the plate
            cv2.putText(result_frame, plate_text, (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            return plate_text
        
        return "None" 