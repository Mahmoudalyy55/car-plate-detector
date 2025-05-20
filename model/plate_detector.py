#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# plate_detector.py

from pathlib import Path
from ultralytics import YOLO
import cv2


class PlateDetector:
    def __init__(self, model_path="model/best.pt"):
        """
        Initialize the YOLO model for license plate detection.
        """
        self.model_path = model_path
        self.model = self.load_model()

    def load_model(self):
        """
        Load the YOLO model from the specified path.
        """
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        model = YOLO(self.model_path)  # Load YOLO model
        print("YOLO model loaded successfully.")
        return model

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