import threading
import time
from datetime import datetime, timedelta
from typing import Optional
from medbox.storage import (load_medications, load_state, save_state,
                             get_last_log_for_med)
from medbox.models import Medication

class MedDaemon(threading.Thread):
    """Background thread – každých 30 sekund kontroluje zda má vyskočit alert."""
    
    def __init__(self, alert_callback):
        super().__init__(daemon=True)
        self.alert_callback = alert_callback
        self._stop_event = threading.Event()
    
    def run(self):
        while not self._stop_event.is_set():
            self._check_medications()
            self._stop_event.wait(30)
    
    def stop(self):
        self._stop_event.set()
    
    def check_missed_on_startup(self):
        """Zavolat JEDNOU při startu – zkontroluje zmeškané dávky z minulosti."""
        self._check_medications(startup=True)
    
    def _get_next_scheduled(self, med: Medication) -> datetime:
        """
        Vypočítá datetime příští dávky pro daný lék.
        """
        last_log = get_last_log_for_med(med.id)
        if last_log:
            try:
                taken_dt = datetime.fromisoformat(last_log.taken_dt)
                return taken_dt + timedelta(hours=med.interval_hours)
            except ValueError:
                pass
        
        now = datetime.now()
        hours, minutes = map(int, med.anchor_time.split(":"))
        anchor = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        
        # Pokud anchor už proběhl před více než 24h nebo v minulosti dnes bez předchozího logu
        if anchor > now:
            # Anchor je dnes v budoucnu
            return anchor
        else:
            # Anchor je v minulosti dnes – pokud je zpoždění do 24h, považujeme ho za dávku ke splnění
            return anchor

    def _check_medications(self, startup: bool = False):
        meds = load_medications()
        now = datetime.now()
        state = load_state()
        alerted_dict = state.get("alerted", {})
        state_updated = False

        for med in meds:
            if not med.active:
                continue
            
            next_scheduled = self._get_next_scheduled(med)
            
            # Kontrola, zda už alert pro tento čas neproběhl
            last_alerted_iso = alerted_dict.get(med.id)
            if last_alerted_iso == next_scheduled.isoformat():
                continue

            # Čas nastal
            if next_scheduled <= now:
                overdue_seconds = (now - next_scheduled).total_seconds()
                overdue_delta = now - next_scheduled if overdue_seconds > 120 else None

                # Limit na dávky zmeškané maximálně o 24 hodin
                if overdue_seconds <= 86400:
                    alerted_dict[med.id] = next_scheduled.isoformat()
                    state_updated = True
                    self.alert_callback(med, next_scheduled, overdue_delta)

        if state_updated:
            state["alerted"] = alerted_dict
            save_state(state)
