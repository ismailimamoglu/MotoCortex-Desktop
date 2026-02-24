import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger("MotoCortexDesktop")
    logger.info("Initializing MotoCortex Desktop Application...")
    
    app = QApplication(sys.argv)
    
    # Initialize main window
    window = MainWindow()
    window.show()
    
    logger.info("Application loop started.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
