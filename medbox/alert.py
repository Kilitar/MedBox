import uuid
import time
import threading
from datetime import datetime, timedelta
from typing import Optional

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QCheckBox, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QCloseEvent, QKeyEvent

from medbox.models import Medication, DoseLog
from medbox.storage import append_log_entry

try:
    import winsound
except ImportError:
    winsound = None

COLOR_MAP = {
    "critical": "#ff4444",
    "high": "#ff8800",
    "normal": "#4488ff",
    "optional": "#888888"
}

class MedAlertDialog(QDialog):
    def __init__(self, medication: Medication, scheduled_dt: datetime,
                 overdue_delta: Optional[timedelta] = None, parent=None):
        super().__init__(parent)
        self.medication = medication
        self.scheduled_dt = scheduled_dt
        self.overdue_delta = overdue_delta
        self.seconds_remaining = 10

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumSize(480, 360)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
            }
            QProgressBar {
                border: 2px solid #333;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #0f0f1b;
            }
            QProgressBar::chunk {
                background-color: #4e54c8;
            }
            QPushButton {
                background-color: #2e7d32;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
            }
        """)

        self._init_ui()
        self._start_timer()
        self.play_sound_async()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("💊 ČAS LÉKU")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        reg_color = COLOR_MAP.get(self.medication.regularity.lower(), "#888888")
        badge = QLabel(f" [{self.medication.regularity.upper()}] ")
        badge.setStyleSheet(f"background-color: {reg_color}; color: white; border-radius: 3px; font-weight: bold; padding: 2px 6px;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(badge)
        layout.addLayout(header_layout)

        # Details
        med_name = QLabel(self.medication.name)
        med_name.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        med_name.setStyleSheet("color: #ffffff;")
        layout.addWidget(med_name)

        details_str = f"<b>Dávkování:</b> {self.medication.dosage}"
        if self.medication.note:
            details_str += f"<br><b>Poznámka:</b> {self.medication.note}"
        details_label = QLabel(details_str)
        details_label.setFont(QFont("Arial", 12))
        layout.addWidget(details_label)

        sched_str = f"<b>Plánováno:</b> {self.scheduled_dt.strftime('%H:%M')}"
        sched_label = QLabel(sched_str)
        sched_label.setFont(QFont("Arial", 11))
        layout.addWidget(sched_label)

        # Overdue Warning
        if self.overdue_delta:
            total_seconds = int(self.overdue_delta.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            missed_str = f"⚠️ Zmeškáno o: ETA -{hours}h:{minutes:02d}min"
            missed_label = QLabel(missed_str)
            missed_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            missed_label.setStyleSheet("color: #ff4444; background-color: #331111; padding: 6px; border-radius: 4px;")
            layout.addWidget(missed_label)

        # Progress bar odpočet
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10)
        self.progress_bar.setValue(10)
        self.progress_bar.setFormat("Odpočet: 10s")
        layout.addWidget(self.progress_bar)

        # Checkbox & Button
        self.checkbox = QCheckBox("Vzal(a) jsem lék")
        self.checkbox.stateChanged.connect(self._toggle_button)
        layout.addWidget(self.checkbox)

        self.confirm_btn = QPushButton("POTVRDIT")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self._on_confirm)
        layout.addWidget(self.confirm_btn)

    def _start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_countdown)
        self.timer.start(1000)

    def _update_countdown(self):
        if self.seconds_remaining > 0:
            self.seconds_remaining -= 1
            self.progress_bar.setValue(self.seconds_remaining)
            self.progress_bar.setFormat(f"Odpočet: {self.seconds_remaining}s")
        else:
            self.timer.stop()
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Odpočet dokončen")

    def _toggle_button(self, state):
        self.confirm_btn.setEnabled(self.checkbox.isChecked())

    def _on_confirm(self):
        now = datetime.now()
        delay_min = int((now - self.scheduled_dt).total_seconds() / 60)
        log_entry = DoseLog(
            id=str(uuid.uuid4()),
            medication_id=self.medication.id,
            medication_name=self.medication.name,
            scheduled_dt=self.scheduled_dt.isoformat(),
            taken_dt=now.isoformat(),
            delay_minutes=delay_min,
            missed=False
        )
        append_log_entry(log_entry)
        self.accept()

    def play_sound_async(self):
        def _sound():
            if winsound:
                pattern = [(880, 150), (1100, 150), (1320, 200), (0, 100),
                           (880, 150), (1100, 150), (1320, 200), (0, 100),
                           (880, 150), (1100, 150), (1320, 400)]
                for _ in range(3):
                    for freq, dur in pattern:
                        if freq > 0:
                            winsound.Beep(freq, dur)
                        else:
                            time.sleep(dur / 1000.0)
                    time.sleep(0.6)
        threading.Thread(target=_sound, daemon=True).start()

    def closeEvent(self, event: QCloseEvent):
        event.ignore()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            event.ignore()
        else:
            super().keyPressEvent(event)
