import json
import re

CRITICAL_KEYWORDS = [
    "douleur thoracique", "poitrine", "chest pain",
    "difficulte a respirer", "essoufflement", "suffocation",
    "perte de conscience", "evanouissement",
    "saignement abondant", "hemorragie",
    "paralysie", "avc", "stroke",
    "convulsions",
    "overdose", "intoxication",
    "suicide", "se tuer",
]

VALID_RISK_LEVELS = ["low", "medium", "high"]
CONFIDENCE_THRESHOLD = 0.4


def validate_response(raw_response, original_symptoms):
    # Parse JSON
    try:
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if not json_match:
            return None, "Format JSON invalide"
        data = json.loads(json_match.group())
    except json.JSONDecodeError:
        return None, "Erreur de parsing JSON"

    # Champs requis
    for field in ["symptoms", "risk_level", "confidence", "explanation", "specialty"]:
        if field not in data:
            return None, f"Champ manquant : {field}"

    # Valeur risk_level
    if data["risk_level"] not in VALID_RISK_LEVELS:
        return None, f"Niveau de risque invalide : {data['risk_level']}"

    # Confiance
    try:
        data["confidence"] = float(data["confidence"])
        data["confidence"] = max(0.0, min(1.0, data["confidence"]))
    except (ValueError, TypeError):
        return None, "Score de confiance invalide"

    # Override : mots critiques
    symptoms_lower = original_symptoms.lower()
    for keyword in CRITICAL_KEYWORDS:
        if keyword in symptoms_lower:
            data["risk_level"] = "high"
            data["confidence"] = max(data["confidence"], 0.8)
            break

    # Flag confiance faible
    data["low_confidence"] = data["confidence"] < CONFIDENCE_THRESHOLD

    return data, None
