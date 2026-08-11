import sys
import os

log_file = "d:/Antigravity Projects/MedBox/startup_log.txt"

def log(msg):
    with open(log_file, "a") as f:
        f.write(msg + "\n")
    print(msg)

try:
    if os.path.exists(log_file):
        os.remove(log_file)
    
    log("1. Starting test")
    
    import PyQt6
    log(f"2. Imported PyQt6, version: {PyQt6.QtCore.QT_VERSION_STR if hasattr(PyQt6, 'QtCore') else 'unknown'}")
    
    from PyQt6.QtWidgets import QApplication, QLabel
    log("3. Imported QtWidgets")
    
    app = QApplication(sys.argv)
    log("4. Created QApplication")
    
    label = QLabel("Test")
    log("5. Created QLabel")
    
    label.show()
    log("6. Called label.show()")
    
    # Timeout after 2 seconds just in case it blocks
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(2000, app.quit)
    log("7. Set up timer, calling app.exec()")
    
    app.exec()
    log("8. Finished app.exec()")
    
except Exception as e:
    import traceback
    log(f"EXCEPTION: {str(e)}")
    log(traceback.format_exc())
