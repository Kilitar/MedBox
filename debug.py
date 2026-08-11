import sys
import traceback

def run():
    try:
        from PyQt6.QtWidgets import QApplication
        from medbox.main import MedBoxApp
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        medbox = MedBoxApp(app)
        
        # Override the check_missed_on_startup for debugging
        print("Starting app loop...")
        app.exec()
    except Exception as e:
        print("ERROR:")
        traceback.print_exc()

if __name__ == '__main__':
    run()
