"""Spouštěč bez konzolového okna (přípona .pyw = pythonw)"""
import sys
import os

# Přidej adresář projektu do path
sys.path.insert(0, os.path.dirname(__file__))

from medbox.main import MedBoxApp
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    medbox = MedBoxApp(app)
    sys.exit(app.exec())
