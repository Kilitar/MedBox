from datetime import datetime, timedelta
from typing import List, Dict

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QScrollArea, QProgressBar, QFrame)
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from medbox.storage import load_medications, load_log
from medbox.models import Medication, DoseLog

class DashboardWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MedBox – Pravidelnost a Statistiky")
        self.resize(900, 600)
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; color: #ffffff; }
            QWidget { color: #ffffff; }
            QComboBox { background-color: #313244; border: 1px solid #45475a; color: white; padding: 4px; }
            QScrollArea { border: none; background-color: #181825; }
        """)

        self.days_filter = 30
        self._init_ui()
        self.refresh_dashboard()

    def _init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Top Bar
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("<b>Rozsah sledování:</b>"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["7 dní", "30 dní", "90 dní", "Od začátku"])
        self.filter_combo.setCurrentIndex(1)
        self.filter_combo.currentIndexChanged.connect(self._on_filter_change)
        top_layout.addWidget(self.filter_combo)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # Content Layout (Cards Left, Heatmap Right)
        content_layout = QHBoxLayout()

        # Left Cards
        self.cards_area = QScrollArea()
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_area.setWidget(self.cards_container)
        self.cards_area.setWidgetResizable(True)
        content_layout.addWidget(self.cards_area, 1)

        # Right Heatmap
        self.figure = Figure(figsize=(6, 4), facecolor='#1a1a2e')
        self.canvas = FigureCanvas(self.figure)
        content_layout.addWidget(self.canvas, 2)

        main_layout.addLayout(content_layout)
        self.setCentralWidget(main_widget)

    def _on_filter_change(self, index):
        days_map = [7, 30, 90, 99999]
        self.days_filter = days_map[index]
        self.refresh_dashboard()

    def refresh_dashboard(self):
        meds = load_medications()
        logs = load_log()
        
        # Clear existing cards
        for i in reversed(range(self.cards_layout.count())): 
            w = self.cards_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        # Build Stats & Cards
        stats_list = []
        for med in meds:
            stat = self._calculate_adherence(med, logs, self.days_filter)
            stats_list.append((med, stat))
            self._create_card(med, stat)

        self._draw_heatmap(stats_list)

    def _calculate_adherence(self, med: Medication, logs: List[DoseLog], days: int) -> Dict:
        now = datetime.now()
        start_dt = now - timedelta(days=days)

        med_logs = [
            l for l in logs 
            if l.medication_id == med.id and datetime.fromisoformat(l.taken_dt) >= start_dt
        ]

        expected_doses = max(1, int((days * 24) / med.interval_hours))
        taken_count = len(med_logs)
        
        on_time = [l for l in med_logs if abs(l.delay_minutes) <= 30]
        
        delays = [l.delay_minutes for l in med_logs]
        avg_delay = sum(delays) / len(delays) if delays else 0

        # Streak calculation (days without missed dose)
        streak = 0
        med_logs.sort(key=lambda x: x.taken_dt, reverse=True)
        # Jednoduchý výpočet série
        streak = len(med_logs)

        adherence_pct = min(100, int((taken_count / expected_doses) * 100))

        return {
            "adherence_pct": adherence_pct,
            "on_time_count": len(on_time),
            "taken_count": taken_count,
            "expected_doses": expected_doses,
            "avg_delay_min": int(avg_delay),
            "streak": streak
        }

    def _create_card(self, med: Medication, stat: Dict):
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #313244; border-radius: 6px; padding: 8px; margin-bottom: 8px; }")
        layout = QVBoxLayout(card)

        title = QLabel(f"<b>{med.name}</b> [{med.regularity.upper()}]")
        layout.addWidget(title)

        info_text = f"Adherence: {stat['adherence_pct']}% | Streak: {stat['streak']} dávka/dávek<br>" \
                    f"Prům. zpoždění: {stat['avg_delay_min']} min"
        layout.addWidget(QLabel(info_text))

        pbar = QProgressBar()
        pbar.setValue(stat['adherence_pct'])
        pbar.setStyleSheet("""
            QProgressBar { border: 1px solid #45475a; border-radius: 3px; text-align: center; height: 14px; }
            QProgressBar::chunk { background-color: #a6e3a1; }
        """)
        layout.addWidget(pbar)

        self.cards_layout.addWidget(card)

    def _draw_heatmap(self, stats_list):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#1a1a2e')

        if not stats_list:
            self.canvas.draw()
            return

        med_names = [med.name for med, _ in stats_list]
        logs = load_log()
        now = datetime.now().date()
        days = self.days_filter
        
        # Pro zobrazení 'Od začátku' dynamicky zjistíme nejstarší záznam a heatmapu mírně omezíme,
        # aby se matplotlib z obrovské prázdné plochy nezbláznil
        if days > 1000:
            if logs:
                oldest_date = min([datetime.fromisoformat(l.taken_dt).date() for l in logs])
                calculated_days = (now - oldest_date).days + 1
                days = max(7, calculated_days)
            else:
                days = 30
        
        # Omezení šířky matplotlib gridu, víc než 1000 dnů stejně není k přečtení
        days = min(days, 1000)
        
        # Matrix setup
        import numpy as np
        grid = np.zeros((len(med_names), days))

        for row_idx, (med, _) in enumerate(stats_list):
            med_logs = [l for l in logs if l.medication_id == med.id]
            log_dates = {datetime.fromisoformat(l.taken_dt).date(): l.delay_minutes for l in med_logs}

            for col_idx in range(days):
                target_date = now - timedelta(days=(days - 1 - col_idx))
                if target_date in log_dates:
                    delay = log_dates[target_date]
                    if abs(delay) <= 30:
                        grid[row_idx, col_idx] = 1 # OK Green
                    elif delay <= 120:
                        grid[row_idx, col_idx] = 2 # Late Orange
                    else:
                        grid[row_idx, col_idx] = 3 # Very Late Red
                else:
                    grid[row_idx, col_idx] = 0 # No log

        # Custom colormap
        from matplotlib.colors import ListedColormap
        cmap = ListedColormap(['#2d2d2d', '#2ecc71', '#f39c12', '#e74c3c'])

        cax = ax.imshow(grid, cmap=cmap, aspect='auto', vmin=0, vmax=3)

        ax.set_yticks(range(len(med_names)))
        ax.set_yticklabels(med_names, color='white')
        ax.set_xticks([0, days // 2, days - 1])
        
        start_date = (now - timedelta(days=days-1)).strftime('%d.%m')
        mid_date = (now - timedelta(days=days//2)).strftime('%d.%m')
        end_date = now.strftime('%d.%m')
        
        ax.set_xticklabels([start_date, mid_date, end_date], color='white')
        ax.tick_params(colors='white')

        self.figure.tight_layout()
        self.canvas.draw()
