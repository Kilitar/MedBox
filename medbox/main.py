import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from medbox.models import Medication
from medbox.alert import MedAlertDialog
from medbox.config_ui import ConfigWindow
from medbox.dashboard import DashboardWindow

class MedBoxApp(QObject):
    show_alert_signal = pyqtSignal(object, object, object)
    
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.config_window = None
        self.dashboard_window = None
        self.active_dialogs = []

        self._setup_tray()
        self.show_alert_signal.connect(self._show_alert_dialog)
        self._start_daemon()
        
        QTimer.singleShot(2000, self.daemon.check_missed_on_startup)

    def _setup_tray(self):
        # Use a standard system icon to ensure it renders correctly on Windows
        icon = self.app.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        self.tray_icon = QSystemTrayIcon(icon, self.app)
        self.tray_icon.setToolTip("MedBox – Připomínač léků")

        menu = QMenu()
        
        title_action = menu.addAction("💊 MedBox")
        title_action.setEnabled(False)
        menu.addSeparator()

        config_action = menu.addAction("📋 Nastavení")
        config_action.triggered.connect(self._open_config)

        dashboard_action = menu.addAction("📊 Dashboard")
        dashboard_action.triggered.connect(self._open_dashboard)

        menu.addSeparator()
        quit_action = menu.addAction("❌ Ukončit")
        quit_action.triggered.connect(self._quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def _start_daemon(self):
        from medbox.daemon import MedDaemon
        self.daemon = MedDaemon(
            alert_callback=lambda med, sdt, od: self.show_alert_signal.emit(med, sdt, od)
        )
        self.daemon.start()

    def _show_alert_dialog(self, medication: Medication, scheduled_dt, overdue_delta):
        dialog = MedAlertDialog(medication, scheduled_dt, overdue_delta)
        self.active_dialogs.append(dialog)
        dialog.finished.connect(lambda: self.active_dialogs.remove(dialog) if dialog in self.active_dialogs else None)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _open_config(self):
        if not self.config_window:
            self.config_window = ConfigWindow()
        self.config_window.show()
        self.config_window.raise_()
        self.config_window.activateWindow()

    def _open_dashboard(self):
        if not self.dashboard_window:
            self.dashboard_window = DashboardWindow()
        self.dashboard_window.refresh_dashboard()
        self.dashboard_window.show()
        self.dashboard_window.raise_()
        self.dashboard_window.activateWindow()

    def _quit(self):
        if hasattr(self, 'daemon'):
            self.daemon.stop()
        self.app.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    medbox = MedBoxApp(app)
    sys.exit(app.exec())
