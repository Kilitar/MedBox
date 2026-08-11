import uuid
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QListWidgetItem, QFormLayout, 
                             QLineEdit, QComboBox, QTimeEdit, QSpinBox, 
                             QTextEdit, QCheckBox, QPushButton, QMessageBox)
from PyQt6.QtCore import QTime
from medbox.models import Medication
from medbox.storage import load_medications, save_medications

class ConfigWindow(QMainWindow):
    def __init__(self, parent=None, on_save_callback=None):
        super().__init__(parent)
        self.setWindowTitle("MedBox – Správa a Editace Léků")
        self.resize(700, 480)
        self.on_save_callback = on_save_callback
        self.medications = load_medications()
        self.selected_index = -1
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; color: #ffffff; }
            QWidget { color: #ffffff; }
            QListWidget { background-color: #181825; border: 1px solid #313244; }
            QLineEdit, QComboBox, QTimeEdit, QSpinBox, QTextEdit { 
                background-color: #313244; border: 1px solid #45475a; color: white; padding: 4px; 
            }
            QPushButton { background-color: #45475a; color: white; border: none; padding: 6px 12px; border-radius: 4px; }
            QPushButton:hover { background-color: #585b70; }
        """)

        self._init_ui()
        self._populate_list()

    def select_medication_by_id(self, med_id: str):
        self.medications = load_medications()
        self._populate_list()
        for idx, med in enumerate(self.medications):
            if med.id == med_id:
                self.list_widget.setCurrentRow(idx)
                break

    def _init_ui(self):
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)

        # Left panel: List
        left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._on_select)
        left_layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Přidat")
        self.add_btn.clicked.connect(self._add_med)
        self.del_btn = QPushButton("🗑 Smazat")
        self.del_btn.clicked.connect(self._del_med)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        left_layout.addLayout(btn_layout)

        layout.addLayout(left_layout, 1)

        # Right panel: Form
        right_layout = QVBoxLayout()
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.dosage_edit = QLineEdit()
        self.regularity_combo = QComboBox()
        self.regularity_combo.addItems(["critical", "high", "normal", "optional"])
        self.time_edit = QTimeEdit()
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 168)
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(60)
        self.active_check = QCheckBox("Aktivní")

        form.addRow("Název:", self.name_edit)
        form.addRow("Dávkování:", self.dosage_edit)
        form.addRow("Regularita:", self.regularity_combo)
        form.addRow("Čas (anchor):", self.time_edit)
        form.addRow("Interval (h):", self.interval_spin)
        form.addRow("Poznámka:", self.note_edit)
        form.addRow("", self.active_check)

        right_layout.addLayout(form)

        self.save_btn = QPushButton("💾 Uložit Vše")
        self.save_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b; font-weight: bold;")
        self.save_btn.clicked.connect(self._save_all)
        right_layout.addWidget(self.save_btn)

        layout.addLayout(right_layout, 2)
        self.setCentralWidget(main_widget)

    def _populate_list(self):
        self.list_widget.clear()
        for med in self.medications:
            status = "🟢" if med.active else "⚫"
            item = QListWidgetItem(f"{status} {med.name}")
            self.list_widget.addItem(item)

    def _on_select(self, row: int):
        if row < 0 or row >= len(self.medications):
            return
        self.selected_index = row
        med = self.medications[row]
        self.name_edit.setText(med.name)
        self.dosage_edit.setText(med.dosage)
        self.regularity_combo.setCurrentText(med.regularity)
        
        h, m = map(int, med.anchor_time.split(":"))
        self.time_edit.setTime(QTime(h, m))
        
        self.interval_spin.setValue(med.interval_hours)
        self.note_edit.setText(med.note)
        self.active_check.setChecked(med.active)

    def _update_current_from_form(self):
        if 0 <= self.selected_index < len(self.medications):
            med = self.medications[self.selected_index]
            med.name = self.name_edit.text()
            med.dosage = self.dosage_edit.text()
            med.regularity = self.regularity_combo.currentText()
            t = self.time_edit.time()
            med.anchor_time = f"{t.hour():02d}:{t.minute():02d}"
            med.interval_hours = self.interval_spin.value()
            med.note = self.note_edit.toPlainText()
            med.active = self.active_check.isChecked()

    def _add_med(self):
        new_med = Medication(
            id=f"med-{uuid.uuid4().hex[:6]}",
            name="Nový Lék",
            dosage="1 tbl",
            regularity="normal",
            anchor_time="12:00",
            interval_hours=24,
            note="",
            active=True
        )
        self.medications.append(new_med)
        self._populate_list()
        self.list_widget.setCurrentRow(len(self.medications) - 1)

    def _del_med(self):
        if 0 <= self.selected_index < len(self.medications):
            reply = QMessageBox.question(self, "Smazat Lék", "Opravdu chcete smazat tento lék?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.medications.pop(self.selected_index)
                self.selected_index = -1
                save_medications(self.medications)
                self._populate_list()
                if self.on_save_callback:
                    self.on_save_callback()

    def _save_all(self):
        self._update_current_from_form()
        save_medications(self.medications)
        self._populate_list()
        if self.on_save_callback:
            self.on_save_callback()
        QMessageBox.information(self, "Uloženo", "Konfigurace léků byla úspěšně uložena.")
