import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QGroupBox, QGridLayout, QComboBox,
    QTabWidget, QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from ui.styles import INDUSTRIAL_DARK_THEME
from core.serial_connection import ECUConnection
from core.protocol_manager import ProtocolManager

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MotoCortex Desktop - Diagnostic System")
        self.setMinimumSize(1024, 768)
        self.setStyleSheet(INDUSTRIAL_DARK_THEME)
        
        self.ecu = ECUConnection()
        self.protocol = ProtocolManager(self.ecu)
        
        self.live_data_timer = QTimer(self)
        self.live_data_timer.timeout.connect(self.update_live_data)
        
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

        # Header Row - Global Connection Panel
        header_group = QGroupBox("Global Connection Panel")
        header_inner_layout = QHBoxLayout()
        header_inner_layout.setContentsMargins(15, 15, 15, 15)
        
        # Port Selection Area
        self.combo_ports = QComboBox()
        self.combo_ports.setMinimumHeight(40)
        self.combo_ports.setMinimumWidth(250)
        
        self.btn_refresh_ports = QPushButton("↻")
        self.btn_refresh_ports.setMinimumHeight(40)
        self.btn_refresh_ports.setMaximumWidth(60)
        self.btn_refresh_ports.clicked.connect(self.refresh_ports)
        
        self.btn_connect = QPushButton("CONNECT TO ECU")
        self.btn_connect.setMinimumWidth(200)
        self.btn_connect.clicked.connect(self.handle_connect)
        
        self.connection_status = QLabel("STATUS: DISCONNECTED")
        self.connection_status.setObjectName("status_error")
        self.connection_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        header_inner_layout.addWidget(self.combo_ports)
        header_inner_layout.addWidget(self.btn_refresh_ports)
        header_inner_layout.addSpacing(20)
        header_inner_layout.addWidget(self.btn_connect)
        header_inner_layout.addStretch()
        header_inner_layout.addWidget(self.connection_status)
        
        header_group.setLayout(header_inner_layout)
        main_layout.addWidget(header_group)

        # Content Split Layout (Tabs on Left, Log on Right)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Left Panel - Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14pt;
                background-color: #2b2b2b;
                color: #FFFFFF;
                border: 2px solid #555555;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3f3f3f;
                border-color: #00A8FF;
                border-bottom-color: transparent; 
            }
            QTabWidget::pane {
                border: 2px solid #555555;
                background-color: #1a1a1a;
                border-radius: 6px;
                padding: 10px;
                top: -2px;
            }
        """)
        
        self.tab_diagnostics = QWidget()
        self.tab_advanced = QWidget()
        self.tab_tuning = QWidget()
        
        self.tabs.addTab(self.tab_diagnostics, "Diagnostics")
        self.tabs.addTab(self.tab_advanced, "Advanced Functions")
        self.tabs.addTab(self.tab_tuning, "Tuning & Flashing")
        
        self.setup_diagnostics_tab()
        self.setup_advanced_tab()
        self.setup_tuning_tab()
        
        content_layout.addWidget(self.tabs, stretch=1)
        
        # Right Panel - Log Output
        log_group = QGroupBox("Serial Monitor / Telemetry Data")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(10, 15, 10, 10)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.append(">>> MotoCortex System Booting...")
        self.log_output.append(">>> Awaiting COM Port Configuration...")
        
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        
        content_layout.addWidget(log_group, stretch=1)
        
        # Add split layout to main layout
        main_layout.addLayout(content_layout, stretch=1)

    def setup_diagnostics_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        self.btn_read_dtc = QPushButton("Arıza Kodu (DTC) Oku")
        self.btn_read_dtc.setEnabled(False)
        self.btn_read_dtc.clicked.connect(self.handle_read_dtc)
        self.btn_clear_dtc = QPushButton("Arıza Kodu Sil")
        self.btn_clear_dtc.setEnabled(False)
        
        dtc_layout = QHBoxLayout()
        dtc_layout.addWidget(self.btn_read_dtc)
        dtc_layout.addWidget(self.btn_clear_dtc)
        layout.addLayout(dtc_layout)
        
        layout.addSpacing(10)
        
        live_data_layout = QHBoxLayout()
        live_data_label = QLabel("Canlı Veri İzleme (Live Data Monitoring):")
        live_data_label.setStyleSheet("font-weight: bold; color: #E0E0E0; font-size: 14pt;")
        
        self.btn_live_data = QPushButton("Canlı Veriyi Başlat")
        self.btn_live_data.setCheckable(True)
        self.btn_live_data.setEnabled(False)
        self.btn_live_data.clicked.connect(self.toggle_live_data)
        
        live_data_layout.addWidget(live_data_label)
        live_data_layout.addStretch()
        live_data_layout.addWidget(self.btn_live_data)
        
        layout.addLayout(live_data_layout)
        
        self.table_live_data = QTableWidget(5, 2)
        self.table_live_data.setHorizontalHeaderLabels(["DTC Kodu", "Açıklama"])
        self.table_live_data.horizontalHeader().setStretchLastSection(True)
        self.table_live_data.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_live_data.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b; 
                color: #FFFFFF;
                gridline-color: #555555;
                font-size: 13pt;
            }
            QHeaderView::section {
                background-color: #3f3f3f;
                padding: 5px;
                border: 1px solid #555555;
                font-weight: bold;
            }
        """)
        self.table_live_data.setEnabled(False)
        layout.addWidget(self.table_live_data)
        
        self.tab_diagnostics.setLayout(layout)

    def setup_advanced_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        self.btn_read_km = QPushButton("Orijinal KM Okuma")
        self.btn_read_km.setEnabled(False)
        self.btn_cancel_vmax = QPushButton("Hız Limiti (VMAX) İptali")
        self.btn_cancel_vmax.setEnabled(False)
        self.btn_cancel_immo = QPushButton("İmmobilizer (Immo) İptali")
        self.btn_cancel_immo.setEnabled(False)
        
        layout.addWidget(self.btn_read_km)
        layout.addWidget(self.btn_cancel_vmax)
        layout.addWidget(self.btn_cancel_immo)
        layout.addStretch()
        
        self.tab_advanced.setLayout(layout)

    def setup_tuning_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        warning_label = QLabel("⚠️ EN RİSKLİ BÖLGE / MOST RISKY AREA")
        warning_label.setStyleSheet("color: #FF3333; font-weight: bold; font-size: 16pt;")
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warning_label)
        
        layout.addSpacing(10)
        
        self.btn_read_ecu_id = QPushButton("ECU Kimliği (ID) Oku")
        self.btn_read_ecu_id.setEnabled(False)
        self.btn_read_map = QPushButton("Mevcut Haritayı İndir (Read BIN/HEX)")
        self.btn_read_map.setEnabled(False)
        self.btn_write_map = QPushButton("Chip Tuning / Yeni Harita Yükle (Write Flash)")
        self.btn_write_map.setStyleSheet("""
            QPushButton { background-color: #8B0000; color: white; border-color: #FF0000; }
            QPushButton:hover { background-color: #A52A2A; border-color: #FF3333; }
            QPushButton:disabled { background-color: #4A1010; color: #888888; border-color: #555555; }
        """)
        self.btn_write_map.setEnabled(False)
        
        layout.addWidget(self.btn_read_ecu_id)
        layout.addWidget(self.btn_read_map)
        layout.addWidget(self.btn_write_map)
        layout.addStretch()
        
        self.tab_tuning.setLayout(layout)

    def update_tab_buttons_state(self, connected):
        """Enable or disable all tab specific buttons based on connection state"""
        self.btn_read_dtc.setEnabled(connected)
        self.btn_clear_dtc.setEnabled(connected)
        self.btn_live_data.setEnabled(connected)
        self.table_live_data.setEnabled(connected)
        
        self.btn_read_km.setEnabled(connected)
        self.btn_cancel_vmax.setEnabled(connected)
        self.btn_cancel_immo.setEnabled(connected)
        
        self.btn_read_ecu_id.setEnabled(connected)
        self.btn_read_map.setEnabled(connected)
        self.btn_write_map.setEnabled(connected)

    def refresh_ports(self):
        """Scan for available serial ports and populate the combo box."""
        self.combo_ports.clear()
        
        # Always add the simulator option at the top
        self.combo_ports.addItem("SIMULATOR - MOCK ECU", "SIMULATOR")
        
        ports = self.ecu.list_available_ports()
        if not ports:
            self.log_output.append(">>> [INFO] Serial scanning done. Only Simulator available.")
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
                if port == "SIMULATOR":
                    self.log_output.append(">>> [INFO] Simulation Mode Engaged. No physical hardware required.")
                else:
                    self.log_output.append(f">>> [SUCCESS] Link established on {port}.")
                
                # Update UI for connected state
                self.btn_connect.setText("DISCONNECT")
                self.btn_connect.setStyleSheet("background-color: #00A8FF; color: black;")
                self.connection_status.setText(f"STATUS: CONNECTED ({port})")
                self.connection_status.setObjectName("status_ok")
                
                # Unblock operations
                self.update_tab_buttons_state(True)
                self.combo_ports.setEnabled(False)
            else:
                self.log_output.append(f">>> {msg}")
        else:
            # Disconnect
            self.ecu.disconnect()
            self.log_output.append(">>> Link disconnected.")
            
            if self.live_data_timer.isActive():
                self.btn_live_data.setChecked(False)
                self.toggle_live_data(False)
            
            # Update UI for disconnected state
            self.btn_connect.setText("CONNECT TO ECU")
            self.btn_connect.setStyleSheet("") # Revert to default stylesheet
            self.connection_status.setText("STATUS: DISCONNECTED")
            self.connection_status.setObjectName("status_error")
            
            # Block operations
            self.update_tab_buttons_state(False)
            self.combo_ports.setEnabled(True)
            
        # Refresh stylesheet to apply objectName changes dynamically
        self.connection_status.style().unpolish(self.connection_status)
        self.connection_status.style().polish(self.connection_status)

    def handle_read_dtc(self):
        """Handle the Read DTC button click by querying the ProtocolManager."""
        self.log_output.append(">>> Querying ECU for Diagnostic Trouble Codes...")
        try:
            dtcs = self.protocol.get_dtc()
        except Exception as e:
            self.log_output.append(f">>> [WARN] {str(e)}")
            return
            
        if self.live_data_timer.isActive():
            self.btn_live_data.setChecked(False)
            self.toggle_live_data(False)

        self.table_live_data.setHorizontalHeaderLabels(["DTC Kodu", "Açıklama"])
        self.table_live_data.setRowCount(len(dtcs))
        for row, dtc in enumerate(dtcs):
            code_item = QTableWidgetItem(dtc["code"])
            code_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            
            desc_item = QTableWidgetItem(dtc["description"])
            desc_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            
            self.table_live_data.setItem(row, 0, code_item)
            self.table_live_data.setItem(row, 1, desc_item)
            
        self.log_output.append(f">>> Fetched {len(dtcs)} DTC(s) from ECU.")

    def toggle_live_data(self, checked):
        if checked:
            self.btn_live_data.setText("Durdur")
            self.btn_live_data.setStyleSheet("background-color: #8B0000; color: white;")
            
            self.table_live_data.setHorizontalHeaderLabels(["Parametre", "Değer"])
            self.log_output.append(">>> Canlı Veri İzleme Başlatıldı...")
            self.update_live_data()
            self.live_data_timer.start(1000)
        else:
            self.btn_live_data.setText("Canlı Veriyi Başlat")
            self.btn_live_data.setStyleSheet("")
            
            self.live_data_timer.stop()
            self.log_output.append(">>> Canlı Veri İzleme Durduruldu.")

    def update_live_data(self):
        try:
            data = self.protocol.get_live_data()
        except Exception as e:
            self.log_output.append(f">>> [WARN] {str(e)}")
            return
            
        if data is None:
            return
            
        self.table_live_data.setRowCount(len(data))
        for row, (param, value) in enumerate(data.items()):
            param_item = QTableWidgetItem(param)
            param_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            
            value_item = QTableWidgetItem(str(value))
            value_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            
            self.table_live_data.setItem(row, 0, param_item)
            self.table_live_data.setItem(row, 1, value_item)
