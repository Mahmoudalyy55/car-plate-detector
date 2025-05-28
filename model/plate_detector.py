#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# plate_detector.py

from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np
import os
import torch

class PlateDetector:
    def __init__(self):
        """Initialize the license plate detector with pre-trained models."""
        # Define paths to models
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.plate_model_path = os.path.join(current_dir, r"D:\car-plate-detector\runs\detect\yolo_car_plate\weights\best.pt")
        self.ocr_model_path = os.path.join(current_dir, r"D:\car-plate-detector\runs\detect\yolo11m_car_plate\weights\best.pt")
        
        # Arabic character mapping
        self.arabic_mapping = {
            # Arabic Letters (used in Egyptian license plates)
            "alif": "أ",     # أ
            "baa": "ب",      # ب
            "taa": "ت",      # ت
            "tha": "ث",      # ث
            "jeem": "ج",     # ج
            "geem": "ج",     # ج (added as alias)
            "haa": "ح",      # ح
            "khaa": "خ",     # خ
            "daal": "د",     # د
            "dal": "ذ",      # ذ
            "thal": "ذ",     # ذ (optional alias)
            "raa": "ر",      # ر
            "zay": "ز",      # ز
            "seen": "س",     # س
            "sheen": "ش",    # ش
            "sad": "ص",      # ص
            "dad": "ض",      # ض
            "taa": "ط",       # ط
            "zaa": "ظ",      # ظ
            "ain": "ع",      # ع
            "aain": "ع",     # ع (added as alias)
            "ghain": "غ",    # غ
            "faa": "ف",      # ف
            "qaf": "ق",      # ق
            "kaf": "ك",      # ك
            "kaaf": "ك",     # ك (added as alias)
            "laam": "ل",     # ل
            "meem": "م",     # م
            "noon": "ن",     # ن
            "ha": "ه",       # ه
            "waw": "و",      # و
            "waaw": "و",     # و (added as alias)
            "yaa": "ي",      # ي
            "lamalef": "لا", # لا
            "hamza": "ء",    # ء

            # Arabic Numbers
            "0": "٠",  # ٠ - Zero
            "1": "١",  # ١ - One
            "2": "٢",  # ٢ - Two
            "3": "٣",  # ٣ - Three
            "4": "٤",  # ٤ - Four
            "5": "٥",  # ٥ - Five
            "6": "٦",  # ٦ - Six
            "7": "٧",  # ٧ - Seven
            "8": "٨",  # ٨ - Eight
            "9": "٩",  # ٩ - Nine
        }
        
        # Load YOLO model for plate detection
        try:
            self.plate_model = YOLO(self.plate_model_path)
            print("License plate detector model loaded successfully.")
        except Exception as e:
            print(f"Error: Could not load license plate detector model: {e}")
            raise

        # Load OCR model (also a YOLO model)
        try:
            self.ocr_model = YOLO(self.ocr_model_path)
            print("OCR model loaded successfully.")
        except Exception as e:
            print(f"Error: Could not load OCR model: {e}")
            raise

    def preprocess_plate(self, plate_img):
        """
        Preprocess the cropped plate image for OCR.
        Returns preprocessed image ready for OCR model.
        """
        # Convert to grayscale for processing
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Convert back to 3 channels (RGB) for YOLO model
        rgb_denoised = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
        
        return rgb_denoised

    def detect_plate(self, frame):
        """
        Detect license plates in the given frame.
        Returns list of detected bounding boxes and confidence scores.
        """
        results = self.plate_model(frame)
        plates = []

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()     # Bounding box coordinates
            scores = result.boxes.conf.cpu().numpy()    # Confidence scores
            classes = result.boxes.cls.cpu().numpy()    # Class IDs

            for box, score, cls in zip(boxes, scores, classes):
                if int(cls) == 0:  # Assuming class 0 is "license plate"
                    plates.append((box, score))

        return plates

    def recognize_text(self, plate_img):
        """
        Extract text from the cropped plate image using OCR model.
        Returns the recognized text.
        """
        # Preprocess the plate image
        processed_img = self.preprocess_plate(plate_img)
        
        # Get prediction from OCR model
        results = self.ocr_model(processed_img)
        
        # Process results to get text
        text = self.decode_output(results)
        
        return text

    def decode_output(self, results):
        """
        Decode the OCR model output to text.
        """
        text = ""
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            confs = result.boxes.conf.cpu().numpy()
            names = result.names  # Get class names from the model
            
            # Sort boxes from left to right
            sorted_indices = np.argsort(boxes[:, 0])
            boxes = boxes[sorted_indices]
            classes = classes[sorted_indices]
            confs = confs[sorted_indices]
            
            # Convert class indices to characters
            for cls, conf in zip(classes, confs):
                if conf > 0.5:  # Confidence threshold
                    # Get class name from model's class mapping
                    class_name = names[int(cls)]
                    # Convert to Arabic character
                    char = self.class_to_char(class_name)
                    text += char
        
        return text

    def class_to_char(self, class_name):
        """
        Convert class name to Arabic character.
        """
        return self.arabic_mapping.get(class_name.lower(), '')

    def detect_and_recognize(self, frame):
        """
        Detect license plates and extract their text.
        Returns list of dictionaries containing plate information.
        """
        plates = self.detect_plate(frame)

        detected_plates = []
        for box, score in plates:
            x1, y1, x2, y2 = map(int, box)
            plate_img = frame[y1:y2, x1:x2]

            # Extract text using OCR
            plate_text = self.recognize_text(plate_img)

            detected_plates.append({
                "text": plate_text,
                "bbox": [x1, y1, x2 - x1, y2 - y1],  # x, y, w, h format
                "confidence": float(score)
            })

            # Draw rectangle around plate
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, plate_text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return detected_plates