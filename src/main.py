import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import setup_exception_hook, log_info

def main():
    setup_exception_hook()
    log_info("Application starting...")
    
    app = QApplication(sys.argv)
    
    try:
        window = MainWindow()
        window.show()
        log_info("MainWindow shown.")
        sys.exit(app.exec())
    except Exception as e:
        log_info(f"Error in main loop: {e}")
        raise e

if __name__ == "__main__":
    main()
