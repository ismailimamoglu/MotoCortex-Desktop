import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QGroupBox, QGridLayout, QComboBox
)
from PyQt6.QtCore import Qt
from ui.styles import INDUSTRIAL_DARK_THEME
from core.serial_connection import ECUConnection

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MotoCortex Desktop - Diagnostic System")
        self.setMinimumSize(1024, 768)
        self.setStyleSheet(INDUSTRIAL_DARK_THEME)
        
        self.ecu = ECUConnection()
        
        self.init_ui()
        self.refresh_ports()
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
        
        # Port Selection Area
        port_layout = QHBoxLayout()
        self.combo_ports = QComboBox()
        self.combo_ports.setMinimumHeight(40)
        
        self.btn_refresh_ports = QPushButton("↻")
        self.btn_refresh_ports.setMinimumHeight(40)
        self.btn_refresh_ports.setMaximumWidth(60)
        self.btn_refresh_ports.clicked.connect(self.refresh_ports)
        
        port_layout.addWidget(self.combo_ports)
        port_layout.addWidget(self.btn_refresh_ports)
        
        self.btn_connect = QPushButton("CONNECT TO ECU")
        self.btn_connect.clicked.connect(self.handle_connect)
        
        self.btn_read = QPushButton("READ PARAMETERS")
        self.btn_read.setEnabled(False)
        self.btn_flash = QPushButton("FLASH FIRMWARE (BIN/HEX)")
        self.btn_flash.setEnabled(False)
        
        control_layout.addLayout(port_layout)
        control_layout.addSpacing(10)
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

    def refresh_ports(self):
        """Scan for available serial ports and populate the combo box."""
        self.combo_ports.clear()
        ports = self.ecu.list_available_ports()
        if not ports:
            self.combo_ports.addItem("No COM ports found")
            self.log_output.append(">>> [WARN] No active COM ports detected on the system.")
        else:
            for device, description in ports:
                self.combo_ports.addItem(f"{device} - {description}", device)
            self.log_output.append(f">>> Found {len(ports)} COM port(s).")

    def handle_connect(self):
        """Toggle connection to the selected serial port."""
        if self.btn_connect.text() == "CONNECT TO ECU":
            port = self.combo_ports.currentData()
            if not port:
                self.log_output.append(">>> [ERROR] Valid COM port must be selected.")
                return

            self.log_output.append(f">>> Attempting to connect to {port}...")
            
            success, msg = self.ecu.connect(port)
            if success:
                self.log_output.append(f">>> [SUCCESS] Link established on {port}.")
                # Update UI for connected state
                self.btn_connect.setText("DISCONNECT")
                self.btn_connect.setStyleSheet("background-color: #00A8FF; color: black;")
                self.connection_status.setText(f"STATUS: CONNECTED ({port})")
                self.connection_status.setObjectName("status_ok")
                
                # Unblock operations
                self.btn_read.setEnabled(True)
                self.btn_flash.setEnabled(True)
                self.combo_ports.setEnabled(False)
            else:
                self.log_output.append(f">>> {msg}")
        else:
            # Disconnect
            self.ecu.disconnect()
            self.log_output.append(">>> Link disconnected.")
            
            # Update UI for disconnected state
            self.btn_connect.setText("CONNECT TO ECU")
            self.btn_connect.setStyleSheet("") # Revert to default stylesheet
            self.connection_status.setText("STATUS: DISCONNECTED")
            self.connection_status.setObjectName("status_error")
            
            # Block operations
            self.btn_read.setEnabled(False)
            self.btn_flash.setEnabled(False)
            self.combo_ports.setEnabled(True)
            
        # Refresh stylesheet to apply objectName changes dynamically
        self.connection_status.style().unpolish(self.connection_status)
        self.connection_status.style().polish(self.connection_status)

