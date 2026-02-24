# Industrial High-Contrast Dark Theme for MotoCortexDesktop
# Designed for harsh lighting and touch screens

INDUSTRIAL_DARK_THEME = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    background-color: #121212;
    color: #FFFFFF;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14pt;
}

/* Large, high-contrast buttons for touch screens */
QPushButton {
    background-color: #2b2b2b;
    border: 2px solid #555555;
    border-radius: 8px;
    padding: 15px 30px;
    font-weight: bold;
    font-size: 16pt;
    color: #FFFFFF;
    min-height: 50px;
}

QPushButton:hover {
    background-color: #3f3f3f;
    border-color: #00A8FF;
}

QPushButton:pressed {
    background-color: #00A8FF;
    color: #000000;
}

/* Status Labels */
QLabel#status_ok {
    color: #00FF00;
    font-weight: bold;
    font-size: 18pt;
}

QLabel#status_error {
    color: #FF3333;
    font-weight: bold;
    font-size: 18pt;
}

QLabel#title_label {
    font-size: 24pt;
    font-weight: bold;
    color: #E0E0E0;
    margin-bottom: 20px;
}

/* Group Boxes for organizing logs and parameters */
QGroupBox {
    border: 2px solid #444444;
    border-radius: 6px;
    margin-top: 1.5ex;
    font-weight: bold;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 5px 0 5px;
    color: #00A8FF;
}

/* Text output for hex/serial data */
QTextEdit {
    background-color: #000000;
    color: #00FF00; /* Classic terminal green for raw data */
    font-family: 'Courier New', Consolas, monospace;
    font-size: 12pt;
    border: 2px solid #333333;
    border-radius: 4px;
    padding: 10px;
}
"""
