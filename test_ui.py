import sys
from PyQt6.QtWidgets import QApplication, QLabel, QSystemTrayIcon, QStyle

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

label = QLabel('Test UI')
label.show()

icon = app.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
tray = QSystemTrayIcon(icon, app)
tray.show()

sys.exit(app.exec())
