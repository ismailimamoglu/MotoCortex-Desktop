import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
from ui.styles import INDUSTRIAL_DARK_THEME

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MotoCortex Desktop - Diagnostic System")
        self.setMinimumSize(1024, 768)
        self.setStyleSheet(INDUSTRIAL_DARK_THEME)
        
        self.init_ui()
        logger.info("Main Window Initialized.")

    def init_ui(self):
        # Main central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header Row
        header_layout = QHBoxLayout()
        title_label = QLabel("MotoCortex ECU Diagnostics")
        title_label.setObjectName("title_label")
        
        self.connection_status = QLabel("STATUS: DISCONNECTED")
        self.connection_status.setObjectName("status_error")
        self.connection_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.connection_status)
        main_layout.addLayout(header_layout)

        # Content Grid
        content_layout = QGridLayout()
        
        # Left Panel - Controls
        control_group = QGroupBox("Hardware Controls")
        control_layout = QVBoxLayout()
        
        self.btn_connect = QPushButton("CONNECT TO ECU")
        self.btn_connect.clicked.connect(self.handle_connect)
        
        self.btn_read = QPushButton("READ PARAMETERS")
        self.btn_flash = QPushButton("FLASH FIRMWARE (BIN/HEX)")
        
        control_layout.addWidget(self.btn_connect)
        control_layout.addSpacing(20)
        control_layout.addWidget(self.btn_read)
        control_layout.addWidget(self.btn_flash)
        control_layout.addStretch()
        
        control_group.setLayout(control_layout)
        content_layout.addWidget(control_group, 0, 0, 1, 1)

        # Right Panel - Log Output
        log_group = QGroupBox("Serial Monitor / Telemetry Data")
        log_layout = QVBoxLayout()
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.append(">>> MotoCortex System Booting...")
        self.log_output.append(">>> Awaiting COM Port Configuration...")
        
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        
        content_layout.addWidget(log_group, 0, 1, 1, 3)
        
        # Add grid to main layout
        main_layout.addLayout(content_layout)

    def handle_connect(self):
        # Stub for connection logic
        logger.info("Connection button pressed.")
        self.log_output.append(">>> Attempting to establish serial connection...")
        # In a real scenario, this will interact with core/serial_connection.py
