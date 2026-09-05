import os
import json

from config import SCHEDULES_FILE, STORES_FILE, DEFAULT_TEMPLATES


def load_stores():
    stores = []
    if os.path.exists(STORES_FILE):
        with open(STORES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split(",")
                    if len(parts) >= 3:
                        stores.append({
                            "ip": parts[0].strip(),
                            "user": parts[1].strip(),
                            "pwd": parts[2].strip()
                        })
    return stores


def load_schedules():
    if os.path.exists(SCHEDULES_FILE):
        try:
            with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    save_schedules(DEFAULT_TEMPLATES)
    return DEFAULT_TEMPLATES


def save_schedules(schedules):
    with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, indent=2)
