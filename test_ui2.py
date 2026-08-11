import sys
import os
import time

log_file = "d:/Antigravity Projects/MedBox/test_ui_log.txt"

def log(msg):
    with open(log_file, "a") as f:
        f.write(msg + "\n")
    print(msg)

try:
    if os.path.exists(log_file):
        os.remove(log_file)
    log("1")
    from PyQt6.QtWidgets import QApplication, QLabel, QSystemTrayIcon, QStyle
    log("2")
    app = QApplication(sys.argv)
    log("3")
    app.setQuitOnLastWindowClosed(False)
    log("4")
    icon = app.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
    log("5")
    tray = QSystemTrayIcon(icon, app)
    log("6")
    tray.show()
    log("7")
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(2000, app.quit)
    log("8")
    app.exec()
    log("9")
except Exception as e:
    log(f"Err: {e}")
