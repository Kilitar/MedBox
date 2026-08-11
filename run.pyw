"""Spouštěč bez konzolového okna (přípona .pyw = pythonw)"""
import sys
import os
import traceback

# Přidej adresář projektu do path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Zachycení chyb do log souboru (pythonw.exe nemá konzoli)
LOG_FILE = os.path.join(BASE_DIR, "data", "medbox_error.log")

def log_exception(exc_type, exc_value, exc_tb):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        import datetime
        f.write(f"\n=== {datetime.datetime.now().isoformat()} ===\n")
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)

sys.excepthook = log_exception

try:
    from medbox.main import MedBoxApp
    from PyQt6.QtWidgets import QApplication

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        medbox = MedBoxApp(app)
        sys.exit(app.exec())
except Exception:
    log_exception(*sys.exc_info())

