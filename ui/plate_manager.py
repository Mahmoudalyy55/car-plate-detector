#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt

class PlateManagerDialog(QDialog):
    def __init__(self, db_handler, parent=None):
        super().__init__(parent)
        self.db_handler = db_handler
        self.setup_ui()
        self.load_plates()
        
    def setup_ui(self):
        self.setWindowTitle("Manage License Plates")
        self.setMinimumSize(800, 600)  
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Form for adding/editing plates
        form_group = QFormLayout()
        
        self.plate_input = QLineEdit()
        self.owner_input = QLineEdit()
        self.national_id_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.model_input = QLineEdit()
        self.color_input = QLineEdit()
        
        form_group.addRow("Plate Number:", self.plate_input)
        form_group.addRow("Owner Name:", self.owner_input)
        form_group.addRow("National ID:", self.national_id_input)
        form_group.addRow("Phone Number:", self.phone_input)
        form_group.addRow("Car Model:", self.model_input)
        form_group.addRow("Car Color:", self.color_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add/Update")
        self.add_button.clicked.connect(self.add_or_update_plate)
        button_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_plate)
        button_layout.addWidget(self.delete_button)
        
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_button)
        
        # Table for displaying plates
        self.plate_table = QTableWidget()
        self.plate_table.setColumnCount(6)
        self.plate_table.setHorizontalHeaderLabels([
            "Plate Number", "Owner Name", "National ID", 
            "Phone Number", "Car Model", "Car Color"
        ])
        self.plate_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.plate_table.setAlternatingRowColors(True)
        self.plate_table.itemClicked.connect(self.load_plate_data)
        
        # Add all widgets to main layout
        layout.addLayout(form_group)
        layout.addLayout(button_layout)
        layout.addWidget(self.plate_table)
        
    def load_plates(self):
        """Load all plates from the database into the table."""
        try:
            plates = self.db_handler.get_all_allowed_cars()
            self.plate_table.setRowCount(len(plates))
            
            for i, plate in enumerate(plates):
                for j, value in enumerate(plate):
                    item = QTableWidgetItem(str(value))
                    self.plate_table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load plates: {str(e)}")
    
    def load_plate_data(self, item):
        """Load selected plate data into the form."""
        row = item.row()
        self.plate_input.setText(self.plate_table.item(row, 0).text())
        self.owner_input.setText(self.plate_table.item(row, 1).text())
        self.national_id_input.setText(self.plate_table.item(row, 2).text())
        self.phone_input.setText(self.plate_table.item(row, 3).text())
        self.model_input.setText(self.plate_table.item(row, 4).text())
        self.color_input.setText(self.plate_table.item(row, 5).text())
    
    def add_or_update_plate(self):
        """Add or update a plate in the database."""
        try:
            plate_number = self.plate_input.text().strip()
            owner_name = self.owner_input.text().strip()
            national_id = self.national_id_input.text().strip()
            phone_number = self.phone_input.text().strip()
            car_model = self.model_input.text().strip()
            car_color = self.color_input.text().strip()
            
            if not all([plate_number, owner_name, national_id, phone_number]):
                QMessageBox.warning(self, "Error", "Required fields cannot be empty")
                return
            
            self.db_handler.add_allowed_car(
                plate_number, owner_name, national_id, 
                phone_number, car_model, car_color
            )
            
            self.load_plates()
            self.clear_form()
            QMessageBox.information(self, "Success", "Plate information saved successfully")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save plate: {str(e)}")
    
    def delete_plate(self):
        """Delete the selected plate from the database."""
        plate_number = self.plate_input.text().strip()
        if not plate_number:
            QMessageBox.warning(self, "Error", "No plate selected")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete plate {plate_number}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_handler.remove_allowed_car(plate_number)
                self.load_plates()
                self.clear_form()
                QMessageBox.information(self, "Success", "Plate deleted successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete plate: {str(e)}")
    
    def clear_form(self):
        """Clear all input fields."""
        self.plate_input.clear()
        self.owner_input.clear()
        self.national_id_input.clear()
        self.phone_input.clear()
        self.model_input.clear()
        self.color_input.clear() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt

class PlateManagerDialog(QDialog):
    def __init__(self, db_handler, parent=None):
        super().__init__(parent)
        self.db_handler = db_handler
        self.setup_ui()
        self.load_plates()
        
    def setup_ui(self):
        self.setWindowTitle("Manage License Plates")
        self.setMinimumSize(800, 600)
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Form for adding/editing plates
        form_group = QFormLayout()
        
        self.plate_input = QLineEdit()
        self.owner_input = QLineEdit()
        self.national_id_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.model_input = QLineEdit()
        self.color_input = QLineEdit()
        
        form_group.addRow("Plate Number:", self.plate_input)
        form_group.addRow("Owner Name:", self.owner_input)
        form_group.addRow("National ID:", self.national_id_input)
        form_group.addRow("Phone Number:", self.phone_input)
        form_group.addRow("Car Model:", self.model_input)
        form_group.addRow("Car Color:", self.color_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add/Update")
        self.add_button.clicked.connect(self.add_or_update_plate)
        button_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_plate)
        button_layout.addWidget(self.delete_button)
        
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_button)
        
        # Table for displaying plates
        self.plate_table = QTableWidget()
        self.plate_table.setColumnCount(6)
        self.plate_table.setHorizontalHeaderLabels([
            "Plate Number", "Owner Name", "National ID", 
            "Phone Number", "Car Model", "Car Color"
        ])
        self.plate_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.plate_table.setAlternatingRowColors(True)
        self.plate_table.itemClicked.connect(self.load_plate_data)
        
        # Add all widgets to main layout
        layout.addLayout(form_group)
        layout.addLayout(button_layout)
        layout.addWidget(self.plate_table)
        
    def load_plates(self):
        """Load all plates from the database into the table."""
        try:
            plates = self.db_handler.get_all_allowed_cars()
            self.plate_table.setRowCount(len(plates))
            
            for i, plate in enumerate(plates):
                for j, value in enumerate(plate):
                    item = QTableWidgetItem(str(value))
                    self.plate_table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load plates: {str(e)}")
    
    def load_plate_data(self, item):
        """Load selected plate data into the form."""
        row = item.row()
        self.plate_input.setText(self.plate_table.item(row, 0).text())
        self.owner_input.setText(self.plate_table.item(row, 1).text())
        self.national_id_input.setText(self.plate_table.item(row, 2).text())
        self.phone_input.setText(self.plate_table.item(row, 3).text())
        self.model_input.setText(self.plate_table.item(row, 4).text())
        self.color_input.setText(self.plate_table.item(row, 5).text())
    
    def add_or_update_plate(self):
        """Add or update a plate in the database."""
        try:
            plate_number = self.plate_input.text().strip()
            owner_name = self.owner_input.text().strip()
            national_id = self.national_id_input.text().strip()
            phone_number = self.phone_input.text().strip()
            car_model = self.model_input.text().strip()
            car_color = self.color_input.text().strip()
            
            if not all([plate_number, owner_name, national_id, phone_number]):
                QMessageBox.warning(self, "Error", "Required fields cannot be empty")
                return
            
            self.db_handler.add_allowed_car(
                plate_number, owner_name, national_id, 
                phone_number, car_model, car_color
            )
            
            self.load_plates()
            self.clear_form()
            QMessageBox.information(self, "Success", "Plate information saved successfully")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save plate: {str(e)}")
    
    def delete_plate(self):
        """Delete the selected plate from the database."""
        plate_number = self.plate_input.text().strip()
        if not plate_number:
            QMessageBox.warning(self, "Error", "No plate selected")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete plate {plate_number}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_handler.remove_allowed_car(plate_number)
                self.load_plates()
                self.clear_form()
                QMessageBox.information(self, "Success", "Plate deleted successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete plate: {str(e)}")
    
    def clear_form(self):
        """Clear all input fields."""
        self.plate_input.clear()
        self.owner_input.clear()
        self.national_id_input.clear()
        self.phone_input.clear()
        self.model_input.clear()
        self.color_input.clear() 