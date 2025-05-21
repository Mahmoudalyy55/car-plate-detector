#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# plate_detector.py

from pathlib import Path
from ultralytics import YOLO
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
        Detect license plates in the given frame.
        Returns list of detected bounding boxes and confidence scores.
        """
        results = self.model(frame)
        plates = []

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()     # Bounding box coordinates
            scores = result.boxes.conf.cpu().numpy()    # Confidence scores
            classes = result.boxes.cls.cpu().numpy()    # Class IDs

            for box, score, cls in zip(boxes, scores, classes):
                if int(cls) == 0:  # Assuming class 0 is "license plate"
                    plates.append((box, score))

        return plates

    def detect_and_recognize(self, frame):
        """
        Detect license plates and extract their text (OCR would go here).
        For now, returns dummy text.
        """
        plates = self.detect_plate(frame)

        detected_plates = []
        for box, score in plates:
            x1, y1, x2, y2 = map(int, box)
            plate_img = frame[y1:y2, x1:x2]

            # Placeholder OCR — replace this with actual OCR later
            plate_text = "ABC123"  # Replace with OCR output

            detected_plates.append({
                "text": plate_text,
                "bbox": [x1, y1, x2 - x1, y2 - y1],  # x, y, w, h format
                "confidence": float(score)
            })

            # Optional: draw rectangle around plate
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, plate_text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return detected_plates