import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "data", "history.json")


def _ensure_file():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_history():
    _ensure_file()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_consultation(analysis):
    history = load_history()
    entry = {
        "date": datetime.now().isoformat(),
        "symptoms": analysis["symptoms"],
        "risk_level": analysis["risk_level"],
        "confidence": analysis["confidence"],
        "explanation": analysis["explanation"],
        "specialty": analysis["specialty"],
    }
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    return entry


def check_evolution(current_symptoms):
    history = load_history()
    if not history:
        return None

    current_set = {s.lower() for s in current_symptoms}
    for past in reversed(history[-5:]):
        past_set = {s.lower() for s in past["symptoms"]}
        common = current_set & past_set
        if common:
            return {
                "previous_date": past["date"],
                "previous_risk": past["risk_level"],
                "common_symptoms": list(common),
            }
    return None
