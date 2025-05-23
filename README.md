# License Plate Recognition System

A PyQt5 desktop application that uses computer vision to detect license plates, extract text, and look up vehicle and driver information in a database.

## Features

- Live camera feed using OpenCV
- License plate detection using pre-trained models
- OCR for extracting letters and numbers from license plates
- SQLite database integration for vehicle and driver information lookup
- User-friendly interface for displaying results
- Plate management system for adding, editing, and deleting plates

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd <repository-directory>
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Prepare your pre-trained models:
   - Place your license plate detection model in `model/models/plate_detector.xml`
   - Place your OCR model in `model/models/ocr_model.pb`

## Usage

Run the application:
```
python main.py
```

1. Click "Start Camera" to begin the camera feed
2. When a license plate is visible, click "Detect Plate"
3. The system will detect the plate, extract its text, and display vehicle and driver information if found in the database
4. Use the "Manage Plates" button to add, edit, or delete plates in the database

## Project Structure

- `main.py`: Application entry point
- `config.py`: Configuration settings
- `ui/`
  - `main_window.py`: Main UI implementation
  - `plate_manager.py`: Plate management dialog
- `model/`
  - `plate_detector.py`: License plate detection and OCR logic
  - `models/`: Pre-trained models
    - `plate_detector.xml`: License plate detection model
    - `ocr_model.pb`: OCR model
    - `test_images/`: Test images for development
      - `sample_plates/`: Sample license plate images
      - `test_cases/`: Test cases for validation
- `database/`
  - `init_db.py`: Database operations
- `requirements.txt`: Required dependencies

## Database

The application uses an SQLite database with the following structure:

- `allowed_cars` table: Contains vehicle and owner information
  - plate_number (TEXT, PRIMARY KEY)
  - owner_name (TEXT, NOT NULL)
  - national_id (TEXT, NOT NULL)
  - phone_number (TEXT, NOT NULL)
  - car_model (TEXT)
  - car_color (TEXT)

- `detected_cars` table: Records detected license plates
  - id (INTEGER, PRIMARY KEY AUTOINCREMENT)
  - plate_number (TEXT, NOT NULL)
  - timestamp (TEXT, NOT NULL)

A sample database is automatically created if none exists.

## Requirements

- Python 3.7+
- PyQt5
- OpenCV
- SQLite3 (included with Python)
- Pre-trained models for license plate detection and character recognition 