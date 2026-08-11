import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QBrush
from PyQt6.QtCore import Qt

def run():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    try:
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor("#4e54c8")))
        painter.drawEllipse(2, 2, 28, 28)
        painter.setBrush(QBrush(QColor("#ffffff")))
        # Zde byla pouzita hexa hodnota 0x0084, ktera v PyQt6 obcas zpusobuje ValueError
        painter.drawText(pixmap.rect(), 0x0084, "M")
        painter.end()
        icon = QIcon(pixmap)
        tray = QSystemTrayIcon(icon, app)
        tray.show()
        print("Tray icon shown successfully")
    except Exception as e:
        print("Error showing tray:", e)
        sys.exit(1)
    
    # Exit shortly after
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(1000, app.quit)
    sys.exit(app.exec())

if __name__ == '__main__':
    run()
