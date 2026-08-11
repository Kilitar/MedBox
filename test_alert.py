"""
Diagnostický test - spusť v konzoli:
python test_alert.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testuji PyQt6 import...")
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import QTimer
print("PyQt6 OK")

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

print("Načítám modely...")
from medbox.models import Medication
from medbox.storage import load_medications

print("Načítám léky...")
meds = load_medications()
print(f"Nalezeno {len(meds)} léků: {[m.name for m in meds]}")

print("Vytvářím testovací dialog...")
from datetime import datetime, timedelta
from medbox.alert import MedAlertDialog

med = meds[0] if meds else Medication("test","TestLék","1tbl","normal","10:00",24,"",True)
scheduled = datetime.now() - timedelta(hours=2)
overdue = timedelta(hours=2, minutes=30)

try:
    dialog = MedAlertDialog(med, scheduled, overdue)
    print("Dialog vytvořen, volám exec()...")
    result = dialog.exec()
    print(f"Dialog uzavřen s výsledkem: {result}")
except Exception as e:
    import traceback
    print(f"CHYBA: {e}")
    traceback.print_exc()

sys.exit(0)
