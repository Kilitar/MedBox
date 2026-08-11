from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Medication:
    id: str                    # "med-001" atd.
    name: str                  # "Siofor 1000"
    dosage: str                # "1 tbl"
    regularity: str            # "critical" | "high" | "normal" | "optional"
    anchor_time: str           # "10:00" – výchozí čas první dávky
    interval_hours: int        # 24
    note: str                  # "po jídle"
    active: bool               # True/False

@dataclass
class DoseLog:
    id: str                    # uuid4 jako string
    medication_id: str
    medication_name: str
    scheduled_dt: str          # ISO format: "2026-08-11T10:00:00"
    taken_dt: str              # ISO format: "2026-08-11T10:14:32"
    delay_minutes: int         # kladné = pozdě, záporné = brzy
    missed: bool               # True pokud uživatel nezapsal (legacy/future use)
