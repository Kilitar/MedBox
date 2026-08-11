import json
import threading
from pathlib import Path
from typing import Optional, List
from medbox.models import Medication, DoseLog

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MEDS_FILE = DATA_DIR / "medications.json"
LOG_FILE = DATA_DIR / "log.json"
STATE_FILE = DATA_DIR / "state.json"

_lock = threading.Lock()

def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_medications() -> List[Medication]:
    _ensure_data_dir()
    if not MEDS_FILE.exists():
        return []
    with _lock:
        with open(MEDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Medication(**item) for item in data]

def save_medications(meds: List[Medication]) -> None:
    _ensure_data_dir()
    with _lock:
        data = [med.__dict__ for med in meds]
        with open(MEDS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def load_log() -> List[DoseLog]:
    _ensure_data_dir()
    if not LOG_FILE.exists():
        return []
    with _lock:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [DoseLog(**item) for item in data]

def append_log_entry(entry: DoseLog) -> None:
    _ensure_data_dir()
    with _lock:
        logs = []
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(entry.__dict__)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

append_log = append_log_entry

def get_last_log_for_med(medication_id: str) -> Optional[DoseLog]:
    logs = load_log()
    med_logs = [log for log in logs if log.medication_id == medication_id]
    if not med_logs:
        return None
    med_logs.sort(key=lambda x: x.taken_dt, reverse=True)
    return med_logs[0]

def load_state() -> dict:
    _ensure_data_dir()
    if not STATE_FILE.exists():
        return {"alerted": {}}
    with _lock:
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "alerted" not in data:
                    data["alerted"] = {}
                return data
        except Exception:
            return {"alerted": {}}

def save_state(state: dict) -> None:
    _ensure_data_dir()
    with _lock:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
